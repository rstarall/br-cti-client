import os,json,sys,hashlib
from datetime import datetime


def get_project_root_path():
    """
        获取当前项目根目录绝对路径
    """
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

def get_sha256_hash(data:bytes):
    """
        获取数据的sha256哈希值
        param:
            data: 数据,bytes类型
        return:
            sha256_hash: 数据的sha256哈希值,str类型
    """
    return hashlib.sha256(data).hexdigest()

def get_file_sha256_hash(file_path):
    """
        获取文件的sha256哈希值
        :param file_path: 文件路径
        :return: 文件的sha256哈希值
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        #每次读取512MB
        for byte_block in iter(lambda: f.read(512*1024*1024), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_file_md5_hash(file_path):
    """
        获取文件的MD5哈希值
        :param file_path: 文件路径
        :return: 文件的MD5哈希值
    """
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        # 每次读取64MB
        for byte_block in iter(lambda: f.read(64 * 1024 * 1024), b""):
            md5_hash.update(byte_block)
    return md5_hash.hexdigest()

def get_file_by_hash(upload_file_path,file_hash):
    """
        根据文件的sha256哈希值,获取文件路径
        param:
            upload_file_path:上传文件路径
            file_hash:文件的sha256哈希值
        return:
            file_path:文件路径,如果文件不存在则返回None
    """
    return check_file_by_hash(upload_file_path,file_hash)

def check_file_by_hash(upload_file_path,file_hash):
    """
        根据文件的sha256哈希值,检查文件是否存在
        param:
            upload_file_path:上传文件路径
            file_hash:文件的sha256哈希值
        return:
            file_path:文件路径,如果文件不存在则返回None
    """
    #扫描该目录下所有文件(不对后缀判断)
    #深度递归扫描
    for root, dirs, files in os.walk(upload_file_path):
        for file in files:
            if file.startswith(file_hash):
                #返回文件路径
                return os.path.join(root, file)
    return None


def get_date_file_dir(upload_file_path):
    """
        创建以当前日期(年月日)命名的文件夹
        param:
            upload_file_path:上传文件路径
        return:
            dir_path:日期文件夹路径
    """
    today = datetime.now().strftime("%Y-%m-%d")
    #现判断是否存在该文件夹
    dir_path = os.path.join(upload_file_path, today)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    return dir_path


def replace_file_name_with_hash(file_path):
    """
        将文件名替换为文件的sha256哈希值
        如果文件已存在则删除源文件
        param:
            file_path:文件路径
        return:
            file_hash:文件的sha256哈希值
            file_size:文件大小
    """
    #获取文件大小
    file_size = get_file_size(file_path)

    old_file_dir_path = os.path.dirname(file_path)
    file_hash = ""
    # 计算文件的 SHA256 哈希值 or MD5 哈希值
    file_hash = get_file_sha256_hash(file_path)
    
    
    # 重命名文件
    new_filename = f"{file_hash}{os.path.splitext(file_path)[1]}"
    new_filepath = os.path.join(old_file_dir_path, new_filename)
    
    #如果文件已存在则删除源文件
    if os.path.exists(new_filepath):
        os.remove(file_path)
        return file_hash,file_size
    os.rename(file_path, new_filepath)
    
    return file_hash,file_size


def get_file_size(file_path):
    """
        获取文件大小

        param:
            file_path:文件路径
        return:
            file_size:文件大小,单位为字节
    """
    return os.path.getsize(file_path)

def save_json_to_file(file_path,data):
    """
        保存json数据到文件
        param:
            file_path:文件路径
            data:json数据
    """
    #创建文件夹
    chain_data_dir_path = os.path.dirname(file_path)
    if not os.path.exists(chain_data_dir_path):
        os.makedirs(chain_data_dir_path)
    with open(file_path,"w") as fp:
        fp.write(json.dumps(data))

def load_json_from_file(file_path):
    """
        读取json文件
        param:
            file_path:文件路径
        return:
            json数据
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)
    
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