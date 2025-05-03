from adb_wrapper.adb import ADB  # change this to from adb_wrapper.adb
import argparse
import os
from shlex import quote

"""A script designed to transfer files from your device to your pc and vice versa."""

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("source_files", nargs="+", type=str)
    parser.add_argument("--destination_directory", type=str, default="/sdcard/Download")
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
    if destination_directory is None:
        raise ValueError("Destination directory must be given.")

    if destination_directory:
        if is_push:
            assert device.is_directory(destination_directory)
        else:
            assert os.path.isdir(destination_directory)

    idx = 0
    while idx < len(source_files):
        try:
            source_file = source_files[idx]

            # Local PC directory
            if os.path.isdir(source_file):
                base_dir = source_file
                new_source_files = []
                for root, dirs, files in os.walk(base_dir):
                    rel_root = os.path.relpath(root, os.path.dirname(base_dir))
                    device_dir = os.path.join(destination_directory, rel_root)
                    device.create_directory(
                        device_dir
                    )  # create each directory on device

                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_file_path = os.path.join(rel_root, file)
                        new_source_files.append(
                            (full_path, rel_file_path)
                        )  # tuple of source and relative path

                source_files[idx : idx + 1] = new_source_files

            # Remote device directory
            elif device.is_directory(source_file):
                base_dir = source_file
                new_source_files = []

                def walk_device_dir(path, root_path):
                    entries = device.get_files_in_directory(path)
                    for entry in entries:
                        full_path = os.path.join(path, entry)
                        if device.is_directory(full_path):
                            rel_dir = os.path.relpath(full_path, root_path)
                            local_dir = os.path.join(destination_directory, rel_dir)
                            os.makedirs(local_dir, exist_ok=True)
                            walk_device_dir(full_path, root_path)
                        else:
                            rel_file_path = os.path.relpath(full_path, root_path)
                            new_source_files.append((full_path, rel_file_path))

                walk_device_dir(base_dir, base_dir)
                source_files[idx : idx + 1] = new_source_files

            # File (push/pull)
            else:
                if isinstance(source_file, tuple):
                    src_path, rel_path = source_file
                    dest_file = os.path.join(destination_directory, rel_path)
                    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                else:
                    src_path = source_file
                    dest_file = os.path.join(
                        destination_directory, os.path.basename(src_path)
                    )

                if is_push:
                    output = device.push_file(src_path, dest_file)
                else:
                    output = device.pull_file(src_path, dest_file)

                idx += 1

        except Exception as e:
            print("Exception:", e)
            idx += 1
