from adb_wrapper.adb import ADB, Device, Package
import argparse
import os


def degoogle(device: Device, remove_dirs: bool = False):
    packages = device.get_google_packages()

    for package in packages:
        device.uninstall_package(package)
        print(package.name, package.package_name, package.package_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--device_id", default=None)
    parser.add_argument("--remove_dirs", action="store_true", default=None)

    args = parser.parse_args()

    adb = ADB()
    adb.get_device(args.device_id)
