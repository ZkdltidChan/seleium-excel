from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
from urllib.parse import parse_qs
import csv

DATA_LIST = [
"개포2차현대아파트(220)",
"개포6차우성아파트1동~8동"
]
URL = "https://map.naver.com/v5/search"

time.sleep(5)
driver = webdriver.Remote(
    command_executor="http://selenium:4444/wd/hub",
    desired_capabilities=DesiredCapabilities.CHROME
)
css_selector = {
       'search_button': '#container > shrinkable-layout > div > app-base > search-input-box > div > div.search_box > button',
   }

result_list = []
try:
    print(f"total data: {len(DATA_LIST)}")
    for index, data in enumerate(DATA_LIST):
        res = []
        print(f"data {index+1} of {len(DATA_LIST)} ...")
        print(f"data : {data}")
        driver.get(URL)
        print(f"web is loading")
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, css_selector['search_button']))
        )
        search_box = driver.find_element_by_css_selector("div.input_box>input.input_search")
        search_box.send_keys(data)
        print(f"input search keyword :{data}")
        time.sleep(3)
        search_box.send_keys(Keys.ENTER)
        time.sleep(2)
        url = driver.current_url
        print(f"{data} URL:{url}")
        parsed_url = urlparse(url)
        captured_value = parse_qs(parsed_url.query)['c'][0]
        captured_value_split = captured_value.split(",")
        print(captured_value_split[0],captured_value_split[1])
        res = [data, captured_value_split[0], captured_value_split[1]]
        result_list.append(res)
        print("\n")
        # print(captured_value)

except Exception as e:
    print(f"error: {e}\n")
    driver.close()

csv_header = ['name', 'x', 'y']
with open('result.csv', 'w') as file:
    writer = csv.writer(file)
    writer.writerow(csv_header)
    writer.writerows(result_list)
