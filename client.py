import sys
import socket
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLineEdit, QLabel, QInputDialog

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
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.start()
        else:
            self.close()

    def initUI(self):
        self.setWindowTitle('Chat Application')

        self.chat_area = QTextEdit(self)
        self.chat_area.setReadOnly(True)

        self.entry = QLineEdit(self)
        self.entry.returnPressed.connect(self.send_message)

        self.send_button = QPushButton('Send', self)
        self.send_button.clicked.connect(self.send_message)

        self.exit_button = QPushButton('Exit', self)
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
        message = f'{self.nickname}: {self.entry.text()}'
        client.send(message.encode('ascii'))
        self.entry.clear()

    def receive_messages(self):
        while True:
            try:
                message = client.recv(1024).decode('ascii')
                self.chat_area.append(message)
            except:
                self.chat_area.append('An error occurred!')
                client.close()
                break

app = QApplication(sys.argv)
chat_app = ChatApp()
chat_app.show()
sys.exit(app.exec_())
