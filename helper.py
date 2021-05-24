#to decode sheets to data
#import classes
import pandas
from pandas.core.frame import DataFrame
import time

def saveAllData():
    file = pandas.read_excel("file.xlsx", 0, engine="openpyxl", na_values="-", keep_default_na=False)
    width = file.shape[1]
    dataFrames = []
    x = 0
    while x in range(width):
        print(x)
        try:
            dataFrame = pandas.DataFrame()
            test = file.iloc[[x, x+1, x+2, x+3]]
            dataFrame = test.T
            dataFrames.append(dataFrame)
            x+=4
        except IndexError:
            break
    id = 1
    wrt = pandas.ExcelWriter("out.xlsx", "openpyxl", mode="w+")
    dataFrames[0].to_excel(wrt, sheet_name=str(id))
    wrt.save()
    dataFrames.pop(0)
    for x in dataFrames:
        id+=1
        with pandas.ExcelWriter("out.xlsx", "openpyxl", mode="a") as wrt:
            x.to_excel(wrt, sheet_name=str(id))
    return

saveAllData()