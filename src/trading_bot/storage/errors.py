"""Storage exception taxonomy."""


class StorageError(RuntimeError):
    """Base error for durable local-storage failures."""


class AtomicWriteError(StorageError):
    """Raised when a local file cannot be atomically replaced."""


class StorageCommitError(StorageError):
    """Raised when a transaction cannot be durably committed."""


class StorageMigrationError(StorageError):
    """Raised when migration history cannot be applied or verified."""


class StorageTransactionError(StorageError):
    """Raised when a SQLite write transaction cannot begin."""