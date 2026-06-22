from PyQt6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout
)

from PyQt6.QtCore import (
    pyqtSignal
)


class VPNCard(QFrame):

    connect_clicked = pyqtSignal(str)
    disconnect_clicked = pyqtSignal(str)
    delete_clicked = pyqtSignal(str)

    def __init__(self, profile_name):
        super().__init__()

        self.profile_name = profile_name

        self.setFrameShape(
            QFrame.Shape.Box
        )

        self.setLineWidth(1)

        layout = QVBoxLayout()

        self.title_label = QLabel(
            profile_name
        )

        self.status_label = QLabel(
            "Status : 🔴 Disconnected"
        )

        self.ip_label = QLabel(
            "VPN IP : -"
        )

        self.duration_label = QLabel(
            "Connected : -"
        )

        layout.addWidget(
            self.title_label
        )

        layout.addWidget(
            self.status_label
        )

        layout.addWidget(
            self.ip_label
        )

        layout.addWidget(
            self.duration_label
        )

        button_layout = QHBoxLayout()

        self.connect_btn = QPushButton(
            "Connect"
        )

        self.disconnect_btn = QPushButton(
            "Disconnect"
        )

        self.delete_btn = QPushButton(
            "Delete"
        )

        self.connect_btn.clicked.connect(
            self.emit_connect
        )

        self.disconnect_btn.clicked.connect(
            self.emit_disconnect
        )

        self.delete_btn.clicked.connect(
            self.emit_delete
        )

        button_layout.addWidget(
            self.connect_btn
        )

        button_layout.addWidget(
            self.disconnect_btn
        )

        button_layout.addWidget(
            self.delete_btn
        )

        layout.addLayout(
            button_layout
        )

        self.setLayout(layout)

    def emit_connect(self):

        self.connect_clicked.emit(
            self.profile_name
        )

    def emit_disconnect(self):

        self.disconnect_clicked.emit(
            self.profile_name
        )

    def emit_delete(self):

        self.delete_clicked.emit(
            self.profile_name
        )

    def set_status(
        self,
        status
    ):

        self.status_label.setText(
            f"Status : {status}"
        )

    def set_ip(
        self,
        ip
    ):

        self.ip_label.setText(
            f"VPN IP : {ip}"
        )

    def set_duration(
        self,
        duration
    ):

        self.duration_label.setText(
            f"Connected : {duration}"
        )