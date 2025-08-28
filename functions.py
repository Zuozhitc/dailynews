import re

from sympy.core.random import choice

import api_func as api
import copy
from datetime import date
from bs4 import BeautifulSoup
import requests
import json
import PyPDF2
from io import BytesIO

# 通过解析内容来筛选可能有用的标题
def title_filter_rough(full_text):
    # prompt模板
    prompt_prefix = '''你是一个分析师，今天的日期是{date}，需要筛选有关AI日报的新闻。你需要筛选有关 AI 、人工智能、大模型、或者相关公司的新闻，以及如下方向相关内容的新闻：
                        1）重点玩家：主要关注AI公司、大模型公司、AI创业公司的信息，关注内容包括模型发布、AI产品与服务、模型评测、模型性能、新闻爆料、用户数量、产品调整、投融资等。
                        2）前沿方向：LLM、文生图、多模态、Agent 等
                        3）应用结合：AI + 医疗应用、AI + 音乐等。热门应用方向以及最新落地进度
                        4）法律法规：各国出台的新规、有关 AI 版权、数据隐私等
                        注意，不要纳入股价、裁员、财报信息。对于下列相关的信息，不要收录：
                        1）酷睿、锐龙、ZEN等消费级产品的发布不要纳入，NAND、DRAM 产品也不需要，只有在发布新的AI芯片时才需要纳入
                        2）手机、电脑等消费电子产品的发布新闻不要纳入
                    '以下是网页的标题，请摘出来相关的标题。网页标题：\n{text}' 
                    "直接输出一个可执行的python程序，用一个列表全局变量news_current存储结果,最终存储的结果是筛选出来的标题对应的序号,示例：```python\nnews_current=[1,2,4,6,10,15,100]```" 
                    '不需要print。如果没有任何可用的信息，直接让news_current为一个空list。'''


    # 让gpt找到所有相关的词条和对应网址，result变量还不是可以运行的python文件
    result = api.gpt_request(prompt_prefix.format(text=full_text, date=date.today()))
    # print(result)


    # print('粗筛成功')
    # 分割出可执行文件，然后运行，获得news_current字典
    result_run = re.search(r"```(.*?)```", result, re.DOTALL).group(1).split('python')[1].strip()
    exec_namespace = {}
    exec(result_run, exec_namespace)
    news_current = exec_namespace.get('news_current', {})

    # 深拷贝 news_current 并添加到 news_list 中
    news_list = copy.deepcopy(news_current)

    return news_list

# 用来精细筛选，输出最终内容，格式是一个字典，key是公司名，value是一个字典，key是标题，value是序号
def title_filter_final(titles_text):
    # prompt模板
    prompt_prefix = '''你是一个分析师，需要写一份AI大模型日报，我已经帮你搜集好了新闻的标题，这些标题如下：\n{titles}\n。
        你需要将这些 AI 新闻划分到各个玩家，根据新闻的主体玩家，将每条新闻分别填入该玩家的分类：
        重点玩家名单如下：
        OpenAI、Google、Meta、苹果、微软、亚马逊、三星、
        Anthropic、Mistral、Perplexity、xAI、Midjourney、Stability AI、Runway、Cohere、Pika、Suno、ElevenLabs、
        字节、百度、阿里、微信、快手、科大讯飞、商汤、360、昆仑万维、华为、小米、
        智谱、月之暗面 Kimi、零一万物、百川智能、MiniMax、面壁智能、DeepSeek、秘塔、
        英伟达、AMD、英特尔、Groq、摩尔线程
        其他类别、不属于以上名单的 AI 公司或者新闻，都直接归到这一类。包括发布AI相关产品的公司、数据中心等
        注意，有哪几个 AI 公司有相关新闻，那么就有几个子类，分别填入他们的内容。
        要求：
        1. 一个新闻只能被选入一个门类，不要有重复的新闻。
        2. 输出的格式是python可执行文件，把结果存储到一个变量titles_fine里面，按门类分层使用字典存储，最终存储的结果是筛选出来的标题对应的序号。
        示例： python\ntitles_fine = {{"重点玩家":{{"OpenAI":2,"Meta":11}} }}。'''

    result = api.gpt_request(prompt_prefix.format(titles = titles_text))

    result_run = re.search(r"```(.*?)```", result, re.DOTALL).group(1).split('python')[1].strip()
    exec(result_run,globals())
    titles_fine = eval('titles_fine')

    return titles_fine



# 获取网页信息
import requests
from bs4 import BeautifulSoup
from readability.readability import Document
import logging

