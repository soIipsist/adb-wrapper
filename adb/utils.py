import json
import os
from pathlib import Path
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

    platform_str = platform.system().lower()
    download_link = f"https://dl.google.com/android/repository/platform-tools-latest-{platform_str}.zip"

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


def set_environment_variable(sdk_path: str):
    if os.name == "nt":  # Windows
        os.environ["PATH"] += ";C:\\MyCustomPath"
    else:  # macOS/Linux
        os.environ["PATH"] += f":{sdk_path}"

    return os.environ["PATH"]


def check_adb_path():
    """
    Checks if 'platform-tools' exists in the PATH environment variable.
    Prompts the user to download it if not found and returns the platform-tools directory.
    """
    path_variable = os.environ.get("PATH", "")

    platform_tools_path = None
    for path in path_variable.split(os.pathsep):
        if "platform-tools" in path and Path(path).is_dir():
            platform_tools_path = path
            break

    if not platform_tools_path:
        user_input = (
            input(
                "ADB was not found in your PATH environment variable. "
                "Would you like to download the latest version of SDK platform-tools? (y/n): "
            )
            .strip()
            .lower()
        )

        if user_input == "y":
            download_dir = input(
                "Enter the directory where platform-tools should be downloaded: "
            ).strip()
            download_dir = Path(download_dir).resolve()

            sdk_path = download_sdk_platform_tools(download_dir)
            if not sdk_path:
                raise RuntimeError("Failed to download SDK platform-tools.")

            os.environ["PATH"] += os.pathsep + str(sdk_path)
            print(f"Added '{sdk_path}' to the PATH environment variable.")
            return str(sdk_path)
        else:
            raise FileNotFoundError(
                "ADB commands cannot be executed because platform-tools is not in your PATH."
            )

    return platform_tools_path
