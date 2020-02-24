#: -*- coding:utf-8 -*-
# !/bin/python3
# chrome: /Users/lbc/Documents/python_project/Spider/chromed
import re
import os
import csv
import codecs
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import pandas as pd
from myfirstvis.models import News
import datetime
from statsmodels.tsa.arima_model import ARIMA





def Search(url, text, browser, waiter):
    # url="http://www.jindu626.com/"
    try:
        browser.get(url)
        text_input = browser.find_element_by_xpath('//*[@id="keyboard"]')
        submit_btn = browser.find_element_by_xpath('//*[@class="cn-btn"]')

        text_input.click()
        text_input.send_keys(text)
        submit_btn.click()
        print("Browser opened URL successfully！")
        items_counts = waiter.until(
            ec.presence_of_element_located((By.XPATH, "/html/body"))
        )
        # print(items_counts.text)
        return items_counts.text
        # option + Enter 提醒库
    except TimeoutException as e:
        print("ERROR: Failed Open URL!\n", e)
        return Search(url, text)


def is_element_exits(btn_text, browser):
    try:
        status = browser.find_element_by_link_text(btn_text)
        if status is not None:
            return True
    except:

        return False


# 跳转页面成功
def next_page(browser, waiter):
    try:
        if is_element_exits("下一页", browser):
            next_btn = waiter.until(
                ec.element_to_be_clickable((By.LINK_TEXT, "下一页"))
            )
            next_btn.click()
    except TimeoutError:
        next_page(browser, waiter)


def page_count(items_count):
    items_count = re.findall(r"\d+\.?\d* 条", items_count)[0]
    items_count = re.findall(r"\d+\.?\d*", items_count)
    print("Items Counts:\t%s 条" % (items_count[0]))
    # get pages
    if int(items_count[0]) % 12 != 0:
        page_total = 1 + int(items_count[0]) / 12
    else:
        page_total = int(items_count[0]) / 12
    print("Page Numbers:\t %d 页" % (page_total))
    return page_total


def get_items(action_par, drug_name_par, province, city, county, browser, waiter,
              date_max, city2province_dict, county2province_dict):
    waiter.until(ec.presence_of_element_located((By.CLASS_NAME, "mainM")))
    results = browser.find_elements_by_class_name("searchResults")
    data_page = list()

    for item in results:
        item_details = item.text.split("\n")  # item_details[0] is title
        url_time = item_details[len(item_details) - 1]

        if "http://" in str(url_time):
            url = re.findall(r"[a-zA-z]+://[^\s]*", url_time)[0]  # news_url
        else:
            url = ''
        date = re.findall("([0-9]{3}[1-9]|[0-9]{2}[1-9][0-9]{1}|"
                          "[0-9]{1}[1-9][0-9]{2}|[1-9][0-9]{3})-"
                          "(((0[13578]|1[02])-(0[1-9]|[12][0-9]|3[01]))"
                          "|((0[469]|11)-(0[1-9]|[12][0-9]|30))|"
                          "(02-(0[1-9]|[1][0-9]|2[0-8])))", url_time)[0][0:2]
        theme = re.findall(r' - [\u4e00-\u9fa5]+', url_time)[0][3:]

        all_details = ''.join(item_details)
        # 毒品名称匹配
        drug = ''
        name = list(set(drug_name_par.findall(all_details)))
        if len(name) > 0:
            drug = ','.join(name)
        # 行为匹配
        news_action = ''
        action = list(set(action_par.findall(all_details)))
        if len(action) > 0:
            news_action = ','.join(action)

        # 地区匹配
        temp_province = []
        temp_city = []
        temp_county = []
        for x in province:
            if x in all_details:
                temp_province.append(x)
        for x in city:
            if x in all_details:
                temp_city.append(x)
        for x in county:
            if x in all_details:
                temp_county.append(x)
        # city, county --> province
        for x in temp_city:
            if x in city2province_dict:
                temp_province.append(city2province_dict[x])
        for x in temp_county:
            if x in county2province_dict:
                temp_province.append(county2province_dict[x])
        temp_province = list(set(temp_province))

        temp_province = ','.join(list(set(temp_province)))
        temp_city = ','.join(list(set(temp_city)))
        temp_county = ','.join(list(set(temp_county)))

        # 标题，主题，内容，毒品，省，市，县，网址，日期
        data_page.append([str(item_details[0]), theme, str(item_details[1]), drug,
                          temp_province, temp_city, temp_county, url, date[0] + "-" + date[1], news_action])
    count = 0
    for x in data_page:
        same_name_user = News.objects.filter(news_url=x[7])
        if x[8] < str(date_max):
            print(x[8], str(date_max))
            count += 1
        if not same_name_user:
            print(x[0])
            news = News()
            news.news_title = x[0]
            news.news_theme = x[1]
            news.news_content = x[2]
            news.news_drug = x[3]
            news.news_province = x[4]
            news.news_city = x[5]
            news.news_county = x[6]
            news.news_url = x[7]
            news.news_date = x[8]
            news.news_action = x[9]
            news.save()
        else:
            print('该新闻已被抓取！')
    if count == len(data_page):
        return True
    return False

