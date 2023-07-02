'''
UCFCrimes_Social bot

04.05.2023
'''
import requests
from math import floor
import json
from notify_case import notify_case
latest_case_id = None
import psycopg2, psycopg2.extras
import os, platform
if platform.system() == "Linux":
    if os.path.exists("/tmp/crime_social"):
        import shutil
        shutil.rmtree("/tmp/crime_social")
    os.makedirs("/tmp/crime_social")
    os.makedirs("/tmp/crime_social/chrome")
from configparser import ConfigParser
main_config = ConfigParser()
main_config.read('config.ini')
import time, calendar, datetime
table = main_config.get('postgresql', 'table')
def setup_db(main_config):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host = main_config.get('postgresql', 'host'),
        database = main_config.get('postgresql', 'database'),
        user = main_config.get('postgresql', 'user'),
        password = main_config.get('postgresql', 'password')

    )
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    return conn, cur
while True:
    conn, cur = setup_db(main_config)
    #First Run
    if not latest_case_id:
        sql = f"""
        SELECT id, case_id
        FROM {table}
        ORDER BY id DESC
        LIMIT 1
        """
        # Execute the SQL statement with fetchone() method
        cur.execute(sql)
        if cur.rowcount > 0:
            latest_case_id = cur.fetchone()['id']
        else:
            latest_case_id = None
        print(f"Started newest case is  {latest_case_id}")

    else: 
        sql = f"""
        SELECT *
        FROM {table} WHERE id > %s
        ORDER BY id ASC
        """
        cur.execute(sql, (latest_case_id,))
        if cur.rowcount > 0:
            cases = cur.fetchall()

            reached_old = False
            new_count = 0
            for case in cases:
                #print(case)
                new_count += 1
                print(f"New case {case['case_id'], case['id']}")
                notify_case(case)
            latest_case_id = cases[-1]['id']
            print(f"New cases detected  {new_count}")
        else:
            print("No new cases")
    cur.close()
    conn.close()
    conn = None
    cur = None
    # get current date and time
    now = datetime.datetime.now()
    # get the number of days in the current month
    last_day = calendar.monthrange(now.year, now.month)[1]
    # calculate time until next day at 12:05 am
    if now.day == last_day:
        target_time = datetime.datetime(now.year, now.month+1, 1, 0, 5)
    else:
        target_time = datetime.datetime(now.year, now.month, now.day+1, 0, 5)
    time_delta = target_time - now
    print(f"Sleeping until {target_time} ({time_delta})")
    seconds_until_target = time_delta.total_seconds()
    time.sleep(seconds_until_target)
    print("Running new check")

