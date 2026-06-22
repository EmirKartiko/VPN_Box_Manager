import sys
import os
import shutil

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QTextEdit,
    QMessageBox,
    QScrollArea,
    QSystemTrayIcon,
    QMenu,
    QStyle
)

from services.password_store import PasswordStore
from services.vpn_service import VPNService

from widgets.password_dialog import PasswordDialog
from widgets.vpn_card import VPNCard


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "VPN BOX V2"
        )

        self.resize(
            1100,
            800
        )

        self.password_store = PasswordStore()
        self.vpn_service = VPNService()

        self.cards = {}

        self.init_ui()

        self.load_profiles()

        self.setup_tray()

    def init_ui(self):

        layout = QVBoxLayout()

        top_bar = QHBoxLayout()

        self.import_btn = QPushButton(
            "Import OVPN"
        )

        self.disconnect_all_btn = QPushButton(
            "Disconnect All"
        )

        self.clear_log_btn = QPushButton(
            "Clear Log"
        )

        self.export_log_btn = QPushButton(
            "Export Log"
        )

        self.import_btn.clicked.connect(
            self.import_profile
        )

        self.disconnect_all_btn.clicked.connect(
            self.disconnect_all
        )

        self.clear_log_btn.clicked.connect(
            self.clear_log
        )

        self.export_log_btn.clicked.connect(
            self.export_log
        )

        top_bar.addWidget(
            self.import_btn
        )

        top_bar.addWidget(
            self.disconnect_all_btn
        )

        top_bar.addWidget(
            self.clear_log_btn
        )

        top_bar.addWidget(
            self.export_log_btn
        )

        layout.addLayout(
            top_bar
        )

        self.scroll_area = QScrollArea()

        self.scroll_widget = QWidget()

        self.card_layout = QVBoxLayout()

        self.scroll_widget.setLayout(
            self.card_layout
        )

        self.scroll_area.setWidget(
            self.scroll_widget
        )

        self.scroll_area.setWidgetResizable(
            True
        )

        layout.addWidget(
            self.scroll_area
        )

        self.log_box = QTextEdit()

        self.log_box.setReadOnly(
            True
        )

        layout.addWidget(
            self.log_box
        )

        self.setLayout(
            layout
        )

    def setup_tray(self):

        self.tray = QSystemTrayIcon(
            self
        )

        self.tray.setIcon(
            self.style().standardIcon(
                QStyle.StandardPixmap.SP_ComputerIcon
            )
        )

        menu = QMenu()

        show_action = menu.addAction(
            "Show"
        )

        disconnect_action = menu.addAction(
            "Disconnect All"
        )

        exit_action = menu.addAction(
            "Exit"
        )

        show_action.triggered.connect(
            self.showNormal
        )

        disconnect_action.triggered.connect(
            self.disconnect_all
        )

        exit_action.triggered.connect(
            self.exit_app
        )

        self.tray.setContextMenu(
            menu
        )

        self.tray.show()

    def load_profiles(self):

        profiles = self.vpn_service.get_profiles()

        for profile in profiles:

            if profile in self.cards:
                continue

            card = VPNCard(
                profile
            )

            card.connect_clicked.connect(
                self.connect_vpn
            )

            card.disconnect_clicked.connect(
                self.disconnect_vpn
            )

            card.delete_clicked.connect(
                self.delete_profile
            )

            self.cards[
                profile
            ] = card

            self.card_layout.addWidget(
                card
            )

    def import_profile(self):

        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select OVPN",
            "",
            "*.ovpn"
        )

        if not file_name:
            return

        target = os.path.join(
            "profiles",
            os.path.basename(
                file_name
            )
        )

        shutil.copy(
            file_name,
            target
        )

        profile_name = os.path.basename(
            file_name
        )

        dialog = PasswordDialog(
            profile_name
        )

        if dialog.exec():

            if dialog.remember_password():

                self.password_store.set_password(
                    profile_name,
                    dialog.get_password()
                )

        self.load_profiles()

    def connect_vpn(
        self,
        profile_name
    ):

        password = self.password_store.get_password(
            profile_name
        )

        if not password:

            dialog = PasswordDialog(
                profile_name
            )

            if not dialog.exec():
                return

            password = dialog.get_password()

            if dialog.remember_password():

                self.password_store.set_password(
                    profile_name,
                    password
                )

        worker = self.vpn_service.connect_vpn(
            profile_name,
            password
        )

        if not worker:
            return

        worker.log_signal.connect(
            self.add_log
        )

        worker.status_signal.connect(
            self.update_status
        )

        worker.ip_signal.connect(
            self.update_ip
        )

        worker.duration_signal.connect(
            self.update_duration
        )

        worker.start()

    def disconnect_vpn(
        self,
        profile_name
    ):

        self.vpn_service.disconnect_vpn(
            profile_name
        )

    def disconnect_all(self):

        self.vpn_service.disconnect_all()

    def clear_log(self):

        self.log_box.clear()

    def export_log(self):

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Log",
            "vpn-log.txt",
            "Text Files (*.txt)"
        )

        if not filename:
            return

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                self.log_box.toPlainText()
            )

        QMessageBox.information(
            self,
            "Success",
            "Log exported successfully"
        )

    def delete_profile(
        self,
        profile_name
    ):

        reply = QMessageBox.question(
            self,
            "Delete Profile",
            f"Delete profile '{profile_name}' ?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        self.vpn_service.disconnect_vpn(
            profile_name
        )

        profile_path = os.path.join(
            "profiles",
            profile_name
        )

        if os.path.exists(
            profile_path
        ):
            os.remove(
                profile_path
            )

        card = self.cards.pop(
            profile_name,
            None
        )

        if card:

            card.setParent(None)

            card.deleteLater()

        self.add_log(
            f"[SYSTEM] Deleted profile {profile_name}"
        )

    def add_log(
        self,
        text
    ):

        self.log_box.append(
            text
        )

        while (
            self.log_box.document().blockCount()
            > 5000
        ):
            cursor = self.log_box.textCursor()

            cursor.movePosition(
                cursor.MoveOperation.Start
            )

            cursor.select(
                cursor.SelectionType.BlockUnderCursor
            )

            cursor.removeSelectedText()

            cursor.deleteChar()

    def update_status(
        self,
        status,
        profile_name
    ):

        card = self.cards.get(
            profile_name
        )

        if card:

            card.set_status(
                status
            )

    def update_ip(
        self,
        profile_name,
        ip
    ):

        card = self.cards.get(
            profile_name
        )

        if card:

            card.set_ip(
                ip
            )

    def update_duration(
        self,
        profile_name,
        duration
    ):

        card = self.cards.get(
            profile_name
        )

        if card:

            card.set_duration(
                duration
            )

    def closeEvent(
        self,
        event
    ):

        self.hide()

        event.ignore()

    def exit_app(self):

        self.vpn_service.disconnect_all()

        QApplication.quit()


if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )

    window = MainWindow()

    window.show()

    sys.exit(
        app.exec()
    )