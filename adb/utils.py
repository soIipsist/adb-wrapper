import json
import os
import shutil
import platform
import urllib.request


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

    try:
        # Ensure the output directory exists
        os.makedirs(output_directory, exist_ok=True)

        file_name = os.path.basename(download_link)
        sdk_path = os.path.join(output_directory, file_name)

        print("Downloading SDK platform tools...")
        with urllib.request.urlopen(download_link) as response:
            with open(sdk_path, "wb") as out_file:
                shutil.copyfileobj(response, out_file)

        print("Extracting SDK platform tools...")
        shutil.unpack_archive(sdk_path, output_directory)

        os.remove(sdk_path)

        print(
            f"SDK platform-tools was successfully downloaded and extracted at '{output_directory}'."
        )
    except Exception as e:
        print(f"An error occurred: {e}")

    return sdk_path
