import pandas as pd
import datetime
import time
import urllib.request
import feedparser

import certifi
import ssl
ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where( ))


# 获取arXiv上的论文信息
def get_arxiv_from_api(input_num):
    base_url = 'http://export.arxiv.org/api/query?'
    search_query = 'cat:cs.AI+OR+cat:cs.CL+OR+cat:cs.CV+OR+cat:cs.LG'  # 只搜索cs.CL、cs.HC和cs.CV类别
    start = 0

    sort_by = 'submittedDate'  # 按提交日期排序
    sort_order = 'descending'  # 降序排列
    # 构建API请求URL
    query_url = f"{base_url}search_query={search_query}&start={start}&max_results={input_num}&sortBy={sort_by}&sortOrder={sort_order}"

    # 使用urllib.request获取API响应
    with urllib.request.urlopen(query_url) as response:
        xml_data = response.read()

    # 使用feedparser解析API响应
    parsed_data = feedparser.parse(xml_data)
    return parsed_data


def get_number_from_user():
    day = datetime.datetime.now().day
    #如果是星期二，获取 800 条数据约3天，否则获取 400 条数据，约1天
    if day == 2:
        input_num = 800
    else:
        input_num = 400
    return input_num

#将论文信息保存到Excel文件中。返回所有 llm_related_score > 8 的论文html链接
def get_and_write_excel(paper_days=1, save_to_excel = False):
    # 创建一个空的DataFrame，用于存储论文信息
    columns = ['Title', 'Published','Summary']
    papers_df = pd.DataFrame(columns=columns)

    llm_keywords = ["llm","gpt","language model","foundation model","chain of thought","sota",
        "chatbot","RAG","llama","Gemini", "mixtral", "qwen", "claude", "sora", "vlm",
        "pre-train","generative","transformer","prompt","token","inference","expert","parameters","vision-language",
        "agent","multi-modal","multimodal","ai","reinforced","reinforcement","rlhf"]
    vision_related_keywords = ["diffusion","midjourney","vision","visual","image","shape","augmentation","segmentation"]
    # game_related_keywords = ["game","agent","aigc","AI","simulate","2D","3D","audio","video","bot","NPC","scene"]
    unrelated = ["protein","medical","medicine","chemical","chemistry","biological","law","drive","driving"]

    input_num = get_number_from_user()
    parsed_data = get_arxiv_from_api(input_num)
    entry_length = len(parsed_data.entries)
    # print("entry_length",entry_length)
    # print("first entry \n",parsed_data.entries[0])

    # 添加最大尝试次数
    max_attempts = 3
    current_attempt = 0

    #确保返回的数目与input_num一致，如果不一致，可能是网络原因，需要等待5秒，重新获取
    while entry_length < input_num and current_attempt < max_attempts:
        print(f"尝试重新获取链接数量：{entry_length}，第{current_attempt + 1}次尝试")
        time.sleep(5)
        parsed_data = get_arxiv_from_api(input_num)
        entry_length = len(parsed_data.entries)
        current_attempt += 1
        # 如果达到最大尝试次数但仍未获取足够数量，打印警告并继续
        if entry_length < input_num:
            print(f"警告：无法获取请求的{input_num}篇论文，只获取到{entry_length}篇。继续处理可用数据。")

    # 获取论文中最新一篇论文的发布时间，然后只获取其24小时内的论文
    published_time = parsed_data.entries[0].published
    print("最新论文发布时间：",published_time)
    #时间格式为 2024-08-15T17:59:57Z，需转换为datetime格式
    published_time = published_time.replace("T"," ").replace("Z","")
    published_time = datetime.datetime.strptime(published_time, "%Y-%m-%d %H:%M:%S")
    # print("published_time:",published_time)
    # cuttime, 只获取 published_time往前24或者72小时内的论文
    cut_time = published_time - datetime.timedelta(days=paper_days)
    # print("cut_time:",cut_time)

    # 将论文信息添加到DataFrame中。只获取24小时内的论文
    for entry in parsed_data.entries:
        #如果论文发布时间早于cut_time，跳出循环
        published_time = entry.published
        published_time = published_time.replace("T"," ").replace("Z","")
        published_time = datetime.datetime.strptime(published_time, "%Y-%m-%d %H:%M:%S")

        if published_time < cut_time:
            break
        #initialze settings
        title = entry.title
        published = entry.published
        abs_link = entry.link
        summary = entry.summary
        category = entry.arxiv_primary_category['term']
        pdf_link = None
        html_link = None

        #initialze scores
        is_llm_related_score = 0
        is_vision_related_score = 0

        for link in entry['links']:
            if link.get('title')  == 'pdf':
                pdf_link = link['href']
                # 上面的链接为 http://arxiv.org/pdf/2408.08313v1，目标格式是 https://arxiv.org/html/2408.08313v1。将pdf链接转换为html链接
                html_link = pdf_link.replace('pdf','html')

        for keyword in llm_keywords:# Check llm related score
            if keyword.lower() in title.lower():
                is_llm_related_score += 3
            if keyword.lower() in summary.lower():
                is_llm_related_score += 1

        for keyword in vision_related_keywords: # Check vision related score
            if keyword.lower() in title.lower():
                is_vision_related_score += 3
                is_llm_related_score -= 1
            if keyword.lower() in summary.lower():
                is_vision_related_score += 1
                is_llm_related_score -= 1

        for keyword in unrelated: # Check game related score
            if keyword.lower() in title.lower():
                is_llm_related_score -= 3
            if keyword.lower() in summary.lower():
                is_llm_related_score -= 1


        # 将论文信息添加到DataFrame中
        newrow = {'Title': title, 'Summary': summary,'Category': category,'Published': published,
            'Link': abs_link, 'pdf_link': pdf_link, 'html_link': html_link,
            "is_llm_related":is_llm_related_score,"is_vision_related_score":is_vision_related_score}
        papers_df = pd.concat([papers_df,pd.DataFrame.from_records([newrow])], ignore_index=True)

        #按照is_llm_related相关性降序排序
        papers_df = papers_df.sort_values(by='is_llm_related', ascending=False)

    if save_to_excel:
        output_file = f'AI_Report_papers'
        import os
        if not os.path.exists(output_file):
            os.makedirs(output_file)
        try:
            papers_df.to_excel(output_file, index=False, engine='openpyxl')
        except:
            now = datetime.datetime.now().strftime("%Y%m%d")
            papers_df.to_excel(f'{output_file}/arxiv_papers_{now}.xlsx', index=False, engine='openpyxl')


    #返回所有 llm_related_score > 6 的论文pdf链接。但是不要超过40条
    llm_related_papers = papers_df[papers_df['is_llm_related'] > 6].head(40)
    print(llm_related_papers["pdf_link"].tolist())
    return llm_related_papers["pdf_link"].tolist()

# get_and_write_excel()
