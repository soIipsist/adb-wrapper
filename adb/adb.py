from enum import Enum
import subprocess
import shlex
import os
from typing import List
from .utils import *
from functools import wraps
from importlib import resources


def command(command: str):
    def decorator(func):
        @wraps(func)
        def wrapper(cls, **kwargs):
            print("ARGS", kwargs)

            if not isinstance(command, str):
                raise TypeError("command is not of type string.")

            command_args = shlex.split(command)
            command_args.insert(0, "adb")

            if isinstance(cls, Device):
                device_id = getattr(cls, "id")
                command_args.insert(1, "-s")
                command_args.insert(2, device_id)

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

            setattr(cls, "output", output)
            return func(cls, **kwargs)

        return wrapper

    return decorator


class PackageType(str, Enum):
    THIRD_PARTY = "-3"
    SYSTEM = "-f"
    GOOGLE = None


class SettingsType(str, Enum):
    SECURE = "secure"
    GLOBAL = "global"
    SYSTEM = "system"


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
        return f"<Package({self.package_name})>"

    def __str__(self) -> str:
        return f"<Package({self.package_name})>"

    @classmethod
    def filter_packages(self, packages: list, **filters):
        def matches(package):
            return all(
                getattr(package, key) == value
                for key, value in filters.items()
                if value is not None
            )

        return [package for package in packages if matches(package)]


def get_google_packages():
    packages = []

    with resources.open_text(__package__, "google.json") as file:
        packages = json.load(file)

        for idx, package in enumerate(packages):
            package: dict
            package = Package(**package, package_type=PackageType.GOOGLE)
            packages[idx] = package

    return packages


class Device:
    id = None
    output = None
    system_settings = {}
    global_settings = {}
    secure_settings = {}

    system_packages = []
    third_party_packages = []
    do_not_delete_packages = []

    def __init__(self, id) -> None:
        self.id = id

    def execute(self, command_args: str):
        """
        Executes an adb command and returns its output.
        """

        @command(command_args)
        def run_command(cls):
            return cls.output

        return run_command(self)

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
    ):
        """
        Retrieve a list of packages based on the package type.
        If no package type is specified, all packages are returned.
        """
        package_mapping = {
            PackageType.GOOGLE: get_google_packages,
            PackageType.SYSTEM: self.get_system_packages,
            PackageType.THIRD_PARTY: self.get_third_party_packages,
        }

        if package_type is None:
            packages = (
                set(get_google_packages())
                | set(self.get_system_packages())
                | set(self.get_third_party_packages())
            )
        else:
            packages = set(package_mapping[package_type]())

        filtered_packages = Package.filter_packages(
            packages, package_name=package_name, name=name, package_type=package_type
        )

        return list(filtered_packages)

    @command("shell getprop")
    def get_shell_property(self, prop):
        return self.output

    def parse_settings(self, settings: str):
        lines = settings.strip().splitlines()

        settings = {}
        for line in lines:
            if "=" in line:
                key, value = line.split("=", 1)
                settings[key.strip()] = value.strip()

        return settings

    def get_settings(self):
        system_settings = self.get_system_settings()
        global_settings = self.get_global_settings()
        secure_settings = self.get_secure_settings()

        settings = {
            "system_settings": system_settings,
            "global_settings": global_settings,
            "secure_settings": secure_settings,
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

    @command("shell pm list packages -f")
    def get_system_packages(self):
        return self.output

    @command("shell pm list packages -3")
    def get_third_party_packages(self):
        return self.output

    @command("install")
    def install_package(self, package):
        return self.output

    @command("uninstall --user 0")
    def uninstall_package(self, package):
        return self.output

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
        packages = [
            Package(package_name=package) if isinstance(package, Package) else package
            for package in packages
        ]

        for p in packages:
            print("Installing package {0}...".format(p))
            self.install_package(p)

    def uninstall_packages(self, packages: List[str]):
        packages = [
            Package(package_name=package) if isinstance(package, Package) else package
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
        google_packages = get_google_packages()
        self.uninstall_packages(google_packages)

    def backup(self, shared_storage=False, apks=False, system=False, path: str = None):
        cmd = ["backup", "-all"]

        if shared_storage:
            cmd.append("-shared")

        if apks:
            cmd.append("-apk")

        if system:
            cmd.append("-system")

        if path:
            cmd.append("-f")
            # check if valid directory
            directory = os.path.dirname(path)
            file_name = os.path.basename(path)
            print(directory, file_name)

            if not os.path.isdir(directory):
                raise FileNotFoundError("Directory not valid")

            if not file_name.endswith(".ab"):
                raise FileNotFoundError("Backup files must be of .ab type.")
            cmd.append(path)

        self.execute(cmd)

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


class ADB:

    output: str = None
    google_packages: list = []
    sdk_path = None

    def __init__(self) -> None:
        self.sdk_path = check_sdk_path()

    @command("devices")
    def get_devices(self) -> list[Device]:
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

    def execute(self, command_args: str):
        """
        Executes an adb command and returns its output.
        """

        @command(command_args)
        def run_command(cls):
            return cls.output

        return run_command(self)
