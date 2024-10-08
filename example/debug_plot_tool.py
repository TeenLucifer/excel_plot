import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from excel_plot.debug_figure import CursorInfo, ExcelPlotCurve, ExcelPlotSubfigure, ExcelPlotUi

TOOL_VERSION = "DEBUG_PLOT_TOOL 240907"

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

    ref_v_real_sc    = ExcelPlotCurve(ref_v_real,  'PlanVel', 'tab:blue', True)
    obj_v_sc         = ExcelPlotCurve(obj_v,       'ObjVel',  'tab:red',  True)
    ref_at_real_sc   = ExcelPlotCurve(ref_at_real, 'PlanAcc', 'tab:blue', True)
    obj_at_sc        = ExcelPlotCurve(obj_at,      'ObjAcc',  'tab:red',  True)
    dis_sc           = ExcelPlotCurve(dis,         'Dis',     'tab:blue', True)
    dis2_sc          = ExcelPlotCurve(dis2,        'Dis2',    'tab:red',  True)
    vel_subplot      = ExcelPlotSubfigure(name='Velocity    ', cursor_info=cursor_info)
    acc_subplot      = ExcelPlotSubfigure(name='Acceleration', cursor_info=cursor_info)
    dis_subplot      = ExcelPlotSubfigure(name='Distance    ', cursor_info=cursor_info)
    lon_debug_figure = ExcelPlotUi(TOOL_VERSION)

    vel_subplot.add_curve(ref_v_real_sc)
    vel_subplot.add_curve(obj_v_sc)
    acc_subplot.add_curve(ref_at_real_sc)
    acc_subplot.add_curve(obj_at_sc)
    dis_subplot.add_curve(dis_sc)
    dis_subplot.add_curve(dis2_sc)
    lon_debug_figure.add_subplot(vel_subplot)
    lon_debug_figure.add_subplot(acc_subplot)
    lon_debug_figure.add_subplot(dis_subplot)

    lon_debug_figure.plot("Velocity", timestamp)
    plt.show()

if __name__ == '__main__':
    main()