from adb.adb import ADB, Device

apk_dirs = ['C:/Desktop/apk.apk','C:/Desktop/package.apk']
packages = ['com.example.package','com.example.package2']
permissions = ["android.permission.CAMERA"]

adb = ADB()

# get all available devices
devices = adb.get_devices()

# execute adb command
output = adb.execute('devices -l')

# which is the same as executing
output = adb.execute(['devices', '-l'])

# get packages from list
packages = adb.get_packages_from_json('lists/google.json', key='package_name')

# download sdk platform-tools (can be used if adb is not installed on your device)
from adb.adb import download_sdk_platform_tools
download_sdk_platform_tools()

device: Device
for device in devices:
    # get device details
    print(device.get_model())
    print(device.get_name())
    print(device.get_sdk())
    
    # get packages
    print(device.get_system_packages())
    print(device.get_third_party_packages())
    print(device.get_packages())
    
    # get settings 
    # adb lists device settings based on namespace value (system, global or secure)
    print(device.get_system_settings())
    print(device.get_global_settings())
    print(device.get_secure_settings())
    print(device.get_settings()) # returns a dictionary of namespaces and their values
    
    # set settings
    settings = [ "global.user_switcher_enabled=0", "secure.lock_screen_show_notifications=0"]
    # format can be:
    # a) namespace.key=value
    # b) namespace.key value
    # c) namespace.key.other_value value  
    device.set_settings(settings)
    
    
    # device backup
    # adb device backup, with flags
    device.backup(shared_storage=False, apks=False, system=False, path='C:/Desktop/backup.ab')
    
    # device restore
    device.restore('C:/Desktop/backup.ab')
    
    # install packages (accepts list of apk directories)
    device.install_packages(apk_dirs)
    device.install_package(apk_dirs[0])
    
    # uninstall packages (accepts list of package names)
    # you can also set do not delete packages
    device.do_not_delete_packages = ['com.example.pkg']
    device.uninstall_packages(packages)
    device.uninstall_package(packages[0])
    
    # google debloat (uninstalls google packages, as defined in a google.json list)
    device.google_debloat()
    
    # expand notification bar
    device.expand_notifications()
    
    # set home app
    device.set_home_app(packages[0])
    
    # execute touch event
    device.execute_touch_event(100,100) # x and y coordinates
    
    # disable lock screen
    device.disable_lock_screen()
    
    # grant/revoke permissions
    device.grant_permissions(packages[0], permissions)
    device.grant_permission(packages[0], permissions[0])
    device.revoke_permissions(packages[0], permissions)
    device.revoke_permission(packages[0], permissions[0])
    
    # enable/disable wifi
    device.enable_wifi()
    device.disable_wifi()
    
    # enable/disable mobile data
    device.enable_mobile_data()
    device.disable_mobile_data()
    
    # set device password
    device.set_password('1234')
    
    # clear device password
    device.clear_password('1234') # previous password is required
    
    # pull files (device to pc)
    device.pull_files(['/sdcard/example.txt', '/sdcard/example2.txt'],'C:/Desktop')
    device.pull_file('/sdcard/example2.txt','C:/Desktop')
    
    # push files (pc to device)
    device.push_files(['C:/example.txt', 'C:/example2.txt'], '/sdcard/')
    device.push_file('C:/example.txt', '/sdcard/')