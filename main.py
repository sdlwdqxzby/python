import backtest as b
import os
import csv

def getinf_csv(path):
    output = []
    with open(path) as f:
        file = csv.reader(f)
        for row in file:
            seq = row[0]
            output.append(seq)
    return output


if __name__ == '__main__':
    list = getinf_csv(r'C:\Users\Administrator\Desktop\quant_result\测试条件.csv')
    for i in list:
        quant = b.quant(i)
        data = quant.result_backtest()
        quant.result_historydetail()
        print('\n')
    # 结束之后打开结果文件夹
    path = os.path.join(os.path.expanduser('~'), 'Desktop','quant_result')
    os.startfile(path)
