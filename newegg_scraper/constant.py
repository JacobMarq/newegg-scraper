# product pages csv file headers
CSV_HEADER_1 = 'Page Number'
CSV_HEADER_2 = 'Product Page URL'
CSV_HEADER_3 = 'Entry Number'

# info for URL
# ORDER_BY = '&Order=': orders products on display page by desired metric
# set to 2 by default
# options are: [0,1,2,3,4,5]
# 0 = featured items
# 1 = lowest price
# 2 = highest price
# 3 = best selling
# 4 = best rating
# 5 = most reviews

# PAGE_SIZE = '&PageSize=': number of products displayed per page
# set to 96 by default
# options are: [36, 60, 96]

# PAGE_NUM = '&page=': current page number
# SOLD_BY_NE = %208000: sets items displayed are sold by newegg
SOLD_BY_NE = '%208000'
ORDER_BY = '&Order=2'
PAGE_SIZE = '&PageSize=96'
PAGE_NUM = '&page='
E_PER_PAGE = int(PAGE_SIZE.split('=')[1])

# Desktop core components
MEMORY_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100007611'
CPU_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100007671'
INTEL_MOBO_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100007627'
AMD_MOBO_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100007625'
GPU_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100007709'
WORKSTATION_GPU_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100008333'
CASE_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100007583'
PSU_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100007657'
CASE_FANS_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100007998'
CPU_FANS_HEATSINKS_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100008000'
LIQUID_COOLING_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100008008'
SOUND_CARD_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100161258'
# storage devices
INTERNAL_HDD_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100167523'
EXTERNAL_HDD_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100167525'
INTERNAL_SSD_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100011693'
EXTERNAL_SSD_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100011694'
ENTERPRISE_SSD_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100011695'
# Server core components
SERVER_CPU_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100008494'
SERVER_MEMORY_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100161261'
SERVER_MOBO_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100161257'
SERVER_CHASSIS_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100161262'
SERVER_PSU_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100161263'
SERVER_BAREBONES_SEARCH_URL = 'https://www.newegg.com/p/pl?N=101696295'
CONTROLLERS_RAID_CARDS_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100161256'
SERVER_RACKS_CABINETS_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100161264'
# Mac components
MAC_MEMORY_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100007968'
MAC_HDD_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100007970'

STORAGE_DEVICES = {
    'internal_hdd':INTERNAL_HDD_SEARCH_URL,
    'external_hdd':EXTERNAL_HDD_SEARCH_URL,
    'internal_ssd':INTERNAL_SSD_SEARCH_URL,
    'external_ssd':EXTERNAL_SSD_SEARCH_URL,
    'enterprise_ssd':ENTERPRISE_SSD_SEARCH_URL,
    'mac_hdd':MAC_HDD_SEARCH_URL,
}
DESKTOP = {
    'memory':MEMORY_SEARCH_URL,
    'cpu':CPU_SEARCH_URL,
    'intel_mobo':INTEL_MOBO_SEARCH_URL,
    'amd_mobo':AMD_MOBO_SEARCH_URL,
    'gpu':GPU_SEARCH_URL,
    'workstation_gpu':WORKSTATION_GPU_SEARCH_URL,
    'case':CASE_SEARCH_URL,
    'psu':PSU_SEARCH_URL,
    'case_fans':CASE_FANS_SEARCH_URL,
    'cpu_fans':CPU_FANS_HEATSINKS_SEARCH_URL,
    'liquid_cooling':LIQUID_COOLING_SEARCH_URL,
    'sound_card':SOUND_CARD_SEARCH_URL,
}
SERVER = {
    'server_cpu':SERVER_CPU_SEARCH_URL,
    'server_memory':SERVER_MEMORY_SEARCH_URL,
    'server_mobo':SERVER_MOBO_SEARCH_URL,
    'server_chassis':SERVER_CHASSIS_SEARCH_URL,
    'server_psu':SERVER_PSU_SEARCH_URL,
    'server_barebones':SERVER_BAREBONES_SEARCH_URL,
    'controllers_raid_cards':CONTROLLERS_RAID_CARDS_SEARCH_URL,
    'server_racks_cabinets':SERVER_RACKS_CABINETS_SEARCH_URL,
}
MAC = {
    'mac_memory':MAC_MEMORY_SEARCH_URL,
}

URLS = {
    'core components':{
        'desktop':DESKTOP, 
        'server':SERVER, 
        'mac':MAC
    },
    'storage devices':STORAGE_DEVICES
}

