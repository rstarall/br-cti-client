
"""
    IPFS接口实现
"""
from env.global_var import getIpfsAddress,getIPFSDownloadPath
import ipfshttpclient2
import os
from utils.file import rename_file_ext_with_content
ipfs_address = getIpfsAddress()
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
        # 连接到本地 IPFS 节点
        with ipfshttpclient2.connect(ipfs_address) as client:
            # 获取文件名和后缀
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_name)[1]
            
            # 上传文件
            res = client.add(file_path)
            
            # 获取文件的 IPFS 哈希
            file_hash = res['Hash']
            
            print(f"文件 {file_name} 上传成功. IPFS Hash: {file_hash}")
            return file_hash,None
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
        # 连接到本地 IPFS 节点
        with ipfshttpclient2.connect(ipfs_address) as client:
            # 下载文件
            client.get(ipfs_hash, filepath=save_path+f"/{ipfs_hash}")
            
            print(f"文件下载成功. 保存路径: {save_path+f'/{ipfs_hash}'}")
            return save_path+f'/{ipfs_hash}',None
    except Exception as e:
        print(f"下载文件出错: {e}")
        return None,f"Error downloading file: {e}"


def get_ipfs_file_url(ipfs_hash:str)->str:
    """
        获取IPFS文件URL
        :param ipfs_hash:IPFS hash
        :return URL
    """
    return f"{ipfs_address}/ipfs/{ipfs_hash}"


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
        with ipfshttpclient2.connect(ipfs_address) as client:
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
