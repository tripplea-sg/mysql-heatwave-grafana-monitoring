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
import hashlib
from datetime import datetime
import mysql.connector
from mysql.connector import Error
from concurrent.futures import ThreadPoolExecutor
import subprocess
import sys
import time  # for sleep

# Add /usr/local/bin to Python path to import do_monitor.py
sys.path.insert(0, "/usr/local/bin")
import do_monitor  # do_monitor.py must have a main() function

# --- Config ---
ENC_FILE = "/home/opc/.mysqlsh/plugins/grafana/mysql.pass.enc"
IP_ADDRESS = "127.0.0.1"
USER_NAME = "root"
MAX_PARALLEL = 5000

# --- Replicate bash SHA256 calculation ---
user = os.getenv("USER", "opc")  # default to opc if $USER not set
hostname = os.uname().nodename  # matches `$(hostname)` in bash

# Run the shell command and capture the output
result = subprocess.run(
    'echo "$USER@$(hostname)" | sha256sum | awk "{print $1}"', 
    shell=True, 
    capture_output=True, 
    text=True
)
AUTO_KEY = result.stdout.strip().split()[0]

print(f"[DEBUG] USER used: {user}")
print(f"[DEBUG] HOSTNAME: {hostname}")
print(f"[DEBUG] SHA256 AUTO_KEY: {AUTO_KEY}")
print(f"[DEBUG] ENC_FILE path: {ENC_FILE}")

if not os.path.isfile(ENC_FILE):
    print(f"[ERROR] Encrypted file does not exist: {ENC_FILE}")
    sys.exit(1)

try:
    result = subprocess.run([
        "openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-d", 
        "-in", ENC_FILE, 
        "-pass", f"pass:{AUTO_KEY}"
    ], capture_output=True, text=True, check=True)
    
    MYSQL_PASSWORD = result.stdout.strip()
    
except subprocess.CalledProcessError as e:
    print(f"Error during decryption: {e}")
    print(f"stderr: {e.stderr}")
    exit(1)

# --- Main loop ---
while True:
    NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{NOW}] Starting MySQL uptime check...")

    try:
        # --- Connect to config database to get targets ---
        conn = mysql.connector.connect(
            host=IP_ADDRESS,
            user=USER_NAME,
            password=MYSQL_PASSWORD,
            database="config"
        )
        cursor = conn.cursor()

        query = """
        SELECT compartment, display_name, ip_address, port, username, password,
        days_retention, minute_interval
        FROM target_database
        WHERE start_date_time<=NOW()
        AND end_date_time>=NOW()
        AND (
            (NOW() >= TIMESTAMP(CURDATE(), start_time) AND NOW() <= TIMESTAMP(CURDATE(), end_time) AND TIMESTAMP(CURDATE(), start_time)<TIMESTAMP(CURDATE(), end_time))
         OR (NOW() <= TIMESTAMP(CURDATE(), start_time) AND NOW() <= TIMESTAMP(CURDATE(), end_time) AND TIMESTAMP(CURDATE(), start_time)>TIMESTAMP(CURDATE(), end_time))
         OR (NOW() >= TIMESTAMP(CURDATE(), start_time) AND NOW() >= TIMESTAMP(CURDATE(), end_time) AND TIMESTAMP(CURDATE(), start_time)>TIMESTAMP(CURDATE(), end_time))
        );
        """
        cursor.execute(query)
        targets = cursor.fetchall()
        cursor.close()
        conn.close()

        # --- Process all targets in parallel ---
        def process_target(row):
            if len(row) < 8:
                return
            COMPARTMENT, DISPLAY_NAME, IP_ADDR, PORT, USERNAME, PASS, RETENTION, MINUTE_INTERVAL = row
            if not DISPLAY_NAME:
                return

            # --- Test target database connection ---
            is_success = 0
            try:
                test_conn = mysql.connector.connect(
                    host=IP_ADDR,
                    port=PORT,
                    user=USERNAME,
                    password=PASS,
                    connection_timeout=3
                )
                is_success = 1
                test_conn.close()
            except mysql.connector.Error:
                is_success = 0

            # --- Connect to local MySQL and insert status ---
            try:
                local_conn = mysql.connector.connect(
                    host="localhost",
                    user=USER_NAME,
                    password=MYSQL_PASSWORD
                )
                local_cursor = local_conn.cursor()
                db_name = f"{COMPARTMENT}#{DISPLAY_NAME}"
                local_cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
                local_cursor.execute(f"USE `{db_name}`")
                local_cursor.execute("""
                    CREATE TABLE IF NOT EXISTS db_status_log (
                        logtime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_success TINYINT(1)
                    )
                """)
                local_cursor.execute("INSERT INTO db_status_log (is_success) VALUES (%s)", (is_success,))
                local_conn.commit()
                local_cursor.close()
                local_conn.close()
                print(f"[{datetime.now()}] {DISPLAY_NAME}@{IP_ADDR}:{PORT} -> {'UP' if is_success else 'DOWN'}")
            except mysql.connector.Error as e:
                print(f"[ERROR] Could not log status for {DISPLAY_NAME}@{IP_ADDR}: {e}")

        with ThreadPoolExecutor(max_workers=MAX_PARALLEL) as executor:
            futures = [executor.submit(process_target, row) for row in targets]
            for future in futures:
                future.result()  # propagate exceptions if any

    except Exception as e:
        print(f"[ERROR] Failed to fetch or process targets: {e}")

    # --- Sleep for 10 seconds before next iteration ---
    time.sleep(10)
