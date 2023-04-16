import requests
from py_pdf_parser.loaders import load_file
from math import floor
import json
import datetime
import calendar
import time
from notify_case import notify_case


class UCFCrimesBot:
    def __init__(self, pdf_url, pdf_filename, locations):
        self.pdf_url = pdf_url
        self.pdf_filename = pdf_filename
        self.locations = locations
        self.latest_case_id = None
        self.cases = {}

    def fetch_pdf(self):
        try:
            rsp = requests.get(self.pdf_url, timeout=30)
            open(self.pdf_filename, 'wb').write(rsp.content)
        except requests.exceptions.RequestException as e:
            print(f"Error occurred while fetching the PDF: {e}")

    def parse_pdf(self):
        document = load_file(self.pdf_filename)
        parsed_current = {}
        for elem in document.elements:
            if "Bold" in elem.font and elem.font_size == 8.0 and parsed_current != {}:
                parsed_current = {}
            if elem.font_size < 9:
                parsed_current[self.locations[floor(elem.original_element.x0)]] = elem.text().replace("\n",
                                                                                                      " ").replace(
                    "Location ", "").strip()
            if len(list(parsed_current.keys())) == 8:
                self.cases[parsed_current['case_id']] = parsed_current

    def save_cases(self):
        with open("cases.json", "w") as file:
            json.dump(self.cases, file, indent=4)

    def check_for_new_cases(self):
        clist = list(self.cases.keys())
        if not self.latest_case_id:
            self.latest_case_id = clist[-1]
            print(f"Started newest case is  {self.latest_case_id}")
            self.save_cases()

        elif self.latest_case_id != clist[-1]:
            reached_old = False
            new_count = 0
            for case_id, case in self.cases.items():
                if case_id == self.latest_case_id:
                    reached_old = True
                elif reached_old:
                    new_count += 1
                    notify_case(case)
                    print(f"New case {case_id}")
            self.latest_case_id = clist[-1]
            print(f"New cases detected  {new_count}")
            self.save_cases()

    def run(self):
        while True:
            self.fetch_pdf()
            self.parse_pdf()
            self.check_for_new_cases()
            now = datetime.datetime.now()
            last_day = calendar.monthrange(now.year, now.month)[1]
            if now.day == last_day:
                target_time = datetime.datetime(now.year, now.month + 1, 1, 0, 5)
            else:
                target_time = datetime.datetime(now.year, now.month, now.day + 1, 0, 5)
            time_delta = target_time - now
            print(f"Sleeping until {target_time} ({time_delta})")
            seconds_until_target = time_delta.total_seconds()
            time.sleep(seconds_until_target)
