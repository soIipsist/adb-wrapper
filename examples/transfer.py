from adb.adb import ADB, Device
import argparse
import os

"""A script designed to transfer files to your pc."""

parser = argparse.ArgumentParser()

parser.add_argument("files", nargs="+", type=str)
parser.add_argument("-d", "--destination_paths", nargs="+", type=str)

args = vars(parser.parse_args())
files = args.get("files")
destination_paths = args.get("destination_paths")

adb = ADB()
device = adb.get_device()
