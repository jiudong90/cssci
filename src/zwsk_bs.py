import configparser
import logging
import traceback
import urllib.request
import time
import re

import math
from bs4 import BeautifulSoup
from writetosqlite import *

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select


class ZWSK:
    def __init__(self, url):
        self.__begin_url = url
        self.driver = None
        self.__urls = []

    def __set_content(self):
        try:
            self.__soup = BeautifulSoup(urllib.request.urlopen(self.__url).read(), 'lxml')
        except Exception as e:
            logging.exception(e)

    def __get_pages(self, journal, year):
        articles = []
        try:
            url = self.__begin_url + 'ly_search.html'
            # url = self.__begin_url+ 'ly_search_view.html' \
            #       + '?title='+ journal \
            #       + '+++8+++AND|||&start_year='+ year+'&end_year='+ year\
            #       + '&nian=&juan=&qi=&xw1=&xw2=&wzlx=&xkfl1=&jj=&' \
            #         'pagenum=20' \
            #         '&order_type=nian&order_px=DESC'
            # url = self.__begin_url+'?id=11G0422011010001'
            # url = r'http://cssci.nju.edu.cn/ly_search_list.html?id=11G0422011010001'
            # print(url)
            # html = urllib.request.urlopen(url, timeout=5000).read()
            # time.sleep(2)
            # print("HTML: %s" % html)

            self.driver = webdriver.Chrome()

            self.driver.get(url)
            time.sleep(3)
            self.driver.find_element_by_xpath('//input[@id="keyword_1"]').send_keys(journal)
            Select(self.driver.find_element_by_xpath('//select[@id="search_type_1"]')).select_by_value('8')
            # self.driver.find_element_by_xpath('//input[@id="qkname_1"]').click()
            Select(self.driver.find_element_by_xpath('//select[@id="start_year"]')).select_by_value(year)
            Select(self.driver.find_element_by_xpath('//select[@id="end_year"]')).select_by_value(year)
            Select(self.driver.find_element_by_xpath('//select[@id="pagenum"]')).select_by_value('50')
            self.driver.find_element_by_xpath('//img[@onclick="search()"]').click()

            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'show_table_content')))

            show_num = int(self.driver.find_element_by_id('search_daohang').find_element_by_xpath('//b[last()-1]')
                           .text.replace(',', ''))
            real_num = int(self.driver.find_element_by_id('search_daohang').find_element_by_xpath('//b[last()-3]')
                           .text.replace(',', ''))
            assert show_num == real_num

            page_num = int(math.ceil(show_num / 50.0))
            for n in range(page_num):
                logging.info('page %d' % n)
                time.sleep(1)

                html = self.driver.page_source

                soup = BeautifulSoup(html, 'lxml')
                time.sleep(5)
                # print(soup.prettify())
                for sub_tr in soup.find_all("tr"):
                    # print(sub_tr)
                    for a in sub_tr.find_all('a'):
                        if re.match('ly_search_list', a['href']):
                            sub_url= self.__begin_url + a['href']
                            print(sub_url)
                            articles.append(sub_url)
                if n < page_num-1:
                    self.driver.find_element_by_xpath('//span[@id="page_style"]/a[text()="下一页"]').click()
            logging.info('%d records are downloaded for %s in %s.' % (show_num, journal, year))
        except Exception as e:
            logging.info('No records for %s in %s.' % (journal, year))
            logging.exception(e)
        finally:
            self.driver.quit()
        return articles

    def __open_pages(self):
        if not isinstance(self.__urls, list):
            return
        for i in range(len(self.__urls)):
            url = self.__urls[i]
            self.__open_page(url)

    def __open_page(self, url):
        try:
            # url = r'http://cssci.nju.edu.cn/ly_search_list.html?id=11G0422011010001'
            # url = r'http://cssci.nju.edu.cn/ly_search_list.html?id=11G0422011010001'

            print(url)

            self.driver = webdriver.Chrome()
            self.driver.get(url)
            # self.driver.wait_for_page_to_load(self, 5000)
            time.sleep(2)
            # 未找到符合条件的记录
            # self.driver.refresh()
            # self.driver.wait_for_page_to_load(self, 5000)
            time.sleep(2)
            # timeout - Number of seconds before timing out
            # WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'show_table_content')))
            html = self.driver.page_source
            save_to_db(html)
            # soup = BeautifulSoup(html, 'lxml')
            # time.sleep(5)
            # # print(soup.prettify())
            #
            # for sub_tr in soup.find_all("tr", style=None):
            #     print(sub_tr)

        except Exception as e:
            logging.exception(e)
        finally:
            self.driver.quit()

    def get_data(self, journal, years):
        for year in years:
            print(year)
            pages = self.__get_pages(journal, year)
            self.__urls = pages
            self.__open_pages()
        return "ok"

    # scroll to the end
    def execute_times(self, times):
        for i in range(times + 1):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)


if __name__ == '__main__':
    try:
        cf = configparser.ConfigParser()
        cf.read('conf.ini')

        if cf.get('zgsk', 'log_file') == '':
            logging.basicConfig(level=logging.INFO,
                                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                                datefmt='%a, %d %b %Y %H:%M:%S,')
        else:
            logging.basicConfig(level=logging.INFO,
                                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                                datefmt='%a, %d %b %Y %H:%M:%S',
                                filename=cf.get('zgsk', 'log_file'),
                                filemode='w',
                                encode='utf-8',
                                encoding='utf-8')

        url = cf.get('zgsk', 'begin_url')
        journals = [line.strip() for line in open(cf.get('zgsk', 'journal_file'), mode='r', encoding='utf-8')]
        years = cf.get('zgsk', 'years').split(',')
        myZWSK = ZWSK(url)
        for journal in journals:
            print(journal)
            data = myZWSK.get_data(journal, years)

    except Exception as e:
        traceback.print_exc()