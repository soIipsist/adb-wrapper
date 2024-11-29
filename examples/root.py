from adb.adb import ADB, RootMethod
from argparse import ArgumentParser

""" An example script that roots your connected devices."""

if __name__ == "__main__":
    parser = ArgumentParser()
    methods = [str(v.value).lower() for v in list(RootMethod)]
    parser.add_argument("-m", "--method", default=methods[0], choices=methods)
    parser.add_argument("-i", "--image_path", default=None)

    args = vars(parser.parse_args())

    root_method = args.get("method")
    image_path = args.get("image_path")
    adb = ADB()
    devices = adb.get_devices()

    for device in devices:
        device.root(root_method, image_path)
