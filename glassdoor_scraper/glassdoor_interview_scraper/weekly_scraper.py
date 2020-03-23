from bs4 import BeautifulSoup
import requests
from time import sleep, time
from random import random, randint
import re
import scraperfunctions as sf
import datetime
import logging

import gspread
from oauth2client.service_account import ServiceAccountCredentials
# pip install gspread oauth2client
    
class Body():
    def __init__(self, company=None, question=None, answer=None, date=None, position=None, id_=None):
        self.company = company
        self.question = question
        self.answer = answer
        self.date = date
        self.position = position
        self.id_ = id_ 

def main():
    logging_file = 'weekly_scraper.log'
    logging.basicConfig(level=logging.INFO, filename=logging_file) 
    logger = logging.getLogger()

    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets' ,"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('DSChallenge-b8fbf48c5803.json', scope)
    client = gspread.authorize(creds)

    today = datetime.datetime.today()
    one_day = datetime.timedelta(days = 1)
    yesterday = today - one_day
    last_week = today - 7*one_day

    position_list = [
        "https://www.glassdoor.com/Interview/data-scientist-interview-questions-SRCH_KO0,14_SDRD_IP", 
        "https://www.glassdoor.com/Interview/machine-learning-engineer-interview-questions-SRCH_KO0,25_SDRD_IP", 
        "https://www.glassdoor.com/Interview/data-analyst-interview-questions-SRCH_KO0,12_SDRD_IP",
        "https://www.glassdoor.com/Interview/product-analyst-interview-questions-SRCH_KO0,15_SDRD_IP",
        "https://www.glassdoor.com/Interview/data-engineer-interview-questions-SRCH_KO0,13_SDRD_IP",
        "https://www.glassdoor.com/Interview/research-scientist-interview-questions-SRCH_KO0,18_SDRD_IP", 
        "https://www.glassdoor.com/Interview/analytics-engineer-interview-questions-SRCH_KO0,18_SDRD_IP", 
        "https://www.glassdoor.com/Interview/business-intelligence-interview-questions-SRCH_KO0,21_SDRD_IP"
        ]
    urls_list = []
    start_time = time()
    logger.info("Begin Collecting URLs: {}".format(str(datetime.datetime.now())))
    for url in position_list:
        i = 1
        while i:
            try:
                page = requests.get(url + str(i) + ".htm", headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36"})
            except ConnectionError:
                logger.error(ConnectionError, exc_info = True)
            soup = BeautifulSoup(page.content, 'html.parser')
            listing_date = soup.find("div", class_ = "cell alignRt noWrap minor hideHH").text
            date_object = datetime.datetime.strptime(listing_date[1:], "%b %d, %Y")
            if date_object >= last_week:
                logger.info("{}.htm".format(url + str(i)))
                urls_list.append(url + str(i) + ".htm")
                i += 1
            else:
                i = 0
    logger.info("Scraping and Pipelining")
    for title_link in urls_list:
        page_questions = []
        page = requests.get(title_link, headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36"})
        soup = BeautifulSoup(page.content, 'html.parser')
        bodies = soup.find_all("div", class_ = re.compile("interviewQuestion noPad"))
        for body in bodies:
            q1 = Body(
                company = sf.attribute_check(sf.scrape_company, body), 
                question = sf.attribute_check(sf.scrape_question,body), 
                answer = sf.attribute_check(sf.scrape_answer, body), 
                date = sf.attribute_check(sf.scrape_date, body), 
                position = sf.attribute_check(sf.scrape_position, body), 
                id_ = sf.attribute_check(sf.scrape_id, body)
            )
            try:
                listing_date_object = datetime.datetime.strptime(q1.date[1:], "%b %d, %Y")
                if listing_date_object <= yesterday and listing_date_object >= last_week:
                    page_questions.append([str(q1.company), str(q1.question), str(q1.answer), str(q1.date), str(q1.position)])
            except TypeError:
                logger.error(TypeError, exc_info = True)

            q1 = Body()
        sleep(3*random())
        current_time = time()
        elapsed_time = current_time - start_time
        i += 1
        logger.info('Request: {}; Frequency: {} request/s'.format(i, i/elapsed_time))
    
        sheet = client.open("Glassdoor Interview Questions Live").sheet1
        for row in page_questions:
            try:
                sheet.insert_row(row)
                sleep(1)
            except gspread.exceptions.APIError as APIError:
                logger.error(APIError, exc_info = True)
                sleep(10)
                sheet.insert_row(row)


    logger.info("Complete: ".format(datetime.datetime.now()))

if __name__ == "__main__":
    main()

    