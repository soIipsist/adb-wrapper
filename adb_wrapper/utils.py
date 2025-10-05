import json
import mimetypes
import os
from pathlib import Path
import shutil
import platform
import subprocess
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

    output_directory = os.path.join(output_directory, "platform-tools.zip")
    sdk_path = download_file_from_link(download_link, output_directory)
    return sdk_path


def find_variable_in_path(value: str):
    path_variable = os.environ.get("PATH", "")
    path_variable = path_variable.split(os.pathsep)
    variable = None
    for path in path_variable:
        normalized_path = os.path.normpath(path)
        if value == os.path.basename(normalized_path) or value == path:
            variable = path
            break
    return variable


def set_path_environment_variable(value: str, set_globally: bool = False):
    """Sets sdk path as a PATH environment variable."""

    if set_globally:
        try:
            if os.name == "nt":
                print("Setting globally.")
                current_path = os.environ.get("PATH", "")
                updated_path = f"{current_path};{value}"
                subprocess.run(["setx", "PATH", updated_path], check=True)
            else:
                # Modify shell configuration files for macOS or Linux
                home_dir = os.path.expanduser("~")
                shell = os.getenv("SHELL", "/bin/bash")
                config_file = None

                # Determine the shell configuration file
                if shell.endswith("bash"):
                    config_file = os.path.join(home_dir, ".bashrc")
                elif shell.endswith("zsh"):
                    config_file = os.path.join(home_dir, ".zshrc")
                elif shell.endswith("fish"):
                    config_file = os.path.join(home_dir, ".config/fish/config.fish")
                else:
                    raise EnvironmentError(f"Unsupported shell: {shell}")

                if config_file:
                    with open(config_file, "a") as f:
                        f.write(f'\nexport PATH="{value}:$PATH"\n')

                    prompt = input(
                        f"PATH variable was updated in {config_file}. Would you like to execute it? (y/n)"
                    )

                    if prompt == "y":
                        subprocess.run(
                            f"source {config_file}",
                            shell=True,
                            check=True,
                            cwd=home_dir,
                        )
                        print("Sourced config file successfully.")

                    else:
                        os.environ["PATH"] = f"{value}:$PATH"
                else:
                    raise FileNotFoundError(
                        "Shell configuration file could not be determined."
                    )

        except Exception as e:
            print(f"An error occurred while setting the environment variable: {e}")

    else:
        if os.name == "nt":  # Windows
            os.environ["PATH"] += f";{value}"
        else:  # macOS/Linux
            os.environ["PATH"] += f":{value}"

    print(f"Added '{value}' to the PATH environment variable.")


def load_env(file_path=".env"):
    """
    Load environment variables from a .env file into the process environment.
    Also supports arrays if values are comma-separated.
    """
    env_vars = {}

    if not os.path.exists(file_path):
        print(f"The .env file at {file_path} was not found.")
        return env_vars

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


def make_executable(file_path):
    try:
        system = platform.system()

        # Adjust for .exe extension on Windows
        if system == "Windows" and not os.path.exists(file_path):
            file_path += ".exe"

        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

        # Make file executable only on Unix-like systems
        if system != "Windows":
            os.chmod(file_path, 0o755)
            print(f"{file_path} is now executable.")
        else:
            pass
    except Exception as e:
        print(f"Error making {file_path} executable: {e}")


def download_file_from_link(download_link, output_path=None):
    """
    Download a file from a given link and save it to the specified output path.
    Archived or zipped files are extracted, and returned as extracted paths.
    """
    try:
        # Determine the output path and directory
        if output_path is None:
            output_directory = os.getcwd()
            file_name = os.path.basename(download_link)
            output_path = os.path.join(output_directory, file_name)
        else:
            output_directory = os.path.dirname(output_path)
            if not output_directory:  # Handle cases like "sample.zip"
                output_directory = os.getcwd()
                output_path = os.path.join(output_directory, output_path)

        os.makedirs(output_directory, exist_ok=True)

        print(f"Downloading file from {download_link} to {output_path}...")

        with urllib.request.urlopen(download_link) as response:
            with open(output_path, "wb") as out_file:
                shutil.copyfileobj(response, out_file)

        print(f"File downloaded at: {output_path}")

        mime_type, _ = mimetypes.guess_type(output_path)
        # print("MIME", mime_type, output_path)

        if mime_type in [
            "application/zip",
            "application/x-tar",
            "application/gzip",
        ] or output_path.endswith(".zip"):

            print("Extracting the archive...")
            extracted_dir = os.path.join(
                output_directory, os.path.splitext(os.path.basename(output_path))[0]
            )
            shutil.unpack_archive(output_path, extracted_dir)
            os.remove(output_path)
            print(f"File extracted to: {extracted_dir}")

            # Handle nested folders (e.g., platform-tools/platform-tools)
            contents = os.listdir(extracted_dir)
            if len(contents) == 1:
                nested_path = os.path.join(extracted_dir, contents[0])
                if os.path.isdir(nested_path):
                    print("Detected nested folder, flattening structure...")
                    for item in os.listdir(nested_path):
                        shutil.move(os.path.join(nested_path, item), extracted_dir)
                    shutil.rmtree(nested_path)

            return extracted_dir

        return output_path
    except Exception as e:
        print(f"An error occurred while downloading or extracting the file: {e}")
        return None


def check_sdk_path():
    """
    Checks if 'platform-tools' exists in the PATH environment variable.
    Prompts the user to download it if not found and returns the platform-tools directory.
    """

    sdk_path = find_variable_in_path("platform-tools")

    if not sdk_path or not os.path.exists(
        sdk_path
    ):  # download sdk platform tools, if adb doesn't exist in PATH
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

            set_path_environment_variable(sdk_path, False)

            # grant permissions to adb and fastboot
            adb_path = os.path.join(sdk_path, "adb")
            fastboot_path = os.path.join(sdk_path, "fastboot")
            make_executable(adb_path)
            make_executable(fastboot_path)
            return str(sdk_path)

    return sdk_path


def is_valid_command(base_cmd, command_checked: bool):
    if base_cmd not in {"adb", "fastboot"}:
        raise ValueError(f"Unsupported command '{base_cmd}'.")

    sdk_path = None

    if not command_checked:
        sdk_path = check_sdk_path()
        command_checked = shutil.which(base_cmd) is not None

    return command_checked, sdk_path


def get_magisk_url():
    api_url = "https://api.github.com/repos/topjohnwu/Magisk/releases/latest"

    request = urllib.request.Request(api_url)
    with urllib.request.urlopen(request, timeout=10) as response:
        data = json.load(response)
        assets = data.get("assets", [])

        for asset in assets:
            name = asset.get("name", "")
            url = asset.get("browser_download_url", "")
            if name.lower().endswith(".apk") and url:
                return url

    return (
        "https://github.com/topjohnwu/Magisk/releases/download/v29.0/Magisk-v29.0.apk"
    )
