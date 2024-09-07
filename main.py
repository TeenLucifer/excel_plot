import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
from debug_figure import CursorInfo, DebugFigureCurve, DebugFigureSubplot, DebugFigure

TOOL_VERSION = "DEBUG_PLOT 240907"

def main():
    plt.rcParams['toolbar'] = 'None'

    timestamp = np.arange(100000, 200000, 66)
    ref_v_real  = np.random.normal(20, 5, timestamp.shape[0])
    obj_v       = np.random.normal(19, 3, timestamp.shape[0])
    ref_at_real = np.random.normal(1, 0.5, timestamp.shape[0])
    obj_at      = np.random.normal(1, 0.3, timestamp.shape[0])
    dis         = np.random.normal(100, 10, timestamp.shape[0])
    dis2        = np.random.normal(95, 10, timestamp.shape[0])
    tar_id      = np.arange(0, timestamp.shape[0], 1)

    # 鼠标点击标签上显示的信息
    cursor_info = CursorInfo()
    cursor_info.add_info(name='timestamp', data=timestamp)
    cursor_info.add_info(name='objective id', data=tar_id)

    ref_v_real_sc    = DebugFigureCurve(ref_v_real,  'PlanVel', 'tab:blue', True)
    obj_v_sc         = DebugFigureCurve(obj_v,       'ObjVel',  'tab:red',  True)
    ref_at_real_sc   = DebugFigureCurve(ref_at_real, 'PlanAcc', 'tab:blue', True)
    obj_at_sc        = DebugFigureCurve(obj_at,      'ObjAcc',  'tab:red',  True)
    dis_sc           = DebugFigureCurve(dis,         'Dis',     'tab:blue', True)
    dis2_sc          = DebugFigureCurve(dis2,        'Dis2',    'tab:red',  True)
    vel_subplot      = DebugFigureSubplot(name='Velocity    ', x_axis_data=timestamp, cursor_info=cursor_info)
    acc_subplot      = DebugFigureSubplot(name='Acceleration', x_axis_data=timestamp, cursor_info=cursor_info)
    dis_subplot      = DebugFigureSubplot(name='Distance    ', x_axis_data=timestamp, cursor_info=cursor_info)
    lon_debug_figure = DebugFigure(TOOL_VERSION)

    vel_subplot.add_curve(ref_v_real_sc)
    vel_subplot.add_curve(obj_v_sc)
    acc_subplot.add_curve(ref_at_real_sc)
    acc_subplot.add_curve(obj_at_sc)
    dis_subplot.add_curve(dis_sc)
    dis_subplot.add_curve(dis2_sc)
    lon_debug_figure.add_subplot(vel_subplot)
    lon_debug_figure.add_subplot(acc_subplot)
    lon_debug_figure.add_subplot(dis_subplot)

    lon_debug_figure.plot("Velocity")
    plt.show()

if __name__ == '__main__':
    main()