from pprint import PrettyPrinter
from adb.utils import check_sdk_path
from test_base import TestBase, run_test_methods
from adb.adb import ADB, Device, Package, get_google_packages
import os

adb = ADB()
devices = adb.get_devices()
target_device = devices[0] if len(devices) > 0 else None


class TestAdb(TestBase):

    def setUp(self) -> None:
        super().setUp()
        # self.assertTrue(target_device is not None)

    def test_get_devices(self):
        devices = adb.get_devices()

        print("DEVICES", devices)
        for device in devices:
            print(device)
            self.assertTrue(isinstance(device, Device))
            device: Device
            self.assertTrue(device.id is not None)
            print(device.id)

    def test_check_adb_path(self):
        platform_tools_path = check_sdk_path()

        self.assertTrue(platform_tools_path is not None)
        self.assertTrue(os.path.exists(platform_tools_path))
        # print(os.environ.get("PATH"))

    def test_execute_command(self):
        output = adb.execute("version")

        print(output)

    def test_get_packages(self):
        devices = adb.get_devices()
        for device in devices:
            device.get_packages()

    def test_get_packages(self):
        packages = target_device.get_packages()

    def test_get_third_party_packages(self):
        packages = target_device.get_third_party_packages()
        print(packages)

    def test_get_system_packages(self):
        packages = target_device.get_system_packages()
        print(packages)

    def test_get_google_packages(self):
        packages = get_google_packages()
        print(packages)

        self.assertTrue(all([isinstance(package, Package) for package in packages]))
        self.assertTrue(len(packages) == 126)

    def test_filter_packages(self):
        packages = get_google_packages()

        filtered = Package.filter_packages(
            packages, name="Android Auto for phone screens"
        )

        print(len(filtered), len(packages))

    def test_get_system_settings(self):
        system_settings = target_device.get_system_settings()
        self.assertTrue(isinstance(system_settings, dict))

    def test_get_global_settings(self):
        global_settings = target_device.get_global_settings()
        self.assertTrue(isinstance(global_settings, dict))

    def test_get_secure_settings(self):
        secure_settings = target_device.get_secure_settings()
        self.assertTrue(isinstance(secure_settings, dict))

    def test_get_settings(self):
        settings = target_device.get_settings()
        global_settings = settings.get("global")
        print(global_settings)

    def test_grant_permissions(self):
        pass

    def test_install_package(self):
        output = target_device.install_package("com.google.android.apps.youtube.music")
        print(output)

    def test_uninstall_package(self):
        output = target_device.uninstall_package(
            "com.google.android.apps.youtube.music"
        )
        print(output)


if __name__ == "__main__":
    test_methods = [
        # TestAdb.test_check_adb_path,
        # TestAdb.test_get_devices,
        # TestAdb.test_execute_command,
        # TestAdb.test_get_packages,
        # TestAdb.test_get_system_packages,
        # TestAdb.test_get_google_packages,
        # TestAdb.test_get_third_party_packages,
        # TestAdb.test_filter_packages,
        # TestAdb.test_get_system_settings,
        # TestAdb.test_get_global_settings,
        # TestAdb.test_get_secure_settings,
        # TestAdb.test_get_settings,
        # TestAdb.test_grant_permissions,
        TestAdb.test_install_package,
        # TestAdb.test_uninstall_package,
    ]
    run_test_methods(test_methods)
