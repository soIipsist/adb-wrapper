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


def set_environment_variable(sdk_path: str, set_globally: bool = False):
    if set_globally:
        set_path_env_variable_globally()
    else:
        if os.name == "nt":  # Windows
            os.environ["PATH"] += f";{sdk_path}"
        else:  # macOS/Linux
            os.environ["PATH"] += f":{sdk_path}"

    print(f"Added '{sdk_path}' to the PATH environment variable.")


def set_path_env_variable_globally(value, shell_restart_required=True):
    """
    Sets an environment variable globally, not just for the current process.

    """

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

        # Notify about shell restart if needed
        if shell_restart_required:
            print(
                f"To apply the changes globally, restart your terminal or run `source ~/.bashrc` "
                f"(or equivalent for your shell)."
            )

        return True
    except Exception as e:
        print(f"An error occurred while setting the environment variable: {e}")
        return False


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
