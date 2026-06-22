from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QCheckBox
)


class PasswordDialog(QDialog):

    def __init__(
        self,
        profile_name,
        saved_password=""
    ):
        super().__init__()

        self.setWindowTitle(
            "VPN Password"
        )

        self.setFixedSize(
            450,
            180
        )

        layout = QVBoxLayout()

        title = QLabel(
            f"Private Key Password\n\n{profile_name}"
        )

        layout.addWidget(title)

        password_layout = QHBoxLayout()

        self.password_input = QLineEdit()

        self.password_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        self.password_input.setText(
            saved_password
        )

        self.show_btn = QPushButton(
            "👁"
        )

        self.show_btn.setFixedWidth(
            50
        )

        self.show_btn.pressed.connect(
            self.show_password
        )

        self.show_btn.released.connect(
            self.hide_password
        )

        password_layout.addWidget(
            self.password_input
        )

        password_layout.addWidget(
            self.show_btn
        )

        layout.addLayout(
            password_layout
        )

        self.remember_checkbox = QCheckBox(
            "Remember Password"
        )

        self.remember_checkbox.setChecked(
            True
        )

        layout.addWidget(
            self.remember_checkbox
        )

        button_layout = QHBoxLayout()

        self.cancel_btn = QPushButton(
            "Cancel"
        )

        self.connect_btn = QPushButton(
            "Connect"
        )

        self.cancel_btn.clicked.connect(
            self.reject
        )

        self.connect_btn.clicked.connect(
            self.accept
        )

        button_layout.addStretch()

        button_layout.addWidget(
            self.cancel_btn
        )

        button_layout.addWidget(
            self.connect_btn
        )

        layout.addLayout(
            button_layout
        )

        self.setLayout(layout)

    def show_password(self):

        self.password_input.setEchoMode(
            QLineEdit.EchoMode.Normal
        )

    def hide_password(self):

        self.password_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )

    def get_password(self):

        return self.password_input.text()

    def remember_password(self):

        return self.remember_checkbox.isChecked()