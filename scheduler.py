import schedule
import time
import datetime
import os
import glob
from crawl_test import make_report
from send_email import send_report_email

# Email configuration
EMAIL_CONFIG = {
    'sender_email': 'email address',
    'sender_password': 'authorization code',  # For QQ mail, this is an authorization code
    'receiver_email': ['email address'],  # Changed to a list for multiple recipients
    'subject': 'AI Daily Report - {date}',
    'body': 'Dear all,\n\nPlease find the AI daily report below.\n\nBest regards,\nAI Report System'
}


def find_latest_report():
    """Find the latest generated report file"""
    year = datetime.datetime.now().year
    today = datetime.datetime.now().strftime("%m%d")
    report_dir = f'AI_Report{year}/{today}'

    if not os.path.exists(report_dir):
        return None

    # Look for final report first, then any report
    final_reports = glob.glob(f'{report_dir}/AI_daily_report_final*.docx')
    if final_reports:
        return max(final_reports, key=os.path.getctime)  # Return the newest file

    all_reports = glob.glob(f'{report_dir}/AI_daily_report_*.docx')
    if all_reports:
        return max(all_reports, key=os.path.getctime)

    return None


def generate_and_send_report():
    """Generate report and send via email"""
    try:
        print(f"正在生成报告： {datetime.datetime.now()}")

        # Generate report content (HTML string) and DOCX file
        manual = False  # Set to False for automated sending
        paper_days = 1 if datetime.datetime.now().weekday() != 1 else 3
        news_days = 2 if datetime.datetime.now().weekday() != 0 else 3

        report_content = make_report(manual, paper_days, news_days, True, True, True, '4o')

        if not report_content:
            print("生成报告内容为空")
            return False

        # Send email with report content in body
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        subject = EMAIL_CONFIG['subject'].format(date=today_str)

        success = send_report_email(
            EMAIL_CONFIG['sender_email'],
            EMAIL_CONFIG['sender_password'],
            EMAIL_CONFIG['receiver_email'],  # Pass as a list
            subject,
            EMAIL_CONFIG['body'],
            report_content  # Pass report content here
        )

        if success:
            print(f"报告已生成并成功发送于 {datetime.datetime.now()}！")
        else:
            print(f"在 {datetime.datetime.now()} 发送报告失败")

        return success

    except Exception as e:
        print(f"生成并发送报告时出错: {e}")
        return False


def send_existing_report():
    """Send the latest existing report without generating a new one"""
    try:
        report_path = find_latest_report()
        if not report_path:
            print("未找到现有报告可发送")
            return False

        # For now, this function will generate a new report and send it as HTML
        # If you want to send the content of an existing DOCX, you would need a DOCX to HTML converter
        print("send_existing_report function is re-purposed to generate and send a new report as HTML.")
        return generate_and_send_report()

    except Exception as e:
        print(f"发送现有报告时出错: {e}")
        return False


def setup_schedule():
    """Setup the scheduled tasks"""
    # Schedule report generation and sending every day at 9:00 AM
    schedule.every().day.at("15:35").do(generate_and_send_report)

    # You can add more schedules as needed
    # schedule.every().monday.at("10:00").do(generate_and_send_report)
    # schedule.every().hour.do(some_other_function)

    print("调度器设置完成。已安排的任务：")
    print("- 每日报告生成和发送时间：15:35")


def run_scheduler():
    """Run the scheduler"""
    setup_schedule()
    print("调度器已启动。按 Ctrl+C 停止。")

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\nScheduler stopped.")


if __name__ == '__main__':
    # You can run different modes:

    # 1. Run the scheduler (default)
    run_scheduler()

    # 2. Generate and send report immediately (uncomment to use)
    # generate_and_send_report()

    # 3. Send existing report immediately (uncomment to use)
    # send_existing_report()

