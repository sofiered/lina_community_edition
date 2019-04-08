from enum import Enum


class ErrorCodes(Enum):
    ADMIN_PERMISSION_REQUIRED = 917
    URI_TOO_LONG = 414


class VKException(Exception):
    def __init__(self, error_text: str, error_code: int) -> None:
        self.text = error_text
        self.code = error_code

    def __str__(self):
        return '%s: %s' % (self.code, self.text)

    def __repr__(self):
        return 'VKException: code: %s, %s' % (self.code, self.text)


class VkSendErrorException(Exception):
    pass
