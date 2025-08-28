
import datetime
import requests
from bs4 import BeautifulSoup

def catch_QBitAI(days=7):
    # Load webpage
    url = 'https://www.qbitai.com/'  # Replace with actual URL
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.RequestException as e:
        print(f"Error loading page: {e}")
        return []

    # Additional logic to click load more button until news from 7 days ago is loaded
    now = datetime.datetime.now()
    seven_days_ago = now - datetime.timedelta(days=days)
    all_news_within_seven_days = True  # Check if news is loaded
    new_info = []

    # Get page HTML content
    html = response.content

    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Find target div element
    target_div = soup.find('div', {'class': 'article_list'})
    # Get all links
    list_items = target_div.find_all('div', {'class': 'text_box'})

    # Print or process the retrieved URL, title, and time information
    for item in list_items:
        link = item.find('h4').find('a')  # Link is in the a tag
        time_info = item.find('span', {'class': 'time'})

        href = link.get('href')
        title = link.get_text(strip=True)
        time_text = time_info.get_text(strip=True)

        # Only return news within 7 days
        news_time = now
        if '前' in time_text or '天' in time_text:
            if "刚刚" in time_text:
                news_time = now
            if "分钟前" in time_text:
                minute = int(time_text.split("分钟前")[0])
                news_time = now - datetime.timedelta(minutes=minute)
            if "小时前" in time_text:
                hour = int(time_text.split("小时前")[0])
                news_time = now - datetime.timedelta(hours=hour)
            if "昨天" in time_text:
                news_time = now - datetime.timedelta(days=1)
            if "前天" in time_text:
                news_time = now - datetime.timedelta(days=2)
            if news_time > seven_days_ago:
                new_info.append({'title': title, 'link': href, 'date': news_time})

        else:
            try:
                news_time = datetime.datetime.strptime(time_text, "%Y-%m-%d")
            except ValueError:
                print(f"Date format mismatch: {time_text}")
                continue
            if news_time > seven_days_ago:
                new_info.append({'title': title, 'link': href, 'date': news_time})

    return new_info

# catch_QBitAI()
