from adb.adb import ADB, Device
import argparse
import os

"""A script designed to transfer files to your pc."""

parser = argparse.ArgumentParser()

parser.add_argument("device_files", nargs="+", type=str)
parser.add_argument("-p", "--pc_files", nargs="+", type=str)

args = vars(parser.parse_args())
device_files = args.get("device_files")
pc_files = args.get("pc_files")

adb = ADB()
device = adb.get_device()

output = device.pull_files(device_files, pc_files)
