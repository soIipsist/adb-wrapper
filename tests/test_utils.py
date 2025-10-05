from pprint import PrettyPrinter
import shutil
from adb_wrapper.utils import (
    download_file_from_link,
    download_sdk_platform_tools,
    load_env,
    make_executable,
    set_path_environment_variable,
    find_variable_in_path,
    check_sdk_path,
    is_valid_command,
    get_magisk_url,
)
from test_base import TestBase, run_test_methods
from adb_wrapper.adb import (
    ADB,
    Device,
    Package,
    RootMethod,
    VolumeType,
    magisk_url,
    apatch_url,
    kernelsu_url,
    command_checked,
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


class TestUtils(TestBase):

    def setUp(self) -> None:
        super().setUp()

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

    def test_is_valid_command(self):
        command = "adb"
        is_valid = is_valid_command(command, False)
        print(is_valid)

    # shell su methods
    def test_is_rooted(self):
        output = target_device.is_rooted()
        print(output)

    def test_get_magisk_url(self):
        url = get_magisk_url()
        print(url)


if __name__ == "__main__":

    methods = [
        # TestUtils.test_load_env,
        # TestUtils.test_download_link,
        # TestUtils.test_download_sdk_platform_tools,
        # TestUtils.test_set_path_environment_variable,
        # TestUtils.test_find_variable_in_path,
        # TestUtils.test_make_executable,
        # TestUtils.test_check_sdk_path,
        # TestUtils.test_is_valid_command,
        TestUtils.test_get_magisk_url
    ]

    run_test_methods(methods)
