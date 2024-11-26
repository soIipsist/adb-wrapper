from enum import Enum
from pathlib import Path
import subprocess
import shlex
import os
from typing import List
from .utils import *
from functools import wraps
from importlib import resources
import json


def command(command: str, logging: bool = True, base_cmd="adb"):
    def decorator(func):
        @wraps(func)
        def wrapper(cls, *args, **kwargs):

            if not isinstance(command, str):
                raise TypeError("command is not of type string.")

            command_args = shlex.split(command)
            command_args.insert(0, base_cmd)

            if isinstance(cls, Device):
                device_id = getattr(cls, "id")
                command_args.insert(1, "-s")
                command_args.insert(2, device_id)

            if args:
                args = [str(arg) for arg in args]
                command_args.extend(args)

            process = subprocess.Popen(
                command_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            output = (
                process.communicate(timeout=None)[0]
                .strip()
                .decode(errors="backslashreplace")
            )

            if process.returncode != 0:
                raise subprocess.CalledProcessError(
                    process.returncode, command_args, output.encode()
                )

            setattr(cls, "return_code", process.returncode)
            setattr(cls, "output", output)

            if logging:
                print(output)

            return func(cls, *args, **kwargs)

        return wrapper

    return decorator


class PackageType(str, Enum):
    THIRD_PARTY = "-3"
    SYSTEM = "-s"
    GOOGLE = None


class SettingsType(str, Enum):
    SECURE = "secure"
    GLOBAL = "global"
    SYSTEM = "system"


class RootMethod(Enum):
    MAGISK = "Magisk"
    APATCH = "Apatch"
    KERNELSU = "KernelSU"


magisk_url = (
    "https://github.com/topjohnwu/Magisk/releases/download/v28.0/Magisk-v28.0.apk"
)

apatch_url = "https://github.com/bmax121/APatch/releases/download/10763/APatch_10763_10763-release-signed.apk"
kernelsu_url = "https://github.com/tiann/KernelSU/releases/download/v1.0.2/KernelSU_v1.0.2_11986-release.apk"


class Package:
    img_src = None
    package_name = None
    name = None
    genre = None
    package_type = PackageType.GOOGLE

    def __init__(
        self,
        img_src: str = None,
        package_name: str = None,
        name: str = None,
        genre: str = None,
        package_type: PackageType = None,
    ):
        self.img_src = img_src
        self.package_name = package_name
        self.name = name
        self.genre = genre
        self.package_type = package_type

    def __repr__(self) -> str:
        return f"{self.package_name}"

    def __str__(self) -> str:
        return f"{self.package_name}"

    @classmethod
    def filter_packages(self, packages: list, **filters):
        def matches(package):
            return all(
                getattr(package, key) == value
                for key, value in filters.items()
                if value is not None
            )

        return [package for package in packages if matches(package)]


class ADB:
    return_code = None
    output: str = None
    sdk_path = None
    google_packages: list = []

    _global_env: bool = False

    def __init__(self, global_env: bool = False) -> None:
        self.global_env = global_env
        self.sdk_path = self.check_sdk_path(self.global_env)

    @property
    def global_env(self):
        return self._global_env

    @global_env.setter
    def global_env(self, global_env: bool):
        self._global_env = global_env

    def check_sdk_path(self, set_globally: bool = False):
        """
        Checks if 'platform-tools' exists in the PATH environment variable.
        Prompts the user to download it if not found and returns the platform-tools directory.
        """

        sdk_path = find_variable_in_path("platform-tools")

        if not sdk_path:  # download sdk platform tools, if adb doesn't exist in PATH
            user_input = (
                input(
                    "ADB was not found in your PATH environment variable. "
                    "Would you like to download the latest version of SDK platform-tools? (y/n): "
                )
                .strip()
                .lower()
            )

            if user_input == "y":

                default_dir = Path.home()
                download_dir = input(
                    f"Enter the directory where platform-tools should be downloaded (default: {default_dir}): "
                ).strip()
                download_dir = (
                    Path(download_dir).resolve() if download_dir else default_dir
                )

                sdk_path = download_sdk_platform_tools(download_dir)

                if not sdk_path:
                    raise RuntimeError("Failed to download SDK platform-tools.")

                set_path_environment_variable(sdk_path, set_globally)
                return str(sdk_path)
            else:
                raise FileNotFoundError(
                    "ADB commands cannot be executed because platform-tools is not in your PATH."
                )

        return sdk_path

    def get_google_packages(self):
        packages = []

        with resources.open_text(__package__, "google.json") as file:
            packages = json.load(file)

            for idx, package in enumerate(packages):
                package: dict
                package = Package(**package, package_type=PackageType.GOOGLE)
                packages[idx] = package

        self.google_packages = packages
        return packages

    @command("tcpip")
    def enable_tcpip_mode(self, port="5555"):
        return self.output

    @command("usb")
    def enable_usb_mode(self):
        return self.output

    def connect(self, device_ip: str, kill_server: bool = False):
        if kill_server:
            self.execute("kill server")
        self.execute(f"connect {device_ip}")

        return self.output

    @command("disconnect")
    def disconnect(self, device_ip: str):
        return self.output

    @command("shell ip route")
    def get_device_ip(self):
        return self.output

    @command("devices")
    def get_devices(self) -> List["Device"]:
        """
        Checks which devices are available and returns them as Device objects.
        """

        devices = []
        output = self.output.splitlines()

        for lines in output:
            lines = lines.strip().split()

            if len(lines) == 2:
                id = lines[0]
                devices.append(Device(id))
        return devices

    def execute(self, command_args: str, logging: bool = True, base_cmd: str = "adb"):
        """
        Executes an adb command and returns its output.
        """

        @command(command_args, logging, base_cmd)
        def run_command(cls):
            return cls.output

        return run_command(self)


class Device(ADB):
    id = None
    system_settings = {}
    global_settings = {}
    secure_settings = {}

    system_packages = []
    third_party_packages = []
    do_not_delete_packages = []

    def __init__(self, id) -> None:
        self.id = id

    def root(self, root_method: RootMethod = RootMethod.MAGISK, image_path: str = None):
        if image_path is None:
            image_path = "boot.img"

        try:
            bootloader_status = self.get_bootloader_status()
            if bootloader_status.strip() == "1":
                print("Your bootloader is locked. Unlock it before proceeding.")
                return
            if root_method == RootMethod.MAGISK:
                self._root_magisk(image_path)
            elif root_method == RootMethod.APATCH:
                self._root_apatch(image_path)
            elif root_method == RootMethod.KERNELSU:
                self._root_kernel_su(image_path)
            else:
                print("Invalid root method selected.")
        except RuntimeError as e:
            print(f"Error during rooting process: {e}")

    def _flash_image(self, image_path: str):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Patched boot image '{image_path}' not found.")
        print("Rebooting device into bootloader...")
        self.reboot_bootloader()

        print("Flashing patched boot image...")
        self.fastboot_flash_boot(image_path)

        print("Rebooting device...")
        self.fastboot_reboot()

    def _root_magisk(self, image_path: str):
        print("Magisk Root Method")
        print("1. Install the Magisk app on your Android device.")
        print(
            "2. Extract the stock boot image from your device's firmware. (Ensure the firmware matches your current OS version.)"
        )
        print("3. Copy the extracted boot image to your device.")
        print("4. Open the Magisk app and use it to patch the boot image.")
        print(
            "5. Transfer the patched boot image back to your computer and save it as boot.img in this script's directory."
        )
        print("6. Press Enter to continue and flash the patched image.\n")

        return self._flash_image(image_path)

    def _root_apatch(self, image_path: str):
        print("Apatch Root Method")
        print("1. Install the Apatch app on your Android device.")
        print("2. Extract the stock boot image from your device's firmware.")
        print("3. Copy the extracted boot image to your device.")
        print("4. Open the Apatch app and use it to patch the boot image.")
        print(
            "5. Transfer the patched boot image back to your computer and save it as boot.img in this script's directory."
        )
        print("6. Press Enter to continue and flash the patched image.\n")

        return self._flash_image(image_path)

    def _root_kernel_su(self, image_path: str = "boot.img"):
        print("KernelSU Root Method")
        print(
            "1. Download a KernelSU-patched boot image that matches your device and current firmware version."
        )
        print("   - Look for the correct image on trusted sources or forums.")
        print(
            "2. Place the downloaded boot image in this script's directory and rename it to boot.img."
        )
        print("3. Press Enter to continue and flash the patched image.\n")

        return self._flash_image(image_path)

    @command("reboot bootloader")
    def reboot_bootloader(self):
        return self.output

    # fastboot commands
    @command("flash boot", base_cmd="fastboot")
    def fastboot_flash_boot(self, image_path: str):
        return self.output

    @command("reboot", base_cmd="fastboot")
    def fastboot_reboot(self):
        return self.output

    @command("flashing unlock", base_cmd="fastboot")
    def unlock_bootloader(self):
        return self.output

    @command("shell getprop ro.boot.flash.locked")
    def get_bootloader_status(self):
        return self.output

    def get_model(self):
        return self.get_shell_property("ro.product.model")

    def get_name(self):
        return self.get_shell_property("ro.product.name")

    def get_sdk(self):
        return self.get_shell_property("ro.build.version.sdk")

    def get_packages(
        self,
        package_type: PackageType = None,
        package_name: str = None,
        name: str = None,
        img_src: str = None,
        genre: str = None,
    ):
        """
        Retrieve a list of packages based on the package type.
        If no package type is specified, all packages are returned.
        """
        package_mapping = {
            PackageType.GOOGLE: self.get_google_packages,
            PackageType.SYSTEM: self.get_system_packages,
            PackageType.THIRD_PARTY: self.get_third_party_packages,
        }

        if package_type is None:
            packages = (
                set(self.get_google_packages())
                | set(self.get_system_packages())
                | set(self.get_third_party_packages())
            )
        else:
            packages = set(package_mapping[package_type]())

        filtered_packages = Package.filter_packages(
            packages,
            package_name=package_name,
            name=name,
            package_type=package_type,
            img_src=img_src,
            genre=genre,
        )

        return list(filtered_packages)

    @command("shell getprop")
    def get_shell_property(self, prop):
        return self.output

    def parse_settings(self, settings: str) -> dict:
        lines = settings.strip().splitlines()

        settings = {}
        for line in lines:
            if "=" in line:
                key, value = line.split("=", 1)
                settings[key.strip()] = value.strip()

        return settings

    def parse_packages(self, packages: str) -> list[Package]:
        packages = packages.strip().splitlines()

        for idx, package in enumerate(packages):
            package_name = package.split(":", 1)[1] if ":" in package else package
            packages[idx] = Package(package_name=package_name)

        return packages

    def get_settings(self):
        system_settings = self.get_system_settings()
        global_settings = self.get_global_settings()
        secure_settings = self.get_secure_settings()

        settings = {
            SettingsType.SYSTEM.value: system_settings,
            SettingsType.GLOBAL.value: global_settings,
            SettingsType.SECURE.value: secure_settings,
        }
        return settings

    @command(f"shell settings list {SettingsType.SYSTEM.value}")
    def get_system_settings(self):
        return self.parse_settings(self.output)

    @command(f"shell settings list {SettingsType.GLOBAL.value}")
    def get_global_settings(self):
        return self.parse_settings(self.output)

    @command(f"shell settings list {SettingsType.SECURE.value}")
    def get_secure_settings(self):
        return self.parse_settings(self.output)

    @command("shell svc wifi enable")
    def enable_wifi(self):
        return self.output

    @command("shell svc wifi disable")
    def disable_wifi(self):
        return self.output

    @command("shell svc data enable")
    def enable_mobile_data(self):
        return self.output

    @command("shell svc data disable")
    def disable_mobile_data(self):
        return self.output

    @command("shell locksettings set-password")
    def set_password(self, password):
        return self.output

    @command("shell locksettings clear --old")
    def clear_password(self, password):
        return self.output

    @command(f"shell pm list packages {PackageType.SYSTEM.value}", logging=False)
    def get_system_packages(self):
        return self.parse_packages(self.output)

    @command(f"shell pm list packages {PackageType.THIRD_PARTY.value}", logging=False)
    def get_third_party_packages(self):
        return self.parse_packages(self.output)

    def install_package(self, package):
        if isinstance(package, Package):
            package = Package.package_name

        return self.execute(f"install {package}")

    def uninstall_package(self, package):
        if isinstance(package, Package):
            package = Package.package_name

        return self.execute(f"uninstall --user 0 {package}")

    @command("shell cmd statusbar expand-notifications")
    def expand_notifications(self):
        return self.output

    @command("shell locksettings set-disabled true")
    def disable_lock_screen(self):
        return self.output

    @command("shell input tap")
    def execute_touch_event(self, x, y):
        return self.output

    @command("shell pm grant")
    def grant_permission(self, package, permission):
        return self.output

    @command("shell pm revoke")
    def revoke_permission(self, package, permission):
        return self.output

    @command("shell cmd package set-home-activity")
    def set_home_app(self, package):
        return self.output

    @command("restore")
    def restore(self, backup_file):
        return self.output

    @command("push")
    def push_file(self, pc_path, device_path):
        return self.output

    @command("pull")
    def pull_file(self, device_path, pc_path):
        return self.output

    # works if rooted
    @command("shell am broadcast -a android.intent.action.MASTER_CLEAR")
    def factory_reset(self):
        return self.output

    def install_packages(self, packages: List[str]):
        for p in packages:
            print("Installing package {0}...".format(p))
            self.install_package(p)

    def uninstall_packages(self, packages: List[str]):
        packages = [
            package
            for package in packages
            if package not in self.do_not_delete_packages
        ]

        for p in packages:
            print("Uninstalling package {0}...".format(p))
            self.uninstall_package(p)

    def grant_permissions(self, package, permissions: List[str]):
        for p in permissions:
            self.grant_permission(package, p)

    def push_files(self, pc_files: List[str], device_path="/sdcard"):
        for f in pc_files:
            self.push_file(f, device_path)

    def pull_files(self, device_files: List[str], pc_path):
        for f in device_files:
            self.pull_file(f, pc_path)

    def revoke_permissions(self, package, permissions: List[str]):
        for p in permissions:
            self.revoke_permission(package, p)

    def google_debloat(self):
        google_packages = self.get_google_packages()
        self.uninstall_packages(google_packages)
        return self.output

    def backup(
        self,
        shared_storage=False,
        apks=False,
        system=False,
        destination_path: str = None,
    ):
        cmd = ["backup", "-all"]

        if shared_storage:
            cmd.append("-shared")

        if apks:
            cmd.append("-apk")

        if system:
            cmd.append("-system")

        if destination_path:
            cmd.append("-f")
            # check if valid directory
            directory = os.path.dirname(destination_path)
            file_name = os.path.basename(destination_path)
            print(directory, file_name)

            if not os.path.isdir(directory):
                raise FileNotFoundError("Directory not valid")

            if not file_name.endswith(".ab"):
                raise FileNotFoundError("Backup files must be of .ab type.")
            cmd.append(destination_path)

        cmd = " ".join(cmd)
        self.execute(cmd)
        return self.output

    def get_setting_cmd(self, input):
        # format can be:
        # a) namespace.key=value
        # b) namespace.key value
        # c) namespace.key.other_value value
        input = input.replace("=", ".", 1).replace(" ", ".").split(".")
        namespace = input[0]
        key = input[1:-1]
        key = key[0] if len(key) == 1 else str.join(".", key)
        value = input[-1]
        output = f"{namespace} {key} {value}"

        return output

    def set_settings(self, settings: List[str]):
        for setting in settings:
            setting_cmd = self.get_setting_cmd(setting)
            cmd = "shell settings put {0}".format(setting_cmd)
            self.execute(cmd)
