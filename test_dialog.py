import sys

from PyQt6.QtWidgets import QApplication

from widgets.password_dialog import (
    PasswordDialog
)

app = QApplication(sys.argv)

dialog = PasswordDialog(
    "vpn-dev.ovpn"
)

if dialog.exec():

    print(
        dialog.get_password()
    )

    print(
        dialog.remember_password()
    )

sys.exit()