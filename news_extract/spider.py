#: -*- coding:utf-8 -*-
# !/bin/python3
# chrome: /Users/lbc/Documents/python_project/Spider/chromed
import re
import csv
import codecs
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from myfirstvis.models import News

browser = webdriver.Chrome("/usr/local/bin/chromedriver")
waiter = WebDriverWait(browser, 10)


def Search(url, text):
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


def is_element_exits(btn_text):
    try:
        status = browser.find_element_by_link_text(btn_text)
        if status is not None:
            return True
    except:

        return False


# 跳转页面成功
def next_page():
    try:
        if is_element_exits("下一页"):
            next_btn = waiter.until(
                ec.element_to_be_clickable((By.LINK_TEXT, "下一页"))
            )
            next_btn.click()
    except TimeoutError:
        next_page()


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


def get_items(search_name):
    waiter.until(ec.presence_of_element_located((By.CLASS_NAME, "mainM")))
    results = browser.find_elements_by_class_name("searchResults")
    data_page = list()

    for item in results:
        item_details = item.text.split("\n")  # item_details[0] is title
        url_time = item_details[len(item_details) - 1]
        if "http://" in str(url_time):
            url = re.findall(r"[a-zA-z]+://[^\s]*", url_time)[0]  # news_url
            date = re.findall("([0-9]{3}[1-9]|[0-9]{2}[1-9][0-9]{1}|"
                              "[0-9]{1}[1-9][0-9]{2}|[1-9][0-9]{3})-"
                              "(((0[13578]|1[02])-(0[1-9]|[12][0-9]|3[01]))"
                              "|((0[469]|11)-(0[1-9]|[12][0-9]|30))|"
                              "(02-(0[1-9]|[1][0-9]|2[0-8])))", url_time)[0][0:2]

            print(item_details[0] + "+" + url, "+" + date[0] + "-" + date[1])
            # write_op.writerow([str(item_details[0]).encode('utf-8').decode('utf-8-sig'),url,date[0]+"-"+date[1]])
            data_page.append([str(item_details[0]), url, date[0] + "-" + date[1]])
        else:
            date = re.findall("([0-9]{3}[1-9]|[0-9]{2}[1-9][0-9]{1}|"
                              "[0-9]{1}[1-9][0-9]{2}|[1-9][0-9]{3})-"
                              "(((0[13578]|1[02])-(0[1-9]|[12][0-9]|3[01]))"
                              "|((0[469]|11)-(0[1-9]|[12][0-9]|30))|"
                              "(02-(0[1-9]|[1][0-9]|2[0-8])))", url_time)[0][0:2]

            print(item_details[0] + "+" + url, "+" + date[0] + "-" + date[1])
            # write_op.writerow([str(item_details[0]).encode('utf-8').decode('utf-8-sig'),url,date[0]+"-"+date[1]])
            data_page.append([str(item_details[0]), "none", date[0] + "-" + date[1]])

    with codecs.open(search_name + ".csv", "a", "utf_8_sig") as f:
        write_op = csv.writer(f)
        write_op.writerows(data_page)
    data_page.clear()


# def write_csv(search_name):
#     with codecs.open(search_name + ".csv", "a", "utf_8_sig") as f:
#         write_op = csv.writer(f)
#         write_op.writerow(['news_title', 'news_url', 'news_date'])
#         f.close()


def main():
    search_name = '禁毒'  # input("输入要搜索的内容：")
    items_total = Search("http://www.jindu626.com/", search_name)
    print("开始查找内容，爬去数据。")
    # get items number
    page_total = page_count(items_total)
    # write_csv(search_name)
    page_index = 0
    page_counted = 0
    while page_index < page_total - 1:
        page_counted += 1
        get_items(search_name)

        next_page()
        page_index += 1

    print("page counted number:\t", page_counted)


if __name__ == "__main__":
    main()