logging.basicConfig(level=logging.INFO)

def catch_link(url):
    try:
        # 发送HTTP请求并获取网页内容
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)

        # 检查请求状态
        if response.status_code != 200:
            raise Exception(f"Failed to fetch the page. Status code: {response.status_code}")

        # 确保编码正确
        response.encoding = 'utf-8'  # 强制设置编码为utf-8
        logging.info(f"Final encoding used: {response.encoding}")

        # 初始化标题和正文
        title, text = '', ''

        # 尝试使用readability提取主要内容
        try:
            doc = Document(response.text)
            clean_html = doc.summary()
            logging.info("Successfully parsed content using readability.")

            # 使用BeautifulSoup解析提取后的HTML
            soup = BeautifulSoup(clean_html, 'html.parser')

            # 尝试提取正文文本
            text = ' '.join(soup.stripped_strings)
            if not text:
                raise ValueError("No content found in readability output")  # 强制触发备用方案
            if len(text) < 100:
                raise ValueError("Content too short")

        except Exception as e:
            # 当readability失败时，记录错误并使用备用方案
            logging.error(f"Readability failed or content not found: {e}")
            logging.info("Falling back to raw content parsing.")

            # 使用BeautifulSoup解析原始HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # 去除不需要的标签， 常见的包括 script, style, header, footer, nav, aside, form, noscript, code, pre
            for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'form', 'noscript', 'code', 'pre']):
                tag.decompose()

            return soup.get_text()

        return text

    except requests.RequestException as e:
        return f"An error occurred while fetching the page: {e}", ''
    except Exception as e:
        return f"An error occurred: {e}", ''



def get_arxiv_pdf_abstract(url):
    response = requests.get(url)
    with BytesIO(response.content) as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages[:3]: #一般仅在前三页
            text += page.extract_text()
            # print(text)

        # 使用非贪婪模式来匹配 "Introduction" 前面的所有内容。注意可能因为排版原因，"Introduction" 会被分割成两行或者空格如 i ntroduction
        match = re.search(r'(.*)ntroduction', text, re.DOTALL | re.IGNORECASE) #匹配 ntroduction之前的所有内容
        if match:
            return match.group(1).strip()  # 返回 "Introduction" 之前的部分，去除首尾空格
        else: #返回第一页，如果没有找到introduction，返回前500个字符
            return text[:5000]



# 总结网页的信息
def summarize_web(link, choice = "gpt5"):
    try :
        text = catch_link(link)
    except:
        text = f"Webpage not available， the link is {link}. 请人工检查"

    prompt = f'''全程使用中文作答。以下是一个新闻的网页内容，你是一个网页内容总结助手，专门帮助用户将网页内容总结为 3 条详细的段落。
    每当用户提供网页内容时，你会按照以下步骤总结内容：
    首先，理解原文并识别关键点，重点关注事实性的信息以及数字，对于“促进、推动、展示、潜力、方向、思路、巩固市场、加强合作、奠定基础”等不重要的信息不要收录；
    接着，根据文章原文摘录出 bullet point，每个 bullet point 继续提供详细内容，确保符合原文、层次分明、逻辑清晰、信息准确，并保留重要细节。
    你的目标是生成易读且信息丰富的文章摘要，帮助用户快速掌握网页内容，注意不要额外添加自己的观点，也不要对原文进行额外的总结。
    注意总结里不要提到与“IT之家”相关的话语
    注意不要使用第一人称，不要使用markdown格式，每个段落结束换行，每个段落开头不要使用特殊符号
    最后的每段内容需要稍微精简一点
    例如，对于新闻“阿里发布全球最强数学大模型 Qwen 2-Math 的 Demo 版本，用户可以上传数学题解题”，
    下面是输出范例：
    阿里发布全球最强数学大模型 Qwen 2-Math 的 Demo，用户可以通过截图或扫描上传数学题目进行解题，目前其 OCR 功能由 Qwen 2-VL 支持，数学推理能力则由 Qwen 2-Math 提供。未来，阿里计划将多模态能力和数学推理能力结合到一个模型中\n
    Qwen 2-Math 基于通义千问开源大语言模型 Qwen 2 研发，专用于数学解题，能够解决竞赛级试题。 Qwen 2-Math 有 72B 、 7B 和 1.5B 三个版本，其中 Qwen 2-Math-72 B-Instruct 是旗舰模型，处理多种数学问题的准确率达到 84%\n
    Qwen 2-Math 在处理数学题目时表现出色，能够准确地解决一些简单的计算题，不能处理几何题。在面对更复杂的题目时，例如只有 GPT-5 答对过的概率题， Qwen 2-Math 未能给出正确答案。目前，Qwen 2-Math 主要针对英文场景，但 Qwen 2-Math 也能解答中文题目，并计划推出中英双语版本\n

    网页信息如下：\n{text}。记得使用中文作答'''
    result = api.gpt_request(prompt, choice)
    # print("API 返回结果：", result)
    result = text_format_beautify(result)
    print("格式化结果：", result)
    return result

