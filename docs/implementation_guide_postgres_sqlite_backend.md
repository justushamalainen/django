# Implementation Guide: PostgreSQL Wire Protocol + SQLite SQL Backend

## Overview

This guide describes how to implement a Django database backend that combines:
- **Connection Layer**: PostgreSQL wire protocol using `psycopg3`
- **SQL Dialect**: SQLite SQL syntax and semantics

This architecture is useful for databases that speak the PostgreSQL wire protocol but use SQLite-compatible SQL syntax (e.g., certain distributed databases, edge databases, or custom database solutions).

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Directory Structure](#2-directory-structure)
3. [Implementation Steps](#3-implementation-steps)
4. [File-by-File Implementation Guide](#4-file-by-file-implementation-guide)
5. [Connection Management](#5-connection-management)
6. [SQL Dialect Handling](#6-sql-dialect-handling)
7. [Feature Flags](#7-feature-flags)
8. [Testing Strategy](#8-testing-strategy)
9. [Configuration](#9-configuration)
10. [Known Challenges](#10-known-challenges)

---

## 1. Architecture Overview

### Inheritance Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    BASE CLASSES                              │
│  (django/db/backends/base/)                                  │
├─────────────────────────────────────────────────────────────┤
│  BaseDatabaseWrapper, BaseDatabaseFeatures,                  │
│  BaseDatabaseOperations, BaseDatabaseIntrospection,          │
│  BaseDatabaseSchemaEditor, BaseDatabaseCreation,             │
│  BaseDatabaseClient, BaseDatabaseValidation                  │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────────┐
│   SQLITE3     │    │  POSTGRESQL   │    │  POSTGRES_SQLITE  │
│   Backend     │    │   Backend     │    │     Backend       │
│               │    │               │    │    (NEW)          │
│ - SQL Dialect │    │ - Connection  │    │                   │
│ - Operations  │    │ - psycopg3    │    │ Connection: PG    │
│ - Schema      │    │ - Pooling     │    │ SQL Dialect: SQLite│
└───────────────┘    └───────────────┘    └───────────────────┘
```

### Component Source Mapping

| Component | Source Backend | Reason |
|-----------|---------------|--------|
| `base.py` (DatabaseWrapper) | **PostgreSQL** (heavily modified) | Uses psycopg3 for wire protocol |
| `operations.py` | **SQLite** | SQLite SQL syntax |
| `schema.py` | **SQLite** (modified) | SQLite DDL limitations |
| `features.py` | **Custom** (hybrid) | Mix based on actual capabilities |
| `introspection.py` | **Custom** | Depends on target database |
| `creation.py` | **PostgreSQL** (modified) | Uses PG connection for DB creation |
| `client.py` | **PostgreSQL** | Uses psql CLI |
| `_functions.py` | **SQLite** (if needed) | Custom SQL functions for SQLite compatibility |

---

## 2. Directory Structure

Create the following structure in `django/db/backends/`:

```
django/db/backends/postgres_sqlite/
├── __init__.py
├── base.py              # DatabaseWrapper - connection management
├── client.py            # CLI client interface
├── creation.py          # Test database creation
├── features.py          # Backend capability flags
├── introspection.py     # Schema introspection
├── operations.py        # SQL generation operations
├── schema.py            # Schema modification editor
├── _functions.py        # Custom SQL functions (optional)
└── psycopg_any.py       # Psycopg adapter (copy from postgresql)
```

---

## 3. Implementation Steps

### Phase 1: Foundation Setup

1. **Create directory structure** with `__init__.py`
2. **Copy `psycopg_any.py`** from PostgreSQL backend (no modifications needed)
3. **Implement `base.py`** - Core connection wrapper
4. **Implement `features.py`** - Define backend capabilities

### Phase 2: SQL Layer

5. **Implement `operations.py`** - SQLite SQL dialect operations
6. **Implement `schema.py`** - Schema modification (SQLite approach)
7. **Implement `_functions.py`** - Custom functions if target DB lacks them

### Phase 3: Utilities

8. **Implement `introspection.py`** - Schema inspection
9. **Implement `creation.py`** - Test database management
10. **Implement `client.py`** - Command-line interface

### Phase 4: Testing & Refinement

11. **Run Django test suite** against new backend
12. **Fix edge cases** and compatibility issues
13. **Document limitations** and workarounds

---

## 4. File-by-File Implementation Guide

### 4.1 `__init__.py`

```python
# Empty file - package marker
```

---

### 4.2 `base.py` - DatabaseWrapper

This is the **most critical file**. It manages database connections using psycopg3 but configures the connection for SQLite-compatible SQL.

#### Key Classes to Define

```python
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.postgresql.psycopg_any import is_psycopg3
```

#### Required Attributes

| Attribute | Value | Notes |
|-----------|-------|-------|
| `vendor` | `"postgres_sqlite"` | Unique identifier |
| `display_name` | `"PostgreSQL-SQLite"` | Human-readable name |
| `data_types` | SQLite types mapping | Copy from SQLite backend |
| `data_types_suffix` | `{}` | SQLite-style (no IDENTITY) |
| `operators` | SQLite operators | Copy from SQLite backend |
| `pattern_esc` | `r"REPLACE(REPLACE(...), '\', '\\')"` | SQLite ESCAPE pattern |

#### Required Component Classes

```python
# In DatabaseWrapper class
from .operations import DatabaseOperations
from .client import DatabaseClient
from .creation import DatabaseCreation
from .features import DatabaseFeatures
from .introspection import DatabaseIntrospection
from .schema import DatabaseSchemaEditor

SchemaEditorClass = DatabaseSchemaEditor
client_class = DatabaseClient
creation_class = DatabaseCreation
features_class = DatabaseFeatures
introspection_class = DatabaseIntrospection
ops_class = DatabaseOperations
```

#### Key Methods to Implement

**`get_connection_params(self)`**
- Source: PostgreSQL backend
- Returns connection parameters for psycopg3
- Must include: `dbname`, `user`, `password`, `host`, `port`

```python
def get_connection_params(self):
    settings_dict = self.settings_dict
    if not settings_dict["NAME"] and not settings_dict.get("OPTIONS", {}).get("service"):
        raise ImproperlyConfigured("...")

    conn_params = {
        "dbname": settings_dict["NAME"] or "postgres",
        "user": settings_dict["USER"] or "",
        "password": settings_dict["PASSWORD"] or "",
        "host": settings_dict["HOST"] or "",
        "port": settings_dict["PORT"] or "",
        "client_encoding": "UTF8",
    }
    conn_params.update(settings_dict.get("OPTIONS", {}))

    # Remove Django-specific options
    conn_params.pop("isolation_level", None)
    conn_params.pop("pool", None)

    return conn_params
```

**`get_new_connection(self, conn_params)`**
- Source: PostgreSQL backend
- Creates new psycopg3 connection
- May need to set SQL mode or compatibility flags

```python
def get_new_connection(self, conn_params):
    # Import psycopg (3 preferred)
    from .psycopg_any import psycopg

    connection = psycopg.connect(**conn_params)

    # Set any SQLite compatibility modes your target DB supports
    # Example: connection.execute("SET sql_dialect = 'sqlite'")

    return connection
```

**`init_connection_state(self)`**
- Initialize connection-specific settings after connect
- May execute PRAGMA-like commands if target DB supports them

**`create_cursor(self, name=None)`**
- Source: PostgreSQL backend
- Returns psycopg cursor

**`_set_autocommit(self, autocommit)`**
- Source: PostgreSQL backend
- Control transaction autocommit behavior

**`get_database_version(self)`**
- Query target database for version
- Return as tuple: `(major, minor, patch)`

---

### 4.3 `features.py` - DatabaseFeatures

Defines what the backend supports. This is a **hybrid** of SQLite and PostgreSQL features.

#### Template Structure

```python
from django.db.backends.base.features import BaseDatabaseFeatures
from django.utils.functional import cached_property


class DatabaseFeatures(BaseDatabaseFeatures):
    # Version requirement for target database
    minimum_database_version = (1, 0)  # Adjust to target DB

    # === TRANSACTION SUPPORT ===
    supports_transactions = True
    can_rollback_ddl = True  # SQLite-like: DDL is transactional
    atomic_transactions = False  # SQLite-like

    # === TYPE SYSTEM ===
    # SQLite-like: no native types for these
    has_native_uuid_field = False
    has_native_duration_field = False
    has_real_datatype = False

    # === JSON SUPPORT ===
    # Depends on target database
    has_native_json_field = False  # or True if supported
    supports_json_field_contains = False

    # === SCHEMA OPERATIONS ===
    # SQLite limitations typically apply
    can_alter_table_rename_column = True
    can_alter_table_drop_column = False  # If SQLite-like
    supports_foreign_keys = True
    can_create_inline_fk = True

    # === QUERY CAPABILITIES ===
    supports_select_for_update = False  # SQLite limitation
    supports_select_for_update_with_limit = False

    # === BULK OPERATIONS ===
    supports_update_conflicts = True
    supports_update_conflicts_with_target = True

    # === INTROSPECTION ===
    can_introspect_foreign_keys = True
    can_introspect_check_constraints = False  # SQLite limitation

    # === PostgreSQL-inherited (via wire protocol) ===
    supports_paramstyle_pyformat = True  # psycopg uses pyformat

    # === TEST CONFIGURATION ===
    test_db_allows_multiple_connections = True  # Unlike pure SQLite
```

#### Important Flags to Consider

| Flag | SQLite Value | PostgreSQL Value | Choose Based On |
|------|--------------|------------------|-----------------|
| `can_rollback_ddl` | `True` | `True` | Target DB behavior |
| `has_select_for_update` | `False` | `True` | Target DB support |
| `supports_timezones` | `False` | `True` | Target DB types |
| `can_return_columns_from_insert` | `False` | `True` | Target DB support |
| `has_native_json_field` | `False` | `True` (jsonb) | Target DB types |

---

### 4.4 `operations.py` - DatabaseOperations

Handles SQL generation. **Base this on SQLite** since SQL dialect is SQLite.

#### Key Methods to Implement

```python
from django.db.backends.base.operations import BaseDatabaseOperations


class DatabaseOperations(BaseDatabaseOperations):
    compiler_module = "django.db.models.sql.compiler"

    # === DATE/TIME OPERATIONS (SQLite-style) ===
    def date_extract_sql(self, lookup_type, sql, params):
        # SQLite: strftime-based extraction
        return f"django_date_extract(%s, {sql})", (lookup_type, *params)

    def date_trunc_sql(self, lookup_type, sql, params):
        return f"django_date_trunc(%s, {sql})", (lookup_type, *params)

    # === QUOTING ===
    def quote_name(self, name):
        if name.startswith('"') and name.endswith('"'):
            return name
        return '"%s"' % name  # SQLite-style double quotes

    # === SQL GENERATION ===
    def sql_flush(self, style, tables, *, reset_sequences=False, allow_cascade=False):
        # SQLite-style: DELETE FROM for each table
        sql = []
        for table in tables:
            sql.append(f"DELETE FROM {self.quote_name(table)}")
        return sql

    def bulk_batch_size(self, fields, objs):
        # SQLite limit: SQLITE_MAX_VARIABLE_NUMBER (default 999)
        # Adjust based on target database
        return 500

    # === TYPE CONVERSIONS ===
    def adapt_datetimefield_value(self, value):
        # SQLite stores as ISO string
        if value is None:
            return None
        return str(value)

    def get_db_converters(self, expression):
        converters = super().get_db_converters(expression)
        # Add SQLite-specific converters for dates, decimals, etc.
        return converters

    # === SEQUENCE/AUTOINCREMENT ===
    def autoinc_sql(self, table, column):
        # SQLite: rowid provides autoincrement
        return None, None

    def sequence_reset_sql(self, style, model_list):
        # SQLite: reset sqlite_sequence table
        return []  # Or implement if target DB has sequences
```

#### SQLite Functions That May Need Registration

If your target database doesn't have SQLite's built-in functions, you may need to handle:

- `django_date_extract` - Date part extraction
- `django_date_trunc` - Date truncation
- `django_power` - Power function
- `REGEXP` - Regular expression matching
- `django_format_dtdelta` - Timedelta formatting

---

### 4.5 `schema.py` - DatabaseSchemaEditor

Handles DDL operations. **Base on SQLite** due to schema modification limitations.

#### Key Considerations

SQLite's schema limitations often require **table recreation**:
1. Create new table with desired schema
2. Copy data from old table
3. Drop old table
4. Rename new table

```python
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


class DatabaseSchemaEditor(BaseDatabaseSchemaEditor):

    # === SQL TEMPLATES ===
    sql_create_fk = None  # SQLite: FKs created inline only
    sql_create_inline_fk = (
        "REFERENCES %(to_table)s (%(to_column)s) "
        "DEFERRABLE INITIALLY DEFERRED"
    )
    sql_delete_column = None  # Requires table rebuild

    # === TABLE RECREATION ===
    def alter_field(self, model, old_field, new_field, strict=False):
        # For most operations, need to rebuild table
        if self._field_should_be_altered(old_field, new_field):
            self._remake_table(model, alter_field=(old_field, new_field))

    def _remake_table(self, model, create_field=None, delete_field=None,
                      alter_field=None):
        """
        Rebuild table to work around SQLite limitations.
        """
        # Implementation follows SQLite pattern:
        # 1. Create new_table with updated schema
        # 2. INSERT INTO new_table SELECT ... FROM old_table
        # 3. DROP TABLE old_table
        # 4. ALTER TABLE new_table RENAME TO old_table
        # 5. Recreate indexes and triggers
        pass

    def delete_model(self, model):
        # Standard drop table
        super().delete_model(model)

    def add_field(self, model, field):
        # SQLite supports ADD COLUMN
        super().add_field(model, field)
```

---

### 4.6 `introspection.py` - DatabaseIntrospection

Handles schema inspection. This needs to query system tables.

#### Introspection Approach

Since you're using PostgreSQL wire protocol, you have two options:

**Option A: Use PostgreSQL system catalogs** (if target DB exposes them)
```python
def get_table_list(self, cursor):
    cursor.execute("""
        SELECT c.relname, c.relkind
        FROM pg_catalog.pg_class c
        LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relkind IN ('r', 'v', 'm', 'f', 'p')
        AND n.nspname NOT IN ('pg_catalog', 'pg_toast')
        AND pg_catalog.pg_table_is_visible(c.oid)
    """)
    return [TableInfo(row[0], {'r': 't', 'v': 'v'}.get(row[1])) for row in cursor.fetchall()]
```

**Option B: Use SQLite-style queries** (if target DB supports them)
```python
def get_table_list(self, cursor):
    cursor.execute(
        "SELECT name, type FROM sqlite_master "
        "WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%'"
    )
    return [TableInfo(row[0], row[1][0]) for row in cursor.fetchall()]
```

#### Key Methods

```python
from django.db.backends.base.introspection import (
    BaseDatabaseIntrospection,
    FieldInfo,
    TableInfo,
)


class DatabaseIntrospection(BaseDatabaseIntrospection):
    # Map database types to Django field types
    data_types_reverse = {
        "bool": "BooleanField",
        "boolean": "BooleanField",
        "smallint": "SmallIntegerField",
        "integer": "IntegerField",
        "bigint": "BigIntegerField",
        "real": "FloatField",
        "text": "TextField",
        "char": "CharField",
        "varchar": "CharField",
        "blob": "BinaryField",
        "date": "DateField",
        "datetime": "DateTimeField",
        "time": "TimeField",
    }

    def get_table_list(self, cursor):
        # Return list of TableInfo objects
        raise NotImplementedError("Implement based on target DB")

    def get_table_description(self, cursor, table_name):
        # Return list of FieldInfo objects describing columns
        raise NotImplementedError("Implement based on target DB")

    def get_constraints(self, cursor, table_name):
        # Return dict of constraint info
        raise NotImplementedError("Implement based on target DB")
```

---

### 4.7 `creation.py` - DatabaseCreation

Handles test database creation/destruction.

```python
from django.db.backends.base.creation import BaseDatabaseCreation


class DatabaseCreation(BaseDatabaseCreation):

    def _create_test_db(self, verbosity, autoclobber, keepdb=False):
        """
        Create the test database using PostgreSQL wire protocol.
        """
        test_database_name = self._get_test_db_name()

        # Connect to default database to create test DB
        with self._nodb_cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE {self.connection.ops.quote_name(test_database_name)}"
            )

        return test_database_name

    def _destroy_test_db(self, test_database_name, verbosity):
        """
        Destroy the test database.
        """
        with self._nodb_cursor() as cursor:
            cursor.execute(
                f"DROP DATABASE IF EXISTS {self.connection.ops.quote_name(test_database_name)}"
            )
```

---

### 4.8 `client.py` - DatabaseClient

Command-line client for interactive shell access.

```python
from django.db.backends.base.client import BaseDatabaseClient


class DatabaseClient(BaseDatabaseClient):
    executable_name = "psql"  # Use psql since we're using PG wire protocol

    @classmethod
    def settings_to_cmd_args_env(cls, settings_dict, parameters):
        args = [cls.executable_name]

        host = settings_dict.get("HOST")
        port = settings_dict.get("PORT")
        dbname = settings_dict.get("NAME")
        user = settings_dict.get("USER")
        passwd = settings_dict.get("PASSWORD")

        if host:
            args += ["-h", host]
        if port:
            args += ["-p", str(port)]
        if user:
            args += ["-U", user]
        if dbname:
            args += [dbname]

        args.extend(parameters)

        env = {}
        if passwd:
            env["PGPASSWORD"] = passwd

        return args, env
```

---

### 4.9 `_functions.py` - Custom SQL Functions (Optional)

If your target database lacks SQLite built-in functions, register them:

```python
"""
Custom SQL functions to provide SQLite compatibility.
These may be registered at connection time or implemented
as database-side functions.
"""

def register_functions(connection):
    """
    Register custom functions needed for SQLite SQL compatibility.

    Note: Implementation depends on target database capabilities.
    Some databases allow registering custom functions, others don't.
    """
    # Example for psycopg3:
    # connection.execute("CREATE OR REPLACE FUNCTION django_date_extract...")
    pass


# Function definitions for date/time operations
DJANGO_DATE_EXTRACT_SQL = """
-- Extract date part (year, month, day, etc.) from a datetime
CREATE OR REPLACE FUNCTION django_date_extract(lookup_type TEXT, dt TEXT)
RETURNS INTEGER AS $$
    -- Implementation depends on target database
$$ LANGUAGE SQL;
"""

DJANGO_DATE_TRUNC_SQL = """
-- Truncate datetime to specified precision
CREATE OR REPLACE FUNCTION django_date_trunc(lookup_type TEXT, dt TEXT)
RETURNS TEXT AS $$
    -- Implementation depends on target database
$$ LANGUAGE SQL;
"""
```

---

### 4.10 `psycopg_any.py`

**Copy directly from PostgreSQL backend**: `django/db/backends/postgresql/psycopg_any.py`

This module provides compatibility between psycopg2 and psycopg3.

---

## 5. Connection Management

### Connection Flow

```
┌──────────────────────────────────────────────────────────────┐
│                     Django Settings                           │
│  DATABASES = {                                                │
│      'default': {                                             │
│          'ENGINE': 'django.db.backends.postgres_sqlite',     │
│          'NAME': 'mydb',                                      │
│          'USER': 'user',                                      │
│          'PASSWORD': 'pass',                                  │
│          'HOST': 'localhost',                                 │
│          'PORT': '5432',  # PostgreSQL wire protocol port     │
│      }                                                        │
│  }                                                            │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                  DatabaseWrapper.connect()                    │
│  1. get_connection_params() - Build psycopg params           │
│  2. get_new_connection() - psycopg.connect(**params)         │
│  3. init_connection_state() - Set SQL mode, pragmas          │
│  4. Signal: connection_created                                │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                   psycopg3 Connection                         │
│  - Speaks PostgreSQL wire protocol                            │
│  - Target DB translates to internal storage                   │
│  - SQL sent as SQLite dialect                                 │
└──────────────────────────────────────────────────────────────┘
```

### Connection Pooling

If your target database supports connection pooling via psycopg_pool:

```python
# In base.py
@property
def pool(self):
    pool_options = self.settings_dict.get("OPTIONS", {}).get("pool")
    if pool_options:
        from psycopg_pool import ConnectionPool
        # ... setup pool
    return None
```

---

## 6. SQL Dialect Handling

### Critical SQLite vs PostgreSQL Differences

| Feature | SQLite | PostgreSQL | Your Backend |
|---------|--------|------------|--------------|
| String quoting | `"identifier"` or `` `identifier` `` | `"identifier"` | Use SQLite style |
| String concat | `||` | `||` | Same |
| Boolean | 0/1 | true/false | SQLite (0/1) |
| LIMIT/OFFSET | `LIMIT n OFFSET m` | `LIMIT n OFFSET m` | Same |
| Upsert | `INSERT OR REPLACE` | `ON CONFLICT DO UPDATE` | SQLite style |
| Date functions | `strftime()` | `extract()`, `date_trunc()` | SQLite style |
| AUTOINCREMENT | `INTEGER PRIMARY KEY` | `SERIAL`/`IDENTITY` | SQLite style |

### Type Mapping

```python
# In base.py
data_types = {
    "AutoField": "integer",
    "BigAutoField": "integer",  # SQLite: all ints are 64-bit
    "BinaryField": "blob",
    "BooleanField": "bool",
    "CharField": "varchar(%(max_length)s)",
    "DateField": "date",
    "DateTimeField": "datetime",
    "DecimalField": "decimal",
    "DurationField": "bigint",
    "FileField": "varchar(%(max_length)s)",
    "FilePathField": "varchar(%(max_length)s)",
    "FloatField": "real",
    "IntegerField": "integer",
    "BigIntegerField": "bigint",
    "IPAddressField": "char(15)",
    "GenericIPAddressField": "char(39)",
    "JSONField": "text",  # Or json/jsonb if supported
    "OneToOneField": "integer",
    "PositiveBigIntegerField": "bigint",
    "PositiveIntegerField": "integer",
    "PositiveSmallIntegerField": "smallint",
    "SlugField": "varchar(%(max_length)s)",
    "SmallAutoField": "integer",
    "SmallIntegerField": "smallint",
    "TextField": "text",
    "TimeField": "time",
    "UUIDField": "char(32)",
}
```

---

## 7. Feature Flags

### Feature Decision Matrix

For each feature flag, determine support based on:
1. **Target database capabilities** - What does the actual database support?
2. **Wire protocol** - What does PostgreSQL protocol enable?
3. **SQL dialect** - What does SQLite SQL allow?

```python
class DatabaseFeatures(BaseDatabaseFeatures):
    # ============================================================
    # TRANSACTION FEATURES
    # ============================================================

    # True if database supports transactions
    supports_transactions = True  # Most databases do

    # True if DDL is wrapped in transactions and can be rolled back
    can_rollback_ddl = True  # SQLite-like behavior

    # ============================================================
    # QUERY FEATURES
    # ============================================================

    # SELECT FOR UPDATE support (typically not in SQLite)
    has_select_for_update = False  # Check target DB

    # Can use LIMIT in subqueries
    supports_subqueries_in_group_by = True

    # ============================================================
    # INSERT/UPDATE FEATURES
    # ============================================================

    # INSERT ... RETURNING support
    can_return_columns_from_insert = False  # Check target DB

    # Bulk insert can return IDs
    can_return_rows_from_bulk_insert = False  # Check target DB

    # ============================================================
    # SCHEMA FEATURES
    # ============================================================

    # ALTER TABLE ADD COLUMN
    can_alter_table_rename_column = True

    # ALTER TABLE DROP COLUMN (SQLite added in 3.35+)
    can_alter_table_drop_column = False  # Conservative default

    # ============================================================
    # TYPE FEATURES
    # ============================================================

    # Native JSON field support
    has_native_json_field = False  # Check target DB

    # Native UUID type
    has_native_uuid_field = False  # SQLite doesn't have this
```

---

## 8. Testing Strategy

### Running Django's Test Suite

```bash
# Set environment for your backend
export DJANGO_SETTINGS_MODULE=tests.settings

# Run tests against your backend
./runtests.py --settings=your_backend_settings
```

### Test Configuration

Create `test_settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgres_sqlite',
        'NAME': 'test_db',
        'USER': 'test_user',
        'PASSWORD': 'test_pass',
        'HOST': 'localhost',
        'PORT': '5432',  # Or your target DB port
    },
    'other': {
        'ENGINE': 'django.db.backends.postgres_sqlite',
        'NAME': 'test_db_other',
        'USER': 'test_user',
        'PASSWORD': 'test_pass',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Expected Test Categories

| Category | Expected Behavior |
|----------|-------------------|
| Basic CRUD | Should pass |
| Transactions | Should pass |
| Foreign Keys | Should pass |
| Migrations | May need adjustments |
| JSON field | Depends on target DB |
| Full-text search | Likely needs skip |
| Window functions | Depends on target DB |
| SELECT FOR UPDATE | Likely needs skip |

### Skip Unsupported Tests

```python
# In features.py, use feature flags to skip tests
class DatabaseFeatures(BaseDatabaseFeatures):
    # Tests will be skipped based on these flags
    supports_json_field_contains = False
    has_select_for_update = False
```

---

## 9. Configuration

### Django Settings Example

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgres_sqlite',
        'NAME': 'myapp_db',
        'USER': 'myapp_user',
        'PASSWORD': 'secure_password',
        'HOST': 'db.example.com',
        'PORT': '5432',
        'OPTIONS': {
            # Connection timeout
            'connect_timeout': 10,

            # SSL mode if needed
            'sslmode': 'require',

            # Connection pool (if supported)
            'pool': {
                'min_size': 2,
                'max_size': 10,
            },

            # Custom options for target database
            'target_db_option': 'value',
        },
        'CONN_MAX_AGE': 600,  # Persistent connections
        'CONN_HEALTH_CHECKS': True,
    }
}
```

---

## 10. Known Challenges

### Challenge 1: SQL Dialect Mismatches

**Problem**: Some SQL statements that work in SQLite may not work over PostgreSQL wire protocol, or vice versa.

**Solution**: Test extensively and override specific SQL generation methods in `operations.py`.

### Challenge 2: Type System Differences

**Problem**: PostgreSQL has rich types (inet, uuid, jsonb), SQLite uses dynamic typing.

**Solution**:
- Use `data_types` mapping to specify SQLite-compatible types
- Implement converters in `get_db_converters()`

### Challenge 3: Schema Introspection

**Problem**: Target database may not expose schema information in standard ways.

**Solution**:
- Investigate target DB's system tables/views
- May need custom introspection queries

### Challenge 4: Auto-increment/Sequences

**Problem**: SQLite uses `INTEGER PRIMARY KEY` for auto-increment, PostgreSQL uses `SERIAL`/`IDENTITY`.

**Solution**:
- Use SQLite-style (`INTEGER PRIMARY KEY`)
- Ensure `data_types_suffix` doesn't add PostgreSQL-isms

### Challenge 5: Transaction Isolation

**Problem**: SQLite and PostgreSQL handle isolation differently.

**Solution**:
- Document supported isolation levels
- Implement `_set_autocommit()` appropriately

### Challenge 6: RETURNING Clause

**Problem**: PostgreSQL supports `INSERT ... RETURNING`, SQLite added limited support in 3.35+.

**Solution**:
- Set `can_return_columns_from_insert` based on target DB
- Fall back to `SELECT last_insert_rowid()` pattern if needed

---

## Appendix A: File Reference Quick Links

| File | Copy From | Modifications Needed |
|------|-----------|---------------------|
| `base.py` | PostgreSQL | Heavy - change data_types, operators |
| `operations.py` | SQLite | Light - adjust for target DB |
| `schema.py` | SQLite | Medium - adjust DDL syntax |
| `features.py` | Custom | New - test each flag |
| `introspection.py` | Custom/SQLite | Heavy - depends on target DB |
| `creation.py` | PostgreSQL | Light - adjust DB creation |
| `client.py` | PostgreSQL | None - use psql |
| `psycopg_any.py` | PostgreSQL | None |
| `_functions.py` | SQLite | Heavy - may not be needed |

---

## Appendix B: Implementation Checklist

- [ ] Create directory `django/db/backends/postgres_sqlite/`
- [ ] Create `__init__.py`
- [ ] Copy `psycopg_any.py` from PostgreSQL backend
- [ ] Implement `base.py` with psycopg3 connection + SQLite types
- [ ] Implement `features.py` with hybrid feature flags
- [ ] Implement `operations.py` based on SQLite
- [ ] Implement `schema.py` based on SQLite
- [ ] Implement `introspection.py` for target database
- [ ] Implement `creation.py` for test database management
- [ ] Implement `client.py` for CLI access
- [ ] Create `_functions.py` if custom functions needed
- [ ] Run Django test suite
- [ ] Document unsupported features
- [ ] Create user documentation

---

## Appendix C: Related Django Source Files

For reference, these are the key files to study:

```
django/db/backends/
├── base/
│   ├── base.py              # BaseDatabaseWrapper (792 lines)
│   ├── features.py          # BaseDatabaseFeatures
│   ├── operations.py        # BaseDatabaseOperations
│   ├── schema.py            # BaseDatabaseSchemaEditor
│   ├── introspection.py     # BaseDatabaseIntrospection
│   ├── creation.py          # BaseDatabaseCreation
│   ├── client.py            # BaseDatabaseClient
│   └── validation.py        # BaseDatabaseValidation
├── sqlite3/
│   ├── base.py              # 378 lines - SQLite connection
│   ├── _functions.py        # 537 lines - Custom SQL functions
│   ├── operations.py        # 420 lines - SQL operations
│   ├── schema.py            # 503 lines - Schema editor
│   ├── introspection.py     # 458 lines - Schema inspection
│   ├── features.py          # 173 lines - Feature flags
│   └── creation.py          # 157 lines - Test DB creation
├── postgresql/
│   ├── base.py              # 620 lines - PG connection, pooling
│   ├── psycopg_any.py       # 114 lines - psycopg2/3 adapter
│   ├── operations.py        # 405 lines - SQL operations
│   ├── schema.py            # 380 lines - Schema editor
│   ├── introspection.py     # 327 lines - Schema inspection
│   ├── features.py          # 186 lines - Feature flags
│   └── creation.py          # 91 lines - Test DB creation
└── utils.py                 # Shared utilities
```
