
import base64
def base64_to_binary(base64_data):
    # 解码 Base64 编码的二进制数据
    decoded_bytes = base64.b64decode(base64_data)
    return decoded_bytes