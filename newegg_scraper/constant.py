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
WORKSTATION_GPU_SEARCH_URL = ''
CASE_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100007583'
PSU_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100007657'
CASE_FANS_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100007998'
CPU_FANS_HEATSINKS_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100008000'
LIQUID_COOLING_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100008008'
SOUND_CARD_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100161258'
# Desktop storage devices
INTERNAL_HDD_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100167523'
EXTERNAL_HDD_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100167525'
INTERNAL_SSD_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100011693'
EXTERNAL_SSD_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100011694'
ENTERPRISE_SSD_SEARCH_URL = 'https://www.newegg.com/p/pl?N=100011695'
# Server core components
SERVER_CPU_SEARCH_URL = ''
SERVER_MEMORY_SEARCH_URL = ''
SERVER_MOBO_SEARCH_URL = ''
SERVER_CHASSIS_SEARCH_URL = ''
SERVER_PSU_SEARCH_URL = ''
SERVER_BAREBONES_SEARCH_URL = ''
CONTROLLERS_RAID_CARDS_SEARCH_URL = ''
SERVER_RACKS_CABINETS_SEARCH_URL = ''
# Mac components
MOBILE_CPU_SEARCH_URL = ''
MAC_MEMORY_SEARCH_URL = ''
MAC_HDD_SEARCH_URL = ''
# Laptop components

DESKTOP_CORE_COMPONENTS = {
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
DESKTOP_STORAGE_DEVICES = {
    'internal_hdd':INTERNAL_HDD_SEARCH_URL,
    'external_hdd':EXTERNAL_HDD_SEARCH_URL,
    'internal_ssd':INTERNAL_SSD_SEARCH_URL,
    'external_ssd':EXTERNAL_SSD_SEARCH_URL,
    'enterprise_ssd':ENTERPRISE_SSD_SEARCH_URL,
}
SERVER_CORE_COMPONENTS = {
    'server_cpu':SERVER_CPU_SEARCH_URL,
    'server_memory':SERVER_MEMORY_SEARCH_URL,
    'server_mobo':SERVER_MOBO_SEARCH_URL,
    'server_chassis':SERVER_CHASSIS_SEARCH_URL,
    'server_psu':SERVER_PSU_SEARCH_URL,
    'server_barebones':SERVER_BAREBONES_SEARCH_URL,
    'controllers_raid_cards':CONTROLLERS_RAID_CARDS_SEARCH_URL,
    'server_racks_cabinets':SERVER_RACKS_CABINETS_SEARCH_URL,
}
MAC_COMPONENTS = {
    'mobile_cpu':MOBILE_CPU_SEARCH_URL,
    'mac_memory':MAC_MEMORY_SEARCH_URL,
    'mac_hdd':MAC_HDD_SEARCH_URL,
}