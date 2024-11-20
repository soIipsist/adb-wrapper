import subprocess
import shlex
import os
from typing import List
from .utils import *
from functools import wraps
import shutil
from importlib import resources


def command(command: str):
    def decorator(func):
        @wraps(func)
        def wrapper(cls, *args, **kwargs):

            if not isinstance(command, str):
                raise TypeError("command is not of type string.")

            command_args = shlex.split(command)
            command_args.insert(0, "adb")

            if isinstance(cls, Device):
                device_id = getattr(cls, "device_id")
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
            return func(cls, *args, **kwargs)

        return wrapper

    return decorator


class Package:
    img_src = None
    package_name = None
    name = None
    genre = None
    privileged = False

    def __init__(
        self,
        img_src: str = None,
        package_name: str = None,
        name: str = None,
        genre: str = None,
        privileged: bool = False,
    ):
        self.img_src = img_src
        self.package_name = package_name
        self.name = name
        self.genre = genre
        self.privileged = privileged


class ADB(object):

    output: str = None
    google_packages: list = []

    def __init__(self) -> None:
        self.check_adb_path()
        self.google_packages = self.get_google_packages()

    def get_google_packages(self):
        pass

    def check_adb_path(self):
        """
        Returns base adb command if PATH variable was found.
        """
        # check if PATH variable was found
        path = os.environ.get("path")

        if "platform-tools" not in path.lower():
            user_input = input(
                "adb was not found as a PATH variable. Would you like to download the latest version of sdk platform-tools? (y/n)"
            )
            if user_input == "y":
                download_dir = input("Download directory: ")
                sdk_path = download_sdk_platform_tools(download_dir)
                return sdk_path
            else:
                raise FileNotFoundError(
                    "Cannot execute adb commands, please add platform-tools to your PATH variable."
                )

    @command("devices")
    def get_devices(self):
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

    def execute(self, command_args: List[str], device_id: str = None):
        """
        Executes an adb command and returns its output. If a device id is provided, the command
        will be executed on the target device.
        """
        output = None

        try:
            # split commands for Popen function if type is str

            if isinstance(command_args, str):
                command_args = shlex.split(command_args)

            if not isinstance(command_args, list) or any(
                not isinstance(arg, str) for arg in command_args
            ):
                raise TypeError("The command passed is not a list of strings.")

            command_args.insert(0, self.command)
            if device_id:
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
                print(output)
                raise subprocess.CalledProcessError(
                    process.returncode, command_args, output.encode()
                )
        except Exception as e:
            print(e)
        return output


class Device(ADB):
    id = None
    settings = {"system_settings": [], "global_settings": [], "secure_settings": []}
    system_packages = []
    third_party_packages = []
    do_not_delete_packages = []

    def __init__(self, id) -> None:
        self.id = id

    def get_devices(self):
        raise AttributeError("'Device' object has no attribute 'get_devices'")

    def download_sdk_platform_tools(self):
        raise AttributeError(
            "'Device' object has no attribute 'download_sdk_platform_tools'"
        )

    def get_model(self):
        return self.get_shell_property("ro.product.model")

    def get_name(self):
        return self.get_shell_property("ro.product.name")

    def get_sdk(self):
        return self.get_shell_property("ro.build.version.sdk")

    def get_packages(self):
        packages = []
        self.system_packages = self.get_system_packages().split("\n")
        self.third_party_packages = self.get_third_party_packages().split("\n")
        packages.extend(self.system_packages)
        packages.extend(self.third_party_packages)
        return packages

    def command(*arguments, **kwargs):
        def command(f):
            def wrapper(self, *args):
                if len(args) > 0:
                    params = str(*arguments).format(*args)
                    return self.execute(params)
                return self.execute(*arguments)

            return wrapper

        return command

    def get_shell_property(self, prop):
        return self.execute("shell getprop {0}".format(prop))

    def get_settings(self):
        system_settings = self.get_system_settings()
        global_settings = self.get_global_settings()
        secure_settings = self.get_secure_settings()
        self.settings.update(
            system_settings=system_settings,
            global_settings=global_settings,
            secure_settings=secure_settings,
        )
        return self.settings

    @command("shell settings list system")
    def get_system_settings(self):
        pass

    @command("shell svc wifi enable")
    def enable_wifi(self):
        pass

    @command("shell svc wifi disable")
    def disable_wifi(self):
        pass

    @command("shell svc data enable")
    def enable_mobile_data(self):
        pass

    @command("shell svc data disable")
    def disable_mobile_data(self):
        pass

    @command("shell settings list global")
    def get_global_settings(self):
        pass

    @command("shell locksettings set-password {0}")
    def set_password(self, password):
        pass

    @command("shell locksettings clear --old {0}")
    def clear_password(self, password):
        pass

    @command("shell settings list secure")
    def get_secure_settings(self):
        pass

    @command("shell pm list packages -f")
    def get_system_packages(self):
        pass

    @command("shell pm list packages -3")
    def get_third_party_packages(self):
        pass

    @command("install {0}")
    def install_package(self, package):
        pass

    @command("uninstall --user 0 {0}")
    def uninstall_package(self, package):
        pass

    @command("shell cmd statusbar expand-notifications")
    def expand_notifications(self):
        pass

    @command("shell locksettings set-disabled true")
    def disable_lock_screen(self):
        pass

    @command("shell input tap {0} {1}")
    def execute_touch_event(self, x, y):
        pass

    @command("shell pm grant {0} {1}")
    def grant_permission(self, package, permission):
        pass

    @command("shell pm revoke {0} {1}")
    def revoke_permission(self, package, permission):
        pass

    @command("shell cmd package set-home-activity {0}")
    def set_home_app(self, package):
        pass

    @command("restore {0}")
    def restore(self, backup_file):
        pass

    @command("push {0} {1}")
    def push_file(self, pc_path, device_path):
        pass

    @command("pull {0} {1}")
    def pull_file(self, device_path, pc_path):
        pass

    # works if rooted
    @command("shell am broadcast -a android.intent.action.MASTER_CLEAR")
    def factory_reset(self):
        pass

    def install_packages(self, packages: List[str]):
        for p in packages:
            print("Installing package {0}...".format(p))
            self.install_package(p)

    def uninstall_packages(self, packages: List[str]):
        packages = [p for p in packages if p not in self.do_not_delete_packages]

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
        with resources.open_text(__package__, "google.json") as file:
            self.uninstall_packages(self.google_packages)

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
        output = "{0} {1} {2}".format(namespace, key, value)

        return output

    def set_settings(self, settings: List[str]):
        for setting in settings:
            setting_cmd = self.get_setting_cmd(setting)
            cmd = "shell settings put {0}".format(setting_cmd)
            self.execute(cmd)
