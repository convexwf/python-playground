# 问题描述

## 假设条件

1. 坐标系原点设定为生产车间的左下角，X 轴方向为车间长度方向，Y 轴方向为车间宽度方向
2. 车间长度为 L，宽度为 W
3. 有 n 个作业单位，形状简化为矩形，长宽已知，第 i 个工作单位的中心点为 $(x_i, y_i)$，长度为 $l_i$，宽度为 $w_i$
4. 车间被上下划分为 A 车间和 B 车间，中间用隔断分开，隔断的位置固定为 $O_y$，宽度为 $o$
5. 在 X 轴方向和 Y 轴方向上各有两条主要通道，通道的宽度一致，均为 $c$
6. 通道和隔断将整个车间划分为 12 个区域，为简化问题，规定每个区域只能放置单行多列工作单位，在同一行的工作单位中心纵坐标相同。
7. 作业单位进出点均为其中心点，运输过程中必须经过通道

## 约束条件

间隔约束：工作单位间不能产生重叠干涉，且彼此要有一定的间隔 $\Delta d$

$\left\{\begin{array}{l}\left|x_{i}-x_{j}\right| \geq \frac{l_{i}+l_{j}}{2}+ \Delta d \\ \left|y_{i}-y_{j}\right| \geq \frac{w_{i}+w_{j}}{2}+ \Delta d\end{array}\right.$

边界约束：车间长度和宽度限定，各工作单位在 在 X 轴方向和 Y 轴方向上均不能超过车间尺寸限定，且到车间边界间隔横向 $\Delta l$ 米，纵向 $\Delta w$ 米

$\left\{\begin{array}{l}\Delta l \leq x_{i}-\frac{l_{i}}{2}, x_{i}+\frac{l_{i}}{2} \leq L-\Delta l \\ \Delta w \leq y_{i}-\frac{w_{i}}{2}, y_{i}+\frac{w_{i}}{2} \leq W-\Delta w\end{array}\right.$

通道和隔断约束：各工作单位不能横跨通道和隔断，且距离通道和隔断要有一定的间隔 $\Delta d$。设水平通道的位置为 $C_{y}^{1}$ 和 $C_{y}^{2}$，竖直通道的位置为 $C_{x}^{1}$ 和 $C_{x}^{2}$。

$\left\{\begin{array}
 {l}x_{i}+\frac{l_{i}}{2}+\Delta d \leq C_{x}^{1} - \frac{c}{2} \\
 C_{x}^{1} + \frac{c}{2} \leq x_{i}-\frac{l_{i}}{2} - \Delta d, x_{i}+\frac{l_{i}}{2} + \Delta d \leq C_{x}^{2} - \frac{c}{2} \\
 C_{x}^{2} + \frac{c}{2} \leq x_{i}-\frac{l_{i}}{2} - \Delta d
\end{array}\right.$

以及

$\left\{\begin{array}
 {l}y_{i}+\frac{w_{i}}{2}+\Delta d \leq C_{y}^{1} - \frac{c}{2} \\
 C_{y}^{1} + \frac{c}{2} \leq y_{i}-\frac{w_{i}}{2} - \Delta d, y_{i}+\frac{w_{i}}{2} + \Delta d \leq O_{y} - \frac{o}{2} \\
 O_{y} + \frac{o}{2} \leq y_{i}-\frac{w_{i}}{2} - \Delta d, y_{i}+\frac{w_{i}}{2} + \Delta d \leq C_{y}^{2} - \frac{c}{2} \\
 C_{y}^{2} + \frac{c}{2} \leq y_{i}-\frac{w_{i}}{2} - \Delta d
\end{array}\right.$

固定区域约束：最右上角区域不能放置任何工作单位

$\left\{\begin{array}
 {l}C_{x}^{2} + \frac{c}{2} \leq x_{i}-\frac{l_{i}}{2} - \Delta d \\
 C_{y}^{2} + \frac{c}{2} \leq y_{i}-\frac{w_{i}}{2} - \Delta d
\end{array}\right.$

## 目标函数

### 距离计算

分为三种情况：工作单位 i 和工作单位 j 在 (1) 同一行 (2) 不同行但是同一车间 (3) 不同车间

(1) 同一行

同在车间 A：$d_{i j}=\left|x_{i}-x_{j}\right| + 2\left|y_{i}-C^{2}_{y}\right|$
同在车间 B：$d_{i j}=\left|x_{i}-x_{j}\right| + 2\left|y_{i}-C^{1}_{y}\right|$

(2) 不同行但是同一车间

$d_{i j}=\left|x_{i}-x_{j}\right| + \left|y_{i}-y_{j}\right|$

(3) 不同车间，设工作单位 $i$ 在车间 A，工作单位 $j$ 在车间 B

$d_{i j}=\left|C^{1}_{y}-C^{2}_{y}\right| + \left|y_{i}-C^{2}_{y}\right| + \left|y_{j}-C^{1}_{y}\right| + \min \left\{\begin{array}{l}
 \left|x_{i}-C^{1}_{x}\right| + \left|x_{j}-C^{1}_{x}\right| \\
 \left|x_{i}-C^{2}_{x}\right| + \left|x_{j}-C^{2}_{x}\right|
\end{array}\right.$
