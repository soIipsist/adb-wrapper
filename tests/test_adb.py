from pprint import PrettyPrinter
from test_base import TestBase, run_test_methods
from adb.adb import ADB, Device

adb = ADB()


class TestAdb(TestBase):

    def setUp(self) -> None:
        super().setUp()

    def test_get_devices(self):
        print("hi")

    def test_check_adb_path(self):
        print("he")
        # adb.check_adb_path()

    def test_execute_command(self):
        pass


if __name__ == "__main__":
    test_methods = [TestAdb.test_get_devices, TestAdb.test_check_adb_path]
    run_test_methods(test_methods)
