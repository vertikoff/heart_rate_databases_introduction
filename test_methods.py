import pytest


def test_is_user_tachycaric():
    from api import is_user_tachycaric
    case_one = is_user_tachycaric(10, 200)
    case_two = is_user_tachycaric(80, 80)
    case_three = is_user_tachycaric(6, 135)

    assert case_one is True
    assert case_two is False
    assert case_three is True


def test_is_email_valid():
    from api import is_email_valid
    case_one = is_email_valid("not_email")
    case_two = is_email_valid("email@domain.com")

    assert case_one is False
    assert case_two is True
