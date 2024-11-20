import io
import json
import os
import shutil
import platform


def create_json_file(json_file, data=None):
    try:
        with open(json_file, "w") as file:
            if data is None:
                data = []
            json.dump(data, file)
    except Exception as e:
        print(e)


def read_json_file(json_file, errors=None):
    try:
        with open(json_file, "r", errors=errors) as file:
            json_object = json.load(file)
            return json_object
    except Exception as e:
        print(e)


def download_sdk_platform_tools(output_directory=None):
    """
    Can be used to easily download SDK platform-tools, if adb doesn't exist as a
    PATH variable.

    """

    if not output_directory:
        print("No directory found, using default home directory.")
        output_directory = os.path.expanduser("~")

    download_link = (
        "https://dl.google.com/android/repository/platform-tools-latest-{0}.zip".format(
            platform.system().lower()
        )
    )

    # download sdk platform tools
    try:
        print("Downloading SDK platform tools...")
        sdk_path = wget.download(download_link, out=output_directory)

        # unzip
        shutil.unpack_archive(sdk_path, output_directory)
        sdk_path = sdk_path.replace(".zip", "").replace("/", "\\")

        print()
        print(
            "SDK platform-tools was successfully downloaded at '{0}'.".format(
                output_directory
            )
        )
    except Exception as e:
        print(e)

    return sdk_path
