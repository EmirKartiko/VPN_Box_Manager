from PyQt6.QtWidgets import (
    QFrame,
    QLabel
)

from PyQt6.QtCore import (
    Qt,
    pyqtSignal
)


class AddProfileCard(QFrame):

    clicked = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setFixedSize(280, 150)

        self.setStyleSheet("""
        QFrame{
            background:#666666;
            border-radius:18px;
        }
        """)

        self.label = QLabel("+", self)

        self.label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.label.setGeometry(
            0,
            0,
            280,
            150
        )

        self.label.setStyleSheet("""
        font-size:48px;
        color:white;
        """)

    def mousePressEvent(self, event):

        self.clicked.emit()