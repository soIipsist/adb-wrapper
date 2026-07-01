import pytest
import os
from adb_wrapper.adb import ADB, check_sdk_path, PackageType
from pprint import PrettyPrinter

pp = PrettyPrinter()
device = ADB().get_device()

def test_check_sdk_path():
    sdk_path = check_sdk_path()
    print(sdk_path)
 
def test_get_devices():
    devices = ADB().get_devices()
    
    for device in devices:
        print(device.get_model())

def test_get_device_settings():
   settings = device.get_settings()
   pp.pprint(settings)

@pytest.mark.integration
def test_set_device_setting():
    device.set_settings([f"system.screen_brightness=255", "system.window_animation_scale=0.5", "system.ui_night_mode=2", "system.stay_on_while_plugged_in=3", "system.volume_ring=8"])

def test_get_packages():
    packages = device.get_packages(PackageType.GOOGLE)
    pp.pprint(packages)

def test_install_package():
    package_path = os.environ.get("APK_PATH")
    assert os.path.exists(package_path)

    device.install_package(package_path)