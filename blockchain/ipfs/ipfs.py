
"""
    IPFS接口实现
"""
from env.global_var import getIpfsAddress,getIPFSDownloadPath
import ipfshttpclient2
ipfs_address = getIpfsAddress()
download_path = getIPFSDownloadPath()


def upload_file_to_ipfs(file_path:str)->tuple[str,str]:
    """
        上传文件到IPFS
        :param file_path:文件路径
        :return IPFS hash,error
    """
    try:
        # 连接到本地 IPFS 节点
        with ipfshttpclient2.connect(ipfs_address) as client:
            # 上传文件
            res = client.add(file_path)
            
            # 获取文件的 IPFS 哈希
            file_hash = res['Hash']
            
            print(f"stix File uploaded successfully. IPFS Hash: {file_hash}")
            return file_hash,None
    except Exception as e:
        print(f"Error uploading file: {e}")
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


def download_file_with_progress(ipfs_hash: str, save_path=None, progress_callback=None) -> tuple[str, str]:
    """
        从IPFS下载文件,并监听下载进度
        :param ipfs_hash: IPFS hash
        :param save_path: 保存路径
        :param progress_callback: 进度回调函数,参数为(received_bytes, total_bytes)
        :return: (文件路径,错误信息)
    """
    try:
        if save_path is None:
            save_path = download_path
            
        # 连接到本地IPFS节点
        with ipfshttpclient2.connect(ipfs_address) as client:
            # 获取文件大小
            file_stat = client.files.stat(f"/ipfs/{ipfs_hash}")
            total_size = file_stat['Size']
            
            # 下载文件并跟踪进度
            received_size = 0
            save_file_path = save_path + f"/{ipfs_hash}"
            
            with open(save_file_path, 'wb') as f:
                for chunk in client.cat(ipfs_hash, chunk_size=1024*1024):
                    f.write(chunk)
                    received_size += len(chunk)
                    if progress_callback:
                        progress_callback(received_size, total_size)
                        
            print(f"文件下载成功. 保存路径: {save_file_path}")
            return save_file_path, None
            
    except Exception as e:
        print(f"下载文件出错: {e}")
        return None, f"Error downloading file: {e}"
