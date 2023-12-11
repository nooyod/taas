# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from urllib import parse
import time
import pandas as pd
import re
from tqdm import tqdm

def print_hi():
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get('http://taas.koroad.or.kr/gis/mcm/mcl/initMap.do?menuId=GIS_GMP_STS_RSN')
    time.sleep(1)

    year_start = driver.find_element(By.XPATH, '//*[@id="ptsRafYearStart"]/option[2]')
    year_start.click()
    time.sleep(1)

    year_end = driver.find_element(By.XPATH, '//*[ @ id = "ptsRafYearEnd"] / option[2]')
    year_end.click()
    time.sleep(1)

    # 체크박스 등 PM만 체
    elements = driver.find_elements(By.NAME, 'ACDNT_GAE_CODE')[0:4]
    for element in elements:
        if not element.is_selected():
            element.click()

    selectbox = driver.find_element(By.ID, 'ptsRafSigungu')
    select = Select(selectbox)
    select.select_by_value("11350")  # 전체 지역구(서울)
    time.sleep(1)

    vehicle = driver.find_element(By.XPATH, '//*[@id="ptsRaf-ACDNT_CODE"]/a')  # 가해차종 > PM만 체크
    vehicle.click()
    time.sleep(1)

    clear = driver.find_element(By.XPATH,'//*[ @ id = "chk_deselect"]')
    clear.click()
    time.sleep(1)

    pm = driver.find_element(By.XPATH, '//*[@id="ptsRafCh2AccidentType"]/li[1]/span/input')
    if not pm.is_selected():
        pm.click()

    time.sleep(1)
    # search
    driver.find_element(By.XPATH, '//*[@id="regionAccidentFind"]/div[2]/p/a').send_keys(Keys.ENTER)
    time.sleep(1)

    # Crawling
    coord_ls = []
    srs_ls = []

    for i in tqdm(range(0, 280)):
        driver.execute_script(f'gis.srh.msh.selectListUi({i}, 11);')  # 개별 사고지점
        time.sleep(1)  # 로드
        bbox = driver.find_elements(By.CLASS_NAME, 'olTileImage')[-1]
        src = parse.unquote(bbox.get_attribute('src'))  # get src and unquote from 16byte
        src_split = src.split('&')
        bbox_text = src_split[-3][5:]
        coords = [float(i) for i in bbox_text.split(',')]
        x, y = (coords[0] + coords[2]) / 2, (coords[1] + coords[3]) / 2  # center position
        srs = src_split[-4][4:]
        coord_ls.append([x, y])
        srs_ls.append(srs)

    # 데이터프레임 병합
    accident_df = pd.read_csv('accidentInfoList.csv')
    accident_df['좌표'] = coord_ls
    accident_df['좌표계'] = srs_ls
    accident_df.to_csv('accident_df.csv', index=False)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
