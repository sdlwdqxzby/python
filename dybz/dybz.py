from requests import get
from os import path,mkdir
import sqlite3 as sql3
import re
from time import sleep
import sys



class spider():
# url_ml 目录列表 [url,name]
# record_path 数据库地址位于脚本同一路径下的data文件夹中

    def __init__(self, url_rank):
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'}
        self.host = 'https://diyibanzhu9.org'
        self.url_rank = url_rank
        # 创建文件夹，若不存在则在脚本运行位置创建新文件夹
        self.dir_path = path.join(path.dirname(__file__), 'data')
        if path.exists(self.dir_path) == False:
            mkdir(self.dir_path)
        self.file_path = path.join(self.dir_path,'book')
        if path.exists(self.file_path) == False:
            mkdir(self.file_path)

        self.record_path = path.join(self.dir_path, 'record.db')

        # 待用常量
        self.title_i = ''
        self.title_ii = ''
        self.title_iii = '1'
        self.url_i = ''
        self.url_ii = ''
        self.url_iii = '1'
        self.content = '' # 章节内容


    # data =>type str;
    def clean_content(self):
        word_list = self.dbinf('select * from pic_to_word;') # [(piccode,word)(,..)]
        for i in word_list:
            self.content = self.content.replace(i[0],i[1])


    # 数据库读取
    def dbinf(self, sql, flag = 'r'):
        con = sql3.connect(self.record_path)
        cur = con.cursor()
        if flag == 'r':
            output = []
            result = cur.execute(sql)
            for row in result:
                output.append(row)
            return output
        elif flag == 'w':
            cur.execute(sql)
            con.commit()
        con.close()


    def save(self):
        filename = self.title_i + '-' + self.title_ii + '.txt'
        filename.replace('*','')
        file_path = path.join(self.file_path, filename)
        self.clean_content()
        with open(file_path,'w') as f:
            f.write(self.content)
        print('已保存，开始下一章节')


    def get_artical_list(self):
        data = get(self.url_i, headers = self.headers).text
        page_num = re.findall(r'第\s*\d+\s*\/\s*(\d+)\s*页', data)
        if page_num:
            page_num = eval(page_num[0])
        else:
            return '' # 结束函数
        output = []
        for i in range(1,page_num+1):
            perpage_url = re.sub(r'\/$', f'_{i}/', self.url_i)
            sleep(3)
            page_inf = get(perpage_url, headers = self.headers).text
            output += re.findall(r'<li>\s*<a\s*href="([^"]+)">([^<>]*)<\/a>\s*<\/li>',page_inf)
            print(f'目录第{i}页获取完毕')
        output = list(set(output))
        return output     

    def main(self):
        data = get(self.url_rank,headers = self.headers).text
        url_ml_list = re.findall('<a class="name" href="([^"]*)">([^<>]*)<\/a>', data) # [(url,title)(,...)]
        
        # 获取文章列表
        for article_i in url_ml_list:
            self.title_i = article_i[1]
            self.url_i = self.host + article_i[0]
            print(f'当前抓取：{self.title_i},{self.url_i}')
            artical_ii_list = self.get_artical_list()
            for article_ii in artical_ii_list:
                self.title_ii = article_ii[1]
                self.url_ii = self.host + article_ii[0]
                #判断链接是否存在
                sql_exist = f'''select 1 from record \
                            where url_i = "{self.url_i}" \
                                and url_ii = "{self.url_ii}"
                                and isvalid = 1;'''
                exists = self.dbinf(sql_exist)
                if exists:
                    print(f'已抓取，跳过该章')
                    continue
                print(f'开始抓取文章：{self.title_ii}')
                articl_data = get(self.url_ii, headers = self.headers).text

                # 获取三级链接目录
                artical_iii_list = re.findall(r'<a href="([^"]+)"[^<>]*>【(\d+)】<\/a>', articl_data)
                if artical_iii_list:
                    for artical_iii in artical_iii_list:
                        self.title_iii = artical_iii[1]
                        self.url_iii = self.url_i + artical_iii[0]
                        sleep(3)
                        data = get(self.url_iii).text
                        content = re.findall(r'<div class="page-content font-large">(.*?)<\/div>',data,flags=re.DOTALL)
                        if content:
                            self.content += content[0]
                else:
                    content = re.findall(r'<div class="page-content font-large">(.*?)<\/div>',data,flags=re.DOTALL)
                    if content:
                        self.content += content[0]
                
                #保存章节内容
                self.save()
                sql = f'''insert into record 
                (title_i , title_ii, url_i , url_ii) 
                values("{self.title_i}","{self.title_ii}","{self.url_i}","{self.url_ii}");'''
                self.dbinf(sql,'w')


for i in range(1,2):
    url = f'https://diyibanzhu9.org/shuku/0-allvisit-0-{i}.html'
    crawler = spider(url)
    crawler.main()