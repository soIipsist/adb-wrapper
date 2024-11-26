import json
import mimetypes
import os
from pathlib import Path
import shutil
import platform
import urllib.request


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
    sdk_path = download_file_from_link(download_link)
    return sdk_path


def set_environment_variable(sdk_path: str):
    if os.name == "nt":  # Windows
        os.environ["PATH"] += f";{sdk_path}"
    else:  # macOS/Linux
        os.environ["PATH"] += f":{sdk_path}"

    print(f"Added '{sdk_path}' to the PATH environment variable.")


def check_sdk_path():
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

            default_dir = Path.home()
            download_dir = input(
                f"Enter the directory where platform-tools should be downloaded (default: {default_dir}): "
            ).strip()
            download_dir = Path(download_dir).resolve() if download_dir else default_dir

            sdk_path = download_sdk_platform_tools(download_dir)
            if not sdk_path:
                raise RuntimeError("Failed to download SDK platform-tools.")

            set_environment_variable(sdk_path)
            return str(sdk_path)
        else:
            raise FileNotFoundError(
                "ADB commands cannot be executed because platform-tools is not in your PATH."
            )

    return platform_tools_path


def load_env(file_path=".env"):
    """
    Load environment variables from a .env file into the process environment.
    Also supports arrays if values are comma-separated.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The .env file at {file_path} was not found.")

    env_vars = {}

    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            key, sep, value = line.partition("=")
            if sep:
                key = key.strip()
                value = value.strip()

                if "," in value:
                    env_vars[key] = [item.strip() for item in value.split(",")]
                else:
                    env_vars[key] = value

                os.environ[key] = value

    return env_vars


def download_file_from_link(download_link, output_path=None):
    """
    Download a file from a given link and save it to the specified output path.
    If the file is an archive, it is automatically extracted, and the extracted path is returned.
    """

    try:
        if output_path is None:
            output_directory = os.path.expanduser("~")
            file_name = os.path.basename(download_link)
            output_path = os.path.join(output_directory, file_name)
        else:
            output_directory = os.path.dirname(output_path)
            file_name = os.path.basename(output_path)

        os.makedirs(output_directory, exist_ok=True)

        print(f"Downloading file from {download_link} to {output_path}...")
        with urllib.request.urlopen(download_link) as response:
            with open(output_path, "wb") as out_file:
                shutil.copyfileobj(response, out_file)

        print(f"File downloaded at: {output_path}")

        # Check if the file is an archive and extract it
        mime_type, _ = mimetypes.guess_type(output_path)
        if mime_type in ["application/zip", "application/x-tar", "application/gzip"]:
            print("Extracting the archive...")
            extracted_dir = os.path.join(
                output_directory, os.path.splitext(file_name)[0]
            )
            shutil.unpack_archive(output_path, extracted_dir)
            os.remove(output_path)
            print(f"File extracted to: {extracted_dir}")
            return extracted_dir

        return output_path
    except Exception as e:
        print(f"An error occurred while downloading or extracting the file: {e}")
        return None
