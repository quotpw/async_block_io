from typing import Optional


class BlockIo(Exception):
    pass


class InvalidResponse(BlockIo):
    pass


class UnknownError(BlockIo):
    pass


class Throttle(BlockIo):
    pass


class InternalError(BlockIo):
    pass


class ApiError(BlockIo):
    error: Optional[dict] = None
