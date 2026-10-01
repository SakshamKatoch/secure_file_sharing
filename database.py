import sqlite3
from datetime import datetime, timedelta


DATABASE_NAME = "files.db"


# =========================================================
# DATABASE SETUP
# =========================================================

def create_database():

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    # -----------------------------------------------------
    # Users
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # -----------------------------------------------------
    # Files
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            original_filename TEXT NOT NULL,
            stored_filename TEXT NOT NULL,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # -----------------------------------------------------
    # Shared Files
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shared_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER NOT NULL,
            owner_id INTEGER NOT NULL,
            shared_with_id INTEGER NOT NULL,
            expires_at TIMESTAMP,
            UNIQUE(file_id, shared_with_id),
            FOREIGN KEY (file_id) REFERENCES files(id),
            FOREIGN KEY (owner_id) REFERENCES users(id),
            FOREIGN KEY (shared_with_id) REFERENCES users(id)
        )
    """)

    # -----------------------------------------------------
    # Activity Logs
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    connection.commit()

    # =====================================================
    # DATABASE MIGRATION
    # =====================================================

    cursor.execute(
        "PRAGMA table_info(shared_files)"
    )

    columns = [
        column[1]
        for column in cursor.fetchall()
    ]

    if "expires_at" not in columns:

        cursor.execute("""
            ALTER TABLE shared_files
            ADD COLUMN expires_at TIMESTAMP
        """)

    connection.commit()
    connection.close()


# =========================================================
# USERS
# =========================================================

def add_user(username, email, password):

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO users
            (username, email, password)
            VALUES (?, ?, ?)
            """,
            (
                username,
                email,
                password
            )
        )

        connection.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        connection.close()


def get_user_by_email(email):

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            username,
            email,
            password
        FROM users
        WHERE email = ?
        """,
        (email,)
    )

    user = cursor.fetchone()

    connection.close()

    return user


# =========================================================
# FILES
# =========================================================

def add_file(
    user_id,
    original_filename,
    stored_filename
):

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO files
        (
            user_id,
            original_filename,
            stored_filename
        )
        VALUES (?, ?, ?)
        """,
        (
            user_id,
            original_filename,
            stored_filename
        )
    )

    connection.commit()
    connection.close()


def get_user_files(user_id):

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            original_filename,
            stored_filename,
            upload_time
        FROM files
        WHERE user_id = ?
        ORDER BY upload_time DESC
        """,
        (user_id,)
    )

    files = cursor.fetchall()

    connection.close()

    return files


# =========================================================
# SHARING
# =========================================================

def share_file(
    file_id,
    owner_id,
    shared_with_id,
    duration_hours=None
):

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    try:

        expires_at = None

        # -------------------------------------------------
        # Calculate expiration
        # -------------------------------------------------

        if duration_hours is not None:

            expiration_time = (
                datetime.now()
                + timedelta(hours=duration_hours)
            )

            expires_at = expiration_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        # -------------------------------------------------
        # Create share
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO shared_files
            (
                file_id,
                owner_id,
                shared_with_id,
                expires_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                file_id,
                owner_id,
                shared_with_id,
                expires_at
            )
        )

        connection.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        connection.close()


def get_shared_files(user_id):

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            files.id,
            files.original_filename,
            files.stored_filename,
            files.upload_time,
            shared_files.expires_at
        FROM files
        JOIN shared_files
            ON files.id = shared_files.file_id
        WHERE shared_files.shared_with_id = ?
        ORDER BY files.upload_time DESC
        """,
        (user_id,)
    )

    files = cursor.fetchall()

    connection.close()

    return files


def get_files_shared_by_user(owner_id):

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            shared_files.id,
            files.id,
            files.original_filename,
            users.username,
            users.email,
            shared_files.expires_at
        FROM shared_files
        JOIN files
            ON shared_files.file_id = files.id
        JOIN users
            ON shared_files.shared_with_id = users.id
        WHERE shared_files.owner_id = ?
        ORDER BY files.original_filename
        """,
        (owner_id,)
    )

    shared_files = cursor.fetchall()

    connection.close()

    return shared_files


# =========================================================
# REVOKE ACCESS
# =========================================================

def revoke_file_access(
    share_id,
    owner_id
):

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM shared_files
        WHERE id = ?
        AND owner_id = ?
        """,
        (
            share_id,
            owner_id
        )
    )

    deleted = cursor.rowcount > 0

    connection.commit()
    connection.close()

    return deleted


# =========================================================
# CHECK FILE ACCESS
# =========================================================

def has_file_access(
    file_id,
    user_id
):

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    # -----------------------------------------------------
    # Check if user owns the file
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT id
        FROM files
        WHERE id = ?
        AND user_id = ?
        """,
        (
            file_id,
            user_id
        )
    )

    owner = cursor.fetchone()

    if owner is not None:

        connection.close()

        return True

    # -----------------------------------------------------
    # Check shared access
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT expires_at
        FROM shared_files
        WHERE file_id = ?
        AND shared_with_id = ?
        """,
        (
            file_id,
            user_id
        )
    )

    result = cursor.fetchone()

    connection.close()

    # No sharing record
    if result is None:

        return False

    expires_at = result[0]

    # No expiration
    if expires_at is None:

        return True

    # -----------------------------------------------------
    # Check expiration
    # -----------------------------------------------------

    expiration_time = datetime.strptime(
        expires_at,
        "%Y-%m-%d %H:%M:%S"
    )

    if datetime.now() < expiration_time:

        return True

    return False


# =========================================================
# ACTIVITY LOGS
# =========================================================

def add_activity_log(
    user_id,
    action,
    details=""
):

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO activity_logs
        (
            user_id,
            action,
            details
        )
        VALUES (?, ?, ?)
        """,
        (
            user_id,
            action,
            details
        )
    )

    connection.commit()
    connection.close()


def get_activity_logs(user_id):

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            action,
            details,
            timestamp
        FROM activity_logs
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT 50
        """,
        (user_id,)
    )

    logs = cursor.fetchall()

    connection.close()

    return logs