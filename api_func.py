###################     GPT-4o    ###################
from openai import OpenAI
import requests

def openai_4o_request(question):
    client = OpenAI(
        # 将这里换成你在便携AI聚合API后台生成的令牌
        api_key='',
        # 这里将官方的接口访问地址替换成便携AI聚合API的入口地址
        base_url="https://api.bianxie.ai/v1"
    )
    completion = client.chat.completions.create(
        # model="chatgpt-4o-latest",
        # model="gpt-4o-mini",
        model = "gpt-4o",
        temperature=0.5,
        messages=[
            {
                "role": "user",
                "content": question,
            }
        ]
    )
    result = {'answer' : completion.choices[0].message.content,'token_num' : completion.usage.completion_tokens}
    return result['answer']

def gpt_4o_mini_request(question):
    client = OpenAI(
        # 将这里换成你在便携AI聚合API后台生成的令牌
        api_key='',
        # 这里将官方的接口访问地址替换成便携AI聚合API的入口地址
        base_url="https://api.bianxie.ai/v1"
    )
    completion = client.chat.completions.create(
        # model="chatgpt-4o-latest",
        model="gpt-4o-mini",
        # model = "gpt-4o-2024-08-06",
        temperature=0.5,
        messages=[
            {
                "role": "user",
                "content": question,
            }
        ]
    )
    result = {'answer' : completion.choices[0].message.content,'token_num' : completion.usage.completion_tokens}
    return result['answer']

# 在 openai_4o_request 和 gpt_4o_mini_request 函数之后，添加这个新函数
def openai_41_request(question):
    client = OpenAI(
        # 将这里换成你在便携AI聚合API后台生成的令牌
        api_key='',
        # 这里将官方的接口访问地址替换成便携AI聚合API的入口地址
        base_url="https://api.bianxie.ai/v1"
     )
    completion = client.chat.completions.create(
        model = "gpt-4.1",  # 使用GPT-4.1模型
        temperature=0.5,
        messages=[
            {
                "role": "user",
                "content": question,
            }
        ]
    )
    result = {'answer' : completion.choices[0].message.content,'token_num' : completion.usage.completion_tokens}
    return result['answer']

def gpt_request(question, choice = "4o"):  # 您可以保留默认值为"4o"或改为"41"
    if choice == "4o":
        return openai_4o_request(question)
    elif choice == "41":  # 添加这个新的选项
        return openai_41_request(question)
    elif choice == "mini":
        return gpt_4o_mini_request(question)
    else:
        return openai_4o_request(question)  # 或改为 openai_41_request(question)




###################     Claude3.5    ################### 
def claude_request(question):
    api_key = ''
    url = 'https://api.bianxie.ai/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    data = {
        'model': 'claude-3-5-sonnet-20240620',
        'messages': [{'role': 'user', 'content': question}],
        # 'temperature':0.2,
    }
    response = requests.post(url, headers=headers, json=data)
    result = response.json()['choices'][0]['message']['content']
    return result



