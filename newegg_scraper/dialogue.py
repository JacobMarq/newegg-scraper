def welcome_message():
    print('\n')
    print("Welcome to Newegg Scraper!")
    print("view README.md for help with commands")
    print('\n')
    print('++++++ MENU ++++++')
    print('\n')

def select_system_type():
    print('Select system type by number:')
    print('0: All')
    print('1: Desktop')
    print('2: Server')
    print('3: Mac')

def false_save_dir_input_error():
    print('\n')
    print('ERROR: Save directory does not exist')
    print('\n')

def input_success(input):
    print('\n')
    print(input, 'Selected')
    print('++++++++++++++++++')
    print('\n')

def select_component_type(sys_type):
    if sys_type == 'Mac':
        print('Select component type by number:')
        print('0: All Components')
        print('1: RAM')
        print('2: HDD')
    else:
        print('Select component type by number:')
        print('0: All Components')
        print('1: Core Components')
        print('2: Storage Devices')
        print('3: CPU')
        print('4: RAM')
        print('5: MOBO')
        print('6: GPU')
        print('7: PSU')
        print('8: CASE')
        print('9: COOLING')

def enter_save_dir_for_product_data():
    print('Enter save directory for scraped product data:')
    print('default: save within program folder')
    print('\n')
    print('example -> full/path/to/dir')

def select_file_type():
    print('Select file type for scraped product data by number:')
    print('0: json')
    print('1: csv')

def select_pages_to_collect():
    print('Enter a number between 0 and 99 for number of pages to collect')
    print('By default there are 96 products per page')
    print('0: collect all pages')

def type_input_error(input):
    print('\n')
    if input == 'sys':
        print('ERROR: Input must be a number between 0 and 3')
    elif input == 'Mac':
        print('ERROR: Input must be a number between 0 and 2')
    elif input == 'component':
        print('ERROR: Input must be a number between 0 and 9')
    elif input == 'file':
        print('ERROR: Input must be a number between 0 and 1')
    elif input == 'pages':
        print('ERROR: Input must be a number between 0 and 99')
    print('\n')

# dialogue for product url
def continue_scraping(file):
    print('\n')
    print('No new product urls found...')
    print('Would you still like to scrape urls from existing file? (yes/no)')
    print('\n')
    print(file)

def input_error_yn():
    print("ERROR: Input must be 'yes' or 'no'")

# Only dialogue with input because it
# runs in both product_urls and products 
def prompt_complete_captcha():
    print('\n')
    print('This service is suspecting bot behavior.')
    print('please open chrome tab and complete captcha to continue.')
    print('once complete enter "done" below:')
    inp = None
    while inp != 'done':
        inp = input()