from enum import Enum
from itertools import zip_longest
from pathlib import Path
import re
import subprocess
import shlex
import os
from typing import List, Union
from .utils import *
from functools import wraps
from importlib import resources
import json
import urllib.request

command_checked: bool = False


def _command_decorator(base_cmd, command, logging=True, log_cmd=False, root=False):
    def decorator(func):
        @wraps(func)
        def wrapper(cls, *args, **kwargs):
            if not isinstance(command, str):
                raise TypeError("command is not of type string.")

            global command_checked
            command_checked, sdk_path = is_valid_command(base_cmd, command_checked)

            command_args = [base_cmd]

            if isinstance(cls, Device):
                device_id = getattr(cls, "id")
                command_args.extend(["-s", device_id])

            # checks if root
            if root:
                command_args.extend(["shell", "su", "-c", command])
            else:
                command_args.extend(shlex.split(command))

            if args:
                args = [str(arg) for arg in args if arg is not None]
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
                if "permission denied" in output.lower():
                    raise PermissionError("Permission issue occurred during execution.")
                elif "unknown" in output.lower():
                    raise FileNotFoundError(f"Command not found: {command_args}")
                elif "error" in output.lower():
                    raise RuntimeError(f"Critical error: {output}")

            setattr(cls, "return_code", process.returncode)
            setattr(cls, "output", output)

            if logging:
                print(output)

            if log_cmd:
                print(command_args)

            return func(cls, *args, **kwargs)

        return wrapper

    return decorator


def command(command: str, logging: bool = True, base_cmd="adb", log_cmd: bool = False):
    return _command_decorator(
        base_cmd, command, logging=logging, log_cmd=log_cmd, root=False
    )


def root_command(
    command: str, logging: bool = True, base_cmd="adb", log_cmd: bool = False
):
    return _command_decorator(
        base_cmd, command, logging=logging, log_cmd=log_cmd, root=True
    )


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


class VolumeType(Enum):
    CALL = "1"
    RINGTONE = "2"
    MEDIA = "3"
    ALARM = "4"
    NOTIFICATION = "5"
    SYSTEM = "6"


class Package:
    img_src = None
    package_name = None
    package_path = None
    name = None
    genre = None
    package_type = PackageType.GOOGLE

    def __init__(
        self,
        package_name: str = None,
        package_path: str = None,
        package_type: PackageType = None,
        img_src: str = None,
        name: str = None,
        genre: str = None,
    ):
        self.package_name = package_name
        self.package_path = package_path
        self.img_src = img_src
        self.name = name
        self.genre = genre
        self.package_type = package_type

    def __repr__(self) -> str:
        return f"{self.package_name}"

    def __str__(self) -> str:
        return f"{self.package_name}"

    @classmethod
    def filter_packages(self, packages: List["Package"], **filters):
        def matches(package):
            return all(
                getattr(package, key) == value
                for key, value in filters.items()
                if value is not None
            )

        packages = [package for package in packages if matches(package)]
        return packages[0] if len(packages) == 1 else packages

    def normalize_packages(
        packages: List[Union[str, "Package"]],
        do_not_delete_packages: List[Union[str, "Package"]],
    ) -> List["Package"]:
        """Returns safe to delete packages."""

        def to_package(p):
            return p if isinstance(p, Package) else Package(p)

        do_not_delete_packages = [to_package(p) for p in do_not_delete_packages]

        return [
            pkg
            for pkg in (to_package(p) for p in packages)
            if pkg not in do_not_delete_packages
        ]


