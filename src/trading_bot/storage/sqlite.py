"""Fail-closed SQLite connection and transaction boundary."""

import json
import math
import re
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Final, cast

from trading_bot.storage.errors import (
    StorageCommitError,
    StorageError,
    StorageMigrationError,
    StorageTransactionError,
)

_MIGRATION_NAME_PATTERN: Final = re.compile(r"[a-z][a-z0-9_]*")
_MIGRATION_TABLE: Final = "schema_migrations"
_MIGRATION_DENIED_ACTIONS: Final = frozenset(
    {
        sqlite3.SQLITE_ATTACH,
        sqlite3.SQLITE_DETACH,
        sqlite3.SQLITE_PRAGMA,
        sqlite3.SQLITE_SAVEPOINT,
        sqlite3.SQLITE_TRANSACTION,
    }
)
_TRANSACTION_DENIED_ACTIONS: Final = frozenset(
    {
        sqlite3.SQLITE_ATTACH,
        sqlite3.SQLITE_DETACH,
        sqlite3.SQLITE_SAVEPOINT,
        sqlite3.SQLITE_TRANSACTION,
    }
)

type SQLiteValue = bytes | float | int | str | None
type SQLiteParameters = tuple[SQLiteValue, ...] | dict[str, SQLiteValue]


@dataclass(frozen=True, slots=True)
class Migration:
    """One immutable, ordered SQLite schema change."""

    version: int
    name: str
    statements: tuple[str, ...]

    def __post_init__(self) -> None:
        if isinstance(self.version, bool) or self.version < 1:
            raise ValueError("migration version must be a positive integer")
        if _MIGRATION_NAME_PATTERN.fullmatch(self.name) is None:
            raise ValueError("migration name must use lower_snake_case ASCII")
        if not self.statements:
            raise ValueError("migration must contain at least one statement")
        if any(not statement.strip() for statement in self.statements):
            raise ValueError("migration statements must not be blank")

    @property
    def checksum(self) -> str:
        canonical = json.dumps(
            {
                "name": self.name,
                "statements": self.statements,
                "version": self.version,
            },
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
        return sha256(canonical.encode("utf-8")).hexdigest()


def _migration_authorizer(
    action_code: int,
    first_argument: str | None,
    second_argument: str | None,
    database_name: str | None,
    trigger_name: str | None,
) -> int:
    del database_name, trigger_name
    touches_migration_history = _MIGRATION_TABLE in {first_argument, second_argument}
    if action_code in _MIGRATION_DENIED_ACTIONS or touches_migration_history:
        return sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_OK


def _transaction_authorizer(
    action_code: int,
    first_argument: str | None,
    second_argument: str | None,
    database_name: str | None,
    trigger_name: str | None,
) -> int:
    del database_name, trigger_name
    touches_migration_history = _MIGRATION_TABLE in {first_argument, second_argument}
    changes_pragma = action_code == sqlite3.SQLITE_PRAGMA and second_argument is not None
    changes_migration_history = (
        touches_migration_history and action_code != sqlite3.SQLITE_READ
    )
    if (
        action_code in _TRANSACTION_DENIED_ACTIONS
        or changes_pragma
        or changes_migration_history
    ):
        return sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_OK


class SQLiteTransaction:
    """Restricted SQL access inside a database-owned transaction."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.__connection = connection

    def _execute(
        self,
        statement: str,
        parameters: SQLiteParameters,
    ) -> sqlite3.Cursor:
        self.__connection.set_authorizer(_transaction_authorizer)
        try:
            return self.__connection.execute(statement, parameters)
        finally:
            self.__connection.set_authorizer(None)

    def execute(self, statement: str, parameters: SQLiteParameters = ()) -> None:
        """Execute one non-transaction-control statement."""

        cursor = self._execute(statement, parameters)
        cursor.close()

    def fetch_one(
        self,
        statement: str,
        parameters: SQLiteParameters = (),
    ) -> tuple[SQLiteValue, ...] | None:
        """Return one row without exposing the underlying connection."""

        cursor = self._execute(statement, parameters)
        try:
            return cast("tuple[SQLiteValue, ...] | None", cursor.fetchone())
        finally:
            cursor.close()

    def fetch_all(
        self,
        statement: str,
        parameters: SQLiteParameters = (),
    ) -> tuple[tuple[SQLiteValue, ...], ...]:
        """Return every row without exposing the underlying connection."""

        cursor = self._execute(statement, parameters)
        try:
            rows = cast("list[tuple[SQLiteValue, ...]]", cursor.fetchall())
            return tuple(rows)
        finally:
            cursor.close()


class SQLiteDatabase:
    """Create one configured connection for each explicit transaction."""

    def __init__(
        self,
        path: Path,
        migrations: tuple[Migration, ...] = (),
        *,
        timeout_seconds: float = 5.0,
    ) -> None:
        if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be finite and positive")
        expected_versions = tuple(range(1, len(migrations) + 1))
        actual_versions = tuple(migration.version for migration in migrations)
        if actual_versions != expected_versions:
            raise ValueError("migration versions must be ordered and contiguous from one")
        names = tuple(migration.name for migration in migrations)
        if len(set(names)) != len(names):
            raise ValueError("migration names must be unique")
        self._path = path
        self._migrations = migrations
        self._timeout_seconds = timeout_seconds

    def _connect(self) -> sqlite3.Connection:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(
            self._path,
            timeout=self._timeout_seconds,
            isolation_level=None,
        )
        try:
            connection.execute("PRAGMA foreign_keys = ON")
            journal_mode_row = cast(
                "tuple[str, ...]",
                connection.execute("PRAGMA journal_mode = WAL").fetchone(),
            )
            if str(journal_mode_row[0]).casefold() != "wal":
                raise StorageError("SQLite WAL mode is unavailable")
            connection.execute("PRAGMA synchronous = FULL")
            timeout_milliseconds = max(1, math.ceil(self._timeout_seconds * 1000))
            connection.execute(f"PRAGMA busy_timeout = {timeout_milliseconds}")
        except BaseException:
            connection.close()
            raise
        return connection

    def _read_migration_history(
        self,
        connection: sqlite3.Connection,
    ) -> tuple[tuple[int, str, str], ...]:
        try:
            rows = connection.execute(
                "SELECT version, name, checksum FROM schema_migrations ORDER BY version"
            ).fetchall()
        except sqlite3.Error as error:
            raise StorageMigrationError("SQLite schema is not initialized") from error
        return tuple((int(row[0]), str(row[1]), str(row[2])) for row in rows)

    def _verify_migration_history(self, connection: sqlite3.Connection) -> int:
        applied = self._read_migration_history(connection)
        if len(applied) > len(self._migrations):
            raise StorageMigrationError("database schema is newer than the configured migrations")
        for index, applied_migration in enumerate(applied):
            expected = self._migrations[index]
            expected_record = (expected.version, expected.name, expected.checksum)
            if applied_migration != expected_record:
                raise StorageMigrationError("applied migration history does not match source")
        user_version_row = cast(
            "tuple[int, ...]",
            connection.execute("PRAGMA user_version").fetchone(),
        )
        user_version = int(user_version_row[0])
        current_version = len(applied)
        if user_version != current_version:
            raise StorageMigrationError("SQLite user_version disagrees with migration history")
        return current_version

    def migrate(self) -> tuple[int, ...]:
        """Apply each pending migration once and return the applied versions."""

        applied_versions: list[int] = []
        try:
            with self._transaction(verify_schema=False) as connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        version INTEGER PRIMARY KEY CHECK (version > 0),
                        name TEXT NOT NULL UNIQUE,
                        checksum TEXT NOT NULL CHECK (length(checksum) = 64)
                    ) STRICT
                    """
                )
                current_version = self._verify_migration_history(connection)
                for migration in self._migrations[current_version:]:
                    connection.set_authorizer(_migration_authorizer)
                    try:
                        for statement in migration.statements:
                            connection.execute(statement)
                    finally:
                        connection.set_authorizer(None)
                    connection.execute(
                        """
                        INSERT INTO schema_migrations (version, name, checksum)
                        VALUES (?, ?, ?)
                        """,
                        (migration.version, migration.name, migration.checksum),
                    )
                    applied_versions.append(migration.version)
                connection.execute(f"PRAGMA user_version = {len(self._migrations)}")
                self._verify_migration_history(connection)
        except StorageError:
            raise
        except sqlite3.Error as error:
            raise StorageMigrationError("SQLite migration failed") from error
        return tuple(applied_versions)

    @contextmanager
    def _transaction(self, *, verify_schema: bool) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            try:
                connection.execute("BEGIN IMMEDIATE")
            except sqlite3.Error as error:
                raise StorageTransactionError("SQLite write transaction could not begin") from error
            try:
                if verify_schema:
                    current_version = self._verify_migration_history(connection)
                    if current_version != len(self._migrations):
                        raise StorageMigrationError("pending SQLite migrations must be applied")
                yield connection
            except BaseException:
                connection.rollback()
                raise
            try:
                connection.commit()
            except sqlite3.Error as error:
                try:
                    connection.rollback()
                finally:
                    raise StorageCommitError("SQLite transaction commit failed") from error
        finally:
            connection.close()

    @contextmanager
    def transaction(self) -> Iterator[SQLiteTransaction]:
        """Commit all statements together against the current schema."""

        with self._transaction(verify_schema=True) as connection:
            yield SQLiteTransaction(connection)