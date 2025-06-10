import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from adb_wrapper.adb import ADB
import argparse
import os

"""A script designed to transfer files from your device to your pc and vice versa."""


def get_pc_directory_files(pc_directory: str):
    source_files = [
        os.path.join(pc_directory, f)
        for f in os.listdir(pc_directory)
        if os.path.isfile(os.path.join(pc_directory, f))
    ]

    return source_files


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("source_directory", type=str)
    parser.add_argument(
        "destination_directory", type=str, default="/sdcard/Download", nargs="?"
    )
    parser.add_argument("-n", "--nested_files", default=False)

    args = vars(parser.parse_args())
    source_directory = args.get("source_directory")
    destination_directory = args.get("destination_directory")
    nested_files = args.get("nested_files")

    print(args)
    # adb = ADB()
    # device = adb.get_device()

    # if not device:
    #     raise ValueError("Device not found. Please connect your device via adb.")

    is_push = os.path.exists(source_directory)  # indicates these are pc files
    source_files = []

    if is_push:
        source_files = get_pc_directory_files(source_directory)
        # device.push_files(source_files, destination_directory=destination_directory)
    else:
        pass
        # source_files = device.get_files_in_directory(source_directory)
        # device.pull_files(source_files, destination_directory=destination_directory)

    print("Source files: ", source_files)
