# 绘图相关模块
import matplotlib.axes
import matplotlib.backend_bases
import matplotlib.figure
import matplotlib.lines
import matplotlib.widgets
import mplcursors
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons
from matplotlib.widgets import Button
# 计算相关模块
import numpy as np
import pandas as pd
from collections import deque
# 路径相关模块
import tkinter as tk
from tkinter import filedialog

class CursorInfo:
    """
    格式化储存鼠标点击标签上的信息
    """
    def __init__(self) -> None:
        """
        初始化成员变量
        """
        self.info_num = 0
        self.info_name_list: list[str] = []
        self.info_data_list: list = []

    def add_info(self, name: str, data: list) -> None:
        """
        添加一条待显示的信息
        """
        self.info_name_list.append(name)
        self.info_data_list.append(data)
        self.info_num += 1

class ExcelPlotCurve:
    """
    图中需要绘制的单条曲线类
    """
    def __init__(self, y_axis_data: np.ndarray, label: str, color: str, visible: bool = True) -> None:
        """
        初始化曲线
        """
        self.y_axis_data = y_axis_data
        self.label = label
        self.color = color
        self.visible = visible
        self.line: matplotlib.lines.Line2D

    # 绘制曲线
    def plot(self, plot_ax: matplotlib.axes.Axes, x_axis_data: np.ndarray) -> None:
        """
        绘制单条曲线
        """
        self.line, = plot_ax.plot(
            x_axis_data,
            self.y_axis_data,
            label=self.label,
            color=self.color,
            visible=self.visible,
        )

    def set_visible(self, visible: bool) -> None:
        """
        设置曲线是否可见
        """
        self.visible = visible
        self.line.set_visible(visible)