def get_category_to_scrape(sys_type, component_type):
    categories = None

    if sys_type == 'All':
        if component_type == 'All Component':
            core_components = URLS['core components']
            categories = {
                **core_components['desktop'],
                **core_components['server'],
                **core_components['mac'],
                **URLS['storage devices']
            }
        elif component_type == 'Core Components':
            core_components = URLS['core components']
            categories = {
                **core_components['desktop'],
                **core_components['server'],
                **core_components['mac'],
            }
        elif component_type == 'Storage Devices':
            categories = {
                **URLS['storage devices']
            }
        elif component_type == 'CPU':
            categories = {
                'cpu':CPU_SEARCH_URL,
                'server_cpu':SERVER_CPU_SEARCH_URL
            }
        elif component_type == 'RAM':
            categories = {
                'memory':MEMORY_SEARCH_URL,
                'server_memory':SERVER_MEMORY_SEARCH_URL,
                'mac_memory':MAC_MEMORY_SEARCH_URL
            }
        elif component_type == 'MOBO':
            categories = {
                'intel_mobo':INTEL_MOBO_SEARCH_URL,
                'amd_mobo':AMD_MOBO_SEARCH_URL,
                'server_mobo':SERVER_MOBO_SEARCH_URL
            }
        elif component_type == 'GPU':
            categories = {
                'gpu':GPU_SEARCH_URL,
                'workstation_gpu':WORKSTATION_GPU_SEARCH_URL,
            }
        elif component_type == 'PSU':
            categories = {
                'psu':PSU_SEARCH_URL,
                'server_psu':SERVER_PSU_SEARCH_URL
            }
        elif component_type == 'CASE':
            categories = {
                'case':CASE_SEARCH_URL,
                'server_chassis':SERVER_CHASSIS_SEARCH_URL,
                'server_barebones':SERVER_BAREBONES_SEARCH_URL,
                'server_racks_cabinets':SERVER_RACKS_CABINETS_SEARCH_URL
            }
        elif component_type == 'COOLING':
            categories = {
                'liquid_cooling':LIQUID_COOLING_SEARCH_URL,
                'case_fans':CASE_FANS_SEARCH_URL,
                'cpu_fans_heatsinks':CPU_FANS_HEATSINKS_SEARCH_URL
            }
    elif sys_type == 'Desktop':
        if component_type == 'All Component':
            core_components = URLS['core components']
            categories = {
                **core_components['desktop'],
                **URLS['storage devices']
            }
        elif component_type == 'Core Components':
            core_components = URLS['core components']
            categories = {
                **core_components['desktop']
            }
        elif component_type == 'Storage Devices':
            categories = {
                **URLS['storage devices']
            }
        elif component_type == 'CPU':
            categories = {
                'cpu':CPU_SEARCH_URL
            }
        elif component_type == 'RAM':
            categories = {
                'memory':MEMORY_SEARCH_URL
            }
        elif component_type == 'MOBO':
            categories = {
                'intel_mobo':INTEL_MOBO_SEARCH_URL,
                'amd_mobo':AMD_MOBO_SEARCH_URL
            }
        elif component_type == 'GPU':
            categories = {
                'gpu':GPU_SEARCH_URL,
                'workstation_gpu':WORKSTATION_GPU_SEARCH_URL
            }
        elif component_type == 'PSU':
            categories = {
                'psu':PSU_SEARCH_URL
            }
        elif component_type == 'CASE':
            categories = {
                'case':CASE_SEARCH_URL
            }
        elif component_type == 'COOLING':
            categories = {
                'liquid_cooling':LIQUID_COOLING_SEARCH_URL,
                'cpu_fans_heatsinks':CPU_FANS_HEATSINKS_SEARCH_URL,
                'case':CASE_FANS_SEARCH_URL
            }
    elif sys_type == 'Server':
        if component_type == 'All Component':
            core_components = URLS['core components']
            categories = {
                **core_components['server'],
                **URLS['storage devices']
            }
        elif component_type == 'Core Components':
            core_components = URLS['core components']
            categories = {
                **core_components['server']
            }
        elif component_type == 'Storage Devices':
            categories = {
                **URLS['storage devices']
            }
        elif component_type == 'CPU':
            categories = {
                'server_cpu':SERVER_CPU_SEARCH_URL
            }
        elif component_type == 'RAM':
            categories = {
                'server_memory':SERVER_MEMORY_SEARCH_URL
            }
        elif component_type == 'MOBO':
            categories = {
                'server_mobo':SERVER_MOBO_SEARCH_URL
            }
        elif component_type == 'GPU':
            categories = {
                'gpu':GPU_SEARCH_URL,
                'workstation_gpu':WORKSTATION_GPU_SEARCH_URL
            }
        elif component_type == 'PSU':
            categories = {
                'server_psu':SERVER_PSU_SEARCH_URL
            }
        elif component_type == 'CASE':
            categories = {
                'server_barebones':SERVER_BAREBONES_SEARCH_URL,
                'server_chassis':SERVER_CHASSIS_SEARCH_URL,
                'server_racks_cabinets':SERVER_RACKS_CABINETS_SEARCH_URL
            }
        elif component_type == 'COOLING':
            categories = {
                'liquid_cooling':LIQUID_COOLING_SEARCH_URL,
                'case':CASE_FANS_SEARCH_URL,
                'cpu_fans_heatsinks':CPU_FANS_HEATSINKS_SEARCH_URL
            }
    elif sys_type == 'Mac':
        if component_type == 'All Component':
            categories = {
                'mac_hdd': MAC_HDD_SEARCH_URL,
                'mac_ram': MAC_MEMORY_SEARCH_URL
            }
        elif component_type == 'HDD':
            categories = {
                'mac_hdd': MAC_HDD_SEARCH_URL
            }
        elif component_type == 'RAM':
            categories = {
                'mac_ram': MAC_MEMORY_SEARCH_URL
            }
    return categories