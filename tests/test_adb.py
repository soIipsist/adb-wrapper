from pprint import PrettyPrinter
from adb.utils import check_sdk_path
from test_base import TestBase, run_test_methods
from adb.adb import ADB, Device, Package, get_google_packages
import os

adb = ADB()
devices = adb.get_devices()
target_device = devices[0] if len(devices) > 0 else None

package = ""


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

    def test_connect(self):
        device_ip = ""
        output = adb.connect()

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

    def test_install_package(self):
        output = target_device.install_package("com.google.android.apps.youtube.music")
        print(output)

    def test_uninstall_package(self):
        output = target_device.uninstall_package(
            "com.google.android.apps.youtube.music"
        )
        print(output)

    def test_grant_permissions(self):
        permissions = []
        target_device.grant_permissions(package, permissions)

    def test_revoke_permissions(self):
        permissions = []
        target_device.revoke_permissions(package, permissions)

    def test_google_debloat(self):
        output = target_device.google_debloat()
        print(output)

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
        print(output)

    def test_restore(self):
        backup_file = "backup.ab"
        output = target_device.restore(backup_file)

    def test_set_home_app(self):
        package = ""
        output = target_device.set_home_app(package)
        print(output)

    def test_push_file(self):
        pc_path = ""
        device_path = ""
        output = target_device.push_file(pc_path, device_path)

    def test_pull_file(self):
        pc_path = ""
        device_path = ""
        target_device.pull_file(device_path, pc_path)

    def test_get_shell_property(self):
        prop = target_device.get_shell_property("ro.product.model")

        print(prop)

        sdk = target_device.get_sdk()
        name = target_device.get_name()
        model = target_device.get_model()

        print(sdk)
        print(name)
        print(model)

    def test_execute_touch_event(self):
        x = 100
        y = 1000

        output = target_device.execute_touch_event(x, y)

        print(output)

    def test_expand_notifications(self):
        output = target_device.expand_notifications()

        print(output)

    def test_factory_reset(self):
        output = target_device.factory_reset()
        print(output)


if __name__ == "__main__":
    test_methods = [
        TestAdb.test_check_adb_path,
        TestAdb.test_get_devices,
        TestAdb.test_connect,
        TestAdb.test_execute_command,
        TestAdb.test_get_system_packages,
        TestAdb.test_get_google_packages,
        TestAdb.test_get_third_party_packages,
        TestAdb.test_get_packages,
        TestAdb.test_filter_packages,
        TestAdb.test_get_system_settings,
        TestAdb.test_get_global_settings,
        TestAdb.test_get_secure_settings,
        TestAdb.test_get_settings,
        TestAdb.test_set_settings,
        TestAdb.test_grant_permissions,
        TestAdb.test_revoke_permissions,
        TestAdb.test_install_package,
        TestAdb.test_uninstall_package,
        TestAdb.test_google_debloat,
        TestAdb.test_disable_mobile_data,
        TestAdb.test_enable_mobile_data,
        TestAdb.test_disable_wifi,
        TestAdb.test_enable_wifi,
        TestAdb.test_backup,
        TestAdb.test_restore,
        TestAdb.test_push_file,
        TestAdb.test_pull_file,
        TestAdb.test_get_shell_property,
        TestAdb.test_execute_touch_event,
        TestAdb.test_expand_notifications,
        TestAdb.test_factory_reset,
    ]
    run_test_methods(test_methods)
