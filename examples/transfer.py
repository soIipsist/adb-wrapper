from adb.adb import ADB, Device
import argparse
import os
from itertools import zip_longest

"""A script designed to transfer files to from your device to your pc and vice versa."""


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("source_files", nargs="+", type=str)
    parser.add_argument("--destination_files", nargs="+", type=str)
    parser.add_argument("--destination_directory", type=str, default=None)
    parser.add_argument("-i", "--device_ip", type=str, default=None)

    args = vars(parser.parse_args())
    source_files = args.get("source_files")
    destination_files = args.get("destination_files")
    destination_directory = args.get("destination_directory")
    device_ip = args.get("device_ip")

    adb = ADB()

    if device_ip:
        adb.connect(device_ip, True, False, True)
    device = adb.get_device()

    # get source files first

    for idx, source_file in enumerate(source_files):

        if os.path.isdir(
            source_file
        ):  # check if file is a directory, and extend the list

            new_source_files = [
                entry.path for entry in os.scandir(source_file) if entry.is_file()
            ]
            source_files[idx : idx + 1] = new_source_files

        # likewise, do the same if it's a device file

        if device.is_directory(source_file):
            # check if it's a directory
            new_source_files = []

    # for idx, (source_file, destination_file) in enumerate(
    #     zip_longest(source_files, destination_files)
    # ):
    #     print(source_file, destination_file)

    #     if destination_directory:
    #         base_name = (
    #             os.path.basename(destination_file)
    #             if destination_file
    #             else os.path.basename(source_file)
    #         )
    #         os.path.join(destination_directory, base_name)

    # if os.path.exists(
    #     source_files[0]
    # ):  # this is a device file, which means you'll transfer from pc to device
    #     output = device.push_files(source_files, destination_files)
    # else:
    #     output = device.pull_files(source_files, destination_files)

    # print(output)
