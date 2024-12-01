import pandas as pd
import datetime as dt
import stix2
import time
from pathlib import Path
import base64
import json
import uuid
import numpy as np
import os
from utils.file import get_project_root_path,get_sha256_hash
# 调整属性值为合适的数据类型
def apply_transformation(value, transformation):
    if transformation == "list":
        if not isinstance(value, list):
            if not isinstance(value, str):
                value = [value]
            else:
                value = list(value)

    elif transformation == "dict":
        if not isinstance(value, dict):
            value = dict(value)

    elif transformation == "iso":
        value = dt.datetime.fromtimestamp(value, tz=dt.timezone.utc).isoformat()

    elif transformation == "base64":
        value = json.dumps(value)
        value = base64.b64encode(value.encode()).decode()

    # ....后续可根据需要添加

    # 如不需特殊转换（值为none），则检查数据格式是否满足stix库的序列化要求（如不能为numpy.int64 类型的数值，值不能为NaN等）
    else:
        if isinstance(value, (np.int64, np.int32)):
            value = int(value)
        elif pd.isna(value):
            value = 0

    return value


# 构造并返回SDO对象
def stix_transform(mapping_dict, mapped_columns, row, row_count)->tuple[stix2.ObservedData,stix2.AttackPattern,dict]:
    """
        构造并返回SDO对象
        param:
            mapping_dict:映射字典
            mapped_columns:数据集的列名
            row:数据集的行数据
            row_count:行索引
        return:
            observed_data:ObservedData对象
            attack_pattern:AttackPattern对象
            stix_record:额外记录
    """

    observed_objects = {}  # 用于存储生成的SCO对象，以便构造ObservedData对象
    observed_time = []  # 用于存储对象被观测到的时间，以便构造ObservedData对象
    networktraffic_object = {}  # 存储NetworkTraffic需要的属性和对应的属性值
    ipv4address_object = []  # 存储IPv4Address的value属性的值
    attackpattern_object = {}  # 存储AttackPattern需要的属性和对应的属性值
    artifact_object = {}  # 存储Artifact需要的属性和对应的属性值
    url_object = {}  # 存储URL对象需要的属性和对应的属性值
    networktraffic_extensions = {}  # 存储NetworkTraffic的扩展字段

    # 要返回的SDO的对象，初始化为空
    observed_data = None
    attack_pattern = None
    # 额外记录
    stix_record = {
        "ips_list":[]
    }
    # 根据映射关系生成STIX属性并存储属性值，未知映射关系的统一放入NetworkTraffic的扩展字段
    for field in mapped_columns:
        try:
            # 已知映射关系
            if field in mapping_dict:
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
                    #记录一份到本地数据库
                    stix_record["ips_list"].append(property_value)
                elif stix_type == "NetworkTraffic":
                    networktraffic_object[object_property] = property_value
                elif stix_type == "Artifact":
                    artifact_object[object_property] = property_value
                elif stix_type == "AttackPattern":
                    attackpattern_object[object_property] = property_value
                elif stix_type == "ObservedData":
                    observed_time.append(property_value)
                elif stix_type == "URL":
                    url_object[object_property] = property_value

            # 未知映射关系
            else:
                property_value = row[field]  # 从数据集的行数据中获取属性值
                # 将属性值调整为合适的数据类型
                property_value = apply_transformation(property_value, "none")

                networktraffic_extensions[field] = property_value

        except Exception as e:
            print(f"第 {row_count + 1} 行，{field} 列数据处理出错: {e}")
            continue

    # 构造STIX对象
    try:
        # 构造IPv4Address对象
        if len(ipv4address_object):
            create_name = "IPv4Address"
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
        # 既有NetworkTraffic属性且有IPv4Address对象时：
        if len(networktraffic_object) and len(ipv4address_object):
            create_name = "NetworkTraffic"
            # 判断必需属性是否存在，不存在则进行处理以保证对象创建时不会出错
            if "protocols" not in networktraffic_object:
                networktraffic_object["protocols"] = ["NULL"]

            networktraffic_object["src_ref"] = src_ref
            networktraffic_object["dst_ref"] = dst_ref
            networktraffic_object["extensions"] = {f"extension-definition--{uuid.uuid4()}": {**networktraffic_extensions}}
            stix_sco_object = stix2.NetworkTraffic(**networktraffic_object)  # 用**操作符解包字典获取键值对作为参数
            observed_objects[str(len(observed_objects))] = stix_sco_object  # 添加SCO对象到 observed_objects
        # 有NetworkTraffic属性但没有IPv4Address对象时：
        elif len(networktraffic_object):
            create_name = "NetworkTraffic"
            # 判断必需属性是否存在，不存在则进行处理以保证对象创建时不会出错
            if "protocols" not in networktraffic_object:
                networktraffic_object["protocols"] = ["NULL"]

            networktraffic_object["src_ref"] = f"ipv4-addr--{uuid.uuid4()}"
            networktraffic_object["extensions"] = {f"extension-definition--{uuid.uuid4()}": {**networktraffic_extensions}}
            stix_sco_object = stix2.NetworkTraffic(**networktraffic_object)  # 用**操作符解包字典获取键值对作为参数
            observed_objects[str(len(observed_objects))] = stix_sco_object  # 添加SCO对象到 observed_objects
        # 只有extensions属性时：
        elif len(networktraffic_extensions):
            create_name = "NetworkTraffic"
            stix_sco_object = stix2.NetworkTraffic(
                src_ref=f"ipv4-addr--{uuid.uuid4()}",
                protocols=["NULL"],
                extensions={f"extension-definition--{uuid.uuid4()}": {**networktraffic_extensions}}
            )
            observed_objects[str(len(observed_objects))] = stix_sco_object  # 添加SCO对象到 observed_objects

        # 构造Artifact对象
        if len(artifact_object):
            create_name = "Artifact"
            # 判断必需属性是否存在，不存在则进行处理以保证对象创建时不会出错
            if "mime_type" not in artifact_object:
                artifact_object["mime_type"] = "NULL"

            stix_sco_object = stix2.Artifact(**artifact_object)  # 用**操作符解包字典获取键值对作为参数
            observed_objects[str(len(observed_objects))] = stix_sco_object  # 添加SCO对象到 observed_objects

        # 构造URL对象
        if len(url_object):
            create_name = "URL"
            # 判断必需属性是否存在，不存在则进行处理以保证对象创建时不会出错
            if "value" not in url_object:
                url_object["value"] = "NULL"
            elif not url_object["value"]:
                url_object["value"] = "NULL"

            stix_sco_object = stix2.URL(**url_object)  # 用**操作符解包字典获取键值对作为参数
            observed_objects[str(len(observed_objects))] = stix_sco_object  # 添加SCO对象到 observed_objects

        # 构造ObservedData对象
        if len(observed_objects):
            create_name = "ObservedData"
            try:
                # 判断必需属性是否存在，不存在则使用当前时间
                if len(observed_time) == 1:
                    first_observed = observed_time[0]
                    last_observed = observed_time[0]
                elif len(observed_time) > 1:
                    first_observed = observed_time[0]
                    last_observed = observed_time[1]
                else:
                    # 如果没有观察时间，使用当前时间
                    current_time = dt.datetime.now(dt.timezone.utc)
                    first_observed = current_time
                    last_observed = current_time

                # 确保时间对象是datetime类型
                if isinstance(first_observed, str):
                    first_observed = dt.datetime.fromisoformat(first_observed.rstrip('Z'))
                if isinstance(last_observed, str):
                    last_observed = dt.datetime.fromisoformat(last_observed.rstrip('Z'))

                # 确保时间对象有时区信息
                if first_observed.tzinfo is None:
                    first_observed = first_observed.replace(tzinfo=dt.timezone.utc)
                if last_observed.tzinfo is None:
                    last_observed = last_observed.replace(tzinfo=dt.timezone.utc)

                # 转换为STIX所需的ISO格式
                first_observed = first_observed.isoformat().replace('+00:00', 'Z')
                last_observed = last_observed.isoformat().replace('+00:00', 'Z')

                number_observed = 1  # 假设观察到一次
                observed_data = stix2.ObservedData(
                    first_observed=first_observed,
                    last_observed=last_observed,
                    number_observed=number_observed,
                    objects=observed_objects
                )
            except Exception as e:
                print(f"时间格式处理错误: {e}")
                # 发生错误时使用当前时间作为后备方案
                current_time = dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z')
                observed_data = stix2.ObservedData(
                    first_observed=current_time,
                    last_observed=current_time,
                    number_observed=1,
                    objects=observed_objects
                )

        # 构造AttackPattern对象
        if len(attackpattern_object):
            create_name = "AttackPattern"
            # 判断必需属性是否存在，不存在则进行处理以保证对象创建时不会出错
            if "name" not in attackpattern_object:
                attackpattern_object["name"] = "None"

            attack_pattern = stix2.AttackPattern(**attackpattern_object)  # 用**操作符解包字典获取键值对作为参数

    except Exception as e:
        print(f"第 {row_count + 1} 行数据扫描完后构造对象 {create_name} 时出错: {e}")

    return observed_data, attack_pattern, stix_record# 返回SDO对象


