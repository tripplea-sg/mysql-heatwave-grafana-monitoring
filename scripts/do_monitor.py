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

import os
import sys
import hashlib
import subprocess
from pathlib import Path
import mysql.connector
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# -----------------------
# GLOBAL CONFIG
# -----------------------
# ENC_FILE = "/home/opc/.mysqlsh/plugins/grafana/mysql.pass.enc"
# AUTO_KEY = hashlib.sha256(f"{os.environ['USER']}@{os.uname().nodename}".encode()).hexdigest()

IP_ADDRESS = "127.0.0.1"
USER_NAME = "root"
MYSQL_PASSWORD=""

# MYSQL_PASSWORD = subprocess.check_output([
#    "openssl", "enc", "-aes-256-cbc", "-d",
#    "-in", ENC_FILE, "-pass", f"pass:{AUTO_KEY}"
# ]).decode().strip()

# -----------------------
# MYSQL HELPERS
# -----------------------
def get_conn(host, user, password, port=3306, db=None):
    return mysql.connector.connect(
        host=host, user=user, password=password,
        port=port, database=db, autocommit=True
    )

def query_mysql(host, user, password, query):
    try:
        conn = get_conn(host, user, password)
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        return []

# -----------------------
# MAIN FUNCTION
# -----------------------
# def main(compartment, display_name, ip_address, port, username, password, now, retention):
def main(compartment, display_name, tgt_ip, tgt_port, tgt_user, tgt_pass, password, now, db_retention):
    MYSQL_PASSWORD = password
    now_dt = datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
    base_dir = Path(f"/home/opc/mysqlsh/plugins/grafana/{compartment}/{display_name}")
    base_dir.mkdir(parents=True, exist_ok=True)
    log_file = base_dir / "log.txt"

    ORIG = Path("/home/opc/mysql_monitoring/all_tables_reference.txt")
    MASTER_LIST = base_dir / "final_tables_reference.txt"

    # Error logging helper
    def log_error(msg):
        with open(log_file, "a") as f:
            f.write(f"{datetime.now()} ERROR: {msg}\n")

    # -----------------------
    # MASTER LIST
    # -----------------------
    def build_master_list():
        try:
            include_query = f"""
                SELECT table_name,
                (SELECT b.days_retention FROM config.performance_schema_table b WHERE b.table_name=a.table_name)
                FROM config.include_performance_schema a
                WHERE compartment='{compartment}'
                AND display_name='{display_name}'
                AND start_date_time<=NOW()
                AND end_date_time>=NOW();
            """

            exclude_query = f"""
                SELECT table_name
                FROM config.exclude_performance_schema
                WHERE compartment='{compartment}'
                AND display_name='{display_name}'
                AND start_date_time<=NOW()
                AND end_date_time>=NOW();
            """

            include_rows = query_mysql(IP_ADDRESS, USER_NAME, MYSQL_PASSWORD, include_query)
            exclude_rows = query_mysql(IP_ADDRESS, USER_NAME, MYSQL_PASSWORD, exclude_query)

            exclude_set = {r[0] for r in exclude_rows}
            seen = set()
            master = []

            # ORIG
            if ORIG.exists():
                for line in ORIG.read_text().splitlines():
                    if not line.strip():
                        continue
                    table = line.split()[0]
                    if table not in seen and table not in exclude_set:
                        master.append(line)
                        seen.add(table)

            # INCLUDE
            for r in include_rows:
                table = r[0]
                retention = r[1] if r[1] else 7
                line = f"{table},{retention}"
                if table not in seen and table not in exclude_set:
                    master.append(line)
                    seen.add(table)

            master = [x.replace("NULL", "7") for x in master]

            MASTER_LIST.write_text("\n".join(master))
            print(f"MASTER_LIST built: {len(master)} tables")
        except Exception as e:
            log_error(f"MASTER_LIST build failed: {e}")

    # -----------------------
    # DDL HANDLING (src_conn only)
    # -----------------------
    def ensure_table_schema(tablename):
        try:
            src_conn = get_conn(IP_ADDRESS, USER_NAME, MYSQL_PASSWORD)
            src_cur = src_conn.cursor()

            src_cur.execute(f"CREATE DATABASE IF NOT EXISTS `{compartment}#{display_name}`")
            src_cur.execute(f"USE `{compartment}#{display_name}`")

            tgt_conn = get_conn(tgt_ip, tgt_user, tgt_pass, tgt_port)
            tgt_cur = tgt_conn.cursor()
            tgt_cur.execute(f"SHOW CREATE TABLE performance_schema.{tablename}")
            row = tgt_cur.fetchone()
            tgt_cur.close()
            tgt_conn.close()

            if not row:
                return

            ddl = row[1]
            ddl = ddl.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS")
            ddl = ddl.replace("`performance_schema`.", "")
            ddl = ddl.replace("ENGINE=PERFORMANCE_SCHEMA", "ENGINE=InnoDB")

            import re
            ddl = re.sub(r",\s*PRIMARY KEY\s*\([^)]+\)", "", ddl, flags=re.I)
            ddl = re.sub(r",\s*UNIQUE KEY\s*[^\(]*\([^)]+\)", "", ddl, flags=re.I)

            # --- Remove NOT NULL from columns ---
            # This will match column definitions like: `col_name` INT NOT NULL DEFAULT 0
            ddl = re.sub(r"(\sNOT NULL\b)", "", ddl, flags=re.I)
            
            # Robust fix for TIMESTAMP columns: add DEFAULT CURRENT_TIMESTAMP(6)
            # Matches: `col_name` timestamp(6) [NULL] [DEFAULT NULL]
            def fix_timestamp(match):
                col_name = match.group(1)
                return f"`{col_name}` timestamp(6) NULL DEFAULT CURRENT_TIMESTAMP(6)"

            # Regex explanation:
            # - `\s*NULL` → optional NULL
            # - `(\s+DEFAULT\s+NULL)?` → optional DEFAULT NULL
            ddl = re.sub(
                r"`(\w+)`\s+timestamp\(6\)\s*(NULL)?(\s+DEFAULT\s+NULL)?",
                fix_timestamp,
                ddl,
                flags=re.I
            )

            for stmt in ddl.split(";"):
                if stmt.strip():
                    src_cur.execute(stmt)

            src_cur.execute(f"""
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_schema='{compartment}#{display_name}'
                AND table_name='{tablename}'
                AND column_name='logtime'
            """)
            exists = src_cur.fetchone()[0]
            if not exists:
                src_cur.execute(f"""
                    ALTER TABLE `{compartment}#{display_name}`.`{tablename}`
                    ADD COLUMN logtime DATETIME INVISIBLE,
                    ADD INDEX logtime (logtime)
                """)

            src_cur.close()
            src_conn.close()

        except Exception as e:
            log_error(f"[DDL ERROR] {tablename}: {e}")

    # -----------------------
    # TABLE COPY
    # -----------------------
    def backup_restore(tablename, retention):
        try:
            tablename = tablename.split()[0]
            print(f"[START] {tablename}, with table_retention = {retention}")
            ensure_table_schema(tablename)

            src_conn = get_conn(IP_ADDRESS, USER_NAME, MYSQL_PASSWORD)
            src_cur = src_conn.cursor()
            tgt_conn = get_conn(tgt_ip, tgt_user, tgt_pass, tgt_port)
            tgt_cur = tgt_conn.cursor(dictionary=True)

            tgt_cur.execute(f"SELECT * FROM performance_schema.{tablename}")
            rows = tgt_cur.fetchall()
            tgt_cur.close()
            tgt_conn.close()

            if not rows:
                return

            cols = rows[0].keys()
            col_list = ",".join(f"`{c}`" for c in cols)
            placeholders = ",".join(["%s"] * len(cols))

            insert_sql = f"""
            INSERT INTO `{compartment}#{display_name}`.`{tablename}`
            ({col_list}) VALUES ({placeholders})
            """
            batch = []
            for r in rows:
                batch.append(tuple(r.values()))
                if len(batch) >= 500:
                    src_cur.executemany(insert_sql, batch)
                    batch = []
            if batch:
                src_cur.executemany(insert_sql, batch)

            src_cur.execute(f"""
                UPDATE `{compartment}#{display_name}`.`{tablename}`
                SET logtime='{now}' WHERE logtime IS NULL
            """)

            src_cur.execute(f"""
                DELETE FROM `{compartment}#{display_name}`.`{tablename}`
                WHERE logtime < NOW() - INTERVAL {retention} DAY
            """)
            src_cur.execute(f"""
                DELETE FROM `{compartment}#{display_name}`.`{tablename}`
                WHERE logtime < NOW() - INTERVAL {db_retention} DAY
            """)

            if now_dt.minute == 0:
                src_cur.execute(f"ANALYZE TABLE `{compartment}#{display_name}`.`{tablename}`")

            if tablename == "replication_connection_configuration":
                src_cur.execute(f"""
                    INSERT INTO replica.replication_lag 
                        (logtime, source_ip, target_ip, channel_name, lag_seconds)
                        SELECT 
                            logtime,
                            HOST AS source_ip,
                            '{tgt_ip}' AS target_ip,
                            CHANNEL_NAME AS channel_name,
                            COALESCE(MAX(TIMESTAMPDIFF(MICROSECOND, APPLYING_TRANSACTION_ORIGINAL_COMMIT_TIMESTAMP, NOW(6)) / 1000000), 0) AS lag_seconds
                        FROM (
                        SELECT 
                            config.logtime, 
                                    config.HOST, 
                            worker.CHANNEL_NAME, 
                            worker.APPLYING_TRANSACTION_ORIGINAL_COMMIT_TIMESTAMP
                            FROM `{compartment}#{display_name}`.replication_connection_configuration AS config
                        JOIN `{compartment}#{display_name}`.replication_applier_status_by_worker AS worker
                        ON config.CHANNEL_NAME = worker.CHANNEL_NAME
                            WHERE worker.SERVICE_STATE = 'ON'
                            AND worker.CHANNEL_NAME <> 'group_replication_applier'
                        AND config.logtime = worker.logtime
                        ) a
                        GROUP BY logtime, HOST, CHANNEL_NAME
                        ORDER BY logtime DESC
                        LIMIT 1;
                """)
            
            src_cur.close()
            src_conn.close()
            print(f"[DONE] {tablename} ({len(rows)} rows)")

        except Exception as e:
            print(f"[backup_restore ERROR] {tablename}: {e}")
            log_error(f"[backup_restore ERROR] {tablename}: {e}")

    # -----------------------
    # TABLES METADATA
    # -----------------------
    def backup_restore_table():
        try:
            src_conn = get_conn(IP_ADDRESS, USER_NAME, MYSQL_PASSWORD)
            src_cur = src_conn.cursor()
            tgt_conn = get_conn(tgt_ip, tgt_user, tgt_pass, tgt_port)
            tgt_cur = tgt_conn.cursor()
            tgt_cur.execute("""
                SELECT TABLE_SCHEMA,TABLE_NAME,
                ROUND(DATA_LENGTH/1024/1024,2),
                ROUND(INDEX_LENGTH/1024/1024,2),
                DATA_FREE
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA NOT IN ('mysql','performance_schema','information_schema')
            """)
            rows = tgt_cur.fetchall()
            tgt_cur.close()
            tgt_conn.close()

            src_cur.execute(f"""
                CREATE TABLE IF NOT EXISTS `{compartment}#{display_name}`.TABLES (
                    database_name VARCHAR(255),
                    table_name VARCHAR(255),
                    data_mb DOUBLE,
                    index_mb DOUBLE,
                    data_free_mb DOUBLE,
                    logtime DATETIME INVISIBLE,
                    INDEX logtime (logtime)
                )
            """)
            src_cur.executemany(f"""
                INSERT INTO `{compartment}#{display_name}`.TABLES
                (database_name,table_name,data_mb,index_mb,data_free_mb)
                VALUES (%s,%s,%s,%s,%s)
            """, rows)

            src_cur.execute(f"""
                UPDATE `{compartment}#{display_name}`.TABLES
                SET logtime='{now}' WHERE logtime IS NULL
            """) 

            src_cur.execute(f"""
                DELETE FROM `{compartment}#{display_name}`.TABLES
                WHERE logtime < NOW() - INTERVAL 1 DAY
            """)

            if now_dt.minute == 0:
                src_cur.execute(f"ANALYZE TABLE `{compartment}#{display_name}`.TABLES")

            src_cur.close()
            src_conn.close()
            print("[TABLES] done")
        except Exception as e:
            log_error(f"[TABLES ERROR] {e}")

    def backup_restore_plugins():
        try:
            src_conn = get_conn(IP_ADDRESS, USER_NAME, MYSQL_PASSWORD)
            src_cur = src_conn.cursor()
            tgt_conn = get_conn(tgt_ip, tgt_user, tgt_pass, tgt_port)
            tgt_cur = tgt_conn.cursor()
            tgt_cur.execute("""
                SELECT PLUGIN_NAME, PLUGIN_VERSION, PLUGIN_STATUS, PLUGIN_TYPE,
                PLUGIN_TYPE_VERSION, PLUGIN_LIBRARY, PLUGIN_LIBRARY_VERSION, PLUGIN_AUTHOR,
                PLUGIN_DESCRIPTION, PLUGIN_LICENSE, LOAD_OPTION
                FROM information_schema.plugins
            """)
            rows = tgt_cur.fetchall()
            tgt_cur.close()
            tgt_conn.close()

            src_cur.execute(f"""
                CREATE TABLE IF NOT EXISTS `{compartment}#{display_name}`.PLUGINS (
                    `PLUGIN_NAME` varchar(64) NOT NULL DEFAULT '',
                    `PLUGIN_VERSION` varchar(20) NOT NULL DEFAULT '',
                    `PLUGIN_STATUS` varchar(10) NOT NULL DEFAULT '',
                    `PLUGIN_TYPE` varchar(80) NOT NULL DEFAULT '',
                    `PLUGIN_TYPE_VERSION` varchar(20) NOT NULL DEFAULT '',
                    `PLUGIN_LIBRARY` varchar(64) DEFAULT NULL,
                    `PLUGIN_LIBRARY_VERSION` varchar(20) DEFAULT NULL,
                    `PLUGIN_AUTHOR` varchar(64) DEFAULT NULL,
                    `PLUGIN_DESCRIPTION` longtext,
                    `PLUGIN_LICENSE` varchar(80) DEFAULT NULL,
                    `LOAD_OPTION` varchar(64) NOT NULL DEFAULT '',
                    logtime DATETIME INVISIBLE,
                    INDEX logtime (logtime)
                )
            """)
            src_cur.executemany(f"""
                INSERT INTO `{compartment}#{display_name}`.PLUGINS
                (PLUGIN_NAME, PLUGIN_VERSION, PLUGIN_STATUS, PLUGIN_TYPE, PLUGIN_TYPE_VERSION,
                PLUGIN_LIBRARY, PLUGIN_LIBRARY_VERSION, PLUGIN_AUTHOR, PLUGIN_DESCRIPTION, PLUGIN_LICENSE,
                LOAD_OPTION)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, rows)

            src_cur.execute(f"""
                UPDATE `{compartment}#{display_name}`.PLUGINS
                SET logtime='{now}' WHERE logtime IS NULL
            """)

            src_cur.execute(f"""
                DELETE FROM `{compartment}#{display_name}`.PLUGINS
                WHERE logtime < NOW() - INTERVAL 1 DAY
            """)

            if now_dt.minute == 0:
                src_cur.execute(f"ANALYZE TABLE `{compartment}#{display_name}`.PLUGINS")

            src_cur.close()
            src_conn.close()
            print("[PLUGINS] done")
        except Exception as e:
            log_error(f"[PLUGINS ERROR] {e}")

    # USER_PRIVILEGES METADATA
    # -----------------------
    def backup_restore_user_privileges():
        try:
            src_conn = get_conn(IP_ADDRESS, USER_NAME, MYSQL_PASSWORD)
            src_cur = src_conn.cursor()
            tgt_conn = get_conn(tgt_ip, tgt_user, tgt_pass, tgt_port)
            tgt_cur = tgt_conn.cursor()
            tgt_cur.execute("""
                SELECT GRANTEE, TABLE_CATALOG, PRIVILEGE_TYPE, IS_GRANTABLE
                FROM information_schema.user_privileges
            """)
            rows = tgt_cur.fetchall()
            tgt_cur.close()
            tgt_conn.close()

            src_cur.execute(f"""
                CREATE TABLE IF NOT EXISTS `{compartment}#{display_name}`.USER_PRIVILEGES (
                    `GRANTEE` varchar(292) NOT NULL DEFAULT '',
                    `TABLE_CATALOG` varchar(512) NOT NULL DEFAULT '',
                    `PRIVILEGE_TYPE` varchar(64) NOT NULL DEFAULT '',
                    `IS_GRANTABLE` varchar(3) NOT NULL DEFAULT '',
                    logtime DATETIME INVISIBLE,
                    INDEX logtime (logtime)
                )
            """)
            src_cur.executemany(f"""
                INSERT INTO `{compartment}#{display_name}`.USER_PRIVILEGES
                (GRANTEE, TABLE_CATALOG, PRIVILEGE_TYPE, IS_GRANTABLE)
                VALUES (%s,%s,%s,%s)
            """, rows)

            src_cur.execute(f"""
                UPDATE `{compartment}#{display_name}`.USER_PRIVILEGES
                SET logtime='{now}' WHERE logtime IS NULL
            """) 

            src_cur.execute(f"""
                DELETE FROM `{compartment}#{display_name}`.USER_PRIVILEGES
                WHERE logtime < NOW() - INTERVAL 1 DAY
            """)

            if now_dt.minute == 0:
                src_cur.execute(f"ANALYZE TABLE `{compartment}#{display_name}`.USER_PRIVILEGES")

            src_cur.close()
            src_conn.close()
            print("[USER_PRIVILEGES] done")
        except Exception as e:
            log_error(f"[USER_PRIVILEGES ERROR] {e}")

    # component METADATA
    # -----------------------
    def backup_restore_component():
        try:
            src_conn = get_conn(IP_ADDRESS, USER_NAME, MYSQL_PASSWORD)
            src_cur = src_conn.cursor()
            tgt_conn = get_conn(tgt_ip, tgt_user, tgt_pass, tgt_port)
            tgt_cur = tgt_conn.cursor()
            tgt_cur.execute("""
                SELECT component_id, component_group_id, component_urn
                FROM mysql.component
            """)
            rows = tgt_cur.fetchall()
            tgt_cur.close()
            tgt_conn.close()

            src_cur.execute(f"""
                CREATE TABLE IF NOT EXISTS `{compartment}#{display_name}`.component (
                    `component_id` int, `component_group_id` int unsigned NOT NULL, `component_urn` text NOT NULL,
                    logtime DATETIME INVISIBLE,
                    INDEX logtime (logtime)
                )
            """)
            src_cur.executemany(f"""
                INSERT INTO `{compartment}#{display_name}`.component
                (component_id,component_group_id,component_urn)
                VALUES (%s,%s,%s)
            """, rows)

            src_cur.execute(f"""
                UPDATE `{compartment}#{display_name}`.component
                SET logtime='{now}' WHERE logtime IS NULL
            """) 

            src_cur.execute(f"""
                DELETE FROM `{compartment}#{display_name}`.component
                WHERE logtime < NOW() - INTERVAL 1 DAY
            """)

            if now_dt.minute == 0:
                src_cur.execute(f"ANALYZE TABLE `{compartment}#{display_name}`.component")

            src_cur.close()
            src_conn.close()
            print("[component] done")
        except Exception as e:
            log_error(f"[component ERROR] {e}")

    # -----------------------
    # EXECUTE
    # -----------------------
    build_master_list()
    table_lines = []
    for line in MASTER_LIST.read_text().splitlines():
        parts = line.split(',')
        table = parts[0]
        retention = parts[1] if len(parts) > 1 else "7"
        table_lines.append((table, retention))

    with ThreadPoolExecutor(max_workers=32) as executor:
        futures = [executor.submit(backup_restore_table)]
        futures.append(executor.submit(backup_restore_plugins))
        futures.append(executor.submit(backup_restore_user_privileges))
        futures.append(executor.submit(backup_restore_component))
        for table, retention in table_lines:
            futures.append(executor.submit(backup_restore, table, retention))
        for f in as_completed(futures):
            f.result()

    print("ALL DONE")


# -----------------------
# RUN SCRIPT DIRECTLY
# -----------------------
if __name__ == "__main__":
    if len(sys.argv) != 9:
        print("Usage: script.py compartment display_name tgt_ip tgt_port tgt_user tgt_pass password now db_retention")
        sys.exit(1)
    main(*sys.argv[1:])
