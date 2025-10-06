from pprint import PrettyPrinter
import shutil
from adb_wrapper.firmware import extract_firmware
from adb_wrapper.utils import load_env
from test_base import TestBase, run_test_methods
from adb_wrapper.adb import (
    ADB,
    Device,
    Package,
    RootMethod,
    VolumeType,
)
import os


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


class TestDevice(TestBase):

    def setUp(self) -> None:
        super().setUp()

    def test_grant_permissions(self):
        target_device.grant_permissions(package, permissions)

    def test_revoke_permissions(self):
        target_device.revoke_permissions(package, permissions)

    def test_google_debloat(self):
        target_device.google_debloat()

    # device settings methods

    def test_get_ip(self):
        new_device_ip = target_device.get_device_ip()
        new_device_ip = new_device_ip + ":5555"
        self.assertTrue(new_device_ip == device_ip)

    def test_get_shell_property(self):
        prop = target_device.get_shell_property("ro.product.model")
        sdk = target_device.get_sdk()
        name = target_device.get_name()
        model = target_device.get_model()

        print(prop)
        print(sdk)
        print(name)
        print(model)

    def test_is_bootloader_locked(self):
        status = target_device.is_bootloader_locked()
        self.assertTrue(isinstance(status, bool))
        print(status)

    def test_get_system_settings(self):
        system_settings = target_device.get_system_settings()
        self.assertTrue(isinstance(system_settings, dict))
        # print(system_settings)

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
        target_device.get_settings()

        print(target_device.get_settings().keys())

        user_switcher = target_device.global_settings.get("user_switcher_enabled")
        print(user_switcher)

        show_lockscreen_notifications = target_device.secure_settings.get(
            "lock_screen_show_notifications"
        )
        print(show_lockscreen_notifications)

    def test_set_brightness(self):
        output = target_device.set_brightness(255)

    def test_set_volume(self):
        output = target_device.set_volume(0, VolumeType.ALARM)

    def test_enable_lockscreen(self):
        output = target_device.enable_lock_screen()

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
        # destination_path = "/Users/p/Desktop/backup.ab"
        destination_path = None
        output = target_device.backup(shared_storage, apks, system, destination_path)

    def test_restore(self):
        backup_file = "backup.ab"
        output = target_device.restore(backup_file)

    def test_set_home_app(self):
        output = target_device.set_home_app(package)

    def test_push_file(self):
        self.assertTrue(os.path.exists(pc_path))
        target_device.push_file(pc_path, device_path)

    def test_push_files(self):
        target_device.push_files(
            pc_files, destination_directory="/storage/emulated/0/Download/"
        )

    def test_pull_file(self):
        pc_path = "/Users/p/Desktop/conveyor_root.crt"
        target_device.pull_file(device_path, pc_path)
        self.assertTrue(os.path.exists(pc_path))

        # no path provided

    def test_pull_files(self):
        pc_files = []
        target_device.pull_files(device_files, pc_files)

        target_device.pull_files(device_files, destination_directory="/Users/p/Desktop")

    def test_file_exists(self):
        # file that doesn't exist
        file_path = "yooo.txt"
        file_exists = target_device.file_exists(file_path)
        print(file_exists)
        self.assertFalse(file_exists)

        file_exists = target_device.file_exists(apk_device_path)
        self.assertTrue(file_exists)
        print(file_exists)

    def test_get_current_working_directory(self):
        pwd = target_device.get_current_working_directory()

    def test_get_default_download_directory(self):
        dd = target_device.get_default_download_directory()
        print(dd)

    def test_is_valid_path(self):
        path = "/storage/emulated/0/Download"
        output = target_device.is_valid_path(path)
        print(output)
        self.assertTrue(output)

        path = "yo"
        output = target_device.is_valid_path(path)
        print(output)
        self.assertFalse(output)

    # device event methods
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

    def test_unlock_bootloader(self):
        target_device.unlock_bootloader()

    def test_is_oem_unlock_supported(self):
        is_supported = target_device.is_oem_unlock_supported()
        # self.assertTrue(is_supported)
        print(is_supported)

    def test_fastboot_reboot(self):
        target_device.fastboot_reboot()

    def test_fastboot_flash_boot(self):
        target_device.fastboot_flash_boot(image_path)

    def test_extract_firmware(self):
        extract_firmware(target_device)

    # shell su methods
    def test_is_rooted(self):
        output = target_device.is_rooted()
        print(output)


if __name__ == "__main__":
    methods = [
        # TestDevice.test_factory_reset,
        # TestDevice.test_unlock_bootloader,
        # TestDevice.test_is_oem_unlock_supported,
        # TestDevice.test_fastboot_reboot,
        # TestDevice.test_fastboot_flash_boot,
        # TestDevice.test_get_system_packages,
        # TestDevice.test_get_google_packages,
        # TestDevice.test_get_third_party_packages,
        # TestDevice.test_get_packages,
        # TestDevice.test_filter_packages,
        # TestDevice.test_grant_permissions,
        # TestDevice.test_revoke_permissions,
        # TestDevice.test_get_package_path,
        # TestDevice.test_get_package_name,
        # TestDevice.test_install_package,
        # TestDevice.test_uninstall_package,
        # TestDevice.test_google_debloat,
        # TestDevice.test_get_ip,
        # TestDevice.test_get_system_settings,
        # TestDevice.test_get_global_settings,
        # TestDevice.test_get_secure_settings,
        # TestDevice.test_get_settings,
        # TestDevice.test_set_settings,
        # TestDevice.test_is_bootloader_locked,
        # TestDevice.test_get_shell_property,
        # TestDevice.test_enable_lockscreen,
        # TestDevice.test_disable_lockscreen,
        # TestDevice.test_set_brightness,
        # TestDevice.test_set_volume,
        # TestDevice.test_set_password,
        # TestDevice.test_clear_password,
        # TestDevice.test_disable_mobile_data,
        # TestDevice.test_enable_mobile_data,
        # TestDevice.test_disable_wifi,
        # TestDevice.test_enable_wifi,
        # TestDevice.test_backup,
        # TestDevice.test_restore,
        # TestDevice.test_file_exists,
        # TestDevice.test_get_current_working_directory,
        # TestDevice.test_get_default_download_directory,
        # TestDevice.test_is_valid_path,
        # TestDevice.test_push_file,
        # TestDevice.test_push_files,
        # TestDevice.test_pull_files,
        # TestDevice.test_pull_file,
        # TestDevice.test_execute_touch_event,
        # TestDevice.test_expand_notifications,
        # TestDevice.test_is_rooted,
        # TestDevice.test_root,
        TestDevice.test_extract_firmware,
    ]

    run_test_methods(methods)
