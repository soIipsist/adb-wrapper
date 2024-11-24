from pprint import PrettyPrinter
from adb.utils import check_sdk_path, load_env
from test_base import TestBase, run_test_methods
from adb.adb import ADB, Device, Package, RootMethod
import os

adb = ADB()
devices = adb.get_devices()
target_device = devices[0] if len(devices) > 0 else None


class TestAdb(TestBase):

    def setUp(self) -> None:
        super().setUp()
        load_env(file_path=".env")  # change .env path here if you want to test
        self.pc_path = os.getenv("PC_PATH")
        self.device_path = os.getenv("DEVICE_PATH")
        self.device_ip = os.getenv("DEVICE_IP")
        self.package = os.getenv("PACKAGE")
        self.backup_path = os.getenv("BACKUP_FILE_PATH")
        self.image_path = os.getenv("IMAGE_PATH")

    def test_get_devices(self):
        devices = adb.get_devices()

        for device in devices:
            self.assertTrue(isinstance(device, Device))
            device: Device
            self.assertTrue(device.id is not None)
            print(device.id)

    def test_check_adb_path(self):
        platform_tools_path = check_sdk_path()

        self.assertTrue(platform_tools_path is not None)
        self.assertTrue(os.path.exists(platform_tools_path))
        # print(os.environ.get("PATH"))

    def test_connect(self):
        device_ip = os.getenv("DEVICE_IP")
        output = adb.connect(device_ip)
        print(output)

    def test_disconnect(self):
        device_ip = os.getenv("DEVICE_IP")
        adb.disconnect(device_ip)

    def test_enable_usb_mode(self):
        output = adb.enable_usb_mode()

    def test_enable_tcpip_mode(self):
        port = "5555"
        output = adb.enable_tcpip_mode(port)

    def test_execute_command(self):
        output = adb.execute("version")

    def test_get_packages(self):
        packages = target_device.get_packages()

    def test_get_third_party_packages(self):
        packages = target_device.get_third_party_packages()
        print(packages)

        self.assertTrue(
            all(isinstance(package, Package) for package in packages),
        )

    def test_get_system_packages(self):
        packages = target_device.get_system_packages()
        print(packages)

        self.assertTrue(
            all(isinstance(package, Package) for package in packages),
        )

    def test_get_google_packages(self):
        packages = adb.get_google_packages()
        print(packages)

        self.assertTrue(all([isinstance(package, Package) for package in packages]))
        self.assertTrue(len(packages) == 126)

    def test_filter_packages(self):
        packages = adb.get_google_packages()

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

    def test_install_packages(self):
        output = target_device.install_package("com.google.android.apps.youtube.music")

    def test_uninstall_packages(self):
        output = target_device.uninstall_package(
            "com.google.android.apps.youtube.music"
        )

    def test_grant_permissions(self):
        permissions = []
        target_device.grant_permissions(self.package, permissions)

    def test_revoke_permissions(self):
        permissions = []
        target_device.revoke_permissions(self.package, permissions)

    def test_google_debloat(self):
        output = target_device.google_debloat()

    def test_disable_lockscreen(self):
        output = target_device.disable_lock_screen()

    def test_disable_mobile_data(self):
        target_device.disable_mobile_data()

    def test_disable_wifi(self):
        target_device.disable_wifi()

    def test_enable_mobile_data(self):
        target_device.enable_mobile_data()

    def test_enable_wifi(self):
        target_device.enable_wifi()

    def test_set_settings(self):
        settings = [
            "global.user_switcher_enabled=0",
            "secure.lock_screen_show_notifications=0",
        ]

        # format can be:
        # a) namespace.key=value
        # b) namespace.key value
        # c) namespace.key.other_value value
        target_device.set_settings(settings)

    def test_set_password(self):
        password = "1234"
        target_device.set_password(password)

    def test_clear_password(self):
        password = "1234"
        target_device.clear_password(password)

    def test_backup(self):
        shared_storage = False
        apks = False
        system = False
        destination_path = None
        output = target_device.backup(shared_storage, apks, system, destination_path)

    def test_restore(self):
        backup_file = "backup.ab"
        output = target_device.restore(backup_file)

    def test_set_home_app(self):
        output = target_device.set_home_app(self.package)

    def test_push_file(self):
        output = target_device.push_file(self.pc_path, self.device_path)

    def test_pull_file(self):
        target_device.pull_file(self.device_path, self.pc_path)

    def test_get_shell_property(self):
        prop = target_device.get_shell_property("ro.product.model")
        sdk = target_device.get_sdk()
        name = target_device.get_name()
        model = target_device.get_model()

    def test_execute_touch_event(self):
        x = 100
        y = 1000

        output = target_device.execute_touch_event(x, y)

    def test_expand_notifications(self):
        output = target_device.expand_notifications()

    # root methods
    def test_factory_reset(self):
        output = target_device.factory_reset()

    def test_root(self):
        target_device.root(RootMethod.MAGISK)
        # target_device.root(RootMethod.APATCH)
        # target_device.root(RootMethod.KERNELSU)

    def test_get_bootloader_status(self):
        status = target_device.get_bootloader_status()
        print(status)

    def test_unlock_bootloader(self):
        target_device.unlock_bootloader()

    def test_fastboot_reboot(self):
        target_device.fastboot_reboot()

    def test_fastboot_flash_boot(self):
        target_device.fastboot_flash_boot(self.image_path)


if __name__ == "__main__":
    adb_methods = [
        # TestAdb.test_check_adb_path,
        # TestAdb.test_get_devices,
        TestAdb.test_connect,
        # TestAdb.test_disconnect,
        # TestAdb.test_enable_tcpip_mode,
        # TestAdb.test_enable_usb_mode
    ]
    root_methods = [
        TestAdb.test_factory_reset,
        TestAdb.test_root,
        TestAdb.test_get_bootloader_status,
        TestAdb.test_unlock_bootloader,
        TestAdb.test_fastboot_reboot,
        TestAdb.test_fastboot_flash_boot,
    ]
    device_methods = [
        # TestAdb.test_execute_command,
        # TestAdb.test_get_system_packages,
        # TestAdb.test_get_google_packages,
        # TestAdb.test_get_third_party_packages,
        # TestAdb.test_get_packages,
        # TestAdb.test_filter_packages,
        # TestAdb.test_get_system_settings,
        # TestAdb.test_get_global_settings,
        # TestAdb.test_get_secure_settings,
        # TestAdb.test_get_settings,
        # TestAdb.test_set_settings,
        # TestAdb.test_grant_permissions,
        # TestAdb.test_revoke_permissions,
        # TestAdb.test_install_packages,
        # TestAdb.test_uninstall_packages,
        # TestAdb.test_google_debloat,
        # TestAdb.test_disable_mobile_data,
        # TestAdb.test_enable_mobile_data,
        # TestAdb.test_disable_wifi,
        # TestAdb.test_enable_wifi,
        # TestAdb.test_backup,
        # TestAdb.test_restore,
        # TestAdb.test_push_file,
        # TestAdb.test_pull_file,
        # TestAdb.test_get_shell_property,
        # TestAdb.test_execute_touch_event,
        # TestAdb.test_expand_notifications,
    ]
    run_test_methods(device_methods)
