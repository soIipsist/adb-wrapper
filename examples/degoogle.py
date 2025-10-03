from adb_wrapper.adb import ADB, Device, Package
import argparse
import os


def degoogle(device: Device):
    packages = device.get_google_packages()

    for package in packages:
        pass


if __name__ == "__main__":
    devices = ADB().get_devices()

    for device in devices:
        degoogle(device)
