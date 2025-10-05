from pprint import PrettyPrinter
import shutil
from adb_wrapper.utils import load_env
from test_base import TestBase, run_test_methods
from adb_wrapper.adb import (
    ADB,
    Device,
)


adb = ADB()
devices = adb.get_devices()
target_device = devices[0] if len(devices) > 0 else None
environment_variables = load_env(
    file_path=".env",
)  # change .env path here if you want to test


pc_path = environment_variables.get("PC_PATH")
apk_pc_path = environment_variables.get("APK_PC_PATH")
apk_device_path = environment_variables.get("APK_DEVICE_PATH")
device_path = environment_variables.get("DEVICE_PATH")
device_ip = environment_variables.get("DEVICE_IP")
packages = environment_variables.get("PACKAGES")
package_paths = environment_variables.get("PACKAGE_PATHS")
package = packages[0] if packages else None
package_path = package_paths[0] if package_paths else None
backup_path = environment_variables.get("BACKUP_FILE_PATH")
image_path = environment_variables.get("IMAGE_PATH")
permissions = environment_variables.get("PERMISSIONS")
device_files = environment_variables.get("DEVICE_FILES")
pc_files = environment_variables.get("PC_FILES")


class TestAdb(TestBase):

    def setUp(self) -> None:
        super().setUp()

    # adb methods
    def test_get_devices(self):
        devices = adb.get_devices()

        for device in devices:
            self.assertTrue(isinstance(device, Device))
            device: Device
            self.assertTrue(device.id is not None)
            print(device.id)

    def test_get_device(self):
        device = adb.get_device()

        if device:
            self.assertTrue(isinstance(device, Device))

    def test_connect(self):
        print(device_ip)
        output = adb.connect(device_ip)

    def test_disconnect(self):
        print(device_ip)
        adb.disconnect(device_ip)

    def test_enable_usb_mode(self):
        output = adb.enable_usb_mode()

    def test_enable_tcpip_mode(self):
        port = "5555"
        output = adb.enable_tcpip_mode(port)

    def test_execute_command(self):
        output = adb.execute("version")

        # raises error if other base cmd
        adb.execute("--version", base_cmd="fastboot")


if __name__ == "__main__":
    methods = [
        # TestAdb.test_get_devices,
        # TestAdb.test_get_device,
        # TestAdb.test_connect,
        # TestAdb.test_disconnect,
        TestAdb.test_execute_command,
        # TestAdb.test_enable_tcpip_mode,
        # TestAdb.test_enable_usb_mode,
    ]

    run_test_methods(methods)
