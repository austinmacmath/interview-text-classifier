import re
import logging

logging_file = 'weekly_scraper.log'
logging.basicConfig(level=logging.INFO, filename=logging_file) 
logger = logging.getLogger()

def scrape_company(body):
    company = body.find("span", class_ = "authorInfo").text
    start = company.index(" at ") + 4
    end = company.index(" was asked...")
    company = company[start: end]
    return company#.encode('utf-8')

def scrape_question(body):
    question = body.find("p", class_ = "questionText h3").text
    return question#.encode('utf-8')

def scrape_answer(body):
    answer_text = []
    answers = body.find_all("p", class_ = re.compile("cell noMargVert"))
    for answer in answers:
        answer_text.append(answer.text.encode('utf-8').decode('utf-8'))
    return answer_text

def scrape_date(body):
    date = body.find("div", class_ = "cell alignRt noWrap minor hideHH").text
    return date

def scrape_position(body):
    position = body.find("span", class_ = "authorInfo").text
    start = 0
    end = position.index(" at ")
    position = position[start: end]
    return position#.encode('utf-8')

def scrape_id(body):
    id_ = body.find_parent("div").get("id")
    return id_

def attribute_check(func, body):
    try:
        return func(body)
    except AttributeError:
        logger.error(AttributeError, exc_info = True)