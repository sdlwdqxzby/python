import sqlite3 as sql3
import re

def clean(data):
    con = sql3.connect(r'D:\git\python\dybz\data\record.db')
    cur = con.cursor()
    result = cur.execute('select * from pic_to_word;')
    word_list = []
    for row in result:
        word_list.append(row)
    for i in word_list:
        data = re.sub(i[0],i[1],data)
    return data

bookdir = r'D:/git/python/dybz/data/book/'
filename = '艳情短篇合集全文阅读-【夜归的女白领】作者：夜羽寒.txt'
data = ''
with open(bookdir + filename,'r') as f:
     for lines in f.readlines():
         data += lines
         data = clean(data)

with open(bookdir + filename,'w') as f:
    f.write(data)

img = re.findall('.{5}<img[^<>]*>.{5}',data)
img = list(set(img))
print(data)
a = [print(i) for i in img]
print(len(img))