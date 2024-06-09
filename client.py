import sys
import socket
import threading
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QInputDialog, QLabel, QScrollArea
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QTimer

HOST = '127.0.0.1'
PORT = 6789

class Communicator(QObject):
    new_message = pyqtSignal(str, bool)

class ChatApp(QWidget):
    def __init__(self):
        super().__init__()
        self.comm = Communicator()
        self.comm.new_message.connect(self.display_message)
        self.initUI()

        self.nickname, ok = QInputDialog.getText(self, 'Nickname', 'Enter your nickname:')
        if ok and self.nickname:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.client.connect((HOST, PORT))
                join_message = f'{self.nickname} has joined the chat!'
                self.client.send(join_message.encode('utf-8'))
                self.socket_thread = threading.Thread(target=self.receive_messages, daemon=True)
                self.socket_thread.start()
            except Exception as e:
                print(f"Error connecting to server: {e}")
                sys.exit()
        else:
            self.close()

    def initUI(self):
        self.setWindowTitle('Chat Application')

        self.chat_area = QVBoxLayout()
        self.chat_area.addStretch(1)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        scrollContent = QWidget()
        scrollContent.setLayout(self.chat_area)
        self.scroll.setWidget(scrollContent)

        self.entry = QLineEdit(self)
        self.entry.returnPressed.connect(self.send_message)

        self.send_button = QPushButton('Send', self)
        self.send_button.setStyleSheet("background-color: #4CAF50; color: white; border: none; padding: 10px 20px;")
        self.send_button.clicked.connect(self.send_message)

        self.exit_button = QPushButton('Exit', self)
        self.exit_button.setStyleSheet("background-color: #f44336; color: white; border: none; padding: 10px 20px;")
        self.exit_button.clicked.connect(self.close)

        vbox = QVBoxLayout()
        vbox.addWidget(self.scroll)
        vbox.addWidget(self.entry)

        hbox = QHBoxLayout()
        hbox.addWidget(self.send_button)
        hbox.addWidget(self.exit_button)

        vbox.addLayout(hbox)
        self.setLayout(vbox)
        self.setGeometry(100, 100, 400, 300)

    def send_message(self):
        message = f'{self.nickname}: {self.entry.text()}'
        try:
            self.client.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message: {e}")
        self.entry.clear()

    def display_message(self, message, is_own_message):
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("padding: 5px; border-radius: 10px;")

        if is_own_message:
            message_label.setStyleSheet(message_label.styleSheet() + "background-color: lightblue;")
            message_label.setAlignment(Qt.AlignRight)
        else:
            message_label.setStyleSheet(message_label.styleSheet() + "background-color: lightgreen;")
            message_label.setAlignment(Qt.AlignLeft)

        message_layout = QHBoxLayout()
        if is_own_message:
            message_layout.addStretch()
            message_layout.addWidget(message_label)
        else:
            message_layout.addWidget(message_label)
            message_layout.addStretch()

        self.chat_area.insertLayout(self.chat_area.count() - 1, message_layout)
        QTimer.singleShot(100, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())

    def receive_messages(self):
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')
                is_own_message = message.startswith(f'{self.nickname}:')
                self.comm.new_message.emit(message, is_own_message)
            except Exception as e:
                print(f"Error receiving message: {e}")
                self.comm.new_message.emit('<div style="color: red;">An error occurred!</div>', False)
                try:
                    self.client.close()
                    print("Reconnecting...")
                    time.sleep(5)
                    self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.client.connect((HOST, PORT))
                except Exception as e:
                    print(f"Error reconnecting: {e}")
                    break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    chat_app = ChatApp()
    chat_app.show()
    sys.exit(app.exec_())
