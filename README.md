# adb-wrapper

A Python ADB wrapper for executing commands on multiple devices. This tool can be used to uninstall pre-installed Google Play Store packages, store device settings, modify package permissions, backup devices and install APK files.

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
pip install git+https://github.com/soIipsis/adb-wrapper@main
```

### Manual installation

1. Clone the git repository:

```bash
git clone https://github.com/soIipsis/adb-wrapper@main
```

2. Install all package dependencies:

```bash
pip install -r requirements.txt
```

## Usage

#### Example

```Python
from adb.adb import ADB, Device

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

See [commands.py](https://github.com/soIipsis/adb-wrapper/blob/main/examples/commands.py) for an example script showcasing all supported commands.
