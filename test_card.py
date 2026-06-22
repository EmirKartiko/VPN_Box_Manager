import sys

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout
)

from widgets.vpn_card import VPNCard


class Window(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        card = VPNCard(
            "vpn-dev.ovpn"
        )

        card.set_status(
            "🟢 Connected"
        )

        card.set_ip(
            "10.8.0.240"
        )

        card.set_duration(
            "00:13:42"
        )

        card.connect_clicked.connect(
            lambda x: print(
                "CONNECT",
                x
            )
        )

        card.disconnect_clicked.connect(
            lambda x: print(
                "DISCONNECT",
                x
            )
        )

        layout.addWidget(card)

        self.setLayout(layout)


app = QApplication(sys.argv)

window = Window()

window.show()

sys.exit(app.exec())