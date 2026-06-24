from PyQt6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton
)

from PyQt6.QtCore import (
    Qt,
    pyqtSignal
)


class VPNCard(QFrame):

    connect_clicked = pyqtSignal(str)
    disconnect_clicked = pyqtSignal(str)
    delete_clicked = pyqtSignal(str)

    def __init__(self, profile_name):
        super().__init__()

        self.profile_name = profile_name
        self.connected = False

        self.setFixedSize(280, 150)

        self.setStyleSheet("""
        QFrame{
            background:#555555;
            border-radius:18px;
        }
        """)

        self.title = QLabel(profile_name, self)
        self.title.move(20, 20)

        self.title.setStyleSheet("""
        color:white;
        font-size:15px;
        font-weight:bold;
        background:transparent;
        """)

        self.ip_label = QLabel("-", self)
        self.ip_label.move(20, 60)

        self.ip_label.setStyleSheet("""
        color:#dddddd;
        background:transparent;
        """)

        self.duration_label = QLabel("-", self)
        self.duration_label.move(20, 85)

        self.duration_label.setStyleSheet("""
        color:#dddddd;
        background:transparent;
        """)

        self.delete_btn = QPushButton(self)
        self.delete_btn.setGeometry(240, 10, 25, 25)

        self.delete_btn.setStyleSheet("""
        QPushButton{
            background:red;
            border-radius:12px;
        }
        """)

        self.delete_btn.clicked.connect(
            lambda:
            self.delete_clicked.emit(
                self.profile_name
            )
        )

        self.power_btn = QPushButton(self)
        self.power_btn.setGeometry(240, 115, 25, 25)

        self.power_btn.setStyleSheet("""
        QPushButton{
            background:#222;
            border-radius:12px;
        }
        """)

        self.power_btn.clicked.connect(
            self.toggle_connection
        )

    def toggle_connection(self):

        if self.connected:

            self.disconnect_clicked.emit(
                self.profile_name
            )

        else:

            self.connect_clicked.emit(
                self.profile_name
            )

    def set_status(self, status):

        if "Connected" in status:

            self.connected = True

            self.power_btn.setStyleSheet("""
            QPushButton{
                background:limegreen;
                border-radius:12px;
            }
            """)

        elif "Connecting" in status:

            self.power_btn.setStyleSheet("""
            QPushButton{
                background:yellow;
                border-radius:12px;
            }
            """)

        else:

            self.connected = False

            self.power_btn.setStyleSheet("""
            QPushButton{
                background:#222;
                border-radius:12px;
            }
            """)

    def set_ip(self, ip):

        self.ip_label.setText(
            f"IP : {ip}"
        )

    def set_duration(self, duration):

        self.duration_label.setText(
            duration
        )