import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
import os


def send_report_email(sender_email, sender_password, receiver_email, subject, body, report_content):
    msg = MIMEMultipart()
    msg["From"] = sender_email

    # 如果 receiver_email 是一个列表，将其转换为逗号分隔的字符串
    if isinstance(receiver_email, list):
        msg["To"] = ", ".join(receiver_email)
    else:
        msg["To"] = receiver_email

    msg["Subject"] = subject

    # 将报告内容作为HTML正文添加到邮件中
    msg.attach(MIMEText(report_content, "html", "utf-8"))

    try:
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # Using QQ mail as an example
        server.login(sender_email, sender_password)

        # send_message 方法可以正确处理 MIMEMultipart 对象的 To 字段，即使它包含多个收件人
        server.send_message(msg)
        server.quit()
        print("邮件发送成功！")
        return True
    except Exception as e:
        print(f"发送邮件时出错: {e}")
        return False

