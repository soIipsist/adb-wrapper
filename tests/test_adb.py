from pprint import PrettyPrinter
import shutil
from adb.utils import (
    load_env,
    download_file_from_link,
    download_sdk_platform_tools,
    make_executable,
    set_path_environment_variable,
    find_variable_in_path,
)
from test_base import TestBase, run_test_methods
from adb.adb import (
    ADB,
    Device,
    Package,
    RootMethod,
    VolumeType,
    magisk_url,
    apatch_url,
    kernelsu_url,
    sdk_checked,
)
import os

adb = ADB()
devices = adb.get_devices()
target_device = devices[0] if len(devices) > 0 else None
environment_variables = load_env(
    file_path=".env"
)  # change .env path here if you want to test

pc_path = environment_variables.get("PC_PATH")
apk_pc_path = environment_variables.get("APK_PC_PATH")
apk_device_path = environment_variables.get("APK_DEVICE_PATH")
device_path = environment_variables.get("DEVICE_PATH")
device_ip = environment_variables.get("DEVICE_IP")
package = environment_variables.get("PACKAGE")
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

    def test_check_sdk_path(self):

        # remove sdk platform tools
        sdk_path = find_variable_in_path("platform-tools")
        shutil.rmtree(sdk_path)

        # check sdk with environment vars set locally or globally
        # adb.global_env = True
        sdk_path = adb.check_sdk_path()
        self.assertTrue(os.path.exists(sdk_path))
        self.assertTrue(adb.sdk_path == sdk_path)

        adb.get_device()

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

    # device package methods
    def test_get_packages(self):
        packages = target_device.get_packages()
        print(packages, len(packages))

    def test_get_third_party_packages(self):
        packages = target_device.get_third_party_packages()
        for package in packages:
            print(package.package_name, package.package_path)
            self.assertTrue(isinstance(package, Package))

    def test_get_system_packages(self):
        packages = target_device.get_system_packages()
        for package in packages:
            print(package.package_name, package.package_path, package.name)

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

    def test_install_package(self):
        pass

    def test_reinstall_package(self):
        pass

    def test_install_packages(self):
        output = target_device.install_package("com.google.android.apps.youtube.music")

    def test_uninstall_package(self):
        target_device.uninstall_package()

    def test_uninstall_packages(self):
        output = target_device.uninstall_package(
            "com.google.android.apps.youtube.music"
        )

    def test_grant_permissions(self):
        target_device.grant_permissions(package, permissions)

    def test_revoke_permissions(self):
        target_device.revoke_permissions(package, permissions)

    def test_google_debloat(self):
        output = target_device.google_debloat()

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
            pc_files, target_directory="/storage/emulated/0/Download/"
        )

    def test_pull_file(self):
        pc_path = "/Users/p/Desktop/conveyor_root.crt"
        target_device.pull_file(device_path, pc_path)
        self.assertTrue(os.path.exists(pc_path))

        # no path provided

    def test_pull_files(self):
        pc_files = []
        target_device.pull_files(device_files, pc_files)

        target_device.pull_files(device_files, target_directory="/Users/p/Desktop")

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
        print(is_supported)

    def test_fastboot_reboot(self):
        target_device.fastboot_reboot()

    def test_fastboot_flash_boot(self):
        target_device.fastboot_flash_boot(image_path)

    # utility methods
    def test_load_env(self):
        env_vars = load_env()
        print("ENV", env_vars)
        self.assertTrue(isinstance(env_vars, dict))

    def test_download_link(self):
        # test without output_path
        output_path = download_file_from_link(magisk_url)
        print(output_path)
        self.assertTrue(os.path.exists(output_path))

        # test with output_path (directory given)
        output_path = download_file_from_link(magisk_url, "/Users/p/Desktop/magisk.apk")
        self.assertTrue(os.path.exists(output_path))
        print(output_path)

        # test with output_path (directory not given)
        output_path = download_file_from_link(magisk_url, "magisk.apk")
        self.assertTrue(os.path.exists(output_path))
        print(output_path)

    def test_download_sdk_platform_tools(self):
        # with output directory defined
        output_directory = os.getcwd()
        sdk_path = download_sdk_platform_tools(output_directory)
        self.assertTrue(os.path.exists(sdk_path))

        # with output directory not defined
        sdk_path = download_sdk_platform_tools()
        self.assertTrue(os.path.exists(sdk_path))

    def test_set_path_environment_variable(self):
        # set locally
        variable = "/Users/p/"
        set_path_environment_variable(variable)
        self.assertTrue(find_variable_in_path(variable) == variable)

        # set globally
        set_path_environment_variable(variable, set_globally=True)
        self.assertTrue(find_variable_in_path(variable) == variable)
        print(os.environ.get("PATH"))

    def test_find_variable_in_path(self):
        sdk_path = find_variable_in_path("platform-tools")
        print(sdk_path)
        self.assertTrue(os.path.exists(sdk_path))

    def test_make_executable(self):
        file_path = "file.txt"
        if not os.path.exists(file_path):
            # create file.txt
            with open(file_path, "w") as file:
                file.write("some file")

        self.assertTrue(os.path.exists(file_path))
        make_executable(file_path)
        is_executable = os.access(file_path, os.X_OK)
        self.assertTrue(is_executable)


