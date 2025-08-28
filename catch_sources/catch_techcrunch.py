from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import datetime


def catch_techcrunch(days=7):
    # 初始化 Chrome 选项
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    chrome_options.add_argument("--disable-cache")
    chrome_options.add_argument("--disable-application-cache")
    chrome_options.add_argument("--disable-offline-load-stale-cache")
    chrome_options.add_argument("--disk-cache-size=0")
    # chrome_options.add_argument("--headless")  # 添加无头模式
    chrome_options.add_argument("--disable-gpu")  # 禁用 GPU 加速（无头模式下推荐）
    chrome_options.add_argument("--window-size=1920x1080")  # 设置窗口大小（无头模式下也有用）

    # 初始化 WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    # 加载网页
    url = 'https://techcrunch.com'  # 替换为实际 URL 新智元
    driver.get(url)

    # 等待动态内容加载完成（根据具体情况调整等待条件）
    try:
        # 替换为实际的等待条件
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'wp-block-group'))
        )
    except Exception as e:
        print(f"加载动态内容时出错: {e}")

    # 新增逻辑 一直点击加载按钮 直到加载完一周内的新闻
    now = datetime.datetime.now()
    seven_days_ago = now - datetime.timedelta(days=days)
    # all_news_within_seven_days = True  # 检测是否加载完一周内的新闻
    #
    # # 判断是否加载完一周内的新闻
    # while all_news_within_seven_days:
    #     # 获取页面 HTML 内容
    #     html = driver.page_source
    #     soup = BeautifulSoup(html, 'html.parser')
    #
    #     # 查找目标 div 元素
    #     target_div = soup.find('div', {'class': 'wp-block-group'})
    #
    #     # 获取所有链接
    #     list_items = target_div.find_all('div', {'class': 'wp-block-tc23-post-picker'})
    #
    #     for item in list_items:
    #         time_info = item.find('time')
    #         time_text = time_info.getget('datetime')
    #
    #         # 时间格式是 2024-08-18T06:00:00-07:00 或者
    #         try:
    #             news_time = datetime.datetime.strptime(time_text, "%Y-%m-%dT%H:%M:%S%z")
    #         except ValueError:
    #             print(f"日期格式不匹配: {time_text}")
    #             continue
    #
    #         # 如果有一条新闻的时间早于七天前，就退出循环
    #         if news_time < seven_days_ago:
    #             # print(f"找到一条新闻早于七天前: {news_time}")
    #             all_news_within_seven_days = False
    #             break
    #
    #     # 如果所有新闻都在7天内，就点击“加载更多”按钮
    #     if not all_news_within_seven_days:
    #         break
    #
    #     # 无需点击。需要模拟滚动到底部
    #     try:
    #         load_more_button = driver.find_element(By.CLASS_NAME, 'post-picker-group-pagination__next')
    #         # print("找到加载更多按钮成功")
    #         driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
    #         # print("滚动到底部成功")
    #         time.sleep(2)
    #         load_more_button.click()
    #         print("点击加载更多按钮成功")
    #     except Exception as e:
    #         print(f"点击加载更多按钮时出错: {e}")
    #         break

    # 获取页面 HTML 内容
    html = driver.page_source

    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html, 'html.parser')

    # 查找目标 div 元素
    target_div = soup.find('div', {'class': 'wp-block-columns'})
    # # 获取所有链接
    list_items = target_div.find_all('div', {'class': 'wp-block-tc23-post-picker'})
    #
    new_info = []
    #
    # 打印或处理获取到的 URL、标题和时间信息
    for item in list_items:

        link = item.find('h2').find('a')
        time_info = item.find('time')

        href = link.get('href')
        title = link.get_text(strip=True)
        if time_info:
            time_text = time_info.get('datetime')

            try:
                # 2024-08-15T07:49:31-07:00 格式，仅保留前19位
                news_time = datetime.datetime.strptime(time_text[:19], "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                print(f"日期格式不匹配: {time_text}")
                continue
            if news_time > seven_days_ago:
                new_info.append({'title': title, 'link': href, 'date': news_time})
                # print(f"URL: {href}, Title: {title}, Time: {news_time}")

    # 关闭 WebDriver
    driver.quit()

    return new_info

#test
# info = catch_techcrunch()
# for i in info:
#     print(i)
#     print("\n")