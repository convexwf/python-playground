# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : GA
# @FileName : main.py
# @Author : convexwf@gmail.com
# @CreateDate : 2022-02-19 12:33
# @UpdateTime : Todo


import matplotlib.pyplot as plt
import itertools
from math import fabs
import math
import heapq
import random

from utils import *
# plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
# plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 车间长度和宽度
L = 223
W = 63
# 隔断位置和宽度
O_y = 31.7
o = 1.4
# 通道位置和宽度
C_x1 = 88.1
C_x2 = 160.1
C_y1 = 20.1
C_y2 = 49.8
c = 3.2
# 间隔
delta_d = 0.6
delta_l = 2.7
delta_w = 3.0
# 交通工具
value_tuoche = 0.005
value_chache = 0.02
value_pingche = 0.1
tuoche_matrix = read_csv('GA/res/拖车.csv') * value_tuoche
pingche_matrix = read_csv('GA/res/平车.csv') * value_pingche
chache_matrix = read_csv('GA/res/叉车.csv') * value_chache
value_matrix = tuoche_matrix + pingche_matrix + chache_matrix
# 工作单位和固定区域(门 油漆线)
units, gates, paint = read_unit('GA/res/工作单位.csv')
units_ids, units_map = post_process(units)
units_cnt = len(units)
# 交叉率和变异率
crossover_rate = 0.7
mutation_rate = 0.15


class unit(object):

    def __init__(self, id, x, y, l, w):
        self.id = id
        self.x = x
        self.y = y
        self.l = l
        self.w = w
        self.workshop = self.get_workshop()

    def get_workshop(self):
        return 'B' if self.y > O_y else 'A'

    def valid(self):
        score = 0
        # 边界约束 1e-6
        if delta_l <= self.x - self.l/2 + 1e-6 and self.x + self.l/2 - 1e-6 <= L - delta_l:
            score += 0
        else:
            # print('wrong id', self.id, self.x-self.l/2, self.x+self.l/2)
            score += 1
        if delta_w <= self.y - self.w/2 + 1e-6 and self.y + self.w/2 <= W - delta_w + 1e-6:
            score += 0
        else:
            score += 1
        # 通道和隔断约束
        if self.x + self.l/2 + delta_d <= C_x1 - c/2 + 1e-6:
            score += 0
        elif C_x1 + c/2 <= self.x - self.l/2 - delta_d + 1e-6 and self.x + self.l/2 + delta_d <= C_x2 - c/2 + 1e-6:
            score += 0
        elif C_x2 + c/2 <= self.x - self.l/2 - delta_d + 1e-6:
            score += 0
        else:
            score += 1
        if self.y + self.w/2 + delta_d <= C_y1 - c/2 + 1e-6:
            score += 0
        elif C_y1 + c/2 <= self.y - self.w/2 - delta_d + 1e-6 and self.y + self.w/2 + delta_d <= O_y - o/2 + 1e-6:
            score += 0
        elif O_y + o/2 <= self.y - self.w/2 - delta_d + 1e-6 and self.y + self.w/2 + delta_d <= C_y2 - c/2 + 1e-6:
            score += 0
        elif C_y2 + c/2 <= self.y - self.w/2 - delta_d + 1e-6:
            score += 0
        else:
            # print('wrong id', self.id, self.x-self.l/2, self.x+self.l/2)
            # print('wrong id', self.id, self.y-self.w/2, self.y+self.w/2)
            score += 1
        return score

    @staticmethod
    def cal_distance(unit_i, unit_j):
        cpos = C_y1 if unit_j.workshop == 'B' else C_y2
        if unit_i.id == 9:
            return fabs(unit_j.y-cpos) + min([fabs(x-unit_j.x)+fabs(y-cpos) for (x, y) in gates])
        if unit_i.id == 10:
            return fabs(unit_j.y-cpos) + fabs(gates[-1][0]-unit_j.x)+fabs(gates[-1][1]-cpos)
        if unit_i.id == 11:
            return fabs(unit_j.y-cpos) + fabs(paint[0]-unit_j.x)+fabs(paint[1]-cpos)
        if unit_i.y == unit_j.y:  # 同一行
            return fabs(unit_i.x-unit_j.x) + 2 * fabs(unit_i.y-cpos)
        elif unit_i.workshop == unit_j.workshop:  # 不同行但是同一车间
            return fabs(unit_i.x-unit_j.x) + fabs(unit_i.y-unit_j.y)
        else:  # 不同车间
            return fabs(C_y1-C_y2) + fabs(unit_i.y-C_y2) + fabs(unit_j.y-C_y1) + min(fabs(unit_i.x-C_x1) + fabs(unit_j.x-C_x1), fabs(unit_i.x-C_x2) + fabs(unit_j.x-C_x2))

    def print(self):
        print('id: {}  left-bottom:({} ,{})   right-top:({} ,{})'.format(self.id,
              self.x-self.l/2, self.y-self.w/2, self.x+self.l/2, self.y+self.w/2))


