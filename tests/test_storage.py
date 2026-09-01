import os
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Self

import pytest

from trading_bot.storage import (
    AtomicWriteError,
    Migration,
    SQLiteDatabase,
    StorageCommitError,
    StorageError,
    StorageMigrationError,
    StorageTransactionError,
    atomic_write_bytes,
    atomic_write_text,
)

CONSTRAINT_MIGRATION = Migration(
    version=1,
    name="constraint_tables",
    statements=(
        "CREATE TABLE parent (id INTEGER PRIMARY KEY)",
        """
        CREATE TABLE child (
            id INTEGER PRIMARY KEY,
            parent_id INTEGER NOT NULL,
            FOREIGN KEY (parent_id) REFERENCES parent (id)
                DEFERRABLE INITIALLY DEFERRED
        )
        """,
    ),
)


def test_commit_failure_rolls_back_deferred_constraint_write(tmp_path: Path) -> None:
    database = SQLiteDatabase(
        tmp_path / "state" / "trading.sqlite",
        (CONSTRAINT_MIGRATION,),
    )
    assert database.migrate() == (1,)

    with pytest.raises(StorageCommitError) as error_info, database.transaction() as connection:
        connection.execute("INSERT INTO child (id, parent_id) VALUES (1, 99)")

    assert isinstance(error_info.value.__cause__, sqlite3.IntegrityError)
    with database.transaction() as connection:
        row = connection.fetch_one("SELECT COUNT(*) FROM child")
    assert row == (0,)


def test_migrations_apply_in_order_and_replay_without_rewriting_history(
    tmp_path: Path,
) -> None:
    migrations = (
        Migration(
            version=1,
            name="create_records",
            statements=(
                "CREATE TABLE records (id INTEGER PRIMARY KEY, value TEXT NOT NULL)",
            ),
        ),
        Migration(
            version=2,
            name="seed_record",
            statements=("INSERT INTO records (id, value) VALUES (1, 'original')",),
        ),
    )
    database_path = tmp_path / "state.sqlite"
    database = SQLiteDatabase(database_path, migrations)

    assert database.migrate() == (1, 2)
    assert database.migrate() == ()

    reopened = SQLiteDatabase(database_path, migrations)
    assert reopened.migrate() == ()
    with reopened.transaction() as connection:
        record = connection.fetch_one("SELECT id, value FROM records")
        history = connection.fetch_all(
            "SELECT version, name, checksum FROM schema_migrations ORDER BY version"
        )
        user_version = connection.fetch_one("PRAGMA user_version")

    assert record == (1, "original")
    assert history == (
        (1, "create_records", migrations[0].checksum),
        (2, "seed_record", migrations[1].checksum),
    )
    assert user_version == (2,)


def test_changed_applied_migration_is_refused(tmp_path: Path) -> None:
    database_path = tmp_path / "state.sqlite"
    original = Migration(
        version=1,
        name="create_records",
        statements=("CREATE TABLE records (id INTEGER PRIMARY KEY)",),
    )
    assert SQLiteDatabase(database_path, (original,)).migrate() == (1,)
    changed = Migration(
        version=1,
        name="create_records",
        statements=("CREATE TABLE records (id INTEGER PRIMARY KEY, value TEXT)",),
    )

    with pytest.raises(StorageMigrationError, match="does not match source"):
        SQLiteDatabase(database_path, (changed,)).migrate()


def test_failed_migration_rolls_back_schema_and_history(tmp_path: Path) -> None:
    database_path = tmp_path / "state.sqlite"
    broken = Migration(
        version=1,
        name="create_records",
        statements=(
            "CREATE TABLE records (id INTEGER PRIMARY KEY)",
            "INSERT INTO missing_table (id) VALUES (1)",
        ),
    )

    with pytest.raises(StorageMigrationError, match="migration failed"):
        SQLiteDatabase(database_path, (broken,)).migrate()

    corrected = Migration(
        version=1,
        name="create_records",
        statements=("CREATE TABLE records (id INTEGER PRIMARY KEY)",),
    )
    assert SQLiteDatabase(database_path, (corrected,)).migrate() == (1,)


def test_invalid_migration_definitions_are_rejected() -> None:
    with pytest.raises(ValueError, match="positive integer"):
        Migration(version=True, name="invalid_version", statements=("SELECT 1",))
    with pytest.raises(ValueError, match="positive integer"):
        Migration(version=0, name="invalid_version", statements=("SELECT 1",))
    with pytest.raises(ValueError, match="lower_snake_case"):
        Migration(version=1, name="Invalid-Name", statements=("SELECT 1",))
    with pytest.raises(ValueError, match="at least one"):
        Migration(version=1, name="empty", statements=())
    with pytest.raises(ValueError, match="must not be blank"):
        Migration(version=1, name="blank", statements=(" ",))


