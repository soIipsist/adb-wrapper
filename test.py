from adb.adb import Device,ADB

adb = ADB()
devices = adb.get_devices()
device:Device
for device in devices:
    # device.push_files('')
    pass
