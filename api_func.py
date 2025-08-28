from openai import OpenAI
import requests

###################     GPT-5    ###################

# 旧的 GPT-4o 与 mini 接口已停用

def openai_5_request(question):
    client = OpenAI(
        # 将这里换成你在便携AI聚合API后台生成的令牌
        api_key='',
        # 这里将官方的接口访问地址替换成便携AI聚合API的入口地址
        base_url="https://api.bianxie.ai/v1",
    )
    completion = client.chat.completions.create(
        model="gpt-5",
        temperature=0.5,
        messages=[
            {
                "role": "user",
                "content": question,
            }
        ]
    )
    result = {
        'answer': completion.choices[0].message.content,
        'token_num': completion.usage.completion_tokens
    }
    return result['answer']


def gpt_request(question):
    return openai_5_request(question)


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

