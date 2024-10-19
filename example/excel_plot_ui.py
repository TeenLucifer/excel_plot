import os
import sys
import matplotlib.pyplot as plt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from excel_plot.excel_plot import CursorInfo, ExcelPlotCurve, ExcelPlotSubfigure, ExcelPlotUi

TOOL_VERSION = "DEBUG_PLOT_TOOL 241020"

def main():
    plt.rcParams['toolbar'] = 'None'

    # 创建Ui并读取数据
    excel_plot_ui = ExcelPlotUi(TOOL_VERSION)
    data_frame = excel_plot_ui.open_file()

    # 鼠标点击标签上显示的信息
    cursor_info = CursorInfo()
    cursor_info.add_info(name='time',       data=data_frame['time'])
    cursor_info.add_info(name='extra_info', data=data_frame['extra_info'])
    # 创建子图, 一张子图表示一类数据
    vel_subplot      = ExcelPlotSubfigure(name='Velocity    ', cursor_info=cursor_info)
    acc_subplot      = ExcelPlotSubfigure(name='Acceleration', cursor_info=cursor_info)
    dis_subplot      = ExcelPlotSubfigure(name='Distance    ', cursor_info=cursor_info)   
    # 创建每类数据的曲线
    s1_curve = ExcelPlotCurve(y_axis_data=data_frame['s1'], label='obj1_dis', color='tab:blue', visible=True)
    s2_curve = ExcelPlotCurve(y_axis_data=data_frame['s2'], label='obj2_dis', color='tab:red',  visible=True)
    v1_curve = ExcelPlotCurve(y_axis_data=data_frame['v1'], label='obj1_vel', color='tab:blue', visible=True)
    v2_curve = ExcelPlotCurve(y_axis_data=data_frame['v2'], label='obj2_vel', color='tab:red',  visible=True)
    a1_curve = ExcelPlotCurve(y_axis_data=data_frame['a1'], label='obj1_acc', color='tab:blue', visible=True)
    a2_curve = ExcelPlotCurve(y_axis_data=data_frame['a2'], label='obj2_acc', color='tab:red',  visible=True)
    # 在子图中添加曲线
    vel_subplot.add_curve(v1_curve)
    vel_subplot.add_curve(v2_curve)
    acc_subplot.add_curve(a1_curve)
    acc_subplot.add_curve(a2_curve)
    dis_subplot.add_curve(s1_curve)
    dis_subplot.add_curve(s2_curve)
    # 添加子图到Ui
    excel_plot_ui.add_subplot(vel_subplot)
    excel_plot_ui.add_subplot(acc_subplot)
    excel_plot_ui.add_subplot(dis_subplot)

    excel_plot_ui.plot(suptitle="Excel Plot", x_axis_data=data_frame['time'])
    plt.show()

if __name__ == '__main__':
    main()