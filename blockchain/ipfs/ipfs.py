
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
            
            print(f"File uploaded successfully. IPFS Hash: {file_hash}")
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
