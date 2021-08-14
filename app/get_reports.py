from bs4 import BeautifulSoup

from pathlib import Path

from termcolor import cprint
from tqdm import tqdm

from time import sleep

import requests
import os
import re

from app.main import make_report

# years = ['2019', '2020', '2021']
years = ['2021']


ignore_doc1 = '/files/citizens'
ignore_doc2 = '/files/directions'
ignore_doc3 = '/files/daily-log-562021-0'

reports_path = Path("/reports")


directory = '/path/to/reports/folder/'

def sort(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(data, key=alphanum_key)



dirl = sort(os.listdir(directory))


def report_exists(name, read_name):

    for d in dirl:
            

        if os.path.isfile(f'/path/to/reports/folder/{read_name}'):


            # print("TRUE")
            return True


        elif os.path.isfile(f'/path/to/reports/folder/{name}'):
            return True

        else:
            # print("FALSE")

            return False




def download_reports():
    year = '2021'
    url=requests.get(f"https://www.marblehead.org/police-department/pages/daily-log-{year}")
    soup = BeautifulSoup(url.content, "lxml")
    i = 0
    for a in soup.find_all('a', href=True):
        mystr= a['href']

        if "/files/" in mystr and not ignore_doc1 in mystr and not ignore_doc2 in mystr and not ignore_doc3 in mystr: 
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            url = a['href']
            resp = requests.get(url, headers=headers)
            link = resp.url
            if 'login' not in link:
                try:
                    # cprint(f"URL : {url}", 'red')
                    cprint(f"LINK : {link}", 'red')
                    print("\n")
                    i += 1
                    name = f'report-{year}-{i}.pdf'
                    read_name = f'report-{year}-{i}-read.pdf'

                    if not report_exists(name, read_name):


                        os.system(f'''wget -c --read-timeout=10 --tries=2 {link} --output-document="/path/to/reports/folder/report-{year}-{i}.pdf" ''')

                    else:

                        cprint('already exists', 'red')

                except requests.exceptions.MissingSchema:
                    pass

