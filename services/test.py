from password_store import PasswordStore

store = PasswordStore()

store.set_password(
    "vpn-dev.ovpn",
    "Password123!"
)

print(
    store.get_password(
        "vpn-dev.ovpn"
    )
)