class layout(object):

    def __init__(self, gem) -> None:
        self.genotype = gem if type(gem) == list else self.str2list(gem)
        self.phenotype = []
        self.isValid = 0
        self.loss = 0.
        self.decode()

    def __lt__(self, other):
        if self.loss > other.loss:
            return True
        else:
            return False

    def valid(self):
        # 0 成功
        # 1 总装约束失败
        # 2 编码失败
        # 3 边界约束失败
        if self.isValid > 0:
            return self.isValid
        score = 0
        for u in self.phenotype:
            if u.valid() > 0:
                self.isValid = 3
                return self.isValid
            if u.id == 12:
                score += (1 if u.workshop == 'A' else -1)
            if u.id == 14:
                score += (3 if u.workshop == 'A' else -3)
        if score != 0:
            self.isValid = 1
        # print('score: ', score)
        return self.isValid

    def decode(self):
        self.offset = []
        row = [C_y1-c/2-delta_d, C_y1+c/2+delta_d,
               C_y2-c/2-delta_d, C_y2+c/2+delta_d]
        column, length = split_Larea(L, C_x1, C_x2, c, delta_d, delta_l)

        area_idx = 0
        area_accum = 0
        centers = []
        for i in range(units_cnt):
            uid = self.genotype[i]
            l = units_map[uid][0]
            w = units_map[uid][1]
            delta_x = delta_d if self.genotype[units_cnt +
                                               i] <= delta_d else self.genotype[units_cnt+i]
            area_accum += delta_x
            if area_accum < column[area_idx]:
                self.offset.append(column[area_idx])
                area_accum = column[area_idx] + l
            elif area_accum + l <= column[area_idx] + length[area_idx]:
                self.offset.append(delta_x)
                area_accum += l
            else:
                area_idx += 1
                if area_idx > 10:
                    break
                self.offset.append(column[area_idx]-centers[-1][0])
                area_accum = column[area_idx] + l

            center_x = area_accum
            center_y = row[int(area_accum)//L] + \
                math.pow(-1, int(area_accum)//L+1)*w/2
            centers.append([center_x, center_y])

        if area_idx > 10:
            self.isValid = 2
            return self.phenotype

        for i in range(units_cnt):
            uid = self.genotype[i]
            l = units_map[uid][0]
            w = units_map[uid][1]
            center_x = centers[i][0] % L - l/2
            center_y = centers[i][1]
            self.phenotype.append(unit(uid, center_x, center_y, l, w))
        self.genotype = self.genotype[:units_cnt] + self.offset
        return self.phenotype

    def fitness(self):
        pre = [unit(9, 0, 0, 0, 0), unit(10, 0, 0, 0, 0), unit(11, 0, 0, 0, 0)]
        unit_list = pre + self.phenotype
        n = len(unit_list)
        if self.valid() == 0:
            for i in range(0, n-1):
                for j in range(i+1, n):
                    unit_i, unit_j = unit_list[i], unit_list[j]
                    if value_matrix[unit_i.id-1][unit_j.id-1] <= 0.:
                        continue
                    self.loss += unit.cal_distance(unit_i, unit_j) * \
                        value_matrix[unit_i.id-1][unit_j.id-1]
            return 1. / self.loss
        return 0.

    @staticmethod
    def list2str(gem):
        return '-'.join([str(it) for it in gem[:units_cnt]] + ['{:.1f}'.format(it) for it in gem[units_cnt:]])

    @staticmethod
    def str2list(code):
        params = code.strip().split('-')
        return [int(it) for it in params[:units_cnt]] + [float(it) for it in params[units_cnt:]]

    def print(self):
        return self.list2str(self.genotype)

    def display(self):
        # display 前必需计算适应度
        img = np.zeros((W*10+200, L*10+200, 4), np.uint8)

        # 车间
        cv2.rectangle(img, (100, 100), (100+L*10, 100+W*10),
                      color=(0, 0, 0, 255), thickness=5, lineType=cv2.LINE_8)
        cv2.rectangle(img, (100, 100), (100+L*10, 100+W*10),
                      color=(143, 153, 159, 60), thickness=cv2.FILLED)
        # 隔断
        cv2.rectangle(img, (100, int((O_y-o/2)*10+100)), (100+L*10,
                      int((O_y+o/2)*10+100)), color=(0, 0, 0, 220), thickness=cv2.FILLED)
        # 通道
        drawline(img, ((C_x1-c/2)*10+100, 0+100), ((C_x1-c/2)*10+100, 10*W+100),
                 color=(0, 0, 0, 255), thickness=2, style='lined', gap=20)
        drawline(img, ((C_x1+c/2)*10+100, 0+100), ((C_x1+c/2)*10+100, 10*W+100),
                 color=(0, 0, 0, 255), thickness=2, style='lined', gap=20)
        drawline(img, ((C_x2-c/2)*10+100, 0+100), ((C_x2-c/2)*10+100, 10*W+100),
                 color=(0, 0, 0, 255), thickness=2, style='lined', gap=20)
        drawline(img, ((C_x2+c/2)*10+100, 0+100), ((C_x2+c/2)*10+100, 10*W+100),
                 color=(0, 0, 0, 255), thickness=2, style='lined', gap=20)
        drawline(img, (0+100, (C_y1-c/2)*10+100), (10*L+100, (C_y1-c/2) *
                 10+100), color=(0, 0, 0, 255), thickness=2, style='lined', gap=20)
        drawline(img, (0+100, (C_y1+c/2)*10+100), (10*L+100, (C_y1+c/2) *
                 10+100), color=(0, 0, 0, 255), thickness=2, style='lined', gap=20)
        drawline(img, (0+100, (C_y2-c/2)*10+100), (10*L+100, (C_y2-c/2) *
                 10+100), color=(0, 0, 0, 255), thickness=2, style='lined', gap=20)
        drawline(img, (0+100, (C_y2+c/2)*10+100), (10*L+100, (C_y2+c/2) *
                 10+100), color=(0, 0, 0, 255), thickness=2, style='lined', gap=20)

        for u in self.phenotype:
            put_text(img, u.id, u.x, u.y, u.l, u.w)
        cv2.putText(img, 'Loss={:.3f}'.format(self.loss), (100, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255, 255), 4, bottomLeftOrigin=True)

        img = cv2.flip(img, 0)
        cv2.imwrite(
            "GA/display/{}.png".format(self.list2str(self.genotype)), img)


class GA(object):

    def __init__(self) -> None:
        self.init_population = 200
        self.max_population = 1000
        self.min_loss = 5000
        self.epoch = 0
        self.epoch_iters = 100
        self.pk = None
        self.layout_list = []
        self.gem_count = [0] * 4
        self.layout_set = set()
        self.read()

    def read(self):
        save_name = 'GA/res/result.txt'
        with open(save_name, 'r', encoding='utf-8') as fp:
            lines = fp.readlines()
            for line in lines:
                entity = layout(line.strip().split(',')[1])
                entity.fitness()
                self.layout_list.append(entity)
                self.gem_count[entity.valid()] += 1
            heapq.heapify(self.layout_list)

    def save(self):
        save_name = 'GA/res/result.txt'
        layout_res = sorted(self.layout_list, reverse=True)
        if self.epoch % 50 == 0:
            layout_res[0].display()
        with open(save_name, 'w+', encoding='utf-8') as fp:
            fp.writelines(['{:.3f},{}\n'.format(it.loss, it.print())
                          for it in layout_res])

    def output_loss(self):
        with open('GA/res/loss.txt', 'a+', encoding='utf-8') as fp:
            fp.write('{:.3f}\n'.format(self.min_loss))

    def start(self):
        groups = [it.genotype for it in self.layout_list]
        for self.epoch in range(1, self.epoch_iters+1):
            groups = self.selection(self.evolution(groups))
            print("Epoch-{} : All {}\tNum {}\t成功 {}\t总装约束失败 {}\t解码失败 {}\t边界约束失败 {}\t".format(epoch, len(self.layout_set),
                  sum(self.gem_count), self.gem_count[0], self.gem_count[1], self.gem_count[2], self.gem_count[3]))
            print('Min-loss', self.min_loss)
            self.save()
            # self.output_loss()

    def evolution(self, layout_list):
        n = len(layout_list)
        crossover_cnt = math.floor(n*crossover_rate/2) * 2
        mutation_cnt = math.ceil(n*mutation_rate)
        crossover_seq = random.sample(range(n), crossover_cnt)
        mutation_seq = random.sample(range(n), mutation_cnt)

        res = []
        for i in range(crossover_cnt//2):
            res.extend(self.crossover(
                layout_list[crossover_seq[i]], layout_list[crossover_seq[i+1]]))
        for l in mutation_seq:
            res.extend(self.mutation(layout_list[l]))
        return res

    def selection(self, layout_list):
        layout_candidates = []
        values = []
        for entity in self.layout_list:
            values.append(-entity.fitness())
            layout_candidates.append(entity.genotype)
        for l in layout_list:
            if layout.list2str(l) in self.layout_set:
                continue
            self.layout_set.add(layout.list2str(l))
            entity = layout(l)
            # if entity.print() in self.layout_set:
            #     continue
            # self.layout_set.add(entity.print())
            valid_code = entity.valid()
            self.gem_count[valid_code] += 1
            if valid_code == 0:
                value = -entity.fitness()
                self.min_loss = min(self.min_loss, entity.loss)
                if len(self.layout_list) < self.init_population:
                    self.layout_list.append(entity)
                elif self.layout_list[0].loss > entity.loss:
                    self.layout_list[0] = entity
                heapq.heapify(self.layout_list)
                print('entity', self.layout_list[0].loss, self.layout_list[-1].loss,
                      self.min_loss, max(self.layout_list).loss)
            else:
                # value = 1. / (10000 * valid_code)
                value = valid_code
            layout_candidates.append(entity.genotype)
            values.append(value)
        # res = []
        # for i in range(self.max_population):
        #     res.append(layout_candidates[roulette(values)])
        # return res
        layout_candidates = sorted([[layout_candidates[i], values[i]]
                                   for i in range(len(values))], key=lambda x: x[1])
        return [it[0] for it in layout_candidates[:self.max_population]]

    def crossover(self, layout_a, layout_b):
        XA_list, YA_list = layout_a[:units_cnt], layout_a[units_cnt:]
        XB_list, YB_list = layout_b[:units_cnt], layout_b[units_cnt:]

        crossover_r = random.randint(3, 6)
        x_pivots = random.sample(range(units_cnt), crossover_r)
        XA_remove, XB_remove, XA_res, XB_res = [], [], copy.deepcopy(
            XA_list), copy.deepcopy(XB_list)
        for pivot in x_pivots:
            XA_remove.append(XA_list[pivot])
        for pivot in x_pivots:
            if XB_list[pivot] in XA_remove:
                XA_remove.remove(XB_list[pivot])
            else:
                XB_remove.append(XB_list[pivot])
        for i in range(units_cnt):
            if i in x_pivots:
                XA_res[i] = XB_list[i]
                XB_res[i] = XA_list[i]
        instead(XA_res, x_pivots, XB_remove, XA_remove)
        instead(XB_res, x_pivots, XA_remove, XB_remove)

        y_pivots = random.sample(range(units_cnt), crossover_r)
        YA_res, YB_res = swap_point(YA_list, YB_list, y_pivots)

        return [a + b for a in [XA_list, XB_list, XA_res, XB_res] for b in [YA_list, YB_list, YA_res, YB_res]]

    def mutation(self, layout_a):
        mutation_r = random.randint(3, 6)
        x_range = random.sample(range(units_cnt), mutation_r)
        x_list = []
        for num in itertools.permutations(x_range, mutation_r):
            x_list.append(recombinate(layout_a[:units_cnt], x_range, num))

        pivot = random.randint(0, units_cnt-1)
        y_list = [layout_a[units_cnt:]]
        for num in random.sample(range(-5, 11, 1), mutation_r):
            y_list.append(addpoint(y_list[0], pivot, num))

        return [a + b for a in x_list for b in y_list]


if __name__ == '__main__':

    mode = 'display'
    
    if mode == 'display':
        gem = '7-13-13-13-13-13-13-2-5-1-6-12-14-8-4-3-13-13-13-13-13-13-14-12-3.8-3.7-0.6-0.6-4.4-2.5-0.6-4.4-10.4-11.7-11.9-14.5-4.5-18.4-2.7-2.9-1.2-4.5-2.5-0.6-4.4-0.6-19.8-42.6'
        t = layout(gem)
        t.fitness()
        t.display()

    if mode == 'train':
        ga = GA()
        ga.start()

    if mode == 'show':
        with open('GA/res/loss.txt', 'r', encoding='utf-8') as fp:
            y_values = [float(it.strip()) for it in fp.readlines()]
            x_values = range(1, len(y_values) + 1)
        # plt.figure(figsize=(10,5))#设置画布的尺寸
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.title('优化过程', fontsize=20)      # 标题，并设定字号大小
        plt.xlabel(u'代数', fontsize=14)        # 设置x轴，并设定字号大小
        plt.ylabel(u'最优值', fontsize=14)      # 设置y轴，并设定字号大小

        # color：颜色，linewidth：线宽，linestyle：线条类型，label：图例，marker：数据点的类型
        plt.plot(x_values, y_values, color="black", linewidth=1, linestyle='-', marker=',')
        # plt.legend(loc=2) #图例展示位置，数字代表第几象限
        plt.savefig('GA/res/output.png')

    # 0,13-13-13-7-13-13-13-2-12-5-14-6-1-3-4-8-13-13-13-13-13-13-12-14-2.7-0.6-0.6-0.6-8.6-0.6-0.6-6.3-10.4-0.6-20.0-0.6-18.4-21.4-0.6-0.6-0.6-9.5-0.6-0.6-6.3-0.6-19.8-42.6

    # if t.valid() == 0:
    #     t.fitness()
    #     t.display() # display 前必需计算适应度
    # # for u in t.phenotype:
    # #     print(u.x-u.l/2)
    # t.display()
    # print(t.print())
    # print(t.valid())
    # new_gem = t.genotype[:units_cnt] + t.offset
    # new_t = layout(new_gem)
    # if new_t.valid() == 0:
    #     new_t.fitness()
    #     new_t.display()
    # # for u in new_t.phenotype:
    # #     print(u.x-u.l/2)
    # print(new_t.valid())
    # print(t.genotype, new_t.genotype)
