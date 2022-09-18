
import pandas as pd
import openpyxl
import csv

from config import (
    CSV_RESULT,
    FILE_PATH,
    FILE_OUTPUT_EXCEL,
    FILE_PATH_LIST,
    FILE_OUTPUT_EXCEL_LIST,
)

with open(CSV_RESULT, newline='') as f:
    reader = csv.reader(f)
    location_data = list(reader)

# path = FILE_PATH

def write_to_excel(path, output_path):
    df = pd.read_excel(path)
    wb = openpyxl.load_workbook(path)
    sheet = wb['아파트 매매 실거래가']
    for i in location_data:
        for ind in df.index:
            apartment_name = sheet[f'E{ind+2}']
            address = sheet[f'A{ind+2}']
            num = sheet[f'B{ind+2}']
            location_x = sheet[f'M{ind+2}']
            location_y = sheet[f'N{ind+2}']
            if df['단지명'][ind] == i[0]:
                location_x.value = i[1]
                location_y.value = i[2]
    wb.save(output_path)



for i in range (0,len(FILE_PATH_LIST)):
    write_to_excel(FILE_PATH_LIST[i], FILE_OUTPUT_EXCEL_LIST[i])
