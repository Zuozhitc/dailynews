from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import datetime
import os


def catch_producthunt(days=7):
    # 初始化 Chrome 选项
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-cache")
    chrome_options.add_argument("--disable-application-cache")
    chrome_options.add_argument("--disable-offline-load-stale-cache")
    chrome_options.add_argument("--disk-cache-size=0")
    chrome_options.add_argument("--disable-gpu")  # 禁用 GPU 加速（无头模式下推荐）
    chrome_options.add_argument("--window-size=1920x1080")  # 设置窗口大小
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")  # 设置用户代理

    # 初始化 WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    # 加载网页
    url = 'https://www.producthunt.com'
    driver.get(url)
    print("正在加载 ProductHunt 页面...")

    # 等待页面加载完成
    try:
        # 等待页面主要内容加载完成
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, 'h1'))
        )
        print("页面主要内容已加载")

        # 额外等待，确保动态内容完全加载
        time.sleep(5)
    except Exception as e:
        print(f"等待页面加载时出错: {e}")
        try:
            driver.save_screenshot("producthunt_error.png")
            print(f"已保存错误截图到 producthunt_error.png")
        except Exception as screenshot_error:
            print(f"保存截图失败: {screenshot_error}")

    # 获取页面 HTML 内容
    html = driver.page_source

    # 保存原始HTML以便调试
    try:
        # 使用当前目录而不是/tmp
        html_file_path = "producthunt_raw.html"
        with open(html_file_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"已保存原始HTML到 {html_file_path}")
    except Exception as file_error:
        print(f"保存HTML文件失败，但将继续处理: {file_error}")

    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html, 'html.parser')

    # 查找页面标题，确认页面已正确加载
    page_title = soup.title.text if soup.title else "无标题"
    print(f"页面标题: {page_title}")

    new_info = []

    # 查找"Top Products Launching Today"部分
    # 首先尝试查找h1标题
    top_products_heading = soup.find('h1', string=lambda text: text and "Top Products" in text)

    if not top_products_heading:
        print("未找到'Top Products'标题，尝试其他方法...")
        # 尝试查找所有h1标签
        all_h1 = soup.find_all('h1')
        print(f"找到 {len(all_h1)} 个h1标签: {[h.text for h in all_h1]}")

    # 查找所有产品项
    # 现在ProductHunt使用更通用的结构，我们需要查找包含产品信息的section元素
    product_sections = soup.find_all('section', {"class": "group"})
    print(f"找到 {len(product_sections)} 个产品section")

    if not product_sections:
        # 如果找不到特定class的section，尝试其他选择器
        product_sections = soup.select('div > section')
        print(f"使用备选选择器找到 {len(product_sections)} 个产品section")

    # 处理找到的产品
    for item in product_sections:
        try:
            # 尝试查找产品链接和标题
            link_element = item.find('a')
            if not link_element:
                continue

            # 获取链接
            href = link_element.get('href')
            if not href:
                continue

            # 确保链接是完整的URL
            if href.startswith('/'):
                href = url + href

            # 获取标题
            title = link_element.get('aria-label')
            if not title:
                # 尝试从链接内部获取标题
                title_element = link_element.find('h3') or link_element.find('h2') or link_element.find('div', {
                    'class': 'font-bold'})
                if title_element:
                    title = title_element.get_text(strip=True)

            if not title:
                continue

            print(f"找到产品: {title} - {href}")

            # 检查是否与AI相关
            is_ai_related = False

            # 检查标题中是否包含"AI"
            if 'AI' in title.split(' '):
                is_ai_related = True
                print(f"标题包含AI: {title}")

            # 查找标签
            tags = []
            tag_elements = item.find_all('a')
            for tag in tag_elements:
                tag_text = tag.get_text(strip=True)
                tags.append(tag_text)
                if tag_text == 'Artificial Intelligence':
                    is_ai_related = True
                    print(f"找到AI标签: {title}")

            # 如果找不到明确的标签，尝试在产品描述中查找AI相关关键词
            if not is_ai_related:
                description_element = item.find('p') or item.find('div', {'class': 'text-sm'})
                if description_element:
                    description = description_element.get_text(strip=True).lower()
                    ai_keywords = ['artificial intelligence', 'machine learning', 'neural network', 'deep learning',
                                   'gpt', 'llm', 'large language model']
                    if any(keyword in description.lower() for keyword in ai_keywords):
                        is_ai_related = True
                        print(f"描述包含AI关键词: {title}")

            # 如果与AI相关，添加到结果中
            if is_ai_related:
                new_info.append({
                    'title': title,
                    'link': href,
                    'tag': 'Artificial Intelligence',
                    'tags': tags
                })

        except Exception as e:
            print(f"处理产品时出错: {e}")

    # 如果今天是周一，尝试获取更多产品（昨天的）
    now = datetime.datetime.now()
    if now.weekday() == 0:
        print("今天是周一，尝试获取昨天的产品...")
        # 这里可以添加获取昨天产品的逻辑
        # 由于页面结构已变化，我们可能需要查找"Yesterday"部分或其他指示昨天产品的元素

    # 关闭 WebDriver
    driver.quit()

    print(f"总共找到 {len(new_info)} 个AI相关产品")
    return new_info


if __name__ == "__main__":
    # 测试函数
    results = catch_producthunt()
    print("\n最终结果:")
    for item in results:
        print(f"标题: {item['title']}")
        print(f"链接: {item['link']}")
        print(f"标签: {item['tag']}")
        print("---")
