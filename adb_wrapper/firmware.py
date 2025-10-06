from adb_wrapper.adb import Device


def extract_firmware(device: Device):
    region_code = device.get_region_code()
    model = device.get_model()
    vendor = device.get_vendor()

    if vendor == "samsung":
        return get_samsung_firmware(model, region_code)
    elif vendor == "google":
        return get_google_firmware(model)
    elif vendor in ["xiaomi", "redmi", "poco"]:
        return get_xiaomi_firmware(model)
    elif vendor in ["oneplus", "oppo", "realme"]:
        return get_oneplus_firmware(model)
    else:
        raise NotImplementedError(
            f"Firmware extraction not supported for vendor: {vendor}"
        )


def get_google_firmware(model):
    url = "https://developers.google.com/android/images"
    return {"vendor": "google", "model": model, "url": url}


def get_samsung_firmware(model: str, region_code: str):
    print("SAMS")


def get_xiaomi_firmware():
    pass


def get_oneplus_firmware():
    pass
