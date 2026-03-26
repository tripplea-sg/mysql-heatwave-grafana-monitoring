#!/usr/bin/env python3
# Copyright (C) 2026 Hananto Wicaksono
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import mysql.connector
from mysql.connector import Error

# -----------------------
# GLOBAL CONFIG
# -----------------------
IP_ADDRESS = "127.0.0.1"  # Repository DB host
USER_NAME = "root"        # Repository DB user
MYSQL_PASSWORD = ""       # Repository DB password
MAX_WORKERS = 32          # Parallel threads

# -----------------------
# CONNECTION
# -----------------------
def get_conn(host, user, password, port=3306, db=None):
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        port=port,
        database=db,
        autocommit=True
    )

# -----------------------
# GET ALL VIEWS FROM monitor_tools
# -----------------------
def get_views(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'monitor_tools'
          AND table_type = 'VIEW'
    """)
    return [row[0] for row in cursor.fetchall()]

# -----------------------
# GET VIEW COLUMNS
# -----------------------
def get_view_columns(tgt_conn, view_name):
    cursor = tgt_conn.cursor()
    cursor.execute(f"SHOW COLUMNS FROM monitor_tools.`{view_name}`")
    return cursor.fetchall()  # list of (Field, Type, Null, Key, Default, Extra)

# -----------------------
# NORMALIZE COLUMN TYPES
# -----------------------
def normalize_column_type(field_type):
    """
    Convert long VARCHARs (>191) to TEXT to avoid row-size limits.
    """
    ft = field_type.lower()
    if ft.startswith("varchar"):
        size = int(ft[ft.find("(")+1:ft.find(")")])
        if size > 191:
            return "TEXT"
    return field_type

# -----------------------
# BUILD TABLE WITHOUT PRIMARY KEY, LOGTIME INDEXED
# -----------------------
def build_create_table_with_logtime_index(schema_name, table_name, columns):
    col_defs = []

    for col in columns:
        field = col[0]
        col_type = normalize_column_type(col[1])
        null = "NOT NULL" if col[2] == "NO" else "NULL"
        col_defs.append(f"`{field}` {col_type} {null}")

    # Add invisible logtime column
    col_defs.append("`logtime` TIMESTAMP DEFAULT CURRENT_TIMESTAMP INVISIBLE")

    col_defs_str = ",\n  ".join(col_defs)

    create_sql = f"""
    CREATE TABLE `{schema_name}`.`{table_name}` (
      {col_defs_str}
    )
    """

    # Add index on logtime
    create_sql += f";\nCREATE INDEX `{table_name}_logtime_idx` ON `{schema_name}`.`{table_name}`(`logtime`);"

    return create_sql

# -----------------------
# COPY VIEW TO REPO TABLE (thread-safe)
# -----------------------
def copy_view(view_name,
              src_ip, src_user, src_pass,
              tgt_ip, tgt_user, tgt_pass, tgt_port,
              schema_name):
    try:
        # Each thread gets its own connections
        src_conn = get_conn(src_ip, src_user, src_pass, db=schema_name)
        tgt_conn = get_conn(tgt_ip, tgt_user, tgt_pass, tgt_port, db="monitor_tools")

        # Get columns from view
        columns = get_view_columns(tgt_conn, view_name)

        # Check if table exists in repo
        with src_conn.cursor() as src_cursor:
            src_cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables
                WHERE table_schema = %s AND table_name = %s
            """, (schema_name, view_name))
            exists = src_cursor.fetchone()[0] > 0

        # Create table if not exists
        if not exists:
            create_sql = build_create_table_with_logtime_index(schema_name, view_name, columns)
            with src_conn.cursor() as src_cursor:
                src_cursor.execute(create_sql)
                src_conn.commit()

        # Copy data in batches using separate insert cursors
        tgt_data_cursor = tgt_conn.cursor(buffered=True)
        tgt_data_cursor.execute(f"SELECT * FROM monitor_tools.`{view_name}`")

        col_list = ", ".join([f"`{col[0]}`" for col in columns])
        placeholders = ", ".join(["%s"] * len(columns))
        insert_sql = f"INSERT INTO `{schema_name}`.`{view_name}` ({col_list}) VALUES ({placeholders})"

        while True:
            rows = tgt_data_cursor.fetchmany(1000)
            if not rows:
                break
            # Use a separate cursor for each batch insert
            with src_conn.cursor() as insert_cursor:
                insert_cursor.executemany(insert_sql, rows)
                src_conn.commit()

        tgt_data_cursor.close()
        print(f"[OK] Copied view: {view_name}")

    except Error as e:
        print(f"[ERROR] {view_name}: {e}")

    finally:
        try:
            src_conn.close()
            tgt_conn.close()
        except:
            pass

# -----------------------
# MAIN
# -----------------------
def main(compartment, display_name,
         tgt_ip, tgt_port, tgt_user, tgt_pass,
         password, now, db_retention):

    schema_name = f"{compartment}#{display_name}"

    try:
        # Repo connection to create schema
        src_conn = get_conn(IP_ADDRESS, USER_NAME, password)
        with src_conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{schema_name}`")
            src_conn.commit()
        src_conn.close()

        # Monitored MySQL connection to get views
        tgt_conn = get_conn(tgt_ip, tgt_user, tgt_pass, int(tgt_port))
        views = get_views(tgt_conn)
        tgt_conn.close()

        print(f"{schema_name}: Found {len(views)} views in monitor_tools")

        if len(views) == 0:
            pass  # do nothing
        else:
            # Parallel copy
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = [
                    executor.submit(
                        copy_view,
                        v,
                        IP_ADDRESS, USER_NAME, password,
                        tgt_ip, tgt_user, tgt_pass, int(tgt_port),
                        schema_name
                    )
                    for v in views
                ]
                for f in futures:
                    f.result()

        print("All views copied successfully")

    except Error as e:
        src_conn.close()
        tgt_conn.close()
        print(f"[MAIN ERROR]: {e}")

# -----------------------
# ENTRY
# -----------------------
if __name__ == "__main__":
    if len(sys.argv) != 10:
        print("Usage: script.py compartment display_name tgt_ip tgt_port tgt_user tgt_pass password now db_retention")
        sys.exit(1)
    main(*sys.argv[1:])