def summarize_product(link, choice = "gpt5"):
    try:
        text = catch_link(link)
    except:
        text = f"{link}. 请人工检查"
    prompt = f'''全程使用中文作答。以下是一个AI产品的网页内容，你是一个网页内容总结助手，专门帮助用户将产品总结为为 1 个标题（格式为 OpenAI，AI 大模型初创公司）和 2 条详细的 bullet point。
    每当用户提供网页内容时，你会按照以下步骤总结内容：
    首先，理解这个网站中的主要产品，并识别产品特色；
    接着，将产品信息、特点、目标客户写成详细的 bullet point，每个 bullet point 展开详细内容，确保保留重要产品细节。注意不要额外添加自己的观点，也不要对原文进行额外的总结或者提炼标题。
    你的目标是生成易读且信息丰富的AI产品介绍，帮助用户快速掌握该AI产品的功能和特点。
    注意不要使用第一人称，不要使用markdown格式，每个段落结束换行，每个段落开头不要使用特殊符号
    下面是一个范例：
    Undermind，AI 科学论文发现助手\n
    Undermind 是一款专注于帮助研究人员发现和获取科学论文的 AI 代理工具，旨在提高科研效率，帮助用户快速找到相关的学术资源，使研究人员能够轻松地浏览和下载所需的学术论文，提升科研工作的便利性\n
    Undermind 通过分析用户的研究兴趣和需求， Undermind 能够智能推荐相关的科学论文，支持研究人员在海量文献中快速筛选出高价值的内容，并提供用户友好的界面和便捷的访问方式\n

    网页信息如下：\n{text}。记得使用中文作答'''
    result = api.gpt_request(prompt, choice)
    # print("API 返回结果：", result)
    result = text_format_beautify(result)
    print("格式化结果：", result)
    return result

#总结论文的信息
def summarize_paper(link, choice = "gpt5"):
    try:
        text = get_arxiv_pdf_abstract(link)
    except:
        text = f"{link}. 请人工检查"
    prompt = f'''GPT将作为一个总结翻译官，细致、易懂、并详细的将英文翻译成中文。有如下的具体要求
            使用中文回答，请为我将以下论文详细地总结为 1 个标题和 3 个要点。注意以下几点：
            1）标题总结为一行。标题前写出前 3 的主要作者机构名称(例如 UCB、上海交通大学)，然后使用“：”符号分隔标题。然后进行标题翻译
            2）正文abstract翻译，总结要点为最多 3 点的内容总结
            3）术语不要翻译，使用英文表示，例如 few-shot, zero shot, transformer。将大型语言模型统一翻译为 LLM
            4）使用第三人称如“研究人员发现”，避免 "我们发现"“他们发现”
            再次进行规范：
            在标题中，首先写出作者机构，使用“：”符号连接，然后再写出论文的主题，避免使用两个冒号, 后面出现的不管是":"或者"："都要变成"，“
            在要点中，最多列出 3 个，使用 bullet point 格式，用于概括论文的主要内容。
            尽可能保留英文术语，避免翻译引发的误解。
            在总结中，使用第三人称来进行表述，避免使用 "我们"。
            
            此外，对于每个段落，请记住不要在段落结尾使用句号“。”
            下面是输出范例：
            OpenAI、Stanford、清华：EFT，使用小型语言模型作为大型语言模型微调的仿真器 （如果没有作者机构信息，则写出前两位人名）
            研究人员提出了一种新技术，名为 “仿真微调（EFT）”，旨在 LLMs 在预训练和微调阶段获得的知识和技能，以回答 “如果将大型模型在预训练期间学到的知识与小型模型在微调期间学到的知识结合会发生什么” 的问题\n
            使用基于强化学习的框架，EFT 允许在不同规模上近似预训练和微调的结果分布。实验证明，扩大微调倾向于提高帮助性，而扩大预训练倾向于提高真实性\n
            EFT 还使得可以在测试时调整有竞争性的行为特征，如帮助性和无害性，而无需额外的训练。此外，EFT 的一个特例是 LM 上缩放，通过将大型预训练模型与小型微调模型进行合并，模拟了大型预训练模型微调的结果。上缩放在不需要额外的超参数或训练的情况下，一致提高了指示遵循模型在 Llama、Llama-2 和 Falcon 系列中的帮助性和真实性\n
            
            注意不要使用第一人称，不要使用markdown格式，每个段落结束换行，每个段落开头不要使用特殊符号
            如果相应的输入内容缺失，请回复“标题：缺失” 正文：“缺失”。
            网页信息如下：\n{text}
            '''
    result = api.gpt_request(prompt, choice)
    # print("API 返回结果：", result)
    result = text_format_beautify(result)
    print("格式化结果：", result)

    return result


