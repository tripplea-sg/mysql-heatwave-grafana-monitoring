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

# Add /usr/local/bin to Python path to import do_monitor.py
sys.path.insert(0, "/usr/local/bin")
import do_monitor  # do_monitor.py must have a main() function
import custom_monitor

# --- Config ---
ENC_FILE = "/home/opc/.mysqlsh/plugins/grafana/mysql.pass.enc"
IP_ADDRESS = "127.0.0.1"
USER_NAME = "root"
MASTER_LIST_FILE = "/home/opc/mysql_monitoring/all_tables_reference.txt"
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

# Get the output (the AUTO_KEY)
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
#    print(f"Decrypted password: {MYSQL_PASSWORD}")
    
except subprocess.CalledProcessError as e:
    print(f"Error during decryption: {e}")
    print(f"stderr: {e.stderr}")
    exit(1)

# --- Connect to MySQL ---
try:
    conn = mysql.connector.connect(
        host=IP_ADDRESS,
        user=USER_NAME,
        password=MYSQL_PASSWORD,
        database="config"
    )
except Error as e:
    print(f"Error connecting to MySQL: {e}")
    exit(1)

cursor = conn.cursor()

# --- Query 1: Master list ---
query1 = """
SELECT table_name, days_retention
FROM performance_schema_table
WHERE start_date_time<=NOW()
AND end_date_time>=NOW()
AND IFNULL(table_name,'')<>'';
"""
cursor.execute(query1)
master_list = [(row[0], row[1]) for row in cursor.fetchall()]

# Optional: write master list to file
os.makedirs("/home/opc/mysql_monitoring", exist_ok=True)
with open(MASTER_LIST_FILE, "w") as f:
    for table_name, days_retention in master_list:
        f.write(f"{table_name}\t{days_retention}\n")

# --- Query 2: Targets ---
query2 = """
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
cursor.execute(query2)
targets = cursor.fetchall()
cursor.close()
conn.close()

NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- Function to process a single target ---
def custom_process_target(row):
    if len(row) < 8:
        return
    COMPARTMENT, DISPLAY_NAME, IP_ADDRESS, PORT, USERNAME, PASS, RETENTION, MINUTE_INTERVAL = row

    if not DISPLAY_NAME:
        return

    print(f"Call custom-monitor for {DISPLAY_NAME}")

    custom_monitor.main(
            COMPARTMENT,
            DISPLAY_NAME,
            IP_ADDRESS,
            PORT,
            USERNAME,
            PASS,
            MYSQL_PASSWORD,  # pass the already decrypted password
            NOW,
            RETENTION
        )

# --- Function to process a single target ---
def process_target(row):
    if len(row) < 8:
        return
    COMPARTMENT, DISPLAY_NAME, IP_ADDRESS, PORT, USERNAME, PASS, RETENTION, MINUTE_INTERVAL = row

    if not DISPLAY_NAME:
        return

    base_dir = f"/home/opc/mysqlsh/plugins/grafana/{COMPARTMENT}/{DISPLAY_NAME}"
    os.makedirs(base_dir, exist_ok=True)
    tick_file = os.path.join(base_dir, "tick")

    # Read current tick
    if os.path.isfile(tick_file):
        try:
            with open(tick_file, "r") as f:
                current_val = int(f.read().strip())
        except:
            current_val = 0
    else:
        current_val = 0
        with open(tick_file, "w") as f:
            f.write("0")

    new_val = current_val + 1

    if new_val >= int(MINUTE_INTERVAL):
        if os.path.exists(tick_file):
            os.remove(tick_file)

        print(f"Call do-monitor for {DISPLAY_NAME}")

        # Call do_monitor.py directly as a Python function
        do_monitor.main(
            COMPARTMENT,
            DISPLAY_NAME,
            IP_ADDRESS,
            PORT,
            USERNAME,
            PASS,
            MYSQL_PASSWORD,  # pass the already decrypted password
            NOW,
            RETENTION
        )
    else:
        with open(tick_file, "w") as f:
            f.write(str(new_val))

# --- Run all targets in parallel ---
with ThreadPoolExecutor(max_workers=MAX_PARALLEL) as executor:
    futures = [executor.submit(process_target, row) for row in targets]
    futures.extend([executor.submit(custom_process_target, row) for row in targets])
    for future in futures:
        future.result()  # propagate exceptions if any

# --- Print resource usage ---
os.system("times")