class ExcelPlotBaseFigure:
    """
    绘图的基础类, 能够实现多条曲线在同一张图显示, 左键点击曲线显示标签信息, 右键按住空白处拖动移动
    """
    def __init__(self, name: str, fig: matplotlib.figure.Figure, cursor_info: CursorInfo = None, mouse_event_callback = None) -> None:
        """
        初始化成员变量
        """
        self.fig = fig
        self.name = name
        self.x_axis_data: np.ndarray
        self.xticks_density = 30 # 本图横轴刻度密度

        # 画布及坐标轴相关参数
        self.plot_ax_pos: np.ndarray
        self.plot_ax: matplotlib.axes.Axes

        # 图中的曲线
        self.curve_num = 0
        self.curves: list[ExcelPlotCurve] = []

        # 是否可见
        self.visible = True

        # 绑定鼠标事件响应函数
        if self.fig is not None:
            self.fig.canvas.mpl_connect('scroll_event',         self.mouse_toggle_event)
            self.fig.canvas.mpl_connect('button_press_event',   self.mouse_toggle_event)
            self.fig.canvas.mpl_connect('button_release_event', self.mouse_toggle_event)
            self.fig.canvas.mpl_connect('motion_notify_event',  self.mouse_toggle_event)

        # 本图鼠标点击事件参数
        self.mouse_press = False
        self.mouse_move_start_x = 0
        self.mouse_move_start_y = 0
        self.mouse_move_rx = 0.0   # 鼠标移动横向比例, 用于和其它子图同步
        self.mouse_move_ry = 0.0   # 鼠标移动纵向比例, 用于和其它子图同步
        self.mouse_scroll_rx = 1.0 # 鼠标滚轮横向缩放比例, 用于和其它子图同步
        self.mouse_scroll_ry = 1.0 # 鼠标滚轮纵向缩放比例, 用于和其它子图同步
        self.mouse_event_callback = mouse_event_callback
        self.cursor_info: CursorInfo = cursor_info # 鼠标点击信息
        self.cursor: mplcursors._mplcursors.Cursor # 标签

    def plot(self, plot_ax_pos: np.ndarray, x_axis_data: np.ndarray) -> None:
        """
        画图和绘制曲线
        """
        self.plot_ax_pos = plot_ax_pos
        self.plot_ax = self.fig.add_axes(self.plot_ax_pos)
        self.x_axis_data = x_axis_data
        lines = []
        for curve in self.curves:
            curve.plot(self.plot_ax, self.x_axis_data)
            lines.append(curve.line)
        # 给一幅子图绑定标签, 每条曲线都绑定会有重叠现象, 故只绑定一次
        self.cursor = mplcursors.cursor(lines, multiple=True)
        self.cursor.connect('add', self.update_cursor_annotation)

        # 设置显示格式
        self.plot_ax.set_xlim(self.x_axis_data.min(), self.x_axis_data.max())
        self.plot_ax.legend(fontsize=8)
        self.plot_ax.grid()
        self.plot_ax.set_xticks(np.linspace(self.x_axis_data.min(), self.x_axis_data.max(), self.xticks_density))
        self.plot_ax.tick_params(axis='x', rotation=20)
        self.plot_ax.ticklabel_format(axis='x', style='plain')

        # 曲线绘制时设置invisible会导致legend不显示颜色, 因此需要先绘制曲线再设置visible
        for curve in self.curves:
            curve.set_visible(curve.visible)

    def add_curve(self, curve: ExcelPlotCurve) -> None:
        """
        在图中添加曲线
        """
        self.curves.append(curve)
        self.curve_num += 1

    def remove_curve(self, curve: ExcelPlotCurve) -> None:
        """
        在图中删除曲线
        """
        curve.line.remove()
        self.curves.remove(curve)
        self.curve_num -= 1

    def remove_all_curve(self) -> None:
        """
        删除所有曲线
        """
        for curve in self.curves:
            curve.line.remove()
        self.curves = []
        self.curve_num = 0

    def update_cursor_annotation(self, cursor: mplcursors._mplcursors.Cursor) -> None:
        """
        更新鼠标点击曲线显示的标签信息
        """
        cursor_text = f'{cursor.artist.get_label()}:{cursor.target[1]:.2f}\n{round(cursor.target[0])}'
        index = round(cursor.index)
        info = ''
        if self.cursor_info is not None:
            for i in range(self.cursor_info.info_num):
                name = self.cursor_info.info_name_list[i]
                data = self.cursor_info.info_data_list[i][index]
                info = f'\n{name}:{data}'
                cursor_text += info
        cursor.annotation.set_text(cursor_text)

    def mouse_toggle_event(self, event: matplotlib.backend_bases.MouseEvent) -> None:
        """
        鼠标事件回调函数, 实现右键按住空白处拖动, 滚轮缩放
        """
        if self.plot_ax == event.inaxes and \
           (event.name == 'button_press_event' or event.name == 'scroll_event' or\
            event.name == 'button_press_event' or event.name == 'button_release_event' or \
            (event.name == 'motion_notify_event' and event.button == 3 and self.mouse_press == True)):
            # 获取本图横纵轴范围
            x_min, x_max = self.plot_ax.get_xlim()
            y_min, y_max = self.plot_ax.get_ylim()
            subplot_width = x_max - x_min
            subplot_height = y_max - y_min
            updated_x_min = x_min
            updated_x_max = x_max
            updated_y_min = y_min
            updated_y_max = y_max

            # 滚轮缩放事件响应
            if event.name == 'scroll_event':
                scale_factor = 0.9 if event.button == 'up' else 1.1
                fig_width_px, fig_height_px = self.fig.canvas.get_width_height()

                if event.xdata > (x_min + subplot_width / 5.0):
                    self.mouse_scroll_rx = scale_factor # 横轴缩放系数
                    self.mouse_scroll_ry = 1.0          # 纵轴缩放系数

                    # 横轴缩放参数
                    x_mid = (x_max + x_min) / 2.0
                    updated_x_min = x_mid - (subplot_width / 2.0) * self.mouse_scroll_rx
                    updated_x_max = x_mid + (subplot_width / 2.0) * self.mouse_scroll_rx
                else:
                    self.mouse_scroll_rx = 1.0          # 横轴缩放系数
                    self.mouse_scroll_ry = scale_factor # 纵轴缩放系数

                    # 纵轴缩放参数
                    y_mid = (y_max + y_min) / 2.0
                    updated_y_min = y_mid - (subplot_height / 2.0) * self.mouse_scroll_ry
                    updated_y_max = y_mid + (subplot_height / 2.0) * self.mouse_scroll_ry

            # 鼠标拖动事件响应
            if event.name == 'button_press_event' and event.button == 3:
                self.mouse_press = True
                self.mouse_move_start_x = event.xdata
                self.mouse_move_start_y = event.ydata
            elif event.name == 'button_release_event' and event.button == 3:
                self.mouse_press = False
            elif event.name == 'motion_notify_event' and event.button == 3 and self.mouse_press:
                mx = event.xdata - self.mouse_move_start_x
                my = event.ydata - self.mouse_move_start_y
                self.mouse_move_rx = mx / subplot_width
                self.mouse_move_ry = my / subplot_height

                updated_x_min = x_min - mx
                updated_x_max = x_min - mx + subplot_width
                updated_y_min = y_min - my
                updated_y_max = y_min - my + subplot_height
            
            self.plot_ax.set_xlim(updated_x_min, updated_x_max)
            self.plot_ax.set_ylim(updated_y_min, updated_y_max)
            self.plot_ax.set_xticks(np.linspace(updated_x_min, updated_x_max, self.xticks_density))

            if (self.mouse_event_callback is not None) and (event.name == 'scroll_event' or (event.name == 'motion_notify_event' and self.mouse_press) or\
                (event.name == 'button_press_event' and event.button == 1)):
                self.mouse_event_callback(self, event)

            #self.fig.canvas.draw_idle()

