from adb_wrapper.adb import Device


def extract_firmware(device: Device):
    # model = device.get_model()
    region_code = device.get_region_code()
    print(region_code)
    # print(region, model)
