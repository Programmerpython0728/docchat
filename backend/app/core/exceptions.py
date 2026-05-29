"""
Application-specific exceptions.

Bu yerda biznes logikamiz uchun maxsus exception lar.
HTTP layer'da ular HTTPException'ga aylantiriladi (exception_handler orqali).
"""
from fastapi import status


class DocChatException(Exception):
    """Bosh exception. Hammasi shundan meros oladi."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "Server ichki xatosi"

    def __init__(self, detail: str | None = None):
        if detail:
            self.detail = detail
        super().__init__(self.detail)


# === Auth exceptions ===
class UserNotFoundError(DocChatException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Foydalanuvchi topilmadi"


class InvalidCredentialsError(DocChatException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Email yoki parol noto'g'ri"


class EmailAlreadyExistsError(DocChatException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Bu email allaqachon ro'yxatdan o'tgan"


# === Document exceptions ===
class DocumentNotFoundError(DocChatException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Hujjat topilmadi"


class FileTooLargeError(DocChatException):
    status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    detail = "Fayl hajmi juda katta"


class UnsupportedFileTypeError(DocChatException):
    status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    detail = "Qo'llab-quvvatlanmaydigan fayl turi"


# === Chat exceptions ===
class ChatNotFoundError(DocChatException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Suhbat topilmadi"


# === Rate limit ===
class RateLimitExceededError(DocChatException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = "So'rovlar soni chegaradan oshdi, biroz kuting"
