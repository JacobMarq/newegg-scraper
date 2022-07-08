from distutils.spawn import spawn
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager 
from bs4 import BeautifulSoup
from os import link
from os.path import exists, dirname
from newegg_scraper.constant import SOLD_BY_NE, ORDER_BY, PAGE_SIZE, PAGE_NUM, E_PER_PAGE, CSV_HEADER_1, CSV_HEADER_2, CSV_HEADER_3
from newegg_scraper.dialogue import input_error_yn, continue_scraping, prompt_complete_captcha
from collections import deque
import pandas as pd
import csv

# combine url with given params to create desired query
def append_category_url_params(url):
    new_url = url + SOLD_BY_NE + ORDER_BY + PAGE_SIZE + PAGE_NUM
    return new_url

# gather beautiful soup of url
def get_soup(url):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    content = driver.page_source
    soup = BeautifulSoup(content, features="html.parser")
    # newegg monitors traffic for bot activity 
    # redirects request to 'are you human' page
    # requires captcha
    for h1 in soup.find_all('h1'):
        print(h1)
        if h1 is not None:
            if h1.text.lower() == 'human?':
                prompt_complete_captcha()
                soup = get_soup(url)
    return soup

# add product urls to queue
def enqueue_product_urls(soup, queue):
    for div in soup.find_all('div', attrs={'class':'item-container'}):
        a = div.a
        # Motherboard RAM combos are listed in memory category
        # next 2 lines will prevent adding these combo
        # item pages to the queue
        if 'combo-img-0' in a['class']:
            continue
        href = a['href']
        queue.append(href)
    return queue

# recursively pull product urls from category pages
def parse_category_pages(url, queue=None, total_pages=None, pg=1):
    # on first loop append params to category url and pull total page number from pagination text
    if total_pages is None:
        queue = deque()
        url = append_category_url_params(url)
        soup = get_soup(url + ('% s' % pg))
        span = soup.find('span', attrs={'class':'list-tool-pagination-text'}) # contains '"Page" <!-- --> <strong> "x" <!-- --> "/" <!-- --> "y" </strong>'
        strong = span.strong.text # contains 'x/y'
        total_pages = int(strong.split('/')[1])

        queue = enqueue_product_urls(soup, queue)
        return parse_category_pages(url, queue, total_pages, pg + 1)
    elif pg > 2 or pg > total_pages: # when testing recommend hard coding a small number / for production pg > total_pages
        return queue

    soup = get_soup(url + ('% s' % pg))
    queue = enqueue_product_urls(soup, queue)
    return parse_category_pages(url, queue, total_pages, pg + 1)

# create url.csv file path
def create_url_file_path(category):
    file_name = category + '_urls.csv'
    file_dir = '/url_files/'
    file_path = dirname(__file__) + file_dir + file_name
    return file_path

# save a copy of queue to csv file
def write_queue_to_csv(queue, file):
    queue_copy = queue.copy()
    with open(file, 'x') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([CSV_HEADER_1, CSV_HEADER_2, CSV_HEADER_3]) # write header row
        entry_num = 0
        while queue_copy:
            entry_num += 1
            pg = int(entry_num / E_PER_PAGE) + 1 # determine pg number by dividing entry number by the number of entries per page
            writer.writerow([pg ,queue_copy.popleft(), entry_num])
        csv_file.close()

# append queue of new items to url file
def append_queue_to_csv(queue, entry_num, file):
    queue_copy = queue.copy()
    with open(file, 'a') as csv_file:
        writer = csv.writer(csv_file)
        while queue_copy:
            entry_num += 1
            pg = int(entry_num / E_PER_PAGE) + 1 # determine pg number by dividing entry number by the number of entries per page
            writer.writerow([pg, queue_copy.popleft(), entry_num])
        csv_file.close()

# create queue from url file
def get_queue_from_csv(file):
    queue = deque()
    with open(file, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if row:
                queue.append(row[CSV_HEADER_2])
        csv_file.close()
    return queue

# get last 20 rows including page number, url, and entry number from csv
def get_last_rows_from_csv(file):
    last_rows = []
    data = []
    with open(file, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if row:
                data.append(row)
        csv_file.close()
    # last rows set to 20 due to variance in how the page is read and exclusion of combo items
    for i in range(1, 20):
        i = i * -1
        last_rows.append(data[i])  
    return last_rows

# check if the last item, from the category page, already exists in csv file
def last_rows_contain_last_item(rows, item):
    for row in rows:
        if row[CSV_HEADER_2] == item: 
            return True
        else: 
            continue

# find all new items, appending them to new queue in proper order
def enqueue_new_items(queue, last_row):
    new_queue = deque()
    cur_item = queue.pop()
    while cur_item != last_row[CSV_HEADER_2]:
        new_queue.appendleft(cur_item)
        cur_item = queue.pop()
    return new_queue

# yes/no prompt for user
def prompt_yes_no():
    inp = input().lower()
    while inp != 'yes' and inp != 'no':
        input_error_yn()
        inp = input()
    if inp == 'yes': return True
    elif inp == 'no': return False

# handle url file update to check if new urls are needed, update file if so
def update_product_urls(file, category, category_url):
    queue = deque()
    last_rows = get_last_rows_from_csv(file) # array to store last rows scraped and added to file
    # reparse category pages starting from the last recorded page on file
    queue = parse_category_pages(category_url, queue, None, int(last_rows[0][CSV_HEADER_1]))
    last_item = queue.pop() # last item found on category page

    # check if last item already exists on file
    if last_rows_contain_last_item(last_rows, last_item):
        # allow user to continue and scrape existing url file or skip it
        continue_scraping(file)
        if prompt_yes_no(): 
            return get_product_urls(category, category_url, True)
        else: return None
    else:
        # append new items to end of csv file
        queue.append(last_item)
        queue = enqueue_new_items(queue, last_rows[0])
        append_queue_to_csv(queue, int(last_rows[0][CSV_HEADER_3]), file)
        # return queue of new items for product scraping
        return queue

# main product url collection method 
def get_product_urls(category, category_url, dont_update = False):
    # file path to store product_urls.csv file
    url_file = create_url_file_path(category)
    # if url file does exist and no new urls are needed, pull queue from file
    if exists(url_file) and dont_update:
        queue = get_queue_from_csv(url_file) 
        return queue
    # if url file exists but new urls may be needed, update file
    elif exists(url_file) and not dont_update:
        return update_product_urls(url_file, category, category_url)

    # if url file does not exist, create one
    queue = parse_category_pages(category_url)
    write_queue_to_csv(queue, url_file)
    return queue