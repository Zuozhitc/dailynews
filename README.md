Crawl_test 是主程序，make report用于可视化运行这个程序。

catch_sources是单独的网站爬虫，catch_news用于爬取新闻，arxiv_summary用于获得论文pdf链接。

ask_gpt用于辅助人工制作日报，可设置快捷方式直接启动来用。


环境设置：安装python 3.12或以上版本，安装Pycharm，克隆Github项目后，terminal使用 
pip install -r requirements
等待完成安装即可。安装后尝试运行make_report.py。如果报错，就安装提示缺少的依赖项
主要程序：crawl_test.py，make_report.py,ask_gpt.py
主要界面使用方法：点击生成即可，预计10分钟左右。一般下午4点左右生成一次。
保存的链接在本地。生成的内容也在本地文件夹中
ask_gpt.py用于辅助生成日报，输入问题，输出答案。

可能报错：
1）爬虫出错。预计是网页html有更新，需要更新爬虫。（预估1~2个月会发生一次）
2）网络报错。API不可用或者第三方服务器抽风
3）API费用不足，充值。
4）API 返回的内容格式不对，导致程序出错。晚点再试一次即可

# AI 日报系统

本项目用于生成每日AI报告，现在已支持通过电子邮件自动发送报告。

## 新增功能

- **邮件发送**：自动通过电子邮件发送生成的 DOCX 报告。
- **定时任务**：在指定时间定时生成报告并发送邮件。

## 设置与使用

### 1. 前提条件

请确保您已安装 Python 3.x。您还需要安装以下必要的库：

```bash
pip install schedule docx
```

### 2. 邮件配置 (`send_email.py`)

`send_email.py` 文件包含负责发送电子邮件的 `send_docx_email` 函数。该文件不再包含 `if __name__ == '__main__':` 块中的示例用法，因为其主要用途现在是通过 `scheduler.py` 调用。

### 3. 调度器配置 (`scheduler.py`)

`scheduler.py` 文件处理报告的自动生成和发送。它使用 `schedule` 库来管理任务。

打开 `scheduler.py` 并修改 `EMAIL_CONFIG` 字典：

```python
EMAIL_CONFIG = {
    'sender_email': 'your_email@qq.com',
    'sender_password': 'your_authorization_code',  # 对于QQ邮箱，这是授权码，不是您的登录密码
    'receiver_email': 'recipient_email@example.com',
    'subject': 'AI 每日报告 - {date}',
    'body': '各位好,\n\n请查收附件中的AI每日报告。\n\n此致,\nAI 报告系统'
}
```

请确保这些设置与您的电子邮件设置匹配。

#### 自动报告发现

`scheduler.py` 现在包含一个 `find_latest_report()` 函数，该函数会自动定位最新生成的 DOCX 报告文件。此函数会在 `AI_Report{年份}/{月份日期}` 目录（例如，`AI_Report2025/0805`）中搜索文件，并优先查找 `AI_daily_report_final*.docx` 文件。这意味着您不再需要手动指定报告路径。

#### 报告调度

默认情况下，`scheduler.py` 配置为每天上午 9:00 生成并发送报告。您可以在 `setup_schedule` 函数中修改调度：

```python
def setup_schedule():
    # 每天上午 9:00 调度报告生成和发送
    schedule.every().day.at("09:00").do(generate_and_send_report)
    
    # 您可以根据需要添加更多调度
    # schedule.every().monday.at("10:00").do(generate_and_send_report)
    # schedule.every().hour.do(some_other_function)
```

有关更高级的调度选项，请参阅 `schedule` 库的文档。

### 4. 运行调度器

要启动调度器，请运行 `scheduler.py`：

```bash
python scheduler.py
```

此脚本将无限期运行，每分钟检查一次计划任务。您可以按 `Ctrl+C` 停止它。

### 5. 手动报告生成和发送

`scheduler.py` 还提供了立即生成和发送报告的选项，用于测试或手动执行：

- **立即生成并发送**（在 `scheduler.py` 中取消注释）：

  ```python
  # generate_and_send_report()
  ```

- **立即发送现有报告**（在 `scheduler.py` 中取消注释）：

  ```python
  # send_existing_report()
  ```

## 项目结构

- `make_report.py`：用于生成日报的原始脚本。
- `send_email.py`：包含电子邮件发送逻辑的新文件。
- `scheduler.py`：用于调度报告生成和电子邮件发送的新文件，包括自动报告发现功能。
- `doc_create.py`：用于创建 DOCX 文档的辅助函数。
- `crawl_test.py`：用于抓取新闻和论文，并与 `doc_create.py` 集成的核心逻辑。
- `functions.py`：实用函数，可能用于 GPT 交互。
- `catch_news.py`：处理新闻抓取和链接管理。
- `arxiv_summary.py`：处理 arXiv 论文摘要（基于 API）。
- `arxiv_summary_web.py`：处理 arXiv 论文摘要（基于网页）。
- `catch_sources/`：包含各种新闻源特定抓取脚本的目录。

## 重要提示

- 确保您的电子邮件提供商允许通过 SMTP 发送电子邮件，并且如果需要，您已生成授权码/应用程序密码。
- `scheduler.py` 中的 `find_latest_report` 函数会自动查找最新生成的 DOCX 文件。请确保 `make_report.py` 将报告保存到 `AI_Report{年份}/{月份日期}` 目录。
- 为了持续运行，请考虑在服务器上运行 `scheduler.py` 脚本，或使用进程管理器（例如，`systemd`、`supervisor`、`pm2`）来保持其运行。