def city_drug_pattern():
    area = pd.read_excel('data/全国省市区县行政区划明细及人口(2018最全版).xls').iloc[:, 1:4]
    # path = os.getcwd() + '/../data/'
    # area = pd.read_excel(path + '全国省市区县行政区划明细及人口(2018最全版).xls').iloc[:, 1:4]
    area.columns = ['province', 'city', 'county']
    area.province = area.province.str.replace('县|区|市|省|自治区|特别行政区|维吾尔|回族|壮族', '')
    area.city = area.city.str.replace('县|区|市|省|自治区|特别行政区|维吾尔|回族|壮族', '')
    province = list(set(area.province))
    city = list(set(area.city))
    county = list(set(area.county))
    drug_name_par = re.compile('彩虹烟|笑气|蓝精灵|咔哇潮饮|紫水|海洛因|大麻|可卡因|冰毒|K粉|k粉|吗啡|'
                               '摇头丸|麻谷|鸦片|各类毒品|各种毒品|卡痛叶|邮票|开心水|三唑仑|FIVE|止咳水|GHB|神仙水')
    action_par = re.compile('藏毒|贩毒|缴获|戒毒|禁毒|破获|吸毒|运毒|制毒|抓获|走私')

    city2province_dict = dict()
    county2province_dict = dict()
    for i in range(len(area)):
        if area.city[i] not in city2province_dict:
            city2province_dict[area.city[i]] = area.province[i]
        if area.county[i] not in county2province_dict:
            county2province_dict[area.county[i]] = area.province[i]

    return action_par, drug_name_par, province, city, county, city2province_dict, county2province_dict

def main():
    browser = webdriver.Chrome("/usr/local/bin/chromedriver")
    waiter = WebDriverWait(browser, 10)
    search_name = '毒'  # input("输入要搜索的内容：")
    items_total = Search("http://www.jindu626.com/", search_name, browser, waiter)
    print("开始查找内容，爬去数据。")
    # get items number
    page_total = page_count(items_total)
    page_index = 0
    page_counted = 0
    action_par, drug_name_par, province, city, county, city2province_dict, county2province_dict = city_drug_pattern()
    flag = False
    date_max = '2000-01-01'
    dates = News.objects.values_list("news_date", flat=True)
    if len(dates) > 0:
        date_max = max(dates)
    while (not flag) and page_index < page_total - 1:
        page_counted += 1
        flag = get_items(action_par, drug_name_par, province, city, county, browser, waiter,
                         date_max, city2province_dict, county2province_dict)

        next_page(browser, waiter)
        page_index += 1

    print("page counted number:\t", page_counted)

    date = News.objects.values_list("news_date", flat=True)
    date = pd.to_datetime(pd.Series(date))
    date = date.dt.strftime('%Y-%m')
    date = date[date > '2015-06']
    date = date.value_counts().sort_index()
    # -----------------------region1 begin------------------------
    model = ARIMA(date, order=(12, 1, 0))
    model_fit = model.fit(disp=0)
    pred1 = model_fit.forecast(6)
    x = list(date.index)
    temp = max(x)
    y = list(date)
    y_pred = list()
    for i in range(len(y) - 1):
        y_pred.append('')
    y_pred.append(y[-1])
    for t in pred1[0]:
        y_pred.append(int(t))
    for i in range(1, 7):
        temp = datetime.datetime.strptime(temp, '%Y-%m') + datetime.timedelta(days=31)
        temp = datetime.datetime.strftime(temp, '%Y-%m')
        x.append(temp)
        y.append('')
    res = pd.DataFrame()
    res['x']=x
    res['y']=y
    res['y_pred']=y_pred
    res.to_csv('data/regression.csv', index=False)


if __name__ == "__main__":
    main()
