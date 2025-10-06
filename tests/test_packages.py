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


class TestPackages(TestBase):

    def setUp(self) -> None:
        super().setUp()

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

    def test_get_package_path(self):
        package_paths = [
            Package(package_name="com.google.android.apps.youtube.music"),
            # Package(package_path=apk_device_path),
            # apk_device_path,
        ]

        for p in package_paths:
            package_path = target_device.get_package_path(p)
            print(package_path)

    def test_get_package_name(self):
        package_names = [
            Package(package_name="com.google.android.apps.youtube.music"),
            Package(package_path=package),
            "/system/product/app/FMRadio/FMRadio.apk",
        ]

        for p in package_names:
            package_name = target_device.get_package_name(p)
            print("PACKAGE NAME", package_name)

    def test_install_package(self):
        # package path is a device path
        # target_device.install_package(Package(package_path=apk_pc_path))

        # package path is a package
        target_device.install_package(apk_pc_path)

        # target_device.install_package("com")

    def test_uninstall_package(self):
        # device path (should raise an error if it can't find the package name)
        target_device.uninstall_package(apk_device_path)

        # package name
        target_device.uninstall_package(packages[1])


if __name__ == "__main__":
    methods = [
        # TestDevice.test_get_system_packages,
        # TestDevice.test_get_google_packages,
        # TestDevice.test_get_third_party_packages,
        # TestDevice.test_get_packages,
        # TestDevice.test_filter_packages,
        # TestDevice.test_get_package_path,
        # TestDevice.test_get_package_name,
        # TestDevice.test_install_package,
        # TestDevice.test_uninstall_package,
    ]

    run_test_methods(methods)
