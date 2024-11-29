# adb-wrapper

A Python ADB wrapper for executing commands on multiple devices. This tool can be used to uninstall pre-installed Google Play Store packages, adjust device settings and package permissions, back up data, install APK files, and perform rooting operations.

## Prerequisites

To use `adb` as a command, you need to install SDK platform-tools and add it to your `PATH` variable.

- Download [SDK Platform-Tools for Windows](https://dl.google.com/android/repository/platform-tools-latest-windows.zip)
- Download [SDK Platform-Tools for Linux](https://dl.google.com/android/repository/platform-tools-latest-linux.zip)
- [Add ADB to your PATH variable](https://www.xda-developers.com/adb-fastboot-any-directory-windows-linux/)

To check if adb was installed properly, you can run:

```Shell
$ adb version
Android Debug Bridge version 1.0.41
```

## Installation

### Pip (Linux, Windows)

```bash
pip install git+https://github.com/soIipsist/adb-wrapper@main
```

### Manual installation

Clone the git repository:

```bash
git clone https://github.com/soIipsist/adb-wrapper@main
```

## Usage

### Example

```Python
from adb_wrapper import ADB, Device

adb = ADB()
devices = adb.get_devices()

# get packages from list
packages = ['com.example.package','com.example.package2']

device: Device
for device in devices:
    device.install_package('C:/package.apk')
    device.uninstall_packages(packages)
    device.google_debloat()
```

See [commands.py](https://github.com/soIipsist/adb-wrapper/blob/main/examples/commands.py) for an example script showcasing all supported commands.
