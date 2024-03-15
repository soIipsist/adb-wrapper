from adb.adb import ADB, Device
import argparse
import os

""" A sample script that was tested on Lenovo Tab E10 tablets """

def is_valid_file(parser:argparse.ArgumentParser, arg:str):
    if not os.path.exists(arg):
        parser.error("Path %s does not exist!" % arg)
    elif not arg.endswith('.apk'):
        parser.error("Invalid path extension")
    else:
        return arg 


parser = argparse.ArgumentParser()
parser.add_argument("path", type=lambda x: is_valid_file(parser, x))

args = vars(parser.parse_args())
path = args['path']

adb = ADB()
device:Device
for device in adb.get_devices():
    # get device model
    print(device.get_model())
    device.do_not_delete_packages = []
 
    device.set_settings(["global.heads_up_notifications_enabled=0",
                         "global.slide_down_notificationcenter_when_locked=0", 
                         "global.install_non_market_apps=1",
                        "system.screen_off_timeout=600000",
                        "secure.lock_screen_allow_private_notifications=0",
                        "secure.lock_screen_show_notifications=0",
                        "global.user_switcher_enabled=0",
                        "secure.location_mode=0"
                        ])
    
    device.google_debloat()
    device.install_package(path)
    device.disable_lock_screen()
    device.disable_wifi()
    device.enable_mobile_data()
    device.grant_permission("com.example.example","android.permission.WRITE_EXTERNAL_STORAGE")
    device.set_home_app("com.example.example")
    device.uninstall_packages(["com.tblenovo.launcher"])