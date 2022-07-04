from distutils.spawn import spawn
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager 
from bs4 import BeautifulSoup
import pandas as pd

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

data = {'products': None} # Data object to store products in json format
products = [] # List to store products

# Get content from product page
driver.get("https://www.newegg.com/corsair-16gb-288-pin-ddr4-sdram/p/N82E16820236694?Item=N82E16820236694&quicklink=true")
content = driver.page_source
soup = BeautifulSoup(content)

# Product object to store product info in json format
product = { 
    'specs': None,
    'price': None,
    'img': None
}

# Get current price and main img
price = soup.find('li', class_='price-current').text
product.update({'price':price})
print(product['price'])

img = soup.find('div', attrs={'style':'order:-1'}).div.img['src']
product.update({'img':img})
print(product['img'])

# Get memory specifications
def get_memory_specs(soup):
    specs = []
    # all items under specs tab are stored as table row
    # items under 'Compare With Similar Products' are also table rows
    # 'LED color' row does not exist on all RAM product pages
    for tr in soup.find_all('tr', limit=20):
        th = tr.find('th')
        # some table headers contain a question mark button that
        # displays a div giving more information about that
        # header

        # next 2 lines remove that button and its children
        # from the header
        if th.a is not None:
            th.a.decompose()

        th = th.text.strip()
        # Similar Products table begins with 'Products' header
        # next 2 lines exits the loop before Similar Products Table
        if th == 'Products':
            break
        # comment out next lines to record following rows
        if th == 'Features':
            continue 
        if th == 'Recommend Use':
            continue
        if th == 'Date First Available':
            continue

        td = tr.find('td').text.strip()
        spec = {th:td}
        specs.append(spec)
        print(th, td)
    return specs

specs = get_memory_specs(soup)
product.update({'specs':specs})
products.append(product)

data.update({'products':products})
print(data)