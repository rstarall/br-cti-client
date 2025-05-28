
"""
    IPFS接口实现
"""
from env.global_var import getIpfsAddress,getIPFSDownloadPath
import requests
import os
from utils.file import rename_file_ext_with_content

# 转换IPFS多地址为HTTP URL
def convert_multiaddr_to_http_url(multiaddr):
    """
    将IPFS多地址转换为HTTP URL
    例如: /ip4/127.0.0.1/tcp/5001 -> http://127.0.0.1:5001
    """
    if multiaddr.startswith('/ip4/'):
        parts = multiaddr.split('/')
        if len(parts) >= 5:
            ip = parts[2]
            port = parts[4]
            return f"http://{ip}:{port}"
    # 如果已经是HTTP URL格式，直接返回
    if multiaddr.startswith('http://') or multiaddr.startswith('https://'):
        return multiaddr
    # 默认返回本地IPFS API地址
    return "http://127.0.0.1:5001"

ipfs_address_raw = getIpfsAddress()
ipfs_address = convert_multiaddr_to_http_url(ipfs_address_raw)
download_path = getIPFSDownloadPath()


def upload_file_to_ipfs(file_path:str)->tuple[str,str]:
    """
        上传文件到IPFS
        :param file_path:文件路径
        :return IPFS hash,error
    """
    try:
        #判断文件是否存在
        if not os.path.exists(file_path):
            return None,"文件不存在"+file_path
        
        # 使用IPFS HTTP API直接上传文件
        api_url = f"{ipfs_address}/api/v0/add"
        
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(api_url, files=files)
            
            if response.status_code == 200:
                result = response.json()
                file_hash = result['Hash']
                file_name = os.path.basename(file_path)
                print(f"文件 {file_name} 上传成功. IPFS Hash: {file_hash}")
                return file_hash, None
            else:
                return None, f"上传失败: HTTP {response.status_code}"
    except Exception as e:
        print(f"上传文件出错: {e}")
        print(f"上传文件出错: {file_path}")
        return None,f"Error uploading file: {e}"

def download_file_from_ipfs(ipfs_hash:str,save_path=None)->tuple[str,str]:
    """
        从IPFS下载文件
        :param ipfs_hash:IPFS hash
        :param save_path:保存路径
        :return 文件路径,error
    """
    try:
        if save_path is None:
            save_path = download_path
            
        # 使用IPFS HTTP API直接下载文件
        api_url = f"{ipfs_address}/api/v0/get?arg={ipfs_hash}"
        response = requests.post(api_url)
        
        if response.status_code != 200:
            return None, f"下载失败: HTTP {response.status_code}"
            
        file_path = save_path+f"/{ipfs_hash}"
        with open(file_path, 'wb') as f:
            f.write(response.content)
            
        print(f"文件下载成功. 保存路径: {file_path}")
        return file_path, None
    except Exception as e:
        print(f"下载文件出错: {e}")
        return None,f"Error downloading file: {e}"


def get_ipfs_file_url(ipfs_hash:str)->str:
    """
        获取IPFS文件URL
        :param ipfs_hash:IPFS hash
        :return URL
    """
    # 获取网关URL，通常是 http://127.0.0.1:8080
    gateway_url = ipfs_address.replace("5001", "8080")
    return f"{gateway_url}/ipfs/{ipfs_hash}"


def download_file_with_progress(data_source_hash: str,ipfs_hash: str, save_path=None, progress_callback=None) -> tuple[str, str]:
    """
        从IPFS下载文件,并监听下载进度
        :param data_source_hash: 数据源hash
        :param ipfs_hash: IPFS 地址
        :param save_path: 保存路径
        :param progress_callback: 进度回调函数,参数为(received_bytes, total_bytes)
        :return: (文件信息,错误信息)
    """
    file_info = {
        'save_path': "",
        'file_size': 0,
        'file_ext': '.txt', #默认后缀
        'file_name': data_source_hash+'.txt' #默认文件名
    }
    try:
        if save_path is None:
            save_path = download_path
            
        # 连接到本地IPFS节点
        with ipfshttpclient.connect(ipfs_address) as client:
            # 获取文件大小和文件名
            file_stat = client.files.stat(f"/ipfs/{ipfs_hash}")
            total_size = file_stat['Size']
            print("file_stat",file_stat)
            # 获取文件后缀名
            file_name = file_stat.get('Name', '')
            file_ext = os.path.splitext(file_name)[1] if file_name else '.txt'
            
            # 下载文件并跟踪进度
            received_size = 0
            save_file_path = save_path + f"/{data_source_hash}{file_ext}"
            
            with open(save_file_path, 'wb') as f:
                # 使用client.cat()获取字节数据
                data = client.cat(ipfs_hash)
                if isinstance(data, bytes):
                    f.write(data)
                    received_size = len(data)
                    if progress_callback:
                        progress_callback(received_size, total_size)


            #根据内容重命名文件            
            save_file_path,file_name,file_ext = rename_file_ext_with_content(save_file_path)
            print(f"文件下载成功. 保存路径: {save_file_path}")
            file_info['save_path'] = save_file_path
            file_info['file_size'] = total_size
            if file_ext:
                file_info['file_ext'] = file_ext
            if file_name and file_name!='':
                file_info['file_name'] = file_name
            return file_info, None
    except Exception as e:
        print(f"下载文件出错: {e}")
        return file_info, f"Error downloading file: {e}"
