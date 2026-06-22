import subprocess
import time
import re

from PyQt6.QtCore import (
    QThread,
    pyqtSignal
)

OPENVPN_EXE = r"C:\Program Files\OpenVPN\bin\openvpn.exe"


class VPNWorker(QThread):

    log_signal = pyqtSignal(str)

    status_signal = pyqtSignal(
        str,  # status
        str   # profile
    )

    ip_signal = pyqtSignal(
        str,  # profile
        str   # ip
    )

    duration_signal = pyqtSignal(
        str,  # profile
        str   # duration
    )

    connected_signal = pyqtSignal(str)

    disconnected_signal = pyqtSignal(str)

    def __init__(
        self,
        profile_name,
        profile_path,
        password
    ):
        super().__init__()

        self.profile_name = profile_name
        self.profile_path = profile_path
        self.password = password

        self.process = None

        self.running = True

        self.connected = False

        self.start_time = None

        self.retry_interval = 5
        self.retry_timeout = 60

    def run(self):

        reconnect_elapsed = 0

        while self.running:

            self.status_signal.emit(
                "🟡 Connecting",
                self.profile_name
            )

            success = self.start_vpn()

            if success:

                reconnect_elapsed = 0

                while (
                    self.running
                    and
                    self.process
                    and
                    self.process.poll() is None
                ):

                    self.update_duration()

                    self.sleep(1)

                if not self.running:
                    break

            reconnect_elapsed += self.retry_interval

            if reconnect_elapsed >= self.retry_timeout:

                self.status_signal.emit(
                    "🔴 Reconnect Timeout",
                    self.profile_name
                )

                self.log_signal.emit(
                    f"[{self.profile_name}] "
                    "Reconnect timeout exceeded"
                )

                break

            self.status_signal.emit(
                f"🟠 Reconnecting ({reconnect_elapsed}/{self.retry_timeout})",
                self.profile_name
            )

            self.sleep(
                self.retry_interval
            )

        self.cleanup()

    def start_vpn(self):

        try:

            self.process = subprocess.Popen(
                [
                    OPENVPN_EXE,
                    "--disable-dco",
                    "--config",
                    self.profile_path
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            if self.password:

                self.process.stdin.write(
                    self.password + "\n"
                )

                self.process.stdin.flush()

            while self.running:

                line = self.process.stdout.readline()

                if not line:
                    return False

                clean = line.strip()

                self.log_signal.emit(
                    f"[{self.profile_name}] {clean}"
                )

                self.parse_ip(clean)

                if (
                    "Initialization Sequence Completed"
                    in clean
                ):

                    self.connected = True

                    self.start_time = time.time()

                    self.status_signal.emit(
                        "🟢 Connected",
                        self.profile_name
                    )

                    self.connected_signal.emit(
                        self.profile_name
                    )

                    return True

                if (
                    "AUTH_FAILED"
                    in clean
                ):

                    self.status_signal.emit(
                        "🔴 Auth Failed",
                        self.profile_name
                    )

                    return False

                if (
                    "fatal error"
                    in clean.lower()
                ):

                    self.status_signal.emit(
                        "🔴 Failed",
                        self.profile_name
                    )

                    return False

            return False

        except Exception as e:

            self.log_signal.emit(
                f"[{self.profile_name}] ERROR: {e}"
            )

            self.status_signal.emit(
                "🔴 Failed",
                self.profile_name
            )

            return False

    def parse_ip(self, line):

        patterns = [
            r'ifconfig\s+(\d+\.\d+\.\d+\.\d+)',
            r'local IP address (\d+\.\d+\.\d+\.\d+)'
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                line
            )

            if match:

                self.ip_signal.emit(
                    self.profile_name,
                    match.group(1)
                )

                return

    def update_duration(self):

        if not self.start_time:
            return

        uptime = int(
            time.time()
            -
            self.start_time
        )

        hours = uptime // 3600
        minutes = (
            uptime % 3600
        ) // 60
        seconds = uptime % 60

        duration = (
            f"{hours:02}:"
            f"{minutes:02}:"
            f"{seconds:02}"
        )

        self.duration_signal.emit(
            self.profile_name,
            duration
        )

    def stop(self):

        self.running = False

        self.connected = False

        self.start_time = None

        self.status_signal.emit(
            "🔴 Disconnected",
            self.profile_name
        )

        self.cleanup()

    def cleanup(self):

        try:

            if (
                self.process
                and
                self.process.poll() is None
            ):

                self.process.terminate()

                try:

                    self.process.wait(
                        timeout=5
                    )

                except Exception:

                    self.process.kill()

        except Exception:
            pass

        self.disconnected_signal.emit(
            self.profile_name
        )
