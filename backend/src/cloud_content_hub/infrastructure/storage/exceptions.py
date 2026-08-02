"""Stable storage failure vocabulary."""


class StorageError(Exception):
    """Base class for provider-neutral storage failures."""


StorageException = StorageError


class StorageValidationError(StorageError):
    pass


class UploadFailed(StorageError):
    pass


class DownloadFailed(StorageError):
    pass


class BlobNotFoundError(StorageError):
    pass


class BlobAlreadyExistsError(StorageError):
    pass


class ContainerNotFoundError(StorageError):
    pass


class StorageConditionError(StorageError):
    pass


class StorageAuthenticationError(StorageError):
    pass


class StorageTimeoutError(StorageError):
    pass


class StorageUnavailableError(StorageError):
    pass


class InvalidMimeTypeError(StorageValidationError):
    pass


class FileTooLargeError(StorageValidationError):
    pass


class ChecksumMismatchError(StorageValidationError):
    pass


class SASGenerationFailedError(StorageError):
    pass
