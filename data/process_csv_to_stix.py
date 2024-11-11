import pandas as pd
import datetime as dt
import stix2
import time
import psutil
from pathlib import Path
import base64
import json


# 调整属性值为合适的数据类型
def apply_transformation(value, transformation):
    if transformation == "list":
        if not isinstance(value, list):
            value = list(value)

    elif transformation == "dict":
        if not isinstance(value, dict):
            value = dict(value)

    elif transformation == "iso":
        value = dt.datetime.utcfromtimestamp(value).isoformat() + "Z"

    elif transformation == "base64":
        value = json.dumps(value)
        value = base64.b64encode(value.encode()).decode()

        # ....后续可根据需要添加

    return value


# 构造并返回SDO对象
def stix_transform(mapping_dict, mapped_columns, row, row_count):
    observed_objects = {}  # 用于存储生成的SCO对象，以便构造ObservedData对象
    observed_time = []  # 用于存储对象被观测到的时间，以便构造ObservedData对象
    networktraffic_object = {}  # 存储NetworkTraffic需要的属性和对应的属性值
    ipv4address_object = []  # 存储IPv4Address的name属性的值
    attackpattern_object = {}  # 存储AttackPattern需要的属性和对应的属性值
    artifact_object = {}  # 存储Artifact需要的属性和对应的属性值

    # 要返回的SDO的对象， 初始化为空
    observed_data = None
    attack_pattern = None

    # 根据映射关系生成STIX属性并存储属性值
    for field in mapped_columns:
        try:
            property_value = row[field]  # 从数据集的行数据中获取属性值
            mapping = mapping_dict[field]  # 根据列名从映射字典获取映射关系
            stix_type = mapping["stix_object"]  # STIX对象类别
            object_property = mapping["object_property"]  # STIX对象属性
            transformation = mapping["transformation"]  # 属性值规定的数据类型

            # 将属性值调整为合适的数据类型
            property_value = apply_transformation(property_value, transformation)

            # 存入可能使用到的STIX对象的属性和对应的属性值，用于后续构建STIX对象
            if stix_type == "IPv4Address":
                ipv4address_object.append(property_value)
            elif stix_type == "NetworkTraffic":
                networktraffic_object[object_property] = property_value
            elif stix_type == "Artifact":
                artifact_object[object_property] = property_value
            elif stix_type == "AttackPattern":
                attackpattern_object[object_property] = property_value
            elif stix_type == "ObservedData":
                observed_time.append(property_value)

        except Exception as e:
            print(f"第 {row_count + 1} 行，{field} 列数据处理出错: {e}")
            continue

    # 构造STIX对象
    try:
        # 构造IPv4Address对象
        if len(ipv4address_object):
            # NetworkTraffic对象要用到的原地址对象id
            src_ref = None
            dst_ref = None
            for value in ipv4address_object:
                stix_sco_object = stix2.IPv4Address(value=value)
                if not src_ref:
                    src_ref = stix_sco_object.id
                else:
                    dst_ref = stix_sco_object.id
                observed_objects[str(len(observed_objects))] = stix_sco_object  # 添加SCO对象到 observed_objects

        # 构造NetworkTraffic对象
        if len(networktraffic_object) and len(ipv4address_object):
            # 判断必需属性是否存在，不存在则进行处理以保证对象创建时不会出错
            if "protocols" not in networktraffic_object:
                networktraffic_object["protocols"] = ["Unknown"]

            networktraffic_object["src_ref"] = src_ref
            networktraffic_object["dst_ref"] = dst_ref
            stix_sco_object = stix2.NetworkTraffic(**networktraffic_object)  # 用**操作符解包字典获取键值对作为参数
            observed_objects[str(len(observed_objects))] = stix_sco_object  # 添加SCO对象到 observed_objects

        # 构造Artifact对象
        if len(artifact_object):
            stix_sco_object = stix2.Artifact(**artifact_object)  # 用**操作符解包字典获取键值对作为参数
            observed_objects[str(len(observed_objects))] = stix_sco_object  # 添加SCO对象到 observed_objects

        # 构造ObservedData对象
        if len(observed_objects):
            # 判断必需属性是否存在，不存在则进行处理以保证对象创建时不会出错
            if len(observed_time) == 1:
                first_observed = observed_time[0]
                last_observed = observed_time[0]
            elif len(observed_time) > 1:
                first_observed = observed_time[0]
                last_observed = observed_time[1]
            else:
                first_observed = dt.datetime.utcnow().isoformat() + "Z"
                last_observed = dt.datetime.utcnow().isoformat() + "z"
            number_observed = 1  # 假设观察到一次
            observed_data = stix2.ObservedData(
                first_observed=first_observed,
                last_observed=last_observed,
                number_observed=number_observed,
                objects=observed_objects
            )

        # 构造AttackPattern对象
        if len(attackpattern_object):
            # 判断必需属性是否存在，不存在则进行处理以保证对象创建时不会出错
            if "name" not in attackpattern_object:
                attackpattern_object["name"] = "None"

            attack_pattern = stix2.AttackPattern(**attackpattern_object)  # 用**操作符解包字典获取键值对作为参数

    except Exception as e:
        print(f"第 {row_count + 1} 行数据扫描完后构造对象时出错: {e}")

    return observed_data, attack_pattern  # 返回SDO对象

