# _*_ coding: utf-8 _*_
# @Time : 2020/8/14 20:54 
# @Author : wuyiting@myhexin.com
# @File : dbf_cut.py
# @desc : cut big dbf file to small excel files

import xlsxwriter
from dbfread import DBF

print("""
用于dbf文件自动下载失败
需要切割大dbf文件为xlsx
上传后用备用抓取下载入库
""")

MAX = 5000
FILE_list = ['bond634.dbf','BOND634_O.dbf']#input('file: ') #文件名称
for FILE in FILE_list:
    table = DBF(filename=FILE, encoding='GBK')


def write_to_excel(data: [[]], path: str):
    """
    Args:
        data: [[]] double list
        path: export file path

    """
    workbook = xlsxwriter.Workbook(path)
    worksheet = workbook.add_worksheet('sheet1')
    x = 0
    for d in data:
        y = 0
        for value in d:
            worksheet.write(x, y, value)
            y += 1
        x += 1
    workbook.close()


i = 0
file_num = 0
table_list = []
for record in table:
    record_list = []

    if i == MAX:
        write_to_excel(table_list, FILE.replace('.dbf','-cut-{}.xlsx'.format(file_num)))
        table_list.clear()
        file_num += 1
        i = 0

    i += 1
    for field in record:
        v = record[field]
        record_list.append(v if v != '' else '')

    table_list.append(record_list)

write_to_excel(table_list, FILE.replace('.dbf', '-cut-{}.xlsx'.format(file_num)))
