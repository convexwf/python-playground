# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : kmeans
# @FileName : main.py
# @Author : convexwf@gmail.com
# @CreateDate : 2022-01-26 12:51
# @UpdateTime : Todo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data_file = 'kmeans/res/外购外协小件.xlsx'
output_png = 'kmeans/res/output.png'
output_xls = 'kmeans/res/output.xls'
data1_rows = 53
data2_rows = 63
K_clusters = 3


def K_means(data, K):
    """
    程序说明：
    本函数实现二维和三维数据的K_means聚类算法
    data:输入的数据，维度(m, 2)或者(m, 3)
    K:表示希望分出来的类数
    """
    num = np.shape(data)[0]

    cls = np.zeros([num], np.int)

    random_array = np.random.random(size=K)
    random_array = np.floor(random_array*num)
    rarray = random_array.astype(int)
    print('数据集中随机索引', rarray)

    center_point = data[rarray]
    print('初始化随机中心点', center_point)

    change = True  # change表示簇中心是否有过改变，又改变了就需要继续循环程序，没改变则终止程序
    while change:
        for i in range(num):
            # 此句执行之后得到的是两个数或三个数：x-x_0,y-y_0或x-x_0, y-y_0, z-z_0
            temp = data[i] - center_point
            temp = np.square(temp)  # 得到(x-x_0)^2等
            distance = np.sum(temp, axis=1)  # 按行相加，得到第i个样本与所有center point的距离
            cls[i] = np.argmin(distance)  # 取得与该样本距离最近的center point的下标

        change = False
        for i in range(K):
            # 找到属于该类的所有样本
            club = data[cls == i]
            newcenter = np.mean(club, axis=0)  # 按列求和，计算出新的中心点
            # 如果新旧center的差距很小，看做他们相等，否则更新之。run置true，再来一次循环
            ss = np.abs(center_point[i]-newcenter)
            if np.sum(ss, axis=0) > 1e-4:
                center_point[i] = newcenter
                change = True

    print('K-means done!')
    return center_point, cls

def output_minsize(data, center_point, cls, k):
    num, dim = data.shape
    minsize = np.full(shape=[k, dim], fill_value=0., dtype=np.float)
    for i in range(num):
        x, y, z = data[i, :]
        cluster = cls[i]
        minsize[cluster, 0] = max(minsize[cluster, 0], x)
        minsize[cluster, 1] = max(minsize[cluster, 1], y)
        minsize[cluster, 2] = max(minsize[cluster, 2], z)
    return minsize

def show_picture(data, center_point, cls, k):
    num, dim = data.shape
    color = ['r', 'g', 'b', 'c', 'y', 'm', 'k']
    if dim == 2:
        for i in range(num):
            mark = int(cls[i])
            plt.plot(data[i, 0], data[i, 1], color[mark]+'o')

        # 下面把中心点单独标记出来：
        for i in range(k):
            plt.plot(center_point[i, 0], center_point[i, 1], color[i]+'x')

    elif dim == 3:
        ax = plt.subplot(111, projection='3d')
        for i in range(num):
            mark = int(cls[i])
            ax.scatter(data[i, 0], data[i, 1], data[i, 2], c=color[mark])

        for i in range(k):
            ax.scatter(center_point[i, 0], center_point[i, 1],
                       center_point[i, 2], c=color[i], marker='x')
    # plt.show()
    plt.savefig(output_png)


if __name__ == '__main__':
    # sheet_name=0 表示读取第 1 个工作表
    # header=0 表示从第 1 行开始读取（包含列标题）
    # usecols='D:F' 表示只读取 D 列到 F 列
    excel1_df = pd.read_excel(io=data_file, sheet_name=0, header=0)
    excel2_df = pd.read_excel(io=data_file, sheet_name=1, header=0)
    acces1_df = excel1_df.iloc[:data1_rows, :3]
    acces2_df = excel2_df.iloc[:data2_rows, :3]
    acces_array = np.concatenate([acces1_df.values, acces2_df.values])
    data1_df = excel1_df.iloc[:data1_rows, 3:6]
    data2_df = excel2_df.iloc[:data2_rows, 7:10]
    data_array = np.concatenate([data1_df.values, data2_df.values]).astype(np.float)
    cluster_array = np.zeros(shape=[data_array.shape[0], 4], dtype=np.float)
    
    center_point, cls = K_means(data_array, K_clusters)
    minsize = output_minsize(data_array, center_point, cls, K_clusters)
    show_picture(data_array, center_point, cls, K_clusters)

    print(acces_array.shape, data_array.shape, cls.shape, minsize.shape) # (116, 3) (116, 3) (116,) (3, 3)
    for i in range(data_array.shape[0]):
        cluster_array[i, 0] = cls[i]
        cluster_array[i, 1:] = minsize[cls[i]]
    for i in range(K_clusters):
        print('聚类 {}: x={} y={} z={}'.format(i, minsize[i,0], minsize[i,1], minsize[i,2]))
    df_array = np.concatenate([acces_array, data_array, cluster_array], axis=1)
    df = pd.DataFrame(df_array)
    df.columns = ['零件号', '零件名', '总数量', '尺寸(长)', '尺寸(宽)', '尺寸(高)', '类别', '尺寸(长)', '尺寸(宽)', '尺寸(高)']
    df.to_excel(output_xls)
    
    
