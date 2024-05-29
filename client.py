import sys
import socket
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLineEdit, QLabel, QInputDialog
from PyQt5.QtGui import QColor, QTextCursor

HOST = '127.0.0.1'
PORT = 6789

# Client setup
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

class ChatApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.nickname, ok = QInputDialog.getText(self, 'Nickname', 'Enter your nickname:')
        if ok and self.nickname:
            join_message = f'<span style="color: #ff6600">{self.nickname}</span> has joined the chat!'
            client.send(join_message.encode('utf-8'))
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.start()
        else:
            self.close()

    def initUI(self):
        self.setWindowTitle('Chat Application')

        self.chat_area = QTextEdit(self)
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("background-color: #f0f0f0; color: #333;")

        self.entry = QLineEdit(self)
        self.entry.returnPressed.connect(self.send_message)

        self.send_button = QPushButton('Send', self)
        self.send_button.setStyleSheet("background-color: #4CAF50; color: white; border: none; padding: 10px 20px;")
        self.send_button.clicked.connect(self.send_message)

        self.exit_button = QPushButton('Exit', self)
        self.exit_button.setStyleSheet("background-color: #f44336; color: white; border: none; padding: 10px 20px;")
        self.exit_button.clicked.connect(self.close)

        vbox = QVBoxLayout()
        vbox.addWidget(self.chat_area)
        vbox.addWidget(self.entry)

        hbox = QHBoxLayout()
        hbox.addWidget(self.send_button)
        hbox.addWidget(self.exit_button)

        vbox.addLayout(hbox)
        self.setLayout(vbox)
        self.setGeometry(100, 100, 400, 300)

    def send_message(self):
        message = f'<span style="color: #ff6600">{self.nickname}</span>: {self.entry.text()}'
        client.send(message.encode('utf-8'))
        self.entry.clear()

    def receive_messages(self):
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                self.chat_area.append(message)
                self.chat_area.moveCursor(QTextCursor.End)
            except:
                self.chat_area.append('An error occurred!')
                client.close()
                break

app = QApplication(sys.argv)
chat_app = ChatApp()
chat_app.show()
sys.exit(app.exec_())
