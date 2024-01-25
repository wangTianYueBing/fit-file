import fitparse
from datetime import timedelta
timedata = []

def get_message(file_name):
    file = fitparse.FitFile(file_name)
    message = file.messages
    for item in message:
        if item.name == 'record':
            timedata.append(item.as_dict())


def semicircles2degrees(semicircles):
    return semicircles * (180 / 2147483648)


def degrees2semicircles(degrees):
    return degrees * (2147483648 / 180)


if __name__ == '__main__':
    import os
    path = './records'
    for file_name in os.listdir(path):
        get_message("./records/" + file_name)
        presd = 0
        for each in timedata:
            tp, speed = 0, 0
            for ele in each["fields"]:
                if ele["name"] == "cadence":
                    tp = ele["value"]
                if ele["name"] == "enhanced_speed":
                    speed = ele["value"] * 3.6
            acc = speed - prespeed
            prespeed = speed
            # 可调整参数，踏频50以上且加速度大于-1（加速或匀速，允许小规模的减速）
            if tp > 50 and acc > -1:
                k = 0.125444328
                cdb = speed / (tp * k)
                print(cdb)
                with open("cdbsall.txt", "a+", encoding="utf-8") as f:
                    f.write(str(cdb) + "\n")



