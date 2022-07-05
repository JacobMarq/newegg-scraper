from collections import deque
import os.path
import dialogue
import constant
from product_urls import get_product_urls

def welcome():
    dialogue.welcome_message()

# set desired system type
def input_system_type():
    dialogue.select_system_type()
    sys_type = int(input())

    while sys_type < 0 or sys_type > 4:
        dialogue.type_input_error('sys')
        dialogue.select_system_type()
        sys_type = int(input())

    if sys_type == 0:
        sys_type = 'All'
    elif sys_type == 1:
        sys_type = 'Desktop'
    elif sys_type == 2:
        sys_type = 'Server'
    elif sys_type == 3:
        sys_type = 'Mac'
    elif sys_type == 4:
        sys_type = 'Laptop'

    dialogue.input_success(sys_type)
    return sys_type

# set desired component types
def input_component_type():
    dialogue.select_component_type()
    component_type = int(input())

    while component_type < 0 or component_type > 9:
        dialogue.type_input_error('component')
        dialogue.select_component_type()
        component_type = int(input())

    if component_type == 0:
        component_type = 'All Components'
    elif component_type == 1:
        component_type = 'Core Components'
    elif component_type == 2:
        component_type = 'Storage Devices'
    elif component_type == 3:
        component_type = 'CPU'
    elif component_type == 4:
        component_type = 'RAM'
    elif component_type == 5:
        component_type = 'MOBO'
    elif component_type == 6:
        component_type = 'GPU'
    elif component_type == 7:
        component_type = 'PSU'
    elif component_type == 8:
        component_type = 'CASE'
    elif component_type == 9:
        component_type = 'COOLING'

    dialogue.input_success(component_type)
    return component_type

# set save directory for product data
def input_save_dir():
    dialogue.enter_save_dir_for_product_data()
    save_dir = input()

    while not os.path.isdir(save_dir) and save_dir.lower() != 'default':
        dialogue.false_save_dir_input_error()
        dialogue.enter_save_dir_for_product_data()
        save_dir = input()

    if save_dir.lower() == 'default':
        save_dir = os.path.dirname(__file__) + '/scraped_product_data'

    dialogue.input_success(save_dir)
    return save_dir

# decide file type for product data
def input_file_type():
    dialogue.select_file_type()
    file_type = int(input())

    while file_type < 0 or file_type > 1:
        dialogue.type_input_error('file')
        dialogue.select_file_type
        file_type = int(input())

    if file_type == 0:
        file_type = 'json'
    elif file_type == 1:
        file_type = 'csv'

    dialogue.input_success(file_type)
    return file_type

def determine_categories_to_scrape(sel):
    categories = None
    if sel == 'All All Components':
        categories = {
            **constant.DESKTOP_CORE_COMPONENTS, 
            **constant.DESKTOP_STORAGE_DEVICES, 
            **constant.SERVER_CORE_COMPONENTS, 
            **constant.MAC_COMPONENTS,
            }
    elif sel == 'Desktop All Components':
        categories = {
            **constant.DESKTOP_CORE_COMPONENTS,
            **constant.DESKTOP_STORAGE_DEVICES
        }
    elif sel == 'Desktop Core Components':
        categories = {**constant.DESKTOP_CORE_COMPONENTS}
    elif sel == 'Desktop Storage Devices':
        categories = {**constant.DESKTOP_STORAGE_DEVICES}
    elif sel == 'Server Core Components':
        categories = {**constant.SERVER_CORE_COMPONENTS}

    return categories

if __name__ == "__main__":
    welcome()
    sys_type = input_system_type()
    component_type = input_component_type()
    save_dir = input_save_dir()
    file_type = input_file_type()

    sel = sys_type + ' ' + component_type
    categories = determine_categories_to_scrape(sel)
    for category in categories:
        queue = get_product_urls(category, categories[category])
        print(queue)
    
