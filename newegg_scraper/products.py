from datetime import time
from distutils.spawn import spawn
from random import Random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from newegg_scraper.dialogue import prompt_complete_captcha
from bs4 import BeautifulSoup
from collections import deque
from os.path import exists
import pandas as pd
import json
import csv

def get_headers_from_csv(file: str):
    header_dict = {}
    with open(file, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        header_dict = (dict.fromkeys(list(reader)[0]))
        csv_file.close()
    return header_dict

# create header dictionary to be used for a headers list when converting to csv file
def create_header_dict(file: str):
    header_dict = {'price':None, 'image':None, 'newegg_url':None}
    if exists(file):
        header_dict = get_headers_from_csv(file)
    return header_dict

def update_header_dict(specs: dict, header_dict: dict):
    for key in specs.keys():
        if key not in header_dict:
            header_dict[key] = None
        else:
            continue
    return header_dict

# newegg monitors traffic for bot activity 
# redirects request to 'are you human' page
# requires captcha
def check_for_captcha(soup: BeautifulSoup, url: str):
        for h1 in soup.find_all('h1'):
            if h1 is not None:
                if h1.text.lower() == 'human?':
                    options = Options()
                    options.add_experimental_option('detach', True)
                    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
                    driver.get(url)
                    prompt_complete_captcha()
                    soup = get_soup(url)
        return soup

# Get beautiful soup of content from product page
def get_soup(url: str):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    content = driver.page_source
    soup = BeautifulSoup(content, features="html.parser")
    soup = check_for_captcha(soup, url)
    return soup

# handle price collection 
def get_product_price(soup: BeautifulSoup):
    price = soup.find('li', class_='price-current')
    if price is None:
        return None
    price = price.text
    if " –" in price:
        price = price[:-2]
    return price

# handle img collection
def get_product_image(soup: BeautifulSoup):
    img = soup.find('div', attrs={'style':'order:-1'})
    if img is None:
        return None
    elif img.div.img['src'] == 'https://c1.neweggimages.com/ProductImageCompressAll300/AFRX_1_201808132111656731.jpg':
        return None
    img = img.div.img['src']
    return img

# handle specification header collection
def get_spec_header(tr):
    th = tr.find('th')
    if th is None:
        return None
    # some table headers contain a question mark button that
    # displays a div giving more information about that
    # header
    
    # next 2 lines remove that button and its children
    # from the header
    if th.a is not None:
        th.a.decompose()

    if th.has_attr('class'):
        return None

    th = th.text.strip().lower()
    # Similar Products table begins with 'products' header
    # next 2 lines exits the loop before Similar Products Table
    if th == 'products':
        return th
    th = th.replace(" ", "_")
    return th

# Get product specifications
def get_product_specs(soup: BeautifulSoup):
    specs = {}
    # all items under specs tab are stored as table row
    # items under 'Compare With Similar Products' are also table rows
    for tr in soup.find_all('tr', limit=25):
        th = get_spec_header(tr)
        if th is None:
            continue
        elif th == 'products':
            break
        
        td = tr.find('td')
        if td is not None:
            td = tr.text.strip()
        
        specs[th] = td
    return specs

# parse data from product page
def parse_data(url: str):
    product = { 
        'specs': None,
        'price': None,
        'image': None,
        'newegg_url': url
    }
    soup = get_soup(url)

    price = get_product_price(soup)
    product.update({'price':price})

    img = get_product_image(soup)
    product.update({'image':img})

    specs = get_product_specs(soup)
    product.update({'specs':specs})
    return product

# handles file path creation from user input on main
def create_file_path(save_dir: str, category: str, file_type: str):
    file_path = save_dir + category + file_type
    return file_path

# convert data dictionary to json string
# write json string to file
def write_data_to_json(data: dict, file: str):
    json_string = json.dumps(data)
    file_mode = None
    if exists(file):
        file_mode = 'w'
    else:
        file_mode = 'x'
    with open(file, file_mode) as save_file:
        save_file.write(json_string)
        save_file.close()

# handle updating json file
def update_json_file(data: dict, file: str):
    file_data = None
    with open(file, 'r') as json_file:
        file_data = json.load(json_file)
        json_file.close
    file_data['products'].extend(data['products'])
    write_data_to_json(file_data, file)

# handles row creation, corrects for varying order and number of keys in dict to match csv columns
def create_row(product: dict, headers: list):
    if product['specs'] is not None:
        specs = product.pop('specs') 
        product.update(specs)
    new_dict = {}
    for header in headers:
        if header in product:
            new_dict[header] = product[header]
        else:
            new_dict[header] = None
    return new_dict

# use header dictionary and a flattened data dictionary to write csv file
def write_data_to_csv(data: list, file: str, header_dict: dict):
    # header dictionary handles the issue of having an unknown number of various headers on each product within a category  
    headers = header_dict.keys()

    with open(file, 'x') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        for product in data:
            new_dict = create_row(product, headers)
            writer.writerow(new_dict)
        csv_file.close()

# if headers match csv headers then append to file
def append_data_to_csv(data: list, file: str, header_dict: dict):
    headers = header_dict.keys()

    with open(file, 'a') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        for product in data:
            new_dict = create_row(product, headers)
            writer.writerow(new_dict)
        csv_file.close()

# merge csv data with new data, then overwrite file
def overwrite_csv(data: list, file: str, header_dict: dict):
    headers = header_dict.keys()

    with open(file, 'r+') as csv_file:
        reader = csv.DictReader(csv_file)
        data = list(reader) + data
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        for product in data:
            new_dict = create_row(product, headers)
            writer.writerow(new_dict)
        csv_file.close()

# method to handle updating product data
def handle_csv_file_update(data: list, file: str, header_dict: dict, csv_headers: dict):
    if header_dict == csv_headers:
        append_data_to_csv(data, file, header_dict)
    else:
        overwrite_csv(data, file, header_dict)

# main product data collection method
def scrape_product_data(save_dir: str, category: str, file_type: str, queue=deque()):
    data = None
    products_list = []
    file_path = create_file_path(save_dir, category, file_type)
    if file_type == '.csv':
        header_dict = create_header_dict(file_path)
        csv_headers = header_dict

    while queue:
        product_url = queue.popleft()
        product = parse_data(product_url, file_type)
        if file_type == '.csv':
            header_dict = update_header_dict(product['specs'], header_dict)
        products_list.append(product)
        time.sleep(Random.randint(0, 5))

    if file_type == '.json':
        data = {'products':products_list} # stores products in proper dict format for easy json file conversion
        
        if exists(file_path):
            update_json_file(data, file_path)
        else:
            write_data_to_json(data, file_path)
    elif file_type == '.csv':
        data = products_list # keeps products as a list to iterate for easier csv file conversion

        if exists(file_path):
            handle_csv_file_update(data, file_path, header_dict, csv_headers)
        else:
            write_data_to_csv(data, file_path, header_dict)