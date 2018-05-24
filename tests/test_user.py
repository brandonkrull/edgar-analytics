from src.processor import User

def test_user():
    u = User('389247324')

    assert u.ip == u.ip
