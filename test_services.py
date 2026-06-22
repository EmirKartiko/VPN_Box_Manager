from services.vpn_service import (
    VPNService
)

service = VPNService()

profiles = service.get_profiles()

print(
    profiles
)