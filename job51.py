# 前程无忧

import requests
from lxml import etree
from useful_useragent import useful_useragent
from selenium.webdriver import Firefox
from selenium.webdriver import FirefoxOptions
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
from tqdm import tqdm
import csv

class job51(object):
    def __init__(self, position, lit, time):
        # 首页搜索页
        self.start_url = 'https://search.51job.com/list/000000,000000,0000,00,9,99,+,2,1.html'
        # 职位详情页url
        # 搜索关键字[职位，学历要求，工作经验]
        self.key_words = [position, lit, time]
        # 会计，
        # 大专，本科，硕士
        # 应届生，3-5年
        self.df = pd.DataFrame(columns=['职位', '日期', '地点', '网址'])
        with open('职位详情{0}_{1}_{2}.csv'.format(self.key_words[0], self.key_words[1], self.key_words[2]), 'w') as csvfile:
            writer =  csv.writer(csvfile)
            writer.writerow(['公司简介', '职位名称', '职位信息'])
        
        # 用webdriver
        options = FirefoxOptions()
        options.add_argument('-headless')
        self.browser = Firefox(options=options)
        self.wait = WebDriverWait(self.browser, 10)
        
        with open('职位详情{0}_{1}_{2}.csv'.format(self.key_words[0], self.key_words[1], self.key_words[2]), 'w') as csvfile:
                writer =  csv.writer(csvfile)
                writer.writerow(['公司简介', '职位名称', '职位信息'])
        

    def click_search_page(self):
         # 打开搜索页
        self.browser.get(self.start_url)
        time.sleep(0.5)
        # 搜索职位
        input = self.wait.until(
            EC.presence_of_element_located((
                By.XPATH, '//input[@id="keywordInput"]'))
        )
        search_btn = self.wait.until(
            EC.element_to_be_clickable((
                By.XPATH, '//button[@id="search_btn"]'))
        )
        input.send_keys(self.key_words[0])
        time.sleep(0.5)
        search_btn.click()
        time.sleep(0.5)
        
        # 选择限制条件
        # 展开选项
        e_icon = self.wait.until(
            EC.element_to_be_clickable((
                By.XPATH, '//i[@class="e_icons"]'))
        )
        e_icon.click()
        time.sleep(0.5)
        # 点击选择的学历和工作经验限制
        button_j = self.wait.until(
            EC.presence_of_element_located((
                By.XPATH, '//span[contains(text(), "{}")]//parent::a'.format(self.key_words[1])))) 
        button_j.click()
        time.sleep(0.5)
        button_xueli = self.wait.until(
            EC.presence_of_element_located((
                By.XPATH, '//span[contains(text(), "{}")]//parent::a'.format(self.key_words[2]))))
        button_xueli.click()
        time.sleep(0.5)
            
        # 获取总页数
        self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        总页数 = self.wait.until(
            EC.presence_of_element_located((
                By.XPATH, '//span[@class="td"]'))
        )
        print(self.key_words, '{}岗位'.format(总页数.text))
        
        
        for i in tqdm(range(2, int(总页数.text.split(' ')[1]))):
            time.sleep(0.5)
            # 调用pop_url等待提取数据
            self.pop_url(self.browser.page_source)
            
            # 跳转下一页
            self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(0.5)
            input_page = self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH, '//input[@id="jump_page"]')))
            for a in range(len(str(i))): # 有几位数字敲几个空格
                input_page.send_keys(Keys.BACKSPACE)
                time.sleep(0.5)
            input_page.send_keys(str(i))
            time.sleep(0.5)
            button_跳转 = self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH, '//span[contains(text(), "跳转")]')))
            button_跳转.click()
            
        # 保存为本地文件
        self.df.to_csv('搜索页{0}_{1}_{2}.csv'
        .format(self.key_words[0], self.key_words[1], self.key_words[2]))
        self.browser.close()
    
    def pop_url(self, page_source):
        # 遍历并保存搜索页中的职位信息
        # 遍历并返回搜索页面中的详情页的url
        html = etree.HTML(page_source)
        a = html.xpath('//a[@class="el"]')
        companies = html.xpath('//a[@class="cname at"]//@title')
        count = 0
        for i in a:
            self.df.loc[companies[count], :] = [
                i.xpath('.//span[@class="jname at"]//@title')[0],
                i.xpath('.//span[@class="time"]//text()')[0],
                i.xpath('.//span[@class="d at"]//text()')[0].split('|')[0],
                i.xpath('.//@href')[0]
            ]
            count += 1
    
    def for_all_details(self):
        details_url = pd.read_csv(
            '搜索页{0}_{1}_{2}.csv'
            .format(self.key_words[0], self.key_words[1], self.key_words[2]
            )).loc[:, '网址'].to_list()
        print('共{}个岗位信息'.format(len(details_url)))
        count = 0
        for url in tqdm(details_url):
            try:
                self.get_details(url)
            except:
                count += 1
                print(url)
                continue
        print('缺失数据:', count)
        
    
    def get_details(self, details_url):
        # 解析提取职位详情页信息
        response = requests.get(
            url=details_url, headers=useful_useragent(), timeout=10)
        
        if response.status_code == requests.codes.ok:
            # 改变解码方式
            response.encoding = 'GB2312'
            # print(response.status_code)
            html = etree.HTML(response.text)
            # 职位名称
            position = html.xpath(
                '//div[@class="tHeader tHjob"]//h1/@title')
            position = position[0]
            # 公司名称
            company = html.xpath(
                '//div[@class="tHeader tHjob"]//p[@class="cname"]//a[@class="catn"]//@title')
            # print(company)
            company = company[0]
            # 职位信息具体内容
            details = html.xpath(
                '//div[@class="tBorderTop_box"][1]//div[@class="bmsg job_msg inbox"]//text()')
            details_str = ''.join(details).replace(' ', '').replace('\r', '').replace('\n', '')
            # 公司简介
            company_details = html.xpath('//div[@class="com_tag"]//text()')
            company_details = ''.join(company_details).replace(' ', '').replace('\n', '').replace('\r', '')
            # 写入csv
            with open('职位详情{0}_{1}_{2}.csv'.format(self.key_words[0], self.key_words[1], self.key_words[2]), 'a') as csvfile:
                writer =  csv.writer(csvfile)
                writer.writerow([company_details, position, details_str])
                
        else:
            print("响应码错误", response.status_code)
    
    
if __name__ == '__main__':
    positions = ['数据采集', '数据分析', '数据建模', '数据仓库', '信息管理', '会计']
    xueli = ['大专', '本科', '硕士']
    ts = ['应届', '5年']
    for p in positions:
        for l in xueli:
            for t in ts:
                job51_1 = job51(p, l, t)
                job51_1.click_search_page()
                job51_1.for_all_details()