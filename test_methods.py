import pytest
from api import is_user_tachycaric


def test_is_user_tachycaric():
    case_one = is_user_tachycaric(10, 200)
    case_two = is_user_tachycaric(80, 80)
    case_three = is_user_tachycaric(6, 135)

    assert case_one is True
    assert case_two is False
    assert case_three is True
