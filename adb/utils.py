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
    output_path = os.path.join(output_directory, os.path.basename(download_link))

    print("SDK path set to: ", output_path)
    sdk_path = download_file_from_link(download_link, output_path)
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
                subprocess.run(["setx", key, value], check=True)
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
                        f.write(f'\nexport PATH="{os.getenv("PATH")}:{value}"\n')

                    print(f"PATH variable updated in {config_file}.")
                else:
                    raise FileNotFoundError(
                        "Shell configuration file could not be determined."
                    )

            try:
                subprocess.run(["source", f"{config_file}"], check=True)
            except Exception as e:
                print(e)

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
        if mime_type in ["application/zip", "application/x-tar", "application/gzip"]:
            print("Extracting the archive...")
            extracted_dir = os.path.join(
                output_directory, os.path.splitext(os.path.basename(output_path))[0]
            )
            shutil.unpack_archive(output_path, extracted_dir)
            os.remove(output_path)
            print(f"File extracted to: {extracted_dir}")
            return extracted_dir

        return output_path
    except Exception as e:
        print(f"An error occurred while downloading or extracting the file: {e}")
        return None
