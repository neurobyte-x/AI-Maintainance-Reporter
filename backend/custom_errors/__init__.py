class AppError(Exception):
    pass


class AuthError(AppError):
    pass


class ConflictError(AppError):
    pass


class ForbiddenError(AppError):
    pass


class NotFoundError(AppError):
    pass


class ValidationError(AppError):
    pass


class DatabaseError(AppError):
    pass
