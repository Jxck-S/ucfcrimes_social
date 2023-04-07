'''
UCFCrimes bot

03.22.2023
'''
pdf_filename = 'AllDailyCrimeLog.pdf'
import requests
from py_pdf_parser.loaders import load_file
from math import floor
import json
import datetime
import datetime
import calendar
import time
from notify_case import notify_case
latest_case_id = None
locations = {200: "campus", 272: "disposition", 555: "location", 480: "occur_end", 423: "occur_start", 88: "type", 37: "case_id", 343: "reported_dt"}

while True:
    rsp = requests.get("https://police.ucf.edu/sites/default/files/logs/ALL%20DAILY%20crime%20log.pdf", timeout=30)
    open(pdf_filename, 'wb').write(rsp.content)
    document = load_file(pdf_filename)
    cases = []
    cases = {}
    parsed_current = {}
    for elem in document.elements:
        if "Bold" in elem.font and elem.font_size == 8.0 and parsed_current != {}:
            #print("clearing ", parsed_current)
            parsed_current = {}
        #print(elem.text())

        if elem.font_size < 9:
            parsed_current[locations[floor(elem.original_element.x0)]] = elem.text().replace("\n", " ").replace("Location ", "").strip()
        #print(parsed_current)
        if len(list(parsed_current.keys())) == 8:
            cases[parsed_current['case_id']] = parsed_current
    clist = list(cases.keys())
    if not latest_case_id:
        latest_case_id = clist[-1]
        print(f"Started newest case is  {latest_case_id}")
        #print(json.dumps(cases, indent=4))
        with open("cases.json", "w") as file:
            json.dump(cases, file, indent=4)


    elif latest_case_id != clist[-1]:

        reached_old = False
        new_count = 0
        for case_id, case in cases.items():
            if case_id == latest_case_id:
                reached_old = True
            elif reached_old:
                new_count += 1
                notify_case(case)
                print(f"New case {case_id}")
        latest_case_id = clist[-1]
        print(f"New cases detected  {new_count}")

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