class ExcelPlotSubfigure(ExcelPlotBaseFigure):
    """
    excel数据绘图工具子图类, 继承于绘图基类, 添加按键和复选框控件, 添加鼠标左键点击空白处显示时间刻度功能
    """
    def __init__(self, name: str, cursor_info: CursorInfo) -> None:
        super().__init__(name=name, fig=None, cursor_info=cursor_info, mouse_event_callback=None)
        self.vline: matplotlib.lines.Line2D = None
        self.button_event_callback: callable

        # 控件位置参数
        self.plot_ax_pos: np.ndarray
        self.button_ax_pos: np.ndarray
        self.check_buttons_ax_pos: np.ndarray

        # 控件坐标轴及控件
        self.button_ax: matplotlib.axes.Axes
        self.button: matplotlib.widgets.Button
        self.check_buttons_ax: matplotlib.axes.Axes
        self.check_buttons: matplotlib.widgets.CheckButtons

    def plot(
        self,
        fig: matplotlib.figure.Figure,
        plot_ax_pos: np.ndarray,
        button_ax_pos: np.ndarray,
        check_buttons_ax_pos: np.ndarray,
        x_axis_data: np.ndarray,
        mouse_event_callback: callable,
        button_event_callback: callable
    ) -> None:
        """
        子图绘制, 调用父类方法进行绘制, 子类添加复选框控件
        """
        self.fig = fig
        self.fig.canvas.mpl_connect('scroll_event',        self.mouse_toggle_event)
        self.fig.canvas.mpl_connect('button_press_event',  self.mouse_toggle_event)
        self.fig.canvas.mpl_connect('motion_notify_event', self.mouse_toggle_event)
        self.fig.canvas.mpl_connect('button_press_event',  self.mouse_toggle_event)

        # 调用父类方法, 绘制曲线图
        super().plot(plot_ax_pos, x_axis_data)

        # 绑定鼠标事件外部回调函数
        self.mouse_event_callback = mouse_event_callback
        # 绑定按键事件外部回调函数
        self.button_event_callback = button_event_callback

        # 创建子图按键
        self.button_ax = self.fig.add_axes(button_ax_pos)
        self.button = Button(ax=self.button_ax, label=self.name)
        self.button.on_clicked(self.button_toggle_event)

        # 创建子图复选框
        self.check_buttons_ax = self.fig.add_axes(check_buttons_ax_pos)
        labels = [curve.label for curve in self.curves]
        visibility = [curve.visible for curve in self.curves]
        self.check_buttons = CheckButtons(ax=self.check_buttons_ax, labels=labels, actives=visibility)
        self.check_buttons.on_clicked(self.checkbuttons_toggle_event)

    def mouse_toggle_event(self, event: matplotlib.backend_bases.MouseEvent) -> None:
        """
        鼠标事件回调函数, 继承父类的标签显示, 右键拖动, 滚轮缩放功能, 添加左键点击空白处显示时间刻度功能
        """
        # 调用父类方法
        super().mouse_toggle_event(event)

        if self.plot_ax == event.inaxes and \
           (event.name == 'button_press_event' or event.name == 'scroll_event' or\
            event.name == 'button_press_event' or event.name == 'button_release_event' or \
            (event.name == 'motion_notify_event' and event.button == 3 and self.mouse_press == True)):
            if event.name == 'button_press_event' and event.button == 1:
                for sel in self.cursor.selections:
                    annotation = sel.annotation
                    bbox = annotation.get_window_extent()
                    if bbox.contains(event.x, event.y):
                        return
                if self.vline is not None:
                    self.vline.remove()
                self.vline = self.plot_ax.axvline(x=event.xdata, color='black', linewidth=1, visible=True)

            # 鼠标操作有效更新画布, 防止卡顿
            self.fig.canvas.draw_idle()

    def checkbuttons_toggle_event(self, label: str) -> None:
        """
        复选框点击事件回调函数, 设置曲线是否可见
        """
        index = [curve.label for curve in self.curves].index(label)
        self.curves[index].visible = not self.curves[index].visible
        self.curves[index].line.set_visible(self.curves[index].visible)
        self.fig.canvas.draw_idle() 

    def button_toggle_event(self, event) -> None:
        """
        按键点击事件回调函数
        """
        if self.button_event_callback is not None:
            self.button_event_callback(self)

