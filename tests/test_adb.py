from pprint import PrettyPrinter
from adb.utils import check_adb_path
from test_base import TestBase, run_test_methods
from adb.adb import ADB, Device, Package
import os

adb = ADB()


class TestAdb(TestBase):

    def setUp(self) -> None:
        super().setUp()

    def test_get_devices(self):
        devices = adb.get_devices()

        print(device)
        for device in devices:
            self.assertTrue(isinstance(device, Device))
            device: Device
            self.assertTrue(device.id is not None)

    def test_check_adb_path(self):
        platform_tools_path = check_adb_path()
        print(os.environ.get("PATH"))

    def test_execute_command(self):
        pass

    # def test_get_packages(self):
    #     packages = adb.get_google_packages()
    #     for package in packages:
    #         self.assertTrue(isinstance(package, Package))

    def test_get_google_packages(self):
        pass


if __name__ == "__main__":
    test_methods = [
        # TestAdb.test_get_devices,
        # TestAdb.test_execute_command,
        TestAdb.test_check_adb_path,
        # TestAdb.test_get_google_packages,
    ]
    run_test_methods(test_methods)
