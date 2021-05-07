# 应届生求职网

import requests
from requests.exceptions import ProxyError, ConnectTimeout
from lxml import etree
import re
import csv
import time
from useful_useragent import useful_useragent
from tqdm import tqdm  
        

def get_detail_url():
    # 搜索页
    count = 0
    total = 1
    while total > count:
        print('*' * 33)
        na_data = 0
        url = 'https://s.yingjiesheng.com/search.php?word={0}+{1}&area={2}&sort=score&start={3}'.format(key_word_1, key_word_2, area[key_word_3], count)
        print(key_word_1, key_word_2, key_word_3)
        response = requests.get(url, headers=useful_useragent(), timeout=5)
        if response.status_code == requests.codes.ok:
            html = etree.HTML(response.text)
            detail_urls = html.xpath('//h3[@class="title"]//a/@href')
            for i in detail_urls:
                try:
                    na_data += info_to_csv(i)
                except TypeError:
                    na_data += 1
            if na_data >= 9:
                return
            try:
                total = int(re.search(r'\d+', html.xpath('//div[@class="page"]/text()')[0]).group()) - 10
            except (AttributeError, IndexError):
                count += 10
                print('共计：', total, '完成：', count)
                continue
            else:
                count += 10
                print('共计：', total, '完成：', count)
            print('线程休眠5秒······')
            for x in tqdm(range(5)):
                time.sleep(1)


def info_to_csv(url):
    # 详情页
    try:
        response = requests.get(url, headers=useful_useragent(), timeout=5)
    except ConnectTimeout:
        return 1
    else:
        if response.status_code == requests.codes.ok:
            response.encoding = 'GBK'
            html = etree.HTML(response.text)
            c_name = html.xpath('//div[@class="comtit clear"]//h1/text()')
            print(c_name)
            time.sleep(1)
            if len(c_name) > 0:
                if len(c_name[0].split(']')) > 1:
                    c_name = c_name[0].split(']')[1]
                    info = html.xpath('//div[@class="comtit clear"]//span/text()')
                    main_info = ''.join(html.xpath('//div[@class="inf"]//text()')).replace('\t', '').replace('\r', '').replace('\n', '').replace(' ', '')

                    with open('职位_{0}_{1}_{2}.csv'.format(key_word_1, key_word_2, key_word_3), 'a', errors='ignore') as csvfile:
                        writer =  csv.writer(csvfile)
                        writer.writerow([c_name, info[0], info[1], info[2], main_info])
                return 0
            else:
                return 1
            
            
if __name__ == '__main__':
    positions = ['数据分析'] #'会计', '信息管理', '数据仓库'  , '数据采集'
    xueli = ['本科', '硕士'] # '大专', 
    ts = ['深圳', '北京', '上海', '广州', '郑州']

    for key_word_1 in positions:
        for key_word_2 in xueli:
            for key_word_3 in ts:
                area = {'深圳': '1102', '北京': '1056', '上海': '1349', '广州': '1085', '郑州': '2130'}

                with open('职位_{0}_{1}_{2}.csv'.format(key_word_1, key_word_2, key_word_3), 'w') as csvfile:
                    writer =  csv.writer(csvfile)
                    writer.writerow(['公司名称', '发布日期', '工作地点', '全职/兼职'])
                
                get_detail_url()