# 数据端服务函数接口：把流量数据集文件转换成stix格式文件
def processCsvToStix(input_file):
    # 加载映射表，构造映射字典
    try:
        mapping_df = pd.read_csv("./mapping_table.csv")
        mapping_dict = {
            row.dataset_field: {
                # 列名对应的映射关系
                "stix_object": row.stix_object,  # STIX对象类别
                "object_property": row.object_property,  # 对应属性
                "transformation": row.transformation  # 属性值规定的数据类型
            }
            for row in mapping_df.itertuples(index=False)
        }
    except Exception as e:
        print(f"映射表加载错误：{e}")
        return

    # 根据数据集不同的文件类型选择不同的读取方式
    try:
        if input_file.suffix == ".csv":
            dataset = pd.read_csv(input_file)
        elif input_file.suffix == ".txt":
            dataset = pd.read_json(input_file, lines=True)
    except Exception as e:
        print(f"文件打开失败！：{e}")
        return

    mapped_columns = [col for col in dataset.columns if col in mapping_dict]  # 筛选有用列

    # 逐行处理数据集文件，最终生成stix数据文件
    output_directory = Path("./csv")  # 指定输出目录
    output_file = output_directory / f"{input_file.stem}_stix.jsonl"  # 自动命名生成文件
    with open(output_file, "w") as fp:
        batch_size = 1000  # 处理大文件时每次写入文件的批次大小
        buffer = []  # 写入缓存区
        file_size = dataset.shape[0]

        # 大数据集文件分批写入
        if file_size > 1000:
            # 逐行处理数据集
            for i in range(file_size):
                row_data = dataset.iloc[i]  # 获取行数据
                observed_data, attack_pattern = stix_transform(mapping_dict, mapped_columns, row_data, i)  # 构造STIX对象
                if observed_data:
                    # pretty=True为美化打印，JSON 对象会使用缩进和换行，使结构更清晰，便于阅读和调试；
                    # 如果 JSON 数据仅供机器读取或需要更高效的存储，通常建议去掉 pretty=True 以保持紧凑格式；
                    buffer.append(observed_data.serialize(pretty=True) + "\n")
                if attack_pattern:
                    buffer.append(attack_pattern.serialize(pretty=True) + "\n")

                # 分批写入数据
                if i != 0 and i % batch_size == 0:
                    print(f"已处理 {i + 1} 行，正在写入数据...")
                    try:
                        fp.writelines(buffer)  # 写入数据
                    except Exception as e:
                        print(f"写入失败：{e}")
                    buffer.clear()  # 清空缓冲区

            # 写入剩余数据
            if buffer:
                print("文件处理完成，正在写入剩余数据...")
                try:
                    fp.writelines(buffer)  # 写入剩余的数据
                except Exception as e:
                    print(f"写入失败：{e}")
                buffer.clear()

        # 小数据集直接写入
        else:
            # 逐行处理数据集
            for i in range(file_size):
                row_data = dataset.iloc[i]  # 获取行数据
                observed_data, attack_pattern = stix_transform(mapping_dict, mapped_columns, row_data, i)  # 构造STIX对象
                if observed_data:
                    # pretty=True为美化打印，JSON 对象会使用缩进和换行，使结构更清晰，便于阅读和调试；
                    # 如果 JSON 数据仅供机器读取或需要更高效的存储，通常建议去掉 pretty=True 以保持紧凑格式；
                    buffer.append(observed_data.serialize(pretty=True) + "\n")
                if attack_pattern:
                    buffer.append(attack_pattern.serialize(pretty=True) + "\n")

            # 写入数据
            if buffer:
                print("文件处理完成，正在写入数据...")
                try:
                    fp.writelines(buffer)  # 写入剩余的数据
                except Exception as e:
                    print(f"写入失败：{e}")
                buffer.clear()

    return output_file.resolve()  # 返回生成文件的文件路径（绝对路径）


if __name__ == '__main__':
    start_time = time.time()  # 开始计时
    process = psutil.Process()  # 获取当前进程

    # 测试：处理dataset文件夹中的所有文件并将生成文件放入stix_file文件夹
    print("开始处理数据集文件...")
    folder_path = Path("test_dataset")  # 指定要遍历的文件夹
    for file in folder_path.rglob("*"):
        print(f"正在处理文件：{file.name}")
        return_file = processCsvToStix(file)
        if Path.stat(return_file).st_size == 0:
            print(f"生成文件为空！{file.name} 文件处理失败！")
        else:
            print(f"{file.name} 文件处理成功！")

    # 结束时间和内存使用情况
    finish_time = time.time()
    memory_usage = process.memory_info().rss / 1024 / 1024  # 以 MB 为单位
    print("-------------------****************************************************************-------------------")
    print(f"所有文件处理完成! 耗时 {(finish_time - start_time):.2f} 秒")
    print(f"内存使用: {memory_usage:.2f} MB")