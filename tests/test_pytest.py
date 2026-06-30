import pytest
from adb_wrapper.utils import load_env

@pytest.mark.integration
def test_get_device():
    loaded = load_env()
    print(loaded)

def test_get():
    loaded = load_env()
    print(loaded)
