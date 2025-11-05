class AppError(Exception):
    def __init__(self, code: int, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(detail)


class Unauthorized(AppError):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(code=401, detail=detail)


class Forbidden(AppError):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(code=403, detail=detail)


class NotFound(AppError):
    def __init__(self, detail: str = "Not Found"):
        super().__init__(code=404, detail=detail)


class Conflict(AppError):
    def __init__(self, detail: str = "Conflict"):
        super().__init__(code=409, detail=detail)