@pytest.mark.parametrize("timeout_seconds", [0.0, -1.0, float("nan"), float("inf")])
def test_invalid_database_timeout_is_rejected(timeout_seconds: float) -> None:
    with pytest.raises(ValueError, match="finite and positive"):
        SQLiteDatabase(Path("state.sqlite"), timeout_seconds=timeout_seconds)


def test_migration_sequence_and_names_must_be_unambiguous() -> None:
    first = Migration(version=1, name="same_name", statements=("SELECT 1",))
    second = Migration(version=2, name="same_name", statements=("SELECT 2",))
    gap = Migration(version=2, name="gap", statements=("SELECT 2",))

    with pytest.raises(ValueError, match="ordered and contiguous"):
        SQLiteDatabase(Path("state.sqlite"), (gap,))
    with pytest.raises(ValueError, match="names must be unique"):
        SQLiteDatabase(Path("state.sqlite"), (first, second))


def test_transaction_requires_initialized_and_current_schema(tmp_path: Path) -> None:
    database_path = tmp_path / "state.sqlite"
    first = Migration(
        version=1,
        name="create_records",
        statements=("CREATE TABLE records (id INTEGER PRIMARY KEY)",),
    )
    second = Migration(
        version=2,
        name="add_value",
        statements=("ALTER TABLE records ADD COLUMN value TEXT",),
    )

    with pytest.raises(StorageMigrationError, match="not initialized"), SQLiteDatabase(
        database_path,
        (first,),
    ).transaction():
        pass

    assert SQLiteDatabase(database_path, (first,)).migrate() == (1,)
    with pytest.raises(StorageMigrationError, match="pending"), SQLiteDatabase(
        database_path,
        (first, second),
    ).transaction():
        pass


def test_newer_schema_and_tampered_user_version_are_refused(tmp_path: Path) -> None:
    database_path = tmp_path / "state.sqlite"
    first = Migration(
        version=1,
        name="create_records",
        statements=("CREATE TABLE records (id INTEGER PRIMARY KEY)",),
    )
    second = Migration(
        version=2,
        name="add_value",
        statements=("ALTER TABLE records ADD COLUMN value TEXT",),
    )
    assert SQLiteDatabase(database_path, (first, second)).migrate() == (1, 2)

    with pytest.raises(StorageMigrationError, match="newer"):
        SQLiteDatabase(database_path, (first,)).migrate()

    with closing(sqlite3.connect(database_path, isolation_level=None)) as connection:
        connection.execute("PRAGMA user_version = 1")
    with pytest.raises(StorageMigrationError, match="user_version disagrees"):
        SQLiteDatabase(database_path, (first, second)).migrate()


@pytest.mark.parametrize("statement", ["COMMIT", "DELETE FROM schema_migrations"])
def test_migration_cannot_escape_transaction_or_rewrite_history(
    tmp_path: Path,
    statement: str,
) -> None:
    migration = Migration(version=1, name="forbidden", statements=(statement,))

    with pytest.raises(StorageMigrationError, match="migration failed"):
        SQLiteDatabase(tmp_path / f"{statement[:3]}.sqlite", (migration,)).migrate()


def test_multi_statement_migration_is_rejected_atomically(tmp_path: Path) -> None:
    migration = Migration(
        version=1,
        name="multiple_statements",
        statements=("CREATE TABLE first (id INTEGER); CREATE TABLE second (id INTEGER)",),
    )

    with pytest.raises(StorageMigrationError, match="migration failed") as error_info:
        SQLiteDatabase(tmp_path / "state.sqlite", (migration,)).migrate()

    assert isinstance(error_info.value.__cause__, sqlite3.ProgrammingError)


def test_wal_unavailable_is_refused() -> None:
    with pytest.raises(StorageError, match="WAL mode is unavailable"):
        SQLiteDatabase(Path(":memory:")).migrate()


def test_caller_error_rolls_back_the_transaction(tmp_path: Path) -> None:
    migration = Migration(
        version=1,
        name="create_records",
        statements=("CREATE TABLE records (id INTEGER PRIMARY KEY)",),
    )
    database = SQLiteDatabase(tmp_path / "state.sqlite", (migration,))
    database.migrate()

    with pytest.raises(LookupError, match="stop"), database.transaction() as connection:
        connection.execute("INSERT INTO records (id) VALUES (1)")
        raise LookupError("stop")

    with database.transaction() as connection:
        row = connection.fetch_one("SELECT COUNT(*) FROM records")
    assert row == (0,)


def test_transactions_enforce_required_sqlite_pragmas(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "state.sqlite", timeout_seconds=0.25)
    database.migrate()

    with database.transaction() as connection:
        foreign_keys = connection.fetch_one("PRAGMA foreign_keys")
        journal_mode = connection.fetch_one("PRAGMA journal_mode")
        synchronous = connection.fetch_one("PRAGMA synchronous")
        busy_timeout = connection.fetch_one("PRAGMA busy_timeout")

    assert foreign_keys == (1,)
    assert journal_mode == ("wal",)
    assert synchronous == (2,)
    assert busy_timeout == (250,)


