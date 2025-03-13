import pytest

from core.utils.case_convertor import camel_case_to_snake_case


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("SomeSDK", "some_sdk"),
        ("RServoDrive", "r_servo_drive"),
        ("SDKDemo", "sdk_demo"),
        ("CamelCase", "camel_case"),
        ("SimpleTest", "simple_test"),
        ("ABC", "abc"),
        ("Test123", "test123"),
        ("", ""),
    ],
)
def test_camel_case_to_snake_case(input_str, expected):
    assert camel_case_to_snake_case(input_str) == expected
