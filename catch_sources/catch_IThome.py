from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import datetime
import time

def catch_IThome(days = 7):
    # 初始化 Chrome 选项
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    # 初始化 WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    # 加载网页
    url = 'https://www.ithome.com/list/'  # 替换为实际 URL
    driver.get(url)

    # 等待动态内容加载完成（根据具体情况调整等待条件）
    try:
        # 替换为实际的等待条件
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'more'))
        )
    except Exception as e:
        print(f"加载动态内容时出错: {e}")

    #新增逻辑 一直点击加载按钮 直到加载完新闻
    now = datetime.datetime.now()
    seven_days_ago = now - datetime.timedelta(days=days)
    all_news_within_seven_days = True # 检测是否加载完新闻

    # 循环点击“加载更多”按钮，直到加载到7天前的新闻
    while all_news_within_seven_days:
        # 获取页面 HTML 内容
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # 查找目标 div 元素
        target_div = soup.find('ul', {'class': 'datel'})

        # 获取所有链接
        list_items = target_div.find_all('li')

        for item in list_items:
            time_info = item.find('i')
            time_text = time_info.get_text(strip=True)

            # 将时间文本转换为 datetime 对象
            try:
                news_time = datetime.datetime.strptime(time_text,"%Y-%m-%d %H:%M:%S")
            except ValueError:
                print(f"日期格式不匹配: {time_text}")
                continue

            if news_time < seven_days_ago:
                # 如果发现有新闻超过7天，标记停止加载
                all_news_within_seven_days = False
                break

        if not all_news_within_seven_days:
            break

        # 查找并点击“加载更多”按钮
        try:
            load_more_button = driver.find_element(By.CLASS_NAME, 'more')
            driver.execute_script("arguments[0].click();", load_more_button)
            time.sleep(0.5)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'more'))
            )
        except Exception as e:
            print(f"点击加载更多按钮时出错或没有更多内容可加载: {e}")
            break


    # 获取页面 HTML 内容
    html = driver.page_source

    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html, 'html.parser')

    # 查找目标 div 元素
    target_div = soup.find('ul', {'class': 'datel'})

    # 获取所有链接
    list_items = target_div.find_all('li')

    new_info = []

    # 打印或处理获取到的 URL、标题和时间信息
    for item in list_items:

        link = item.find('a', {'class': 't'})
        time_info = item.find('i')
        time_text = time_info.get_text(strip=True)

        href = link.get('href')
        title = link.get_text(strip=True)
        #避免添加 lapin开头域名的链接
        if 'lapin' in href:
            continue
        # 初筛去除无关链接
        keywords = ["淘宝", "京东", "红米", "拼多多", "大促", "预售", "优惠", "直播", "带货", "停售", "渲染", "首发", "退款", "刷单",
                    "价格战", "交付", "金融", "支付", "补贴", "抽奖", "优惠券", "上市", "开售", "商店", "决赛", "电商", "超市", "定档", "动漫",
                    "鼠标", "键盘", "显示器", "手机", "耳机", "手表", "平板", "眼睛", "眼镜",  "电视", "相机", "冰箱", "空调", "电纸书", "音箱",
                    "手柄", "笔记本", "镜头", "电源", "扬声器", "扩展坞", "主机", "WATCH", "掌机", "机型", "风扇", "机箱", "BIOS", "主板", "戒指",
                    "快递", "充电", "车", "高铁", "飞机", "酒店", "物流",  "水冷", "域名", "裁员", "打印", "触屏", "电池", "火箭", "飞行", "电影",
                    "外卖", "宇航", "飞船", "OLED", "探月", "月球", "太阳", "卫星", "iPhone", "Galaxy", "Mac", "维护", "Watch", "罗技",
                    "Steam", "游戏", "教育", "驾驶", "病", "饭", "食", "菜", "肉", "剧", "利率", "社交", "传感", "基因", "地图", "保险",
                    "国服", "电竞", "赛事", "米哈游", "安卓", "招募", "补丁", "手游", "HomeKit", "浴霸", "显示屏", "无人机", "财富", "控制器",
                    "吉利", "特斯拉", "蔚来", "理想", "比亚迪", "五菱", "长安", "吉利", "上汽", "一汽", "广汽", "北汽", "长城", "奇瑞", "江淮",
                    "东风", "大众", "SUV", "宝马", "纯电","增程", "碳化硅", "清洁", "照片", "透明度", "基金会", "路由器", "航班",
                    "阅读", "医疗", "到家", "上门", "货币", "骗", "警", "出版", "罢工", "航空", "合并", "航天", "音乐", "通话", "视频", "投票",
                    "声道", "基站", "东来", "漏洞", "订阅", "液化", "药物", "潜水", "油", "太空", "预览版", "症", "股票",
                    "DRAM", "NAND", "CPU", "SSD", "硬盘", "内存",  "芯片组", "封装",  "射频", "电路", "电容", "电阻", "电感", "遥控", "美光",
                    "处理器", "公牛", "NASA", "火星", "体验店", "评测", "联名", "新作", "钓鱼", "木马", "Android", "原神"]
        if any(keyword in title for keyword in keywords):
            continue

        try:
            news_time = datetime.datetime.strptime(time_text,"%Y-%m-%d %H:%M:%S")
        except ValueError:
            print(f"日期格式不匹配: {time_text}")
            continue
        
        if news_time > seven_days_ago:
            new_info.append({'title': title, 'link': href, 'date': news_time})
            
        # print(f"URL: {href}, Title: {title}, Time: {time_text}")

    # 关闭 WebDriver
    driver.quit()

    return new_info


# print(catch_IThome())
# print(len(catch_IThome()))