if __name__ == "__main__":
    adb_methods = [
        TestAdb.test_check_sdk_path,
        TestAdb.test_get_devices,
        TestAdb.test_get_device,
        TestAdb.test_connect,
        TestAdb.test_disconnect,
        TestAdb.test_execute_command,
        TestAdb.test_enable_tcpip_mode,
        TestAdb.test_enable_usb_mode,
    ]
    root_methods = [
        # TestAdb.test_factory_reset,
        # TestAdb.test_root,
        # TestAdb.test_unlock_bootloader,
        TestAdb.test_is_oem_unlock_supported,
        # TestAdb.test_fastboot_reboot,
        # TestAdb.test_fastboot_flash_boot,
    ]

    device_package_methods = [
        TestAdb.test_get_system_packages,
        # TestAdb.test_get_google_packages,
        # TestAdb.test_get_third_party_packages,
        # TestAdb.test_get_packages,
        # TestAdb.test_filter_packages,
        # TestAdb.test_grant_permissions,
        # TestAdb.test_revoke_permissions,
        # TestAdb.test_install_packages,
        # TestAdb.test_install_package,
        # TestAdb.test_uninstall_package,
        # TestAdb.test_uninstall_packages,
        # TestAdb.test_google_debloat,
    ]
    device_settings_methods = [
        TestAdb.test_get_ip,
        TestAdb.test_get_system_settings,
        TestAdb.test_get_global_settings,
        TestAdb.test_get_secure_settings,
        TestAdb.test_get_settings,
        TestAdb.test_set_settings,
        TestAdb.test_is_bootloader_locked,
        TestAdb.test_get_shell_property,
        TestAdb.test_enable_lockscreen,
        TestAdb.test_disable_lockscreen,
        TestAdb.test_set_brightness,
        TestAdb.test_set_volume,
        TestAdb.test_set_password,
        TestAdb.test_clear_password,
        TestAdb.test_disable_mobile_data,
        TestAdb.test_enable_mobile_data,
        TestAdb.test_disable_wifi,
        TestAdb.test_enable_wifi,
    ]

    device_backup_methods = [
        TestAdb.test_backup,
        TestAdb.test_restore,
    ]
    device_file_methods = [
        TestAdb.test_file_exists,
        TestAdb.test_get_current_working_directory,
        TestAdb.test_is_valid_path,
        TestAdb.test_push_file,
        TestAdb.test_push_files,
        TestAdb.test_pull_files,
        TestAdb.test_pull_file,
    ]
    device_event_methods = [
        TestAdb.test_execute_touch_event,
        TestAdb.test_expand_notifications,
    ]

    util_methods = [
        TestAdb.test_load_env,
        TestAdb.test_download_link,
        TestAdb.test_download_sdk_platform_tools,
        TestAdb.test_set_path_environment_variable,
        TestAdb.test_find_variable_in_path,
        TestAdb.test_make_executable,
    ]

    device_methods = device_package_methods
    # methods = root_methods
    # methods = adb_methods
    methods = device_methods
    # methods = util_methods
    run_test_methods(methods)