class ExcelPlotUi:
    """
    excel数据绘图工具主类, 继承于绘图基类, 根据子图中的操作调整界面布局及同步各子图横轴动作, 默认显示2幅图, 最多显示3幅图
    功能:
        点击按键显示或隐藏某类数据
        点击复选框显示或隐藏某条曲线
        鼠标左键点击曲线显示标签信息
        鼠标左键点击空白处各子图同步显示时间刻度
        鼠标右键按住空白处拖动移动
        鼠标滚轮缩放
    """
    def __init__(self, title: str) -> None:
        """
        初始化成员变量
        """
        self.title = title
        self.fig = matplotlib.figure.Figure
        self.subplot_num = 0
        self.subplots: list[ExcelPlotSubfigure] = []
        self.data_category_num = 0
        self.default_visible_subplot_num = 2
        self.visible_subplot_num_max = 3
        self.visible_subplots_dq = deque(maxlen=self.visible_subplot_num_max)

        # 子图控件布局参数
        self.subplot2left = 0.13
        self.subplot2bottom_max = 1.0
        self.subplot_width = 0.85
        self.subplot_height = 1.0 / max(self.subplot_num, 1)
        self.subplot_plot_step = 1.0 / max(self.subplot_num, 1)

        self.button2left = 0.005
        self.button2bottom_max = 1.0
        self.button_width = 0.08
        self.button_height = 0.03
        self.button_plot_step = self.button_height

        self.check_buttons2left = 0.005
        self.check_buttons2bottom_max = 1.0
        self.check_buttons_width = 0.10
        self.check_buttons_height = 0.10
        self.check_buttons_plot_step = 1.0 / max(self.subplot_num, 1)

        self.y_sync = False # 同画布下多个子图是否同步纵轴

    def add_subplot(self, subplot: ExcelPlotSubfigure) -> None:
        """
        大图添加子图
        """
        self.subplots.append(subplot)
        self.data_category_num += 1
        self.subplot_num += 1
        self.visible_subplots_dq.append(subplot)
        if self.data_category_num > self.default_visible_subplot_num:
            subplot.visible = False
            self.visible_subplots_dq.remove(subplot)
        if self.subplot_num > self.default_visible_subplot_num:
            self.subplot_num = self.default_visible_subplot_num

    def cal_ax_poses(self, data_category_idx: int) -> None:
        """
        大图分配各控件布局位置
        """
        self.subplot_plot_step = 1.0 / self.subplot_num
        self.subplot_height = 1.0 / self.subplot_num
        self.check_buttons_plot_step = 1.0 / self.subplot_num

        subplot_pos       = np.array([self.subplot2left,       self.subplot2bottom_max - (data_category_idx + 1) * self.subplot_plot_step + 0.04, self.subplot_width, self.subplot_height - 0.04])
        button_pos        = np.array([self.button2left,        self.button2bottom_max - (data_category_idx + 1) * self.button_plot_step, self.button_width, self.button_height])
        check_buttons_pos = np.array([self.check_buttons2left, self.check_buttons2bottom_max - (data_category_idx + 1) * self.check_buttons_plot_step + 0.04, self.check_buttons_width, self.check_buttons_height])

        return subplot_pos, button_pos, check_buttons_pos

    def plot(self, suptitle: str, x_axis_data: np.ndarray) -> None:
        """
        绘制界面
        """
        self.fig = plt.figure(self.title)
        self.fig.suptitle(suptitle)

        for i in range(self.data_category_num):
            subplot = self.subplots[i]

            subplot_default_visibile = True
            if i >= self.default_visible_subplot_num:
                subplot_default_visibile = False
            plot_pos, button_pos, check_buttons_pos = self.cal_ax_poses(i)
            subplot.plot(
                fig=self.fig,
                plot_ax_pos=plot_pos,
                button_ax_pos=button_pos,
                check_buttons_ax_pos=check_buttons_pos,
                x_axis_data=x_axis_data,
                mouse_event_callback=self.subplot_mouse_toggle_event,
                button_event_callback=self.subplot_button_toggle_event
            )
        plt.show()

    def subplot_button_toggle_event(self, major_subplot: ExcelPlotSubfigure) -> None:
        """
        子图中按键点击时调用, 设置绘图布局
        """
        if self.subplot_num <= 1 and True == major_subplot.visible: # 子图数只有1且期望隐藏时不响应
            pass
        else: # 否则翻转子图状态
            major_subplot.visible = not major_subplot.visible
            if False == major_subplot.visible:
                self.subplot_num -= 1
                self.visible_subplots_dq.remove(major_subplot)
            else:
                self.subplot_num += 1
                if self.subplot_num > self.visible_subplot_num_max:
                    self.subplot_num = self.visible_subplot_num_max
                    subplot_miss: ExcelPlotSubfigure = self.visible_subplots_dq.pop()
                    subplot_miss.visible = False
                self.visible_subplots_dq.append(major_subplot)

        # 调整整体布局
        for i in range(self.data_category_num):
            subplot = self.subplots[i]
            if subplot in self.visible_subplots_dq:
                # 可见队列中的子图重新布局
                plot_pos, button_pos, check_buttons_pos = self.cal_ax_poses(self.visible_subplots_dq.index(subplot))
            else:
                # 把非可见队列中的子图都放到看不见的区域
                plot_pos, button_pos, check_buttons_pos = self.cal_ax_poses(4)
            # 更新子图布局
            subplot.plot_ax.set_position(plot_pos)
            #subplot.button_ax.set_position(button_pos)
            subplot.check_buttons_ax.set_position(check_buttons_pos)

        # 画布更新
        self.fig.canvas.draw_idle()

    def subplot_mouse_toggle_event(self, major_subplot: ExcelPlotSubfigure, mouse_event: matplotlib.backend_bases.MouseEvent) -> None:
        """
        子图中的鼠标事件回调函数, 同步各子图行为
        """
        for other_subplot in self.subplots:
            if other_subplot is major_subplot:
                continue

            # 获取子图横纵轴更新范围
            x_min, x_max = other_subplot.plot_ax.get_xlim()
            y_min, y_max = other_subplot.plot_ax.get_ylim()
            subplot_width  = x_max - x_min
            subplot_height = y_max - y_min
            updated_x_min = x_min
            updated_x_max = x_max
            updated_y_min = y_min
            updated_y_max = y_max
            if mouse_event.name == 'button_press_event' and mouse_event.button == 1:
                if other_subplot.vline is not None:
                    other_subplot.vline.remove()
                other_subplot.vline = other_subplot.plot_ax.axvline(x=mouse_event.xdata, color='black', linewidth=1, visible=True)
            
            elif mouse_event.name == 'scroll_event':
                # 横向缩放
                x_mid = (x_max + x_min) / 2.0
                y_mid = (y_max + y_min) / 2.0
                updated_x_min = x_mid - (subplot_width  / 2.0) * major_subplot.mouse_scroll_rx
                updated_x_max = x_mid + (subplot_width  / 2.0) * major_subplot.mouse_scroll_rx
                updated_y_min = y_mid - (subplot_height / 2.0) * major_subplot.mouse_scroll_ry
                updated_y_max = y_mid + (subplot_height / 2.0) * major_subplot.mouse_scroll_ry
            
            elif mouse_event.name == 'motion_notify_event':
                # 横向移动
                mx = subplot_width  * major_subplot.mouse_move_rx
                my = subplot_height * major_subplot.mouse_move_ry
                updated_x_min = x_min - mx
                updated_x_max = x_min - mx + subplot_width
                # 纵向移动
                updated_y_min = y_min - my
                updated_y_max = y_min - my + subplot_height

            # 其它子图同步更新
            other_subplot.plot_ax.set_xlim(updated_x_min, updated_x_max)
            if True == self.y_sync:
                other_subplot.plot_ax.set_ylim(updated_y_min, updated_y_max)
            other_subplot.plot_ax.set_xticks(np.linspace(updated_x_min, updated_x_max, other_subplot.xticks_density))

        # 画布更新
        self.fig.canvas.draw_idle()