def text_format_beautify(result):
    # 将 “人工智能” 和“智能” 替换为 “AI”
    result = re.sub(r'人工智能\(AI\)', ' AI ', result)
    result = re.sub(r'人工智能（AI）', ' AI ', result)
    result = re.sub(r'人工智能', ' AI ', result)
    result = re.sub(r'智能\(AI\)', ' AI ', result)
    result = re.sub(r'智能（AI）', ' AI ', result)
    result = re.sub(r'智能', ' AI ', result)

    # 将 “大型语言模型（LLM）” 替换为 “LLM”
    result = re.sub(r'多模态大型语言模型（MLLM）', 'MLLM', result)
    result = re.sub(r'多模态大型语言模型\(MLLM\)', 'MLLM', result)
    result = re.sub(r'多模态大模型（MLLM）', 'MLLM', result)
    result = re.sub(r'多模态大模型\(MLLM\)', 'MLLM', result)
    result = re.sub(r'大型语言模型\(LLM\)', 'LLM', result)
    result = re.sub(r'大型语言模型\(LLMs\)', 'LLM', result)
    result = re.sub(r'大型语言模型（LLM）', 'LLM', result)
    result = re.sub(r'大型语言模型（LLMs）', 'LLM', result)
    result = re.sub(r'大型语言模型', 'LLM', result)
    result = re.sub(r'多模态大模型', 'MLLM', result)

    # 在数字/字母与中文之间添加空格
    result = re.sub(r'(\d)([^\x00-\x7F])', r'\1 \2', result)  # 数字后跟中文
    result = re.sub(r'([^\x00-\x7F])(\d)', r'\1 \2', result)  # 中文后跟数字
    result = re.sub(r'([A-Za-z])([^\x00-\x7F])', r'\1 \2', result)  # 字母后跟中文
    result = re.sub(r'([^\x00-\x7F])([A-Za-z])', r'\1 \2', result)  # 中文后跟字母

    # 去掉连接符两边的空格，保留换行符
    result = re.sub(r'[ \t]*([\-\+,\.、*:：；?？&，。「」《》<>])[ \t]*', r'\1', result)
    # 对于 %$ 符号，仅去掉左边的空格
    result = re.sub(r'[ \t]*(%$)', r'%', result)

    # 去掉括号 "()" 和 "（ ）" 符号两边的空格
    result = re.sub(r'[ \t]*([\(\)（ ）])[ \t]*', r'\1', result)

    # 保留段落间的换行符，去掉多余的空格
    result = re.sub(r'[ \t]+', ' ', result)  # 只处理空格，保留换行符

    # 去掉每个段落末尾的句号，但保留换行符
    result = re.sub(r'。\s*(?=\n|$)', '', result)

    # 将多行换行符替换为单换行符
    result = re.sub(r'\n+', '\n', result)

    # 处理冒号：保留第一个冒号，将后续所有冒号替换为逗号
    # 先处理中文冒号
    def replace_colons(match):
        # 获取整个匹配的字符串
        full_text = match.group(0)
        # 保留第一个冒号，将后面的冒号替换为逗号
        return full_text[0] + re.sub('：', '，', full_text[1:])

    # 处理英文冒号
    def replace_english_colons(match):
        # 获取整个匹配的字符串
        full_text = match.group(0)
        # 保留第一个冒号，将后面的冒号替换为逗号
        return full_text[0] + re.sub(':', '，', full_text[1:])

    # 查找包含至少一个中文冒号的字符串
    result = re.sub(r'：[^：\n]*：[^：\n]*', replace_colons, result)
    # 查找包含至少一个英文冒号的字符串
    result = re.sub(r':[^:\n]*:[^:\n]*', replace_english_colons, result)


    return result
