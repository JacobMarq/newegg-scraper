import csv
from collections import deque
from bs4 import BeautifulSoup
from os.path import exists, dirname

from newegg_scraper.constant import SOLD_BY_NE, ORDER_BY, PAGE_SIZE, PAGE_NUM, E_PER_PAGE, CSV_HEADER_1, CSV_HEADER_2, CSV_HEADER_3
from newegg_scraper.dialogue import input_error_yn, continue_scraping
from newegg_scraper.interface import get_soup, check_for_captcha, handle_captcha

# add product urls to queue
def enqueue_product_urls(soup: BeautifulSoup, queue: deque):
    for div in soup.find_all('div', attrs={'class':'item-container'}):
        if div is None:
            return queue

        a = div.a
        # Motherboard RAM combos are listed in memory category
        # next 2 lines will prevent adding these combo
        # item pages to the queue
        if a is None:
            continue
        elif 'combo-img-0' in a['class']:
            continue
        href = a['href']
        queue.append(href)
    return queue

def create_product_queue_from_category(url: str, pgs_to_collect=0, pg=1):
    queue = deque()
    total_pages = 0
    url = url + SOLD_BY_NE + ORDER_BY + PAGE_SIZE + PAGE_NUM

    while pg <= total_pages or total_pages == 0:
        soup = get_soup(url + ('% s' % pg))
        if check_for_captcha(soup):
            handle_captcha(url)
            soup = get_soup(url)

        if total_pages == 0:
            span = soup.find('span', attrs={'class':'list-tool-pagination-text'}) # contains: '"Page" <!-- --> <strong> "x" <!-- --> "/" <!-- --> "y" </strong>'
            strong = span.strong.text # contains: 'x/y'
            total_pages = int(strong.split('/')[1])
        if pg > total_pages:
            break
            
        if pgs_to_collect == 0 or pgs_to_collect + (pg - 1) > total_pages:
            pgs_to_collect = total_pages
        elif (pg - 1) + pgs_to_collect < total_pages:
            total_pages = pgs_to_collect + (pg - 1)
            
        queue = enqueue_product_urls(soup, queue)
        pg += 1
    return queue

# create url.csv file path
def create_url_file_path(category: str):
    file_name = category + '_urls.csv'
    file_dir = '/url_files/'
    file_path = dirname(__file__) + file_dir + file_name
    return file_path

# save a copy of queue to csv file
def write_queue_to_csv(queue: deque, file: str):
    with open(file, 'x') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([CSV_HEADER_1, CSV_HEADER_2, CSV_HEADER_3])
        entry_num = 0
        while queue:
            entry_num += 1
            pg = int(entry_num / E_PER_PAGE) + 1 # provides an estimate of pg number by dividing entry number by the number of entries per page
            writer.writerow([pg ,queue.popleft(), entry_num])

# append queue of new items to url file
def append_queue_to_csv(queue: deque, entry_num: int, file: str):
    with open(file, 'a') as csv_file:
        writer = csv.writer(csv_file)
        while queue:
            entry_num += 1
            pg = int(entry_num / E_PER_PAGE) + 1 # provides an estimate of pg number by dividing entry number by the number of entries per page
            writer.writerow([pg, queue.popleft(), entry_num])

# get last 20 rows including page number, url, and entry number from csv
def get_last_rows_from_csv(file: str):
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
        if len(data) < i:
            break
        i = i * -1
        last_rows.append(data[i])  
    return last_rows

def last_rows_contain_last_item(rows: list, item: str):
    for row in rows:
        if row[CSV_HEADER_2] == item: 
            return True
        else: 
            continue
    return False

# uses the last item from csv file as a marker for when new items in the queue start
def enqueue_new_items(queue: deque, last_row: dict):
    new_queue = deque()
    cur_item = queue.pop()
    while cur_item != last_row[CSV_HEADER_2]:
        new_queue.appendleft(cur_item)
        cur_item = queue.pop()
    return new_queue

def prompt_yes_no():
    inp = input().lower()
    while inp != 'yes' and inp != 'no':
        input_error_yn()
        inp = input()
    if inp == 'yes': return True
    elif inp == 'no': return False

# handle url file update to check if new urls exist
def update_product_urls(file: str, category: str, category_url: str, pgs_to_collect: int):
    queue = deque()
    # get the last rows from csv to compare to the current site for changes
    last_rows = get_last_rows_from_csv(file) 
    queue = create_product_queue_from_category(category_url, pgs_to_collect, int(last_rows[0][CSV_HEADER_1]))
    last_item = queue.pop()

    if last_rows_contain_last_item(last_rows, last_item):
        continue_scraping(file)
        if prompt_yes_no(): 
            return get_product_urls(category, category_url, True)
        else: return None
    else:
        queue.append(last_item)
        queue = enqueue_new_items(queue, last_rows[0])
        append_queue_to_csv(queue, int(last_rows[0][CSV_HEADER_3]), file)
        return int(last_rows[0][CSV_HEADER_1])

# create queue list from url file
def get_queue_list_from_csv(file: str, pg_num=1):
    queue_list = []
    queue = deque()

    with open(file, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if row:
                if pg_num < int(row[CSV_HEADER_1]):
                    queue_list.append(queue)
                    queue = deque()
                    pg_num += 1
                elif pg_num > int(row[CSV_HEADER_1]):
                    continue

                queue.append(row[CSV_HEADER_2])
    queue_list.append(queue)
    return queue_list

# main product url collection method 
def get_product_urls(category: str, category_url: str, pgs_to_collect: int, dont_update = False):
    url_file = create_url_file_path(category)

    if exists(url_file) and dont_update:
        queue_list = get_queue_list_from_csv(url_file) 
        return queue_list
    elif exists(url_file) and not dont_update:
        pg_num = update_product_urls(url_file, category, category_url, pgs_to_collect)
        queue_list = get_queue_list_from_csv(url_file, pg_num)
        return queue_list

    queue = create_product_queue_from_category(category_url, pgs_to_collect)
    write_queue_to_csv(queue, url_file)
    queue_list = get_queue_list_from_csv(url_file)
    return queue_list