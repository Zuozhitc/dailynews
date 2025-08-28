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
