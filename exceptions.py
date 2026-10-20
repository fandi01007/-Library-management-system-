"""Custom exceptions for the library system."""


class LibraryError(Exception):
    """Base class for all library-related errors."""


class BookNotFoundError(LibraryError):
    pass


class MemberNotFoundError(LibraryError):
    pass


class DuplicateError(LibraryError):
    pass


class BookUnavailableError(LibraryError):
    pass


class BorrowLimitError(LibraryError):
    pass


class LoanNotFoundError(LibraryError):
    pass
