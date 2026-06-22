import os

from workers.vpn_worker import VPNWorker


class VPNService:

    def __init__(self):

        self.profile_dir = "profiles"

        os.makedirs(
            self.profile_dir,
            exist_ok=True
        )

        self.workers = {}

    def get_profiles(self):

        profiles = []

        for file in os.listdir(
            self.profile_dir
        ):

            if file.endswith(
                ".ovpn"
            ):

                profiles.append(
                    file
                )

        return sorted(
            profiles
        )

    def get_profile_path(
        self,
        profile_name
    ):

        return os.path.join(
            self.profile_dir,
            profile_name
        )

    def is_connected(
        self,
        profile_name
    ):

        return profile_name in self.workers

    def connect_vpn(
        self,
        profile_name,
        password
    ):

        if self.is_connected(
            profile_name
        ):
            return None

        profile_path = self.get_profile_path(
            profile_name
        )

        worker = VPNWorker(
            profile_name,
            profile_path,
            password
        )

        self.workers[
            profile_name
        ] = worker

        return worker

    def disconnect_vpn(
        self,
        profile_name
    ):

        worker = self.workers.get(
            profile_name
        )

        if not worker:
            return

        worker.stop()

        worker.wait(
            5000
        )

        del self.workers[
            profile_name
        ]

    def disconnect_all(self):

        profiles = list(
            self.workers.keys()
        )

        for profile in profiles:

            self.disconnect_vpn(
                profile
            )

    def remove_worker(
        self,
        profile_name
    ):

        if (
            profile_name
            in
            self.workers
        ):

            del self.workers[
                profile_name
            ]