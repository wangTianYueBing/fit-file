import numpy as np
import pandas as pd

with open("cdbsall.txt", "r", encoding="utf-8") as f:
    list = f.read().split("\n")
dataarr = []
for each in list:
    if -9991 < float(each) < 9994.6:
        dataarr.append(float(each))

# 创建一个连续数值数组
data = np.array(dataarr)

# 定义分组数量和边界
num_bins = 20
bin_edges = np.linspace(data.min(), data.max(), num_bins+1)

# 计算每个区间的频数
hist, _ = np.histogram(data, bins=bin_edges)

# 计算总数
total_count = len(data)

# 计算每个区间的概率
probability = hist / total_count

# 创建一个DataFrame展示分布列
distribution = pd.DataFrame({'区间': [f'{bin_edges[i]:.1f}-{bin_edges[i+1]:.1f}' for i in range(num_bins)], '概率': probability})

# 打印分布列
print("分布列：")
print(distribution)