import os
import shutil
import smtplib
import schedule
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

# Đường dẫn tuyệt đối đến file database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FOLDER = os.path.join(BASE_DIR, "database")
DB_FILE = os.path.join(DATABASE_FOLDER, "hang.sqlite3")
BACKUP_FOLDER = os.path.join(BASE_DIR, "backup")



def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("Gửi mail thành công.")
    except Exception as e:
        print(f"Gửi mail thất bại: {e}")


def backup_database():
    if not DB_FILE:
        print("Không có file database để backup.")
        return

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"backup_{now}.sqlite3"
    backup_file = os.path.join(BACKUP_FOLDER, backup_filename)

    try:
        shutil.copy(DB_FILE, backup_file)
        relative_path = os.path.join("backup", backup_filename)
        print(f"Backup thành công: {relative_path}")
        send_email(
            subject="Backup thành công",
            body=f"Thao tác thành công vào lúc {now}.\nFile được lưu với tên: {relative_path}"
        )
    except Exception as e:
        print(f"Backup Lỗi: {e}")
        send_email(
            subject="Backup Lỗi",
            body=f"Lỗi trong quá trình backup:\n{e}"
        )
schedule.every().day.at("23:24").do(backup_database)

print("Thông báo sẽ được gửi vào lúc 00:00...")

while True:
    schedule.run_pending()
    time.sleep(60)
