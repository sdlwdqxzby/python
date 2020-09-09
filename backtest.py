# encoding:utf-8
import json,os,sys,datetime,time,csv
from urllib import request
import pandas as pd
from dateutil.relativedelta import relativedelta


'''
http://backtest.10jqka.com.cn/
依附于backtest量化平台，使用平台处理条件得到结果
'''


'''
period    回测持有时间
query    回测请求条件
start_date 历史记录开始日期
end_date    历史记录结束记录
'''


class quant():

    def __init__(self,query,period='1,2,3,4,5,10,20'):
        today = datetime.datetime.today()
        end_date = today.strftime('%Y-%m-%d')
        start_date = (today - relativedelta(years =1)).strftime('%Y-%m-%d')
        self.start_date = start_date
        self.end_date = end_date
        self.period = period
        self.query = query
        self.conditionData = [] #保存页面解析成的条件
        self.id = ''
        self.headers = {'Content-Type':'application/json;charset=UTF-8'}
        self.host = 'http://backtest.10jqka.com.cn/backtestonce'
        self.path = os.path.join(os.path.expanduser('~'), 'Desktop','quant_result')
        self.path_his = os.path.join(self.path,'history')
        if os.path.exists(self.path) is False:
            os.mkdir(self.path)
        if os.path.exists(self.path_his) is False:
            os.mkdir(self.path_his)



#策略整体回测效果整理
    def result_backtest(self):
        print(f'当前条件：{self.query}')
        url =  self.host + '/backtest'
        params = {}
        params['start_date'] = self.start_date
        params['end_date'] = self.end_date
        params['period'] = self.period
        params['query'] = self.query
        params = json.dumps(params)
        params = bytes(params,'utf8')
        req = request.Request(url = url ,data = params,headers = self.headers,method='POST')
        data = request.urlopen(req).read().decode('UTF-8')
        data_json = json.loads(data)
        self.id = data_json['result']['id'] #保存id用于获取回测结果股票结果集
        conditionData = data_json['result']['conditionData']
        self.conditionData = ";".join(conditionData)
        backtestData_list = []
        #回测结果分析，根据持股时间返回结果
        backtestData = data_json['result']['backtestData']
        for i in backtestData:
            period = i['daySaleStrategy']  # 持股时间
            hs300AverageIncome = i['hs300AverageIncome']  # 同期基准
            averageLossRatio = i['averageLossRatio']  # 盈亏比
            winRate = i['winRate']  # 上涨概率
            hs300WinRate = i['hs300WinRate']  # 基准上涨概率
            averageChangeRate = i['averageChangeRate']  # 平均区间涨幅
            maxChangeRate = i['maxChangeRate']  # 最大涨跌幅
            minChangeRate = i['minChangeRate']  # 最小涨跌幅
            highProbability = i['highProbability']  # 次日高开概率
            averageOpenIncome = i['averageOpenIncome']  # 次日开盘平均涨幅
            backtestData_list.append([
                self.conditionData,
                self.start_date,
                self.end_date,
                str(period),
                winRate,
                highProbability,
                averageOpenIncome,
                averageLossRatio,
                hs300AverageIncome,
                hs300WinRate,
                averageChangeRate,
                maxChangeRate,
                minChangeRate
            ])
        save = '1'#input('是否保存结果（1/0）：')
        if save == '1':
            columns = ['查询条件', '回测起始日', '回测截止日', '持股时间', '上涨概率', '次日高开频率', '次日开盘平均涨幅', '盈亏比',
                       '同期基准', '基准上涨概率', '平均区间涨幅', '最大涨跌幅', '最小涨跌幅']
            datasave_csv(data=backtestData_list,path = self.path,name = '回测分析',columns=columns,tag = 4)

#历史明细查询
    def result_historydetail(self):
        period_list = self.period.split(',')
        save = '1'#input('是否保存历史明细（1/0）：')
        if save == '1':
            historyData_list = []
            for i in period_list:
                print('抓取历史明细,持股周期:%s 天'%(i))
                url = self.host + '/historydetail?sort_by=desc&id={}&start_date={}&end_date={}&period={}' \
                    .format(self.id, self.start_date, self.end_date, i)
                req = request.Request(url=url, headers=self.headers)
                data = request.urlopen(req).read().decode('UTF-8')
                data_json = json.loads(data)
                historyData = data_json['result']
                period = i
                for seq in historyData:
                    stock_code = seq['stock_code']
                    stock_name = seq['stock_name']
                    start_date = seq['start_date']
                    end_date = seq['end_date']
                    start_price = seq['start_price']
                    end_price = seq['end_price']
                    change_rate = seq['change_rate']
                    historyData_list.append([
                        self.conditionData,
                        str(period),
                        stock_code,
                        stock_name,
                        start_date,
                        end_date,
                        start_price,
                        end_price,
                        change_rate
                    ])
            columns = ['查询条件', '持股时间','代码','简称','持股起始日',
                           '持股截止日','持股起始价','持股截止价','涨幅']
            datasave_csv(data = historyData_list,path = self.path_his,name = self.query + '_历史明细',columns=columns,tag = 6)



#----独立功能----#


'''
将指标细分为多个维度的指标
XXX&&XXX,将&&替换成为更为细化的数字。带入字段，形成条件的list返回
精确位数
start_num 必须小于 end_num
且两个数都需要是整数
'''
def split_quant(text,start_num,end_num,n=0):
    if start_num > end_num:
        print('输入有误')
        sys.exit(0)#报错退出，结束程序
    else:
        output =[]
        var = 1 / (10 ** n) #表示这个数量级的最小数
        while start_num <= end_num:
            text_change = text.replace('&&',str(start_num))
            output.append(text_change)
            start_num += var
            if n == 0:
                start_num = round(start_num)
            else:
                start_num = round(start_num,n)
        return output

'''
文档保存
'''
def datasave_excel(data,path,tag,name,columns):
    file_path = os.path.join(path, name + '.xlsx')  # 文件路径
    #桌面不存在文件夹就创建结果文件夹
    try:
        file = pd.ExcelFile(file_path)
        data_file = pd.read_excel(file,dtype = str).values.tolist()
        data = data_file + data
    except:
        pass
    output = []
    permary_key_list = []
    for n in data:
        permary_key = n[:tag] #切片将前几行作为主键判断是否入库
        if permary_key not in permary_key_list:
            output.append(n)
            permary_key_list.append(permary_key)
    df = pd.DataFrame(output,columns = columns)
    with pd.ExcelWriter(file_path) as witer:
        df.to_excel(excel_writer=witer,index=False)

def datasave_csv(data,path,tag,name,columns):
    file_path = os.path.join(path, name + '.csv')  # 文件路径
    #桌面不存在文件夹就创建结果文件夹
    try:
        data_file = []
        with open(file_path) as f:
            file = csv.reader(f)
            for row in file:
                if row != columns:
                    data_file.append(row)
        data = data_file + data
    except:
        pass
    output = []
    permary_key_list = []
    for n in data:
        permary_key = n[:tag] #切片将前几行作为主键判断是否入库
        if permary_key not in permary_key_list:
            output.append(n)
            permary_key_list.append(permary_key)
    with open(file_path,'w',newline='') as f:
        file_writer = csv.writer(f)
        file_writer.writerow(columns)
        file_writer.writerows(output)



