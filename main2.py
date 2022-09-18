from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
import csv
import pandas
from config import (
    CSV_RESULT,
    FILE_PATH,
    FAIL_LOG,
)


df = pandas.read_excel(FILE_PATH, usecols=["시군구", "번지", "단지명"])
data_list = []
data_header = []

for ind in df.index:
    d1 = f"{df['시군구'][ind]} {df['번지'][ind]}"
    d2 = df['단지명'][ind]
    if d2 not in data_header:
        data_header.append(d2)
        data_list.append([d1, d2])

# wait the webdriver ready
time.sleep(5)
driver = webdriver.Remote(
    command_executor="http://selenium:4444/wd/hub",
    desired_capabilities=DesiredCapabilities.CHROME
)
css_selector = {
    'search_button': '#container > shrinkable-layout > div > app-base > search-input-box > div > div.search_box > button',
}


result_list = []
fail_list = []

try:
    print(f"total data: {len(data_list)}")
    for index, data in enumerate(data_list):
        print(f"data {index+1} of {len(data_list)} ...")
        address = data[0]
        apartment_name = data[1]
        try:
            res = []
            print(f"apartment name : {apartment_name}")
            driver.get("https://map.naver.com/v5/search")
            print(f"web is loading")
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, css_selector['search_button']))
            )
            search_box = driver.find_element_by_css_selector(
                "div.input_box>input.input_search")
            search_box.send_keys(address)
            print(f"input search keyword :{address}")
            time.sleep(3)
            search_box.send_keys(Keys.ENTER)
            time.sleep(2)
            url = driver.current_url
            print(f"{address} URL:{url}")
            parsed_url = urlparse(url)
            url_split = url.split("address/")
            location = url_split[1].split(",")
            print(location[0], location[1])
            res = [apartment_name, location[0], location[1]]
            result_list.append(res)
            print("\n")
        except Exception as e:
            fail_list.append([address, apartment_name])
            print(f"error: {e}\n")
except Exception as e:
    print(f"error: {e}\n")
    driver.close()

csv_header = ['apartment_name', 'x', 'y']
with open(CSV_RESULT, 'w') as file:
    writer = csv.writer(file)
    writer.writerow(csv_header)
    writer.writerows(result_list)

if fail_list:
    csv_header = ['address','apartment_name']
    with open(FAIL_LOG, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(csv_header)
        writer.writerows(result_list)
