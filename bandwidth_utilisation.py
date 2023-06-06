{\rtf1\ansi\deff0\nouicompat{\fonttbl{\f0\fnil\fcharset0 Calibri;}}
{\colortbl ;\red0\green0\blue255;}
{\*\generator Riched20 6.3.9600}\viewkind4\uc1 
\pard\sa200\sl276\slmult1\f0\fs22\lang9 # This program is free software: you can redistribute it and/or modify\par
# it under the terms of the GNU General Public License as published by\par
# the Free Software Foundation, either version 3 of the License, or\par
# (at your option) any later version.\par
#\par
# This program is distributed in the hope that it will be useful,\par
# but WITHOUT ANY WARRANTY; without even the implied warranty of\par
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the\par
# GNU General Public License for more details.\par
#\par
# You should have received a copy of the GNU General Public License\par
# along with this program. If not, see <{{\field{\*\fldinst{HYPERLINK "https://www.gnu.org/licenses/"}}{\fldrslt{https://www.gnu.org/licenses/\ul0\cf0}}}}\f0\fs22 >.\par
\par
\par
#Author : MANOJ Jagdale\par
#Description : This script calculates bandwidth utilisation based on you NIC interfaces and stores op in log file and database.\par
\par
\par
import os\par
import pyodbc\par
import datetime\par
import time\par
import sys\par
import psutil\par
\par
class BandwidthUtilization:\par
    def __init__(self, server, database, username, password):\par
        self.server = server\par
        self.database = database\par
        self.username = username\par
        self.password = password\par
        self.flush_interval_minutes = 1440\par
        self.last_flush_time = datetime.datetime.now()\par
\par
        self.connection = None\par
        self.cursor = None\par
\par
    def connect(self):\par
        connection_string = f"DRIVER=\{\{SQL Server\}\};SERVER=\{self.server\};DATABASE=\{self.database\};UID=\{self.username\};PWD=\{self.password\}"\par
        try:\par
            self.connection = pyodbc.connect(connection_string)\par
            self.cursor = self.connection.cursor()\par
            print("Database connection successful.")\par
        except pyodbc.Error as e:\par
            error_message = "Error connecting to the database: " + str(e)\par
            print(error_message)\par
            log_file.write(error_message + '\\n')\par
            log_file.flush()\par
            sys.exit(1)\par
\par
    def create_table(self):\par
        table_exists_query = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'bandwidth_utilization'"\par
        self.cursor.execute(table_exists_query)\par
        table_exists = self.cursor.fetchone()\par
\par
        if table_exists:\par
            print("Table 'bandwidth_utilization' already exists in the database.")\par
        else:\par
            create_table_query = '''\par
            CREATE TABLE bandwidth_utilization (\par
                id INT IDENTITY(1,1) PRIMARY KEY,\par
                capture_time DATETIME,\par
                utilization FLOAT,\par
                total_bytes BIGINT\par
            )\par
            '''\par
            try:\par
                self.cursor.execute(create_table_query)\par
                self.connection.commit()\par
                print("Table 'bandwidth_utilization' created successfully.")\par
            except pyodbc.Error as e:\par
                error_message = "Error creating table: " + str(e)\par
                print(error_message)\par
                log_file.write(error_message + '\\n')\par
                log_file.flush()\par
\par
    def save_data(self, capture_time, utilization, total_bytes):\par
        insert_query = '''\par
        INSERT INTO bandwidth_utilization (capture_time, utilization, total_bytes)\par
        VALUES (?, ROUND(?, 2), ?)\par
        '''\par
        self.cursor.execute(insert_query, capture_time, utilization, total_bytes)\par
        self.connection.commit()\par
        #print("Data saved successfully.")\par
\par
    def check_flush_database(self):\par
        current_time = datetime.datetime.now()\par
        time_difference_minutes = (current_time - self.last_flush_time).total_seconds() / 60\par
\par
        if time_difference_minutes >= self.flush_interval_minutes:\par
            self.flush_database()\par
            self.last_flush_time = current_time\par
\par
    def flush_database(self):\par
        truncate_query = "TRUNCATE TABLE bandwidth_utilization"\par
        self.cursor.execute(truncate_query)\par
        self.connection.commit()\par
        print("Database flushed successfully.")\par
\par
    def close_connection(self):\par
        if self.cursor is not None:\par
            self.cursor.close()\par
        if self.connection is not None:\par
            self.connection.close()\par
\par
\par
def truncate_log_file(log_path, max_size_mb):\par
    if os.path.exists(log_path):\par
        log_size = os.path.getsize(log_path) / (1024 * 1024)  \par
        if log_size > max_size_mb:\par
            with open(log_path, 'w') as log_file:\par
                log_file.truncate()\par
                print(f"Log file truncated: \{log_path\}")\par
\par
\par
if __name__ == '__main__':\par
    duration_minutes = 1\par
    ethernet_speed_mbps = 100\par
    log_file_path = 'C:\\\\Program Files\\\\Network_Monitor\\\\logs\\\\bandwidth_utilisation.log'\par
    max_log_size_mb = 100\par
\par
    utilization = BandwidthUtilization('WIN-CE50GU6N1KQ', 'tempdb', 'nuvama', 'nuvama@123')\par
\par
    truncate_log_file(log_file_path, max_log_size_mb)\par
\par
    log_file = open(log_file_path, 'a')\par
\par
    try:\par
        utilization.connect()\par
        utilization.create_table()\par
\par
        while True:\par
            bytes_sent_start = psutil.net_io_counters().bytes_sent\par
            bytes_received_start = psutil.net_io_counters().bytes_recv\par
            time.sleep(duration_minutes * 60)\par
            capture_time = datetime.datetime.now()\par
            bytes_sent_end = psutil.net_io_counters().bytes_sent\par
            bytes_received_end = psutil.net_io_counters().bytes_recv\par
            bytes_sent_total = bytes_sent_end - bytes_sent_start\par
            bytes_received_total = bytes_received_end - bytes_received_start\par
            bits_sent_total = bytes_sent_total * 8\par
            bits_received_total = bytes_received_total * 8\par
            duration_seconds = duration_minutes * 60\par
            ethernet_speed_bps = ethernet_speed_mbps * 1000000\par
            bandwidth_utilization = ((bits_sent_total + bits_received_total) / (duration_seconds * ethernet_speed_bps)) * 100\par
            total_bytes = bytes_sent_total + bytes_received_total\par
            utilization.save_data(capture_time, bandwidth_utilization, total_bytes)\par
            utilization.check_flush_database()\par
            total_bytes_gb = total_bytes / (1024 ** 3)\par
            total_bytes_mb = total_bytes / (1024 ** 2)\par
            output = f"Capture Time: \{capture_time\}, Bandwidth Utilization: \{bandwidth_utilization:.2f\}%, Total Bytes: \{total_bytes_gb:.2f\} GB / \{total_bytes_mb:.2f\} MB"\par
            print(output)\par
            log_file.write(output + '\\n')\par
            log_file.flush()\par
\par
    except Exception as e:\par
        error_message = "An error occurred: " + str(e)\par
        print(error_message)\par
        log_file.write(error_message + '\\n')\par
        log_file.flush()\par
\par
    finally:\par
        utilization.close_connection()\par
        log_file.close()\par
}
 