from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import datetime


def catch_theverge(days=7):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-cache")
    chrome_options.add_argument("--disable-application-cache")
    chrome_options.add_argument("--disable-offline-load-stale-cache")
    chrome_options.add_argument("--disk-cache-size=0")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = None
    new_info = []

    try:
        driver = webdriver.Chrome(options=chrome_options)
        url = 'https://www.theverge.com/ai-artificial-intelligence'
        driver.get(url)

        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.duet--content-cards--content-card'))
            )
        except Exception as e:
            print(f"The Verge: Error waiting for dynamic content: {e}")
            pass  # Attempt to proceed

        html = driver.page_source
        if not html:
            print("The Verge: Failed to get page source.")
            return new_info

        soup = BeautifulSoup(html, 'html.parser')
        if not soup:
            print("The Verge: Failed to parse page source.")
            return new_info

        articles_container = soup.find('div', {'class': 'duet--layout--main'})
        if not articles_container:
            articles = soup.find_all('div', {'class': 'duet--content-cards--content-card'})
        else:
            articles = articles_container.find_all('div', {'class': 'duet--content-cards--content-card'})

        if not articles:
            print("The Verge: No article blocks found with class 'duet--content-cards--content-card'.")
            return new_info

        now = datetime.datetime.now()
        # Ensure target_date is naive if news_time will be naive for comparison
        target_date = (now - datetime.timedelta(days=days)).replace(tzinfo=None)

        for article_div in articles:
            title_tag = article_div.find('h2', {'class': 'font-polysans'})
            if not title_tag:
                continue

            link_tag = title_tag.find('a')
            if not link_tag or not link_tag.has_attr('href'):
                continue

            title = title_tag.get_text(strip=True)
            link_url = link_tag['href']
            if not link_url.startswith('http'):
                link_url = "https://www.theverge.com" + link_url

            time_tag = article_div.find('time')
            if not time_tag or not time_tag.has_attr('datetime'):
                continue

            time_text = time_tag['datetime']
            news_time_aware = None
            try:
                news_time_aware = datetime.datetime.fromisoformat(time_text.replace('Z', '+00:00'))
            except ValueError:
                try:
                    news_time_aware = datetime.datetime.strptime(time_text, "%Y-%m-%dT%H:%M:%S.%fZ")
                    news_time_aware = news_time_aware.replace(
                        tzinfo=datetime.timezone.utc)  # Make it offset-aware if strptime creates naive
                except ValueError:
                    print(f"The Verge: Could not parse date '{time_text}' for article '{title}'.")
                    continue

            news_time_naive_utc = news_time_aware.astimezone(datetime.timezone.utc).replace(tzinfo=None)

            if news_time_naive_utc >= target_date:
                new_info.append({'title': title, 'link': link_url, 'date': news_time_naive_utc})

    except Exception as e:
        print(f"An error occurred in catch_theverge: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()

    new_info.sort(key=lambda x: x['date'], reverse=True)
    return new_info