class ADB:
    return_code = None
    output: str = None
    google_packages: list = []

    def __init__(self) -> None:
        pass

    def enable_tcpip_mode(self, port=None):
        if port is None:
            port = "5555"
        return self.execute(f"tcpip {port}")

    @command("usb")
    def enable_usb_mode(self):
        return self.output

    def connect(
        self,
        device_ip: str,
        kill_server: bool = False,
        enable_tcp: bool = False,
        start_server: bool = False,
    ):
        if kill_server:
            self.execute("kill-server")

        if enable_tcp:
            self.enable_tcpip_mode()

        if start_server:
            self.execute("start-server")

        self.execute(f"connect {device_ip}")

        return self.output

    @command("disconnect")
    def disconnect(self, device_ip: str):
        return self.output

    @command("devices", logging=False)
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

    def get_device(self, device_id: str = None):
        devices = self.get_devices()
        return next(
            (device for device in devices if not device_id or device.id == device_id),
            None,
        )

    def execute(
        self,
        command_args: str,
        logging: bool = True,
        base_cmd: str = "adb",
        log_cmd: bool = False,
        root: bool = False,
    ):
        """
        Executes an adb command and returns its output.
        """
        decorator = root_command if root else command

        @decorator(command_args, logging, base_cmd, log_cmd)
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

    @command("shell ip route")
    def get_device_ip(self):

        ip_pattern = r"\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?!\/)\b"

        match = re.search(ip_pattern, self.output)

        if match:
            return match.group(1)  # Return the matched IP address
        return None

    def root(self, root_method: RootMethod = RootMethod.MAGISK, image_path: str = None):
        if image_path is None:
            image_path = "boot.img"

        try:
            print(root_method)
            if self.is_bootloader_locked():
                q = input(
                    "Your bootloader is locked. Would you like to unlock it? (y/n)"
                )
                if q == "y":
                    self.unlock_bootloader()
                    self.root(root_method, image_path)
                else:
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
        magisk_url = get_apk_asset_url("topjohnwu/magisk")
        output_path = download_file_from_link(magisk_url)

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
        apatch_url = get_apk_asset_url("bmax121/APatch")
        print(apatch_url)
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
        kernel_su_url = get_apk_asset_url("tiann/KernelSU")

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

    def is_bootloader_locked(self):
        return bool(self.get_shell_property("ro.boot.flash.locked"))

    @command("shell getprop ro.oem_unlock_supported", logging=False)
    def is_oem_unlock_supported(self):
        return bool(self.output)

    def get_model(self):
        return self.get_shell_property("ro.product.model")

    def get_vendor(self):
        return self.get_shell_property("ro.product.manufacturer")

    def get_region_code(self):

        # ensure region is correct

        region_code_attrs = [
            "ro.boot.sales_code",
            "ro.csc.sales_code",
            "ro.boot.hwc",
            "ro.boot.region",
            "ro.product.region",
            "ro.product.locale",
            "ro.boot.hardware.sku",
            "ro.boot.region_id",
            "ro.product.system.name",
            "ro.semc.version.cust_revision",
            "ro.build.display.id",
        ]

        # check if any attr has a value

        for attr in region_code_attrs:
            value = self.get_shell_property(attr)
            if value:
                # normalize to uppercase, strip whitespace
                match = re.search(r"[A-Z]{2,5}", value.upper())
                if match:
                    return match.group(0)

    def get_name(self):
        return self.get_shell_property("ro.product.name")

    def get_sdk(self):
        return self.get_shell_property("ro.build.version.sdk")

    def is_rooted(self):
        self.output = self.execute("shell su -c id", logging=False)
        return "uid=0" in self.output

    def get_package_path(self, package):
        if isinstance(package, Package):
            package = (
                package.package_path if package.package_path else package.package_name
            )

        if not package.endswith(
            ".apk"
        ):  # use shell pm <package_name> to get package path
            output = self.execute(f"shell pm path {package}")
            package = output if output else package
        return package

    def get_package_name(self, package):

        if isinstance(package, Package):
            package = package.package_name or package.package_path

        if isinstance(package, str) and package.endswith(".apk"):
            matched = Package.filter_packages(self.get_packages(), package_path=package)
            if matched:
                package = matched.package_name

        return package

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

    @command("shell getprop", logging=False)
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
            package_path = None
            package_name = None

            if package.startswith("package:"):
                package_path = package.split("package:", 1)[1].split("=", 1)[0].strip()

            if "=" in package:
                package_name = package.split("=", 1)[1].strip()

            name = os.path.basename(package_path)
            packages[idx] = Package(
                package_name=package_name, package_path=package_path, name=name
            )

        return packages

    def get_settings(self):
        self.system_settings = self.get_system_settings()
        self.global_settings = self.get_global_settings()
        self.secure_settings = self.get_secure_settings()

        settings = {
            SettingsType.SYSTEM.value: self.system_settings,
            SettingsType.GLOBAL.value: self.global_settings,
            SettingsType.SECURE.value: self.secure_settings,
        }
        return settings

    @command(f"shell settings list {SettingsType.SYSTEM.value}", logging=False)
    def get_system_settings(self):
        system_settings = self.parse_settings(self.output)
        return system_settings

    @command(f"shell settings list {SettingsType.GLOBAL.value}", logging=False)
    def get_global_settings(self):
        global_settings = self.parse_settings(self.output)
        return global_settings

    @command(f"shell settings list {SettingsType.SECURE.value}", logging=False)
    def get_secure_settings(self):
        secure_settings = self.parse_settings(self.output)
        return secure_settings

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

    @command(f"shell pm list packages -f {PackageType.SYSTEM.value}", logging=False)
    def get_system_packages(self):
        return self.parse_packages(self.output)

    @command(
        f"shell pm list packages -f {PackageType.THIRD_PARTY.value}", logging=False
    )
    def get_third_party_packages(self):
        return self.parse_packages(self.output)

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

    def install_package(self, package: Package):
        if not isinstance(package, Package):
            package_path = self.get_package_path(package)
        print("Installing package {0}...".format(package_path))
        is_shell_install = not os.path.exists(package_path)

        cmd = (
            f"shell pm install {package_path}"
            if is_shell_install
            else f"install {package_path}"
        )
        return self.execute(cmd)

    def uninstall_package(self, package: Package, remove_dirs: bool = False):
        package_name = package.package_name
        print("Uninstalling package {0}...".format(package_name))

        if remove_dirs:
            print()
            self.execute()
        return self.execute(f"uninstall --user 0 {package_name}")

    @command("shell cmd statusbar expand-notifications")
    def expand_notifications(self):
        return self.output

    @command("shell locksettings set-disabled true")
    def disable_lock_screen(self):
        return self.output

    @command("shell locksettings set-disabled false")
    def enable_lock_screen(self):
        return self.output

    def set_brightness(self, brightness: int):
        return self.set_settings([f"system.screen_brightness={brightness}"])

    def set_volume(
        self, volume_level: int, volume_type: VolumeType = VolumeType.SYSTEM
    ):
        return self.execute(
            f"shell media volume --stream {volume_type.value} --set {volume_level}"
        )

    @command("shell input tap")
    def execute_touch_event(self, x, y):
        return self.output

    @command("shell pm grant")
    def grant_permission(
        self,
        package,
        permission,
    ):
        if self.return_code == 0:
            print(f"Successfully granted package permission {permission} of {package}.")
        return self.output

    @command("shell pm revoke")
    def revoke_permission(self, package, permission):
        if self.return_code == 0:
            print(f"Successfully revoked package permission {permission} of {package}.")
        return self.output

    @command("shell cmd package set-home-activity")
    def set_home_app(self, package):
        return self.output

    def restore(self, backup_file: str):
        print(f"Restoring backup from {backup_file}...")

        if not os.path.exists(backup_file):
            raise FileNotFoundError("Backup file not found.")

        if not backup_file.endswith(".ab"):
            raise FileNotFoundError("Backup files must be of .ab type.")
        return self.execute(f"restore {backup_file}")

    @command("push")
    def push_file(self, pc_file, device_file):
        """Transfer file from pc to device."""
        print(f"Transferred file {pc_file} to {device_file}.")
        return self.output

    @command("pull")
    def pull_file(self, device_file, pc_file):
        """Transfer file from device to pc."""
        print(f"Transferred file {device_file} to {pc_file}.")
        return self.output

    @command("shell pwd")
    def get_current_working_directory(self):
        return self.output

    @command("shell mkdir")
    def create_directory(self, directory):
        print(f"Created directory {directory}.")
        return self.output

    def get_default_download_directory(self):
        default_download_directory = "/storage/emulated/0/Download"
        output = self.execute(f"shell ls {default_download_directory}", logging=False)

        return default_download_directory if output else "/sdcard"

    @command("shell ls", logging=False)
    def is_valid_path(self, path):
        return not bool(self.return_code)

    @command("shell ls -p", logging=False)
    def get_files_in_directory(self, directory):
        return [
            os.path.join(directory, o.strip())
            for o in self.output.splitlines()
            if not o.endswith("/")
        ]

    @command("shell find {path} -type f", logging=False)
    def get_all_files_in_directory(self, directory):
        files = [
            os.path.join(directory, line.strip())
            for line in self.output.splitlines()
            if line.strip()
        ]
        return files

    @command("shell test -d", logging=False)
    def is_directory(self, path):
        return not bool(self.return_code)

    def push_files(
        self,
        pc_files: List[str],
        device_files: List[str] = [],
        destination_directory: str = None,
    ):
        """Transfer files from pc to device."""

        if device_files is None:
            device_files = []

        if not destination_directory:
            destination_directory = self.get_default_download_directory()

        for pc_file, device_file in zip_longest(pc_files, device_files):
            try:
                if device_file is None:
                    device_file = os.path.join(
                        destination_directory, os.path.basename(pc_file)
                    )

                self.push_file(pc_file, device_file)
            except Exception as e:
                print(e)

        return self.output

    def pull_files(
        self,
        device_files: List[str],
        pc_files: List[str] = [],
        destination_directory: str = None,
    ):
        """Transfer files from device to pc."""
        if pc_files is None:
            pc_files = []

        if not destination_directory:
            destination_directory = os.getcwd()

        for device_file, pc_file in zip_longest(device_files, pc_files):
            try:
                if pc_file is None:
                    pc_file = os.path.join(
                        destination_directory, os.path.basename(device_file)
                    )
                self.pull_file(device_file, pc_file)
            except Exception as e:
                print(e)

        return self.output

    @command("shell test -f")
    def file_exists(self, file_path: str):
        return not bool(self.return_code)

    # works if rooted
    @command("shell am broadcast -a android.intent.action.MASTER_CLEAR")
    def factory_reset(self):
        return self.output

    def install_packages(self, packages: List[str]):
        for p in packages:
            self.install_package(p)

    def uninstall_packages(
        self,
        packages: List[str],
        do_not_delete_packages: List[str] = None,
        remove_dirs: bool = False,
    ):
        packages = Package.normalize_packages(packages, do_not_delete_packages)
        for package in packages:
            self.uninstall_package(package, remove_dirs)

    def grant_permissions(self, package, permissions: List[str]):
        for permission in permissions:
            self.grant_permission(package, permission)

    def revoke_permissions(self, package, permissions: List[str]):
        for permission in permissions:
            self.revoke_permission(package, permission)

    def google_debloat(self):
        google_packages = self.get_google_packages()
        self.uninstall_packages(google_packages)
        return self.output

    def backup(
        self,
        shared_storage=True,
        apks=True,
        system=True,
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

            if not destination_path.endswith(".ab"):
                raise FileNotFoundError("Backup files must be of .ab type.")
            cmd.append(destination_path)

        cmd = " ".join(cmd)
        print("Performing backup...")
        self.execute(cmd)
        return self.output

    def get_setting_cmd(self, input: str):
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
