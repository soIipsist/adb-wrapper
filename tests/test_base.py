import unittest

from pprint import PrettyPrinter


class TestBase(unittest.TestCase):

    def setUp(self) -> None:
        self.logging = True
        self.extension = "json"
        self.pp = PrettyPrinter(indent=3)

    def log_data(self, *args, **kwargs):
        if self.logging:
            for d in args:
                print(d)

    @classmethod
    def generate_default_test_methods(self):
        methods = [
            method_name.replace("test_", "")
            for method_name in dir(self)
            if callable(getattr(self, method_name)) and method_name.startswith("test")
        ]
        return methods

    def assertAllTrue(self, iterable):
        """Assert that all elements in the iterable are True."""
        self.assertTrue(all(iterable), "Not all elements in the iterable are True")

    def assertAllFalse(self, iterable):
        """Assert that all elements in the iterable are False."""
        self.assertFalse(any(iterable), "Not all elements in the iterable are False")


def run_test_methods(test_methods: list):

    if callable(test_methods):
        test_methods = [test_methods]

    default_tests = []
    for test_method in test_methods:
        name = test_method.__name__
        class_name = test_method.__qualname__.split(".")[0]

        default_test = f"{class_name}.{name}"
        default_tests.append(default_test)

    unittest.main(defaultTest=default_tests)


if __name__ == "__main__":
    unittest.main()