# 数据端服务函数接口：把流量数据集文件转换成stix格式文件
def process_dataset_to_stix(data_service, input_file_path:str, file_hash:str, process_config:dict):
    """
        把流量数据集文件转换成stix格式文件
        param:
            data_service:DataService实例
            input_file_path:流量数据集文件路径
            file_hash:流量数据集文件hash
            process_config:stix处理配置
        return:
            output_file_path:stix格式文件路径
            error:错误信息
    """

    input_file = Path(input_file_path)  # 传入的要进行处理的数据集
    # 加载映射表，构造映射字典
    try:
        data_path = get_project_root_path()+"/data"  # 获取当前项目根目录绝对路径
        mapping_df = pd.read_csv(data_path+"/feature_mapping.csv")  # 读取映射表
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
        return None,f"映射表加载错误：{e}"

    # 根据数据集不同的文件类型选择不同的读取方式
    try:
        if input_file.suffix == ".csv":
            dataset = pd.read_csv(input_file)
        elif input_file.suffix == ".txt":
            dataset = pd.read_json(input_file, lines=True)
        elif input_file.suffix == ".xlsx":
            dataset = pd.read_excel(input_file)
    except Exception as e:
        print(f"文件打开失败！：{e}")
        return None,f"文件打开失败！：{e}"
    # 添加检查
    if dataset.empty:
        return None,f"数据集为空！"
    
    mapped_columns = dataset.columns  # 获取数据集的列名

    # 逐行处理数据集文件，最终生成stix数据文件
    output_directory = data_service.get_stix_output_dir_path(file_hash)
    # 检测是否有数据压缩配置
    stix_compress = 500 # 默认压缩500行
    if process_config.get("stix_compress",None):
        stix_compress = process_config.get("stix_compress")
    else:
        stix_compress = 100  # 默认压缩100行
    row_length = dataset.shape[0]  # 数据集行数
    
    # 计算需要分批写入的次数
    batch_count = max(1,row_length // stix_compress)  #确保压缩行数最小为1
    # 初始化处理进度
    process_progress = 0
    data_service.update_stix_process_progress(file_hash,process_progress,batch_count)
    # 初始化行索引
    row_index = 0
    buffer = []  # 写入缓冲区，大小为压缩行数
    errors = []
    stix_record_buffer = []
    ips_record_buffer = {} #dict去重和记录数量
    for k in range(0,batch_count):
        batch_size = stix_compress              
        # 逐行处理数据集
        for i in range(batch_size):
            if row_index >= row_length:
                # 到达数据集末尾,正常结束处理
                break
            row_data = dataset.iloc[row_index]  # 获取行数据
            row_index += 1
            try:
                observed_data, attack_pattern, stix_record = stix_transform(mapping_dict, mapped_columns, row_data, i)  # 构造STIX对象
                if observed_data:
                    buffer.append(observed_data.serialize(pretty=True) + "\n")
                if attack_pattern:
                    buffer.append(attack_pattern.serialize(pretty=True) + "\n")
                if stix_record:
                    stix_record_buffer.append(stix_record)
            except Exception as e:
                errors.append(f"第 {row_index + 1} 行数据转换失败：{e}")
                continue

        #计算数据hash
        stix_data_hash = ""
        try:
            stix_data_hash = get_sha256_hash(json.dumps(buffer).encode())
        except Exception as e:
            print(f"数据hash计算失败：{e}")
            errors.append(f"数据hash计算失败：{e}")
            return None,f"数据hash计算失败：{e}"
        
        output_file = output_directory + "/" + f"{stix_data_hash}.jsonl"  # 自动命名生成文件
        ips_record_output_file = output_directory + "/" + f"{stix_data_hash}_ioc_ips.json" #记录stix内的ip信息 
    
        with open(output_file, "w") as fp:           
            # 写入数据
            try:
                fp.writelines(buffer)
            except Exception as e:
                print(f"{output_file}写入失败：{e}")
                errors.append(f"{output_file}写入失败：{e}")

        #2.写入额外IP记录
        try:
            for record in stix_record_buffer:
                if record["ips_list"]:
                    for ip in record["ips_list"]:
                        ips_record_buffer[ip] = ips_record_buffer.get(ip,0) + 1
            with open(ips_record_output_file, "w") as fp:
                fp.write(json.dumps(ips_record_buffer,indent=4))
        except Exception as e:
            print(f"{ips_record_output_file}写入失败：{e}")
            errors.append(f"{ips_record_output_file}写入失败：{e}")

        #3.保存本地stix处理记录
        try:
            stix_info = {
                "stix_type":"",
                "stix_tags":[],
                "stix_iocs":[],
                "file_hash":file_hash,
                "stix_data_hash":stix_data_hash,
                "ioc_ips_map":ips_record_buffer,
            }
            #暂时使用process_config代替stix_info
            if process_config:
                stix_info["stix_type"] = process_config.get("stix_type",1)
                stix_info["stix_tags"] = process_config.get("stix_iocs",["ip","port","hash","payload"]) #tags也设置为iocs
                stix_info["stix_iocs"] = process_config.get("stix_iocs",["ip","port","hash","payload"])
            data_service.save_local_stix_process_record(file_hash,output_file,stix_info)
        except Exception as e:
            print(f"本地stix处理记录保存失败：{e}")
            errors.append(f"本地stix处理记录保存失败：{e}")


        # 清空缓冲区
        stix_record_buffer = []
        ips_record_buffer = {}
        buffer.clear() 

        # 更新处理进度
        print(f"已处理 {row_index + 1} 行")
        process_progress += 1
        current_task_id = k
        data_service.update_stix_process_progress(file_hash,process_progress,batch_count,current_task_id=current_task_id)
    
    # 更新处理结果(处理完成)
    try:
        data_service.update_stix_process_progress(file_hash,batch_count,batch_count)
    except Exception as e:
        print(f"处理进度更新失败：{e}")
        errors.append(f"处理进度更新失败：{e}")
    return output_directory,errors


def start_process_dataset_to_stix(data_service,file_hash:str,process_config:dict):
    """
        处理数据集文件夹中的所有文件并将生成文件放入stix_file夹
        param:
            data_service:DataService实例
            dataset_dir_path:数据集文件夹路径
            file_hash:数据集文件hash
    """
    start_time = time.time()  # 开始计时
    file_path = data_service.get_upload_file_path_by_hash(file_hash)
    print("开始处理数据集文件...")
    output_directory,errors = process_dataset_to_stix(data_service,file_path,file_hash,process_config)
    if len(errors) > 0:
        print(f"文件处理失败！{errors}")
    elif len([f for f in os.listdir(output_directory) if f.endswith('.jsonl')]) == 0:
        print(f"生成文件为空！{file_path} 文件处理失败！")
    else:
        print(f"{file_path} 文件处理成功！")
    # 结束时间和内存使用情况
    finish_time = time.time()
    print(f"{file_path} 文件处理完成! 耗时 {(finish_time - start_time):.2f} 秒")
    result = {
        "use_time":finish_time - start_time,
    }
    #更新处理结果
    data_service.update_stix_process_progress(file_hash,result=result,errors=errors)
    