@pytest.mark.parametrize(
    "statement",
    [
        "COMMIT",
        "ROLLBACK",
        "SAVEPOINT early_commit",
        "PRAGMA user_version = 99",
        "DELETE FROM schema_migrations",
        "DROP TABLE schema_migrations",
        "ATTACH DATABASE ':memory:' AS other",
    ],
)
def test_transaction_facade_denies_boundary_and_lineage_bypasses(
    tmp_path: Path,
    statement: str,
) -> None:
    database = SQLiteDatabase(tmp_path / f"{statement[:3]}.sqlite")
    database.migrate()

    with (
        pytest.raises(sqlite3.DatabaseError, match="not authorized"),
        database.transaction() as transaction,
    ):
        assert not hasattr(transaction, "commit")
        assert not hasattr(transaction, "rollback")
        assert not hasattr(transaction, "set_authorizer")
        transaction.execute(statement)

    assert database.migrate() == ()


def test_locked_writer_is_reported_as_transaction_failure(tmp_path: Path) -> None:
    database_path = tmp_path / "state.sqlite"
    database = SQLiteDatabase(database_path, timeout_seconds=0.0001)
    database.migrate()

    with closing(sqlite3.connect(database_path, isolation_level=None)) as blocking_connection:
        blocking_connection.execute("BEGIN IMMEDIATE")
        with (
            pytest.raises(StorageTransactionError, match="could not begin") as error_info,
            database.transaction(),
        ):
            pass
        blocking_connection.rollback()

    assert isinstance(error_info.value.__cause__, sqlite3.OperationalError)


def test_atomic_writes_replace_existing_content_and_remove_temporary_files(
    tmp_path: Path,
) -> None:
    bytes_path = tmp_path / "state" / "checkpoint.bin"
    bytes_path.parent.mkdir()
    bytes_path.write_bytes(b"old")

    atomic_write_bytes(bytes_path, b"new-state")
    text_path = tmp_path / "state" / "lineage.json"
    atomic_write_text(text_path, "value=\N{POUND SIGN}\n")

    assert bytes_path.read_bytes() == b"new-state"
    assert text_path.read_bytes() == b"value=\xc2\xa3\n"
    assert list(bytes_path.parent.glob(".*.tmp")) == []


def test_atomic_replace_failure_preserves_target_and_cleans_temporary_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "checkpoint"
    target.write_bytes(b"durable-old-state")

    def fail_replace(source: os.PathLike[str], destination: os.PathLike[str]) -> None:
        del source, destination
        raise PermissionError("replacement denied")

    monkeypatch.setattr(os, "replace", fail_replace)

    with pytest.raises(AtomicWriteError, match="replacement failed") as error_info:
        atomic_write_bytes(target, b"uncommitted-new-state")

    assert isinstance(error_info.value.__cause__, PermissionError)
    assert target.read_bytes() == b"durable-old-state"
    assert list(tmp_path.glob(".*.tmp")) == []


class PartialWriter:
    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        del args

    def write(self, content: bytes) -> int:
        return max(0, len(content) - 1)


def test_incomplete_atomic_write_is_refused_and_cleaned(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def open_partial_writer(path: Path, mode: str) -> PartialWriter:
        del path
        assert mode == "xb"
        return PartialWriter()

    monkeypatch.setattr(Path, "open", open_partial_writer)

    with pytest.raises(AtomicWriteError, match="replacement failed") as error_info:
        atomic_write_bytes(tmp_path / "checkpoint", b"new-state")

    assert isinstance(error_info.value.__cause__, OSError)
    assert list(tmp_path.glob(".*.tmp")) == []


def test_atomic_cleanup_failure_is_reported(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "checkpoint"
    target.write_bytes(b"old-state")

    def fail_replace(source: os.PathLike[str], destination: os.PathLike[str]) -> None:
        del source, destination
        raise PermissionError("replacement denied")

    def fail_cleanup(path: Path, *, missing_ok: bool = False) -> None:
        del path, missing_ok
        raise OSError("cleanup denied")

    with monkeypatch.context() as patch:
        patch.setattr(os, "replace", fail_replace)
        patch.setattr(Path, "unlink", fail_cleanup)
        with pytest.raises(AtomicWriteError, match="cleanup failed") as error_info:
            atomic_write_bytes(target, b"new-state")

    assert isinstance(error_info.value.__cause__, OSError)
    assert target.read_bytes() == b"old-state"


def test_non_io_interruption_is_preserved(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def interrupt_mkdir(path: Path, *, parents: bool, exist_ok: bool) -> None:
        del path, parents, exist_ok
        raise RuntimeError("interrupted")

    monkeypatch.setattr(Path, "mkdir", interrupt_mkdir)

    with pytest.raises(RuntimeError, match="interrupted"):
        atomic_write_bytes(tmp_path / "checkpoint", b"new-state")


def test_unencodable_text_is_refused() -> None:
    with pytest.raises(AtomicWriteError, match="text encoding failed"):
        atomic_write_text(Path("unused"), "\ud800")