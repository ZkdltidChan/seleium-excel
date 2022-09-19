from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from urllib.parse import urlparse
import csv
import pandas as pd
import openpyxl

from config import (
    FILE_PATH_LIST,
    FILE_PATH_OUTPUT_LIST,
    APARTMENT_CSV,
    APARTMENT_LOCATIONS_CSV,
    FAIL_LOG,
)

apartment_name_key = "단지명"
search_header = ["시군구", "번지", "단지명"]


def write_to_csv(header, path, data_list):
    with open(path, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data_list)


def drop_duplicated_apartment_data(path_list):
    data_header = []
    data_list = []
    for path in path_list:
        df = pd.read_excel(path, usecols=["시군구", "번지", "단지명"])
        for ind in df.index:
            d1 = f"{df['시군구'][ind]} {df['번지'][ind]}"
            d2 = df['단지명'][ind]
            if d2 not in data_header:
                data_header.append(d2)
                data_list.append([d1, d2])
    return data_list


def get_apartment_location_with_seleuim(data_list):
    # wait the webdriver ready
    time.sleep(5)
    css_selector = {
        'search_button': '#container > shrinkable-layout > div > app-base > search-input-box > div > div.search_box > button',
    }

    try:
        driver = webdriver.Remote(
            command_executor="http://selenium:4444/wd/hub",
            desired_capabilities=DesiredCapabilities.CHROME
        )
    except Exception as e:
        print("webdriver remote fail")
        print(e)
        exit(0)

    try:
        result_list = []
        fail_list = []
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
                url_split = url.split("address/")
                location = url_split[1].split(",")
                print(f"{address} location:{location[0]},{location[1]}")
                res = [apartment_name, location[0], location[1]]
                result_list.append(res)
            except Exception as e:
                fail_list.append([address, apartment_name])
                print(f"{address} failed add to log.. ")
                print(f"current failed counts: {len(fail_list)}")

        return result_list, fail_list
    except Exception as e:
        print(f"未知錯誤.. {e}\n")
        driver.close()


def write_to_excel(aprtment_location_csv, path, output_path):
    with open(aprtment_location_csv, newline='') as f:
        reader = csv.reader(f)
        location_data = list(reader)
    df = pd.read_excel(path)
    wb = openpyxl.load_workbook(path)
    sheet = wb['아파트 매매 실거래가']
    for i in location_data:
        for ind in df.index:
            # apartment_name = sheet[f'E{ind+2}']
            # address = sheet[f'A{ind+2}']
            # num = sheet[f'B{ind+2}']
            location_x = sheet[f'M{ind+2}']
            location_y = sheet[f'N{ind+2}']
            if df['단지명'][ind] == i[0]:
                location_x.value = i[1]
                location_y.value = i[2]
    wb.save(output_path)




try:
    search_data_list = drop_duplicated_apartment_data(FILE_PATH_LIST)
    write_to_csv(
        header=["시군구+번지", "단지명"],
        path=APARTMENT_CSV,
        data_list=search_data_list
    )
    result_list, fail_list = get_apartment_location_with_seleuim(
        search_data_list)

    # 如果有沒爬蟲成功的資料寫入fail log
    if fail_list:
        try:
            # TODO: rerun fail list
            write_to_csv(
                header=['address', 'apartment_name'],
                path=FAIL_LOG,
                data_list=fail_list
            )
        except:
            print("write fail list to csv failed")
            print("fail list: ")
            print(fail_list)

    # 將爬蟲完的檔案寫入 APARTMENT_LOCATIONS_CSV
    try:
        write_to_csv(
            header=['apartment_name', 'x', 'y'],
            path=APARTMENT_LOCATIONS_CSV,
            data_list=result_list
        )
    except:
        print("write result to csv failed")
        print("data list: ")
        print(result_list)

    # 讀取 APARTMENT_LOCATIONS_CSV 並將座標寫入各個excel檔案裡
    try:
        for i in range(0, len(FILE_PATH_LIST)):
            try:
                write_to_excel(
                    APARTMENT_LOCATIONS_CSV,
                    FILE_PATH_LIST[i], 
                    FILE_PATH_OUTPUT_LIST[i])
            except:
                print(f"寫入excel失敗, excel file name: {FILE_PATH_LIST[i]}")
    except:
        print("write result to excel failed")
except Exception as e:
    print(f"壞掉了QQ, {e}")
