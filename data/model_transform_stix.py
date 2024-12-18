from openai import OpenAI
import re
from pathlib import Path

# 采用 OpenRouter 里的免费大模型：Google: Gemma 2 9B (free)
key = "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"


# 利用大模型提炼数据并返回信息
def ask_model(input_text):
    # 调用大模型
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=key,
        )
        completion = client.chat.completions.create(
            model="google/gemma-2-9b-it:free",
            messages=[
                {
                    "role": "user",
                    "content": input_text
                }
            ]
        )
        response_text = completion.choices[0].message.content
    except Exception as e:
        print(f"模型调用出错：{e}")
        return None

    # 从大模型返回的文本中提取出stix信息
    try:
        # 使用正则表达式提取 JSON 部分
        json_pattern = re.compile(r'\{.*}', re.DOTALL)  # 正则表达式提取大括号内的内容
        match = json_pattern.search(response_text)
        if match:
            json_text = match.group(0)  # 提取到的 JSON 字符串
            return json_text
        else:
            return None
    except Exception as e:
        print(f"提取stix信息出错：{e}")
        return None


# 测试用例
if __name__ == '__main__':
    # 模拟用户的输入信息
    input_text = """
    请从以下文本中提取出可能的 CTI 信息，并以 STIX 格式返回：
    
    攻击者 A 通过使用恶意软件 X 攻击了组织 B 的服务器，导致数据泄露。攻击者 A 通过 IP 地址 192.168.1.1 进行了远程访问。
    
    请根据这些信息生成 STIX 2.1 格式的对象。
    
    """

    stix_information = ask_model(input_text)
    print("提取到的stix信息：")
    print(stix_information)

