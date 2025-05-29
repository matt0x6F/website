from ninja import Schema


class ValidationErrorResponse(Schema):
    detail: str
