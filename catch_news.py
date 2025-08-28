import datetime
import re
import sqlite3

from catch_sources.catch_36kr import catch_36kr
from catch_sources.catch_IThome import catch_IThome
from catch_sources.catch_JQZX import catch_JQZX  # 机器之心
from catch_sources.catch_QBitAI import catch_QBitAI
from catch_sources.catch_theverge import catch_theverge


# Initialize the database and create the table if it doesn't exist
def init_db():
    conn = sqlite3.connect('links.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS links
                 (link TEXT PRIMARY KEY, date_added TEXT)''')
    conn.commit()
    conn.close()

# Check if a link exists in the database
def link_exists(link):
    link = re.sub(r'https?://', '', link)
    conn = sqlite3.connect('links.db')
    c = conn.cursor()
    c.execute('SELECT 1 FROM links WHERE link = ?', (link,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

# Add a group of links to the database
def add_links(links):
    conn = sqlite3.connect('links.db')
    c = conn.cursor()
    date_added = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for link in links:
        #去掉http和https的区别
        link = re.sub(r'https?://', '', link)
        if not link_exists(link):
            try:
                c.execute('INSERT INTO links (link, date_added) VALUES (?, ?)', (link, date_added))
            except sqlite3.IntegrityError:
                print(f"Link already exists: {link}")
    conn.commit()
    conn.close()

# Compare a group of links and retain the unique ones
def get_unique_links(links):
    links = list(set(links))
    unique_links = [link for link in links if not link_exists(link)]
    return unique_links


def delete_today_records():
    # Get today's date in the format "YYYY-MM-DD"
    today = datetime.datetime.now().strftime('%Y-%m-%d')

    # Connect to the database
    conn = sqlite3.connect('links.db')
    c = conn.cursor()

    # Delete records where the date_added is today
    c.execute('DELETE FROM links WHERE date(date_added) = ?', (today,))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def catch_all(days = 1, english_source = True):
    infos = []
    init_db()

    # 英文新闻
    if english_source:
        theverge = catch_theverge(days)
        print('   -- The Verge Catch Success')
        infos += theverge

        # techcrunch = catch_techcrunch(days)
        # print('   -- TechCrunch Catch Success')
        # infos += techcrunch

    # 中文新闻
    IThome = catch_IThome(days)
    print('   -- IT之家 Catch Success')

    info_36kr = catch_36kr(days)
    print('   -- 36氪 Catch Success')

    info_36kr_tech = catch_36kr(days)
    print('   -- 36氪 Tech news Catch Success')

    JQZX = catch_JQZX(days)
    print('   -- 机器之心 Catch Success')

    QBitAI = catch_QBitAI(days)
    print('   -- 量子位 Catch Success')

    infos += (info_36kr
              + JQZX + QBitAI
              + info_36kr_tech
              + IThome) #中文新闻，按质量排序

    # 去掉空格
    for info in infos:
        info['title'] = re.sub(r'(?<![A-Za-z])\s+|\s+(?![A-Za-z])', '', info['title']) #regex 具体
    
    # 替换引号
    for info in infos:
        info['title'] = info['title'].replace('"', '``').replace('“', '「').replace('”', '」')

    # 获取唯一链接
    unique_links = get_unique_links([info['link'] for info in infos])
    unique_infos = [info for info in infos if info['link'] in unique_links]

    return unique_infos
# catch_all()


def read_links_db():
    # Connect to the database
    conn = sqlite3.connect('links.db')
    c = conn.cursor()

    # Execute a SELECT query to fetch all records from the links table
    c.execute('SELECT * FROM links')

    # Fetch all results
    rows = c.fetchall()

    # Print each record
    for row in rows:
        print(f"Link: {row[0]}, Date Added: {row[1]}")

    # Close the connection
    conn.close()


# Call the function to read and print the database contents
# read_links_db()
