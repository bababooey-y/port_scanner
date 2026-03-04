import argparse
import os
import re
import sqlite3
from datetime import datetime

DB_PATH = "db.sqlite"
MIGRATIONS_FOLDER = "migrations"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn


def ensure_migrations_folder():
    os.makedirs(MIGRATIONS_FOLDER, exist_ok=True)


def get_migrations():
    ensure_migrations_folder()
    files = []
    for name in os.listdir(MIGRATIONS_FOLDER):
        if re.match(r"^\d{3}_.+\.sql$", name):
            files.append(name)
    files.sort()
    return files


def get_version(filename):
    return filename.split("_")[0]


def ensure_version_table(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS migrator_version (
            version TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL
        )
        """
    )
    conn.commit()


def get_current_version(conn):
    row = conn.execute(
        "SELECT version FROM migrator_version ORDER BY version DESC LIMIT 1"
    ).fetchone()
    if row is None:
        return None
    return row[0]


def set_current_version(conn, version):
    conn.execute("DELETE FROM migrator_version")
    if version is not None:
        conn.execute(
            "INSERT INTO migrator_version (version, applied_at) VALUES (?, ?)",
            (version, datetime.now().isoformat()),
        )
    conn.commit()


def read_up_down_sql(filename):
    path = os.path.join(MIGRATIONS_FOLDER, filename)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if "-- UP" not in content or "-- DOWN" not in content:
        raise ValueError(f"Le fichier {filename} doit contenir -- UP et -- DOWN")

    parts = content.split("-- DOWN", 1)
    up_part = parts[0]
    down_part = parts[1]

    up_sql = up_part.split("-- UP", 1)[1].strip()
    down_sql = down_part.strip()
    return up_sql, down_sql


def status():
    migrations = get_migrations()
    conn = get_connection()
    ensure_version_table(conn)
    current_version = get_current_version(conn)
    conn.close()

    print("Version    Fichier                                        Statut")
    print("----------------------------------------------------------------------")
    for filename in migrations:
        version = get_version(filename)
        is_applied = current_version is not None and version <= current_version
        if is_applied:
            state = "appliquee"
        else:
            state = "en attente"
        print(f"{version:<10} {filename:<45} {state}")


def up():
    migrations = get_migrations()
    conn = get_connection()
    ensure_version_table(conn)
    current_version = get_current_version(conn)

    to_apply = []
    for filename in migrations:
        version = get_version(filename)
        if current_version is None or version > current_version:
            to_apply.append((version, filename))

    if len(to_apply) == 0:
        print("Aucune migration en attente.")
        conn.close()
        return

    count = 0
    for version, filename in to_apply:
        up_sql, _ = read_up_down_sql(filename)
        print(f"Applying {filename}...")
        conn.executescript(up_sql)
        set_current_version(conn, version)
        print("  -> OK")
        count += 1

    conn.close()
    print(f"\n{count} migration(s) appliquee(s).")


def down():
    migrations = get_migrations()
    conn = get_connection()
    ensure_version_table(conn)
    current_version = get_current_version(conn)

    if current_version is None:
        print("Aucune migration appliquee.")
        conn.close()
        return

    current_file = None
    versions = []
    for filename in migrations:
        version = get_version(filename)
        versions.append(version)
        if version == current_version:
            current_file = filename

    if current_file is None:
        print(f"Version courante introuvable dans migrations/: {current_version}")
        conn.close()
        return

    _, down_sql = read_up_down_sql(current_file)
    print(f"Rollback {current_file}...")
    conn.executescript(down_sql)

    versions.sort()
    index = versions.index(current_version)
    if index == 0:
        previous_version = None
    else:
        previous_version = versions[index - 1]
    set_current_version(conn, previous_version)

    conn.close()
    print("  -> OK")


def create_migration(name):
    migrations = get_migrations()

    if len(migrations) == 0:
        next_number = 1
    else:
        last_version = int(get_version(migrations[-1]))
        next_number = last_version + 1

    safe_name = name.strip().lower()
    safe_name = re.sub(r"[^a-z0-9]+", "_", safe_name)
    safe_name = re.sub(r"_+", "_", safe_name).strip("_")
    if safe_name == "":
        safe_name = "migration"

    filename = f"{next_number:03d}_{safe_name}.sql"
    path = os.path.join(MIGRATIONS_FOLDER, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write("-- UP\n\n-- DOWN\n")

    print(f"Migration creee: {path}")


def main():
    parser = argparse.ArgumentParser(description="Outil de migration SQLite")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status")
    subparsers.add_parser("up")
    subparsers.add_parser("down")

    create_parser = subparsers.add_parser("create")
    create_parser.add_argument("name")

    args = parser.parse_args()

    if args.command == "status":
        status()
    elif args.command == "up":
        up()
    elif args.command == "down":
        down()
    elif args.command == "create":
        create_migration(args.name)


if __name__ == "__main__":
    main()
