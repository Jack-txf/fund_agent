class AppError(Exception):
    pass


class BadRequestError(AppError):
    pass


class NotFoundError(AppError):
    pass


class ConflictError(AppError):
    pass
