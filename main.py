import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
import ollama
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import os.path
import base64
from email.mime.text import MIMEText
import re
import subprocess  # 프로그램 재시작을 위한 모듈

# Gmail API를 사용하기 위한 인증 범위
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# 현재 디렉토리를 기반으로 파일 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRET_FILE = os.path.join(BASE_DIR, 'ollama_email_auto_response.json')
TOKEN_PATH = os.path.join(BASE_DIR, 'token.json')  # token.json 경로 명시

class OllamaWorker(QThread):
    response_received = pyqtSignal(str)

    def __init__(self, recipient, subject, purpose):
        super().__init__()
        self.recipient = recipient
        self.subject = subject
        self.purpose = purpose

    def run(self):
        try:
            prompt = (
                f"Write a professional email to {self.recipient} with the subject '{self.subject}'. "
                f"The purpose of the email is: {self.purpose}. Please write the email body only, "
                f"without including 'Subject:', 'To:', or 'From:' lines."
            )
            response = ollama.chat(
                model="llama3.1",
                messages=[
                    {'role': 'user', 'content': prompt},
                ],
            )
            if 'message' in response:
                email_body = response['message']['content']
                email_body += "\n\n---\nThis email was generated using Meta's Llama 3.1 model."
                self.response_received.emit(email_body)
            else:
                self.response_received.emit("Error in generating email content.")
        except Exception as e:
            self.response_received.emit(f"Error: {str(e)}")


class EmailSender:
    def __init__(self):
        self.creds = None
        self.authenticate()

    def authenticate(self):
        # 절대 경로를 사용하여 파일을 찾도록 수정
        if os.path.exists(TOKEN_PATH):
            print("Found token.json at:", TOKEN_PATH)  # 디버깅 코드
            self.creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # 절대 경로로 OAuth 클라이언트 시크릿 파일 지정
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_SECRET_FILE, SCOPES
                )
                self.creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w') as token:
            print("Creating token.json at:", TOKEN_PATH)  # 디버깅 코드
            token.write(self.creds.to_json())

    def send_email(self, to, subject, body):
        try:
            service = build('gmail', 'v1', credentials=self.creds)
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            send_message = service.users().messages().send(
                userId="me", body={'raw': raw_message}
            ).execute()
            return "Email sent successfully"
        except Exception as e:
            return f"An error occurred while sending the email: {e}"

    def logout(self):
        # 로그아웃 기능 구현: 토큰 파일 삭제
        if os.path.exists(TOKEN_PATH):
            os.remove(TOKEN_PATH)
            return "Logged out successfully"
        else:
            return "You are not logged in."

class AutoEmailApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.email_sender = EmailSender()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Automatic Email Writer')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit, QTextEdit {
                font-size: 13px;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QPushButton {
                font-size: 14px;
                padding: 8px 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title
        title_label = QLabel('Automatic Email Writer', self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont('Arial', 18, QFont.Bold))
        layout.addWidget(title_label)

        # Input fields
        layout.addWidget(QLabel('Recipient Email:'))
        self.recipient_input = QLineEdit(self)
        layout.addWidget(self.recipient_input)

        layout.addWidget(QLabel('Email Subject:'))
        self.subject_input = QLineEdit(self)
        layout.addWidget(self.subject_input)

        layout.addWidget(QLabel('Purpose of the email:'))
        self.purpose_input = QTextEdit(self)
        self.purpose_input.setFixedHeight(100)
        layout.addWidget(self.purpose_input)

        # Generate button
        self.generate_button = QPushButton('Generate Email', self)
        self.generate_button.clicked.connect(self.generate_email)
        layout.addWidget(self.generate_button)

        # Progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # Email content display
        layout.addWidget(QLabel('Generated Email Content:'))
        self.email_content = QTextEdit(self)
        self.email_content.setReadOnly(True)
        layout.addWidget(self.email_content)

        # Send button
        self.send_button = QPushButton('Send Email', self)
        self.send_button.clicked.connect(self.send_email)
        self.send_button.setEnabled(False)  # Initially disable
        layout.addWidget(self.send_button)

        # Logout button
        self.logout_button = QPushButton('Logout', self)
        self.logout_button.clicked.connect(self.logout)
        layout.addWidget(self.logout_button)

    def generate_email(self):
        recipient = self.recipient_input.text()
        subject = self.subject_input.text()
        purpose = self.purpose_input.toPlainText()

        if not recipient or not subject or not purpose:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        if not self.is_valid_email(recipient):
            QMessageBox.warning(self, "Input Error", "The recipient email address is invalid.")
            return

        self.progress_bar.show()
        self.generate_button.setEnabled(False)
        self.worker = OllamaWorker(recipient, subject, purpose)
        self.worker.response_received.connect(self.display_email)
        self.worker.start()

    def is_valid_email(self, email):
        """이메일 주소 형식 검증"""
        regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(regex, email) is not None

    def display_email(self, email_body):
        self.email_content.setText(email_body)
        self.progress_bar.hide()
        self.generate_button.setEnabled(True)
        self.send_button.setEnabled(True)  # Enable send button after generation

    def send_email(self):
        recipient = self.recipient_input.text()
        subject = self.subject_input.text()
        body = self.email_content.toPlainText()

        if recipient and subject and body:
            result = self.email_sender.send_email(recipient, subject, body)
            QMessageBox.information(self, "Send Result", result)
        else:
            QMessageBox.warning(self, "Send Error", "Please generate an email```python first.")

    def logout(self):
        """로그아웃: 현재 로그인 상태를 종료"""
        result = self.email_sender.logout()
        QMessageBox.information(self, "Logout", result)
        # 로그아웃 후 애플리케이션 재시작 유도
        QTimer.singleShot(500, self.restart_application)  # 0.5초 후 재시작

    def restart_application(self):
        """애플리케이션 재시작 로직"""
        # 현재 프로그램 경로를 실행하여 새로운 프로세스로 시작
        subprocess.Popen([sys.executable, os.path.abspath(__file__)])
        sys.exit()  # 현재 프로그램 종료

def main():
    app = QApplication(sys.argv)
    ex = AutoEmailApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
