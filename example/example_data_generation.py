import numpy as np
import pandas as pd

time = np.linspace(0, 10, 500)

t_list = []
s1_list = []
s2_list = []
v1_list = []
v2_list = []
a1_list = []
a2_list = []
extra_info_lit = []

s1 = 0
s2 = 0
a1 = 0.1
a2 = 0.2
v1 = 0
v2 = 0
dt = (10 - 0) / 500

# 生成示例数据, 两个匀加速直线运动物体的运动状态
for t in time:
    dv1 = a1 * dt
    dv2 = a2 * dt
    s1_dot = (v1 + 0.5 * dv1)
    s2_dot = (v2 + 0.5 * dv2)
    v1 = v1 + dv1
    v2 = v2 + dv2
    s1 = s1 + s1_dot * dt
    s2 = s2 + s2_dot * dt
    t_list.append(round(t, 2))
    s1_list.append(round(s1, 2))
    s2_list.append(round(s2, 2))
    v1_list.append(round(v1, 2))
    v2_list.append(round(v2, 2))
    a1_list.append(round(a1, 2))
    a2_list.append(round(a2, 2))
    extra_info_lit.append(f"info{round(t, 2)}")

# 创建dataframe
data = pd.DataFrame({
    'time': t_list,
    's1': s1_list,
    's2': s2_list,
    'v1': v1_list,
    'v2': v2_list,
    'a1': a1_list,
    'a2': a2_list,
    'extra_info': extra_info_lit
})

# 保存数据文件
data.to_csv('example_data.txt', index=False)
data.to_excel('example_data.xlsx', index=False)

print('Data saved to example_data.csv')