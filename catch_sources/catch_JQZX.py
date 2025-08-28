import datetime
import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def catch_JQZX(days=1):
    """
    抓取机器之心（JQZX）网站的AI新闻。
    days: 抓取天数，只抓取指定天数内的新闻。
    """
    today = datetime.date.today()
    limit_date = today - datetime.timedelta(days=days)

    news_list = []

    try:
        # 机器之心新闻页面 URL
        url = 'https://www.jiqizhixin.com/news'
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 如果请求失败则抛出异常

        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找包含新闻列表的容器，通常是一个 div 或 section
        # 根据网页结构，这里我们假定新闻项包含在 class 为 'article-item' 的 div 中
        articles = soup.find_all('div', class_='article-item')

        if not articles:
            logging.warning("未找到任何新闻文章。请检查网页结构是否已改变。")
            return news_list

        for article in articles:
            try:
                # 提取日期
                date_str = article.find('p', class_='article-time').text.strip()
                date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').date()

                # 如果新闻日期早于指定日期，则停止抓取
                if date_obj < limit_date:
                    logging.info("已达到指定天数范围，停止抓取。")
                    return news_list

                # 提取标题和链接
                title_tag = article.find('h3', class_='article-title').find('a')
                link = title_tag['href']
                title = title_tag.text.strip()

                # 过滤掉非新闻链接
                if '/news/' not in link:
                    continue

                # 完善链接，确保是完整的 URL
                if not link.startswith('http'):
                    link = 'https://www.jiqizhixin.com' + link

                news_list.append({
                    'title': title,
                    'link': link,
                    'date': date_obj
                })

            except (AttributeError, ValueError) as e:
                logging.warning(f"处理机器之心新闻时出错，跳过该项: {e}")
                continue

    except requests.exceptions.RequestException as e:
        logging.error(f"访问机器之心网站时发生网络错误: {e}")

    return news_list


if __name__ == '__main__':
    # 测试函数
    news = catch_JQZX(days=1)
    for item in news:
        print(f"标题: {item['title']}")
        print(f"链接: {item['link']}")
        print(f"日期: {item['date']}")
        print("-" * 20)
    print(f"共抓取 {len(news)} 条新闻")

