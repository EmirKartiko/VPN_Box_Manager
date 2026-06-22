import os
import json
from cryptography.fernet import Fernet


class PasswordStore:

    def __init__(self):

        self.data_dir = "data"

        self.key_file = os.path.join(
            self.data_dir,
            "vpn.key"
        )

        self.password_file = os.path.join(
            self.data_dir,
            "passwords.enc"
        )

        os.makedirs(
            self.data_dir,
            exist_ok=True
        )

        self.fernet = Fernet(
            self.load_or_create_key()
        )

    def load_or_create_key(self):

        if not os.path.exists(
            self.key_file
        ):

            key = Fernet.generate_key()

            with open(
                self.key_file,
                "wb"
            ) as f:

                f.write(key)

            return key

        with open(
            self.key_file,
            "rb"
        ) as f:

            return f.read()

    def load_passwords(self):

        if not os.path.exists(
            self.password_file
        ):
            return {}

        try:

            with open(
                self.password_file,
                "rb"
            ) as f:

                encrypted = f.read()

            decrypted = self.fernet.decrypt(
                encrypted
            )

            return json.loads(
                decrypted.decode()
            )

        except Exception:

            return {}

    def save_passwords(
        self,
        data
    ):

        encrypted = self.fernet.encrypt(
            json.dumps(data).encode()
        )

        with open(
            self.password_file,
            "wb"
        ) as f:

            f.write(encrypted)

    def get_password(
        self,
        profile
    ):

        passwords = self.load_passwords()

        return passwords.get(profile)

    def set_password(
        self,
        profile,
        password
    ):

        passwords = self.load_passwords()

        passwords[profile] = password

        self.save_passwords(
            passwords
        )