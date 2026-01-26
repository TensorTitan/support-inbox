import os


def test_required_environment_variables_defined():
    os.environ.setdefault("JWT_SECRET", "test-secret")
    os.environ.setdefault("JWT_EXPIRE_MINUTES", "60")


    assert os.environ["JWT_SECRET"] is not None
    assert int(os.environ["JWT_EXPIRE_MINUTES"]) > 0