class ExcelPlotUiMini(ExcelPlotBaseFigure):
    def __init__(
        self,
        name: str,
        fig: matplotlib.figure.Figure,
        plot_ax_pos: np.ndarray,
        button_ax_pos: np.ndarray,
        check_buttons_ax_pos: np.ndarray,
        data_frame: pd.DataFrame
    ) -> None:
        super().__init__(name=name, fig=fig, cursor_info=None, mouse_event_callback=None)

        self.data_frame = data_frame
        self.check_buttons_labels: list[str] = data_frame.columns
        self.button_ax_pos = plot_ax_pos
        self.button_ax_pos = button_ax_pos
        self.check_buttons_ax_pos = check_buttons_ax_pos
        self.plot_ax = self.fig.add_axes(self.plot_ax_pos)
        self.button_ax = self.fig.add_axes(self.button_ax_pos)
        self.check_buttons_ax = self.fig.add_axes(self.check_buttons_ax_pos)
        self.button = Button(ax=self.button_ax, label=self.name)
        self.check_buttons = CheckButtons(ax=self.check_buttons_ax, labels=self.check_buttons_labels)

        self.button.on_clicked(self.button_toggle_event)
        self.check_buttons.on_clicked(self.checkbuttons_toggle_event)

        self.vline: matplotlib.lines.Line2D = None

        self.is_x_choosed = False
        self.x_label = ""
        self.curves: list[ExcelPlotCurve] = []

    def plot(self, x_axis_data: np.ndarray) -> None:
        self.x_axis_data = x_axis_data
        lines = []
        for curve in self.curves:
            if curve.label == self.x_label:
                continue
            curve.plot(self.plot_ax, self.x_axis_data)
            lines.append(curve.line)
        self.cursor = mplcursors.cursor(lines, multiple=True)
        self.cursor.connect('add', self.update_cursor_annotation)

        self.plot_ax.set_xlim(self.x_axis_data.min(), self.x_axis_data.max())
        self.plot_ax.legend(fontsize=8)
        self.plot_ax.grid()
        self.plot_ax.set_xticks(np.linspace(self.x_axis_data.min(), self.x_axis_data.max(), self.xticks_density))
        self.plot_ax.tick_params(axis='x', rotation=20)
        self.plot_ax.ticklabel_format(axis='x', style='plain')

    def button_toggle_event(self, event) -> None:
        if self.button_ax == event.inaxes:
            root = tk.Tk()
            root.withdraw()
            filepath = filedialog.askopenfilename()
            data_frame: pd.DataFrame
            read_success = False
            try:
                data_frame = pd.read_csv(filepath)
                read_success = True
                print("Read file successfully!")
            except:
                print("Read file failed!")

            if True == read_success:
                self.data_frame = data_frame
                self.remove_all_curve()
                self.plot_ax.clear()
                self.is_x_choosed = False
                self.x_label = ""

                self.check_buttons.ax.remove()
                self.check_buttons_labels = self.data_frame.columns
                self.check_buttons_ax = self.fig.add_axes(self.check_buttons_ax_pos)
                self.check_buttons = CheckButtons(ax=self.check_buttons_ax, labels=self.check_buttons_labels)
                self.check_buttons.on_clicked(self.checkbuttons_toggle_event)
                self.fig.canvas.draw_idle()

    def mouse_toggle_event(self, event: matplotlib.backend_bases.MouseEvent) -> None:
        super().mouse_toggle_event(event)

        if self.plot_ax == event.inaxes and \
           (event.name == 'button_press_event' or event.name == 'scroll_event' or\
            event.name == 'button_press_event' or event.name == 'button_release_event' or \
            (event.name == 'motion_notify_event' and event.button == 3 and self.mouse_press == True)):
            self.fig.canvas.draw_idle()

    # 本图复选框勾选回调函数
    # 复选框勾选曲线显示或隐藏
    def checkbuttons_toggle_event(self, label: str) -> None:
        if False == self.is_x_choosed:
            self.x_flag = True
            self.x_label = label
            self.x_axis_data = self.data_frame[label].values
            return
        elif True == self.is_x_choosed and label == self.x_label:
            self.x_flag = False
            self.x_label = ""
            self.plot_ax.clear()
            return

        if label in [curve.label for curve in self.curves]:
            index = [curve.label for curve in self.curves].index(label)
            curve = self.curves[index]
            self.remove_curve(curve)
        else:
            curve = ExcelPlotCurve(y_axis_data=self.data_frame[label].values, label=label, color=None, visible=True)
            self.add_curve(curve)

        self.plot_ax.clear()
        if self.curve_num > 0:
            self.plot(self.x_axis_data)

        self.fig.canvas.draw_idle()