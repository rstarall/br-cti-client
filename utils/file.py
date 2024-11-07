

import os,json,sys
def get_project_root_path():
    """
        获取当前项目根目录绝对路径
    """
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

def read_all_json_from_path(directory):
    """
        遍历指定目录下所有的json文件，读取内容并以文件名为键存储。
        :param directory: 要遍历的目录路径
        :return: 一个字典，键为文件名（不含路径和扩展名），值为文件内容
    """
    json_file_dict = {}
    for filename in os.listdir(directory):
        if filename.endswith('.json'):  # 确保是json文件
            file_path = os.path.join(directory, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    # 以文件名为键（去除路径和扩展名），文件内容为值
                    key = os.path.splitext(os.path.basename(filename))[0]  # 去除路径和扩展名
                    json_file_dict[key] = json.load(file)  # 加载json文件内容到字典
            except Exception as e:
                print(f"Error loading JSON file: {filename}")
    return json_file_dict