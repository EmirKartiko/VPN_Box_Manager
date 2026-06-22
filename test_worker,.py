from workers.vpn_worker import VPNWorker

worker = VPNWorker(
    "vpn-dev.ovpn",
    r"D:\VPN\vpn-dev.ovpn",
    "PASSWORDVPN"
)

worker.log_signal.connect(
    print
)

worker.status_signal.connect(
    lambda status, profile:
    print(
        profile,
        status
    )
)

worker.ip_signal.connect(
    lambda ip:
    print(
        "VPN IP",
        ip
    )
)

worker.duration_signal.connect(
    lambda duration:
    print(
        "UPTIME",
        duration
    )
)

worker.start()