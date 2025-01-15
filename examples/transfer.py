from adb_wrapper.adb import ADB  # change this to from adb_wrapper.adb
import argparse
import os
from shlex import quote

"""A script designed to transfer files from your device to your pc and vice versa."""

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("source_files", nargs="+", type=str)
    parser.add_argument("--destination_directory", type=str, default=None)
    parser.add_argument("-i", "--device_ip", type=str, default=None)

    args = vars(parser.parse_args())
    source_files = args.get("source_files")
    destination_directory = args.get("destination_directory")
    device_ip = args.get("device_ip")

    adb = ADB()

    if device_ip:
        adb.connect(device_ip)

    device = adb.get_device()

    if not device:
        raise ValueError("Device not found. Please connect your device via adb.")

    is_push = os.path.exists(source_files[0])  # indicates these are pc files

    # check if destination directory is valid
    if destination_directory:
        if is_push:
            assert device.is_directory(destination_directory)
        else:
            assert os.path.isdir(destination_directory)

    idx = 0
    while idx < len(source_files):

        try:
            source_file = source_files[idx]
            source_file = quote(source_file)

            if os.path.isdir(source_file):
                new_source_files = [
                    entry.path for entry in os.scandir(source_file) if entry.is_file()
                ]
                source_files[idx : idx + 1] = new_source_files

            elif device.is_directory(source_file):
                new_source_files = [
                    os.path.join(source_file, file)
                    for file in device.get_files_in_directory(source_file)
                ]
                source_files[idx : idx + 1] = new_source_files

            else:
                dest_file = os.path.join(
                    destination_directory, os.path.basename(source_file)
                )

                if is_push:  # transfer from pc to device
                    output = device.push_file(source_file, dest_file)
                else:  # transfer from device to pc
                    output = device.pull_file(source_file, dest_file)

                idx += 1
        except Exception as e:
            print("Exception:", e)
            idx += 1
