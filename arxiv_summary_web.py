import requests
from bs4 import BeautifulSoup
def get_arxiv_from_web():
    url = "https://arxiv.org/list/cs/recent?skip=0&show=500"
    response = requests.get(url)
    return response.text

def parse_arxiv_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    papers = []

    for item in soup.find_all('dt'):
        paper = {}
        paper['pdf_url'] = item.find('a', title='Download PDF')['href']
        paper['pdf_url'] = f"https://arxiv.org{paper['pdf_url']}"

        details = item.find_next_sibling('dd')
        paper['title'] = details.find('div', class_='list-title').text.strip().replace('Title:', '').strip()

        papers.append(paper)

    return papers

def from_web_to_list():
    html = get_arxiv_from_web()
    papers = parse_arxiv_html(html)
    return papers



def get_arxiv_from_web_advanced():
    url = "https://arxiv.org/search/advanced?advanced=&terms-0-operator=AND&terms-0-term=&terms-0-field=title&classification-computer_science=y&classification-physics_archives=all&classification-include_cross_list=include&date-filter_by=all_dates&date-year=&date-from_date=&date-to_date=&date-date_type=submitted_date&abstracts=show&size=200&order=-announced_date_first"
    response = requests.get(url)
    return response.text

def advanced_search_parse_arxiv_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    soup = soup.find('ol')
    papers = []

    for item in soup.find_all('li'):
        paper = {}
        paper['pdf_url'] = item.find('a', string='pdf')['href']
        #增加 “v1” 在链接末尾
        paper['pdf_url'] = paper['pdf_url'] + 'v1'
        paper['title'] = item.find('p', class_='title').text
        paper["abstract"] = item.find('span', class_='abstract-full').text

        papers.append(paper)

    return papers


def from_web_to_list_advanced():
    # 方法一：获取更多论文
    html = get_arxiv_from_web_advanced()  # 确保 get_arxiv_from_web_advanced 中 size=500 或更高
    papers = advanced_search_parse_arxiv_html(html)

    llm_keywords = ["llm", "gpt", "language model", "foundation model", "chain of thought", "sota",
                    "chatbot", "RAG", "llama", "Gemini", "mixtral", "qwen", "claude", "sora", "vlm",
                    "pre-train", "generative", "transformer", "prompt", "token", "inference", "expert", "parameters",
                    "vision-language",
                    "agent", "multi-modal", "multimodal", "ai", "reinforced", "reinforcement", "rlhf"]
    llm_keywords = [keyword.lower() for keyword in llm_keywords]

    # 第二步：添加禁词列表
    unrelated_keywords = ["protein", "medical", "medicine", "chemical", "chemistry", "biological", "law", "drive",
                          "driving", "robotics"]
    unrelated_keywords = [keyword.lower() for keyword in unrelated_keywords]

    filtered_papers = []

    for paper in papers:
        title = paper['title'].lower()
        abstract = paper['abstract'].lower()

        # 计算加分
        is_llm_related_score = sum([3 for keyword in llm_keywords if keyword in title])
        is_llm_related_score += sum([1 for keyword in llm_keywords if keyword in abstract])

        # 计算减分（禁词惩罚）
        is_llm_related_score -= sum([5 for keyword in unrelated_keywords if keyword in title])
        is_llm_related_score -= sum([3 for keyword in unrelated_keywords if keyword in abstract])

        # 方法二：降低分数门槛
        if is_llm_related_score > 4:  # 例如，将门槛从6降到4
            filtered_papers.append(paper['pdf_url'])

    print(filtered_papers)
    return filtered_papers

# from_web_to_list_advanced()