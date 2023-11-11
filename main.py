import sys
import socket
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextBrowser, QLineEdit


class ServerThread(QThread):
    new_message = pyqtSignal(str)

    def __init__(self, port, parent=None):
        super().__init__(parent)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('localhost', port))
        self.server.listen(1)

    def run(self):
        self.client, addr = self.server.accept()
        while True:
            data = self.client.recv(1024).decode()
            self.new_message.emit(data)


class ClientThread(QThread):
    new_message = pyqtSignal(str)

    def __init__(self, port, parent=None):
        super().__init__(parent)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(('localhost', port))

    def run(self):
        while True:
            message = input()
            self.client.send(message.encode())
            self.new_message.emit(message)


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Local Network Chat')
        self.layout = QVBoxLayout()
        self.text_browser = QTextBrowser()
        self.layout.addWidget(self.text_browser)
        self.line_edit = QLineEdit()
        self.line_edit.returnPressed.connect(self.send_message)
        self.layout.addWidget(self.line_edit)
        self.setLayout(self.layout)

        server_port = int(input())
        self.server_thread = ServerThread(server_port)
        self.server_thread.new_message.connect(self.receive_message)
        self.server_thread.start()

        client_port=int(input())
        self.client_thread = ClientThread(client_port)
        self.client_thread.new_message.connect(self.receive_message)
        self.client_thread.start()

    def receive_message(self, message):
        self.text_browser.append(message)

    def send_message(self):
        message = self.line_edit.text()
        self.text_browser.append(message)
        self.line_edit.clear()
        self.client_thread.client.send(message.encode())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    chat_window = ChatWindow()
    chat_window.show()
    sys.exit(app.exec_())
