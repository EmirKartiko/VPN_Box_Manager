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
    QMessageBox,
    QScrollArea,
    QSystemTrayIcon,
    QMenu,
    QStyle,
    QListWidget,
    QStackedWidget,
    QGridLayout,
    QPlainTextEdit,
    QLabel
)

from services.password_store import PasswordStore
from services.vpn_service import VPNService

from widgets.password_dialog import PasswordDialog
from widgets.vpn_card import VPNCard
from widgets.add_profile_card import AddProfileCard

from PyQt6.QtGui import QMovie
from PyQt6.QtCore import (
    Qt,
    QSize
)


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("VPN BOX MANAGER")
        self.resize(1200, 800)

        self.password_store = PasswordStore()
        self.vpn_service = VPNService()

        self.cards = {}

        self.init_ui()
        self.load_profiles()
        self.setup_tray()

    def init_ui(self):

        main_layout = QHBoxLayout()

        # Sidebar
        self.sidebar_container = QWidget()
        sidebar_layout = QVBoxLayout()

        self.toggle_sidebar_btn = QPushButton("☰")
        self.toggle_sidebar_btn.clicked.connect(
            self.toggle_sidebar
        )

        self.sidebar = QListWidget()
        self.sidebar.addItem("Profiles")
        self.sidebar.addItem("Logs")

        sidebar_layout.addWidget(
            self.sidebar
        )

        sidebar_layout.addStretch()

        self.gif_label = QLabel()

        self.gif_label.setFixedSize(
            100,
            100
        )

        self.gif_label.setStyleSheet("""
        background:transparent;
        """)

        sidebar_layout.addWidget(
            self.toggle_sidebar_btn
        )

        self.movie = QMovie(
            "assets/box-cute.gif"
        )

        self.movie.setScaledSize(
            QSize(
            70,
            65
            )
        )

        self.gif_label.setMovie(
            self.movie
        )

        self.movie.start()

        sidebar_layout.addWidget(
            self.gif_label,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        self.sidebar_container.setLayout(
            sidebar_layout
        )
        self.sidebar.setFixedWidth(130)

        # Pages
        self.pages = QStackedWidget()

        # Profile page
        self.profile_page = QWidget()
        profile_layout = QVBoxLayout()

        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()

        self.profile_grid = QGridLayout()
        self.profile_grid.setSpacing(20)

        self.scroll_widget.setLayout(
            self.profile_grid
        )

        self.scroll_area.setWidget(
            self.scroll_widget
        )
        self.scroll_area.setWidgetResizable(True)

        profile_layout.addWidget(
            self.scroll_area
        )

        self.profile_page.setLayout(
            profile_layout
        )

        # Logs page
        self.logs_page = QWidget()
        logs_layout = QVBoxLayout()

        logs_toolbar = QHBoxLayout()

        self.clear_log_btn = QPushButton("Clear")
        self.export_log_btn = QPushButton("Export")

        self.clear_log_btn.clicked.connect(
            self.clear_log
        )
        self.export_log_btn.clicked.connect(
            self.export_log
        )

        logs_toolbar.addWidget(
            self.clear_log_btn
        )
        logs_toolbar.addWidget(
            self.export_log_btn
        )
        logs_toolbar.addStretch()

        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)

        logs_layout.addLayout(
            logs_toolbar
        )
        logs_layout.addWidget(
            self.log_box
        )

        self.logs_page.setLayout(
            logs_layout
        )

        self.pages.addWidget(
            self.profile_page
        )
        self.pages.addWidget(
            self.logs_page
        )

        self.sidebar.currentRowChanged.connect(
            self.pages.setCurrentIndex
        )
        self.sidebar.setCurrentRow(0)

        main_layout.addWidget(
            self.sidebar_container
        )
        main_layout.addWidget(
            self.pages
        )

        self.status_bar = QLabel("Ready")
        self.status_bar.setFixedHeight(30)

        wrapper = QVBoxLayout()
        wrapper.addLayout(main_layout)
        wrapper.addWidget(self.status_bar)

        self.setLayout(wrapper)

    def toggle_sidebar(self):

        if self.sidebar.isVisible():
            self.sidebar.hide()
            self.gif_label.hide()
            self.sidebar_container.setFixedWidth(60)
        else:
            self.sidebar.show()
            self.gif_label.show()
            self.sidebar_container.setFixedWidth(150)

    def setup_tray(self):

        self.tray = QSystemTrayIcon(self)

        self.tray.setIcon(
            self.style().standardIcon(
                QStyle.StandardPixmap.SP_ComputerIcon
            )
        )

        menu = QMenu()

        menu.addAction("Show", self.showNormal)
        menu.addAction("Disconnect All", self.disconnect_all)
        menu.addAction("Exit", self.exit_app)

        self.tray.setContextMenu(menu)
        self.tray.show()

    def clear_grid(self):

        while self.profile_grid.count():
            item = self.profile_grid.takeAt(0)
            widget = item.widget()

            if widget:
                widget.setParent(None)

    def load_profiles(self):

        self.clear_grid()
        self.cards = {}

        profiles = self.vpn_service.get_profiles()

        for index, profile in enumerate(profiles):

            card = VPNCard(profile)

            card.connect_clicked.connect(
                self.connect_vpn
            )

            card.disconnect_clicked.connect(
                self.disconnect_vpn
            )

            card.delete_clicked.connect(
                self.delete_profile
            )

            self.cards[profile] = card

            row = index // 2
            col = index % 2

            self.profile_grid.addWidget(
                card,
                row,
                col
            )

        self.add_add_card()

    def add_add_card(self):

        add_card = AddProfileCard()

        add_card.clicked.connect(
            self.import_profile
        )

        count = len(self.cards)

        self.profile_grid.addWidget(
            add_card,
            count // 2,
            count % 2
        )

    def import_profile(self):

        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select OpenVPN Profile",
            "",
            "*.ovpn"
        )

        if not file_name:
            return

        os.makedirs(
            "profiles",
            exist_ok=True
        )

        target = os.path.join(
            "profiles",
            os.path.basename(file_name)
        )

        shutil.copy(file_name, target)

        profile_name = os.path.basename(file_name)

        dialog = PasswordDialog(profile_name)

        if dialog.exec() and dialog.remember_password():
            self.password_store.set_password(
                profile_name,
                dialog.get_password()
            )

        self.load_profiles()

    def connect_vpn(self, profile_name):

        password = self.password_store.get_password(
            profile_name
        )

        if not password:

            dialog = PasswordDialog(profile_name)

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

        worker.log_signal.connect(self.add_log)
        worker.status_signal.connect(self.update_status)
        worker.ip_signal.connect(self.update_ip)
        worker.duration_signal.connect(self.update_duration)

        worker.start()

    def disconnect_vpn(self, profile_name):

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

        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.log_box.toPlainText())

        QMessageBox.information(
            self,
            "Success",
            "Log exported successfully"
        )

    def delete_profile(self, profile_name):

        reply = QMessageBox.question(
            self,
            "Delete Profile",
            f"Delete {profile_name}?",
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

        if os.path.exists(profile_path):
            os.remove(profile_path)

        self.load_profiles()

    def add_log(self, text):

        self.log_box.appendPlainText(text)

    def update_status(self, status, profile_name):

        card = self.cards.get(profile_name)

        if card:
            card.set_status(status)

        self.status_bar.setText(
            f"{profile_name} : {status}"
        )

    def update_ip(self, profile_name, ip):

        card = self.cards.get(profile_name)

        if card:
            card.set_ip(ip)

    def update_duration(
        self,
        profile_name,
        duration
    ):

        card = self.cards.get(profile_name)

        if card:
            card.set_duration(duration)

    def closeEvent(self, event):

        self.hide()
        event.ignore()

    def exit_app(self):

        self.vpn_service.disconnect_all()
        QApplication.quit()


if __name__ == "__main__":

    app = QApplication(sys.argv)

    app.setStyleSheet("""
    QWidget{
        background:#08123a;
        color:white;
        font-family:Segoe UI;
    }

    QListWidget{
        background:#6b6b6b;
        border:none;
    }

    QPlainTextEdit{
        background:black;
        color:#00ff66;
    }
    """)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
