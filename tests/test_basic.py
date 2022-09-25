from my_python_api import add

def test_add():
    assert add(1, 2) == 3
    assert add(5, -2) == 3
    assert add(3, 0) == 3
