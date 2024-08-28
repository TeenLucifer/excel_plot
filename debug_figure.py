#·绘图相关模块
import matplotlib.axes
import matplotlib.figure
import matplotlib.lines
import matplotlib.widgets
import mplcursors
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons
from matplotlib.widgets import Button
#·计算相关模块
import numpy as np
from collections import deque

class DebugFigureSingleCurve:
    def __init__(
        self,
        y_axis_data: np.ndarray,
        label: str,
        color: str,
        visible: bool | None = True,
    ) -> None:
        self.y_axis_data = y_axis_data
        self.label = label
        self.color = color
        self.visible = visible
        self.line = matplotlib.lines.Line2D

class DebugFigureSubplot:
    def __init__(self, name: str, x_axis_data: np.ndarray) -> None:
        self.name = name
        self.x_axis_data = x_axis_data

        self.fig = matplotlib.figure.Figure
        self.plot_ax = matplotlib.axes.Axes
        self.button_ax = matplotlib.axes.Axes
        self.button = matplotlib.widgets.Button
        self.check_buttons_ax = matplotlib.axes.Axes
        self.check_buttons = matplotlib.widgets.CheckButtons

        self.curve_num = 0
        self.curves: list[DebugFigureSingleCurve] = []

        self.visible = True

    def add_curve(
        self,
        curve: DebugFigureSingleCurve,
    ) -> None:
        self.curves.append(curve)
        self.curve_num += 1

    def plot(
        self,
        fig: matplotlib.figure.Figure,
        plot_ax_pos: np.ndarray,
        button_ax_pos: np.ndarray,
        check_buttons_ax_pos: np.ndarray,
    ) -> None:
        self.fig = fig
        self.plot_ax = self.fig.add_axes(plot_ax_pos)
        self.button_ax = self.fig.add_axes(button_ax_pos)
        self.check_buttons_ax = self.fig.add_axes(check_buttons_ax_pos)

        for curve in self.curves:
            curve.line = self.plot_ax.plot(
                self.x_axis_data,
                curve.y_axis_data,
                label=curve.label,
                color=curve.color,
                visible=curve.visible,
            )[0]

        self.button = Button(ax=self.button_ax, label=self.name)
        #self.button.on_clicked(self.button_toggle_subplot)

        labels = [curve.label for curve in self.curves]
        visibility = [curve.visible for curve in self.curves]
        self.check_buttons = CheckButtons(
            ax=self.check_buttons_ax,
            labels=labels,
            actives=visibility,
        )
        self.check_buttons.on_clicked(self.checkbuttons_toggle_visibility)

    def checkbuttons_toggle_visibility(self, label: str) -> None:
        index = [curve.label for curve in self.curves].index(label)
        self.curves[index].visible = not self.curves[index].visible
        self.curves[index].line.set_visible(self.curves[index].visible)
        self.fig.canvas.draw_idle()

    # def button_toggle_subplot(self, event) -> None:
    #     self.plot_ax.set_visible(not self.plot_ax.get_visible())
    #     self.check_buttons_ax.set_visible(not self.check_buttons_ax.get_visible())
    #     self.fig.canvas.draw_idle()

class DebugFigure:
    def __init__(self, title: str,) -> None:
        self.title = title
        self.subplot_num = 1
        self.data_category_num = 0
        self.subplots: list[DebugFigureSubplot] = []
        self.visible_subplots_dq = deque(maxlen=3)

        self.fig = matplotlib.figure.Figure

        self.subplot2left = 0.13
        self.subplot2bottom_max = 1.0
        self.subplot_width = 0.85
        self.subplot_height = 1.0 / self.subplot_num
        self.subplot_plot_step = 1.0 / self.subplot_num

        self.button2left = 0.005
        self.button2bottom_max = 1.0
        self.button_width = 0.08
        self.button_height = 0.03
        self.button_plot_step = self.button_height

        self.check_buttons2left = 0.005
        self.check_buttons2bottom_max = 1.0
        self.check_buttons_width = 0.08
        self.check_buttons_height = 0.10
        self.check_buttons_plot_step = 1.0 / self.subplot_num
    
    def add_subplot(self, subplot: DebugFigureSubplot) -> None:
        self.subplots.append(subplot)
        self.data_category_num += 1
        self.subplot_num += 1
        self.visible_subplots_dq.append(subplot)
        if self.data_category_num > 2:
            subplot.visible = False
            self.visible_subplots_dq.remove(subplot)
        if self.subplot_num > 2:
            self.subplot_num = 2

    def cal_ax_poses(self, data_category_idx):
        self.subplot_plot_step = 1.0 / self.subplot_num
        self.subplot_height = 1.0 / self.subplot_num
        self.check_buttons_plot_step = 1.0 / self.subplot_num

        subplot_pos       = np.array([self.subplot2left,       self.subplot2bottom_max - (data_category_idx + 1) * self.subplot_plot_step + 0.04, self.subplot_width, self.subplot_height - 0.04])
        button_pos        = np.array([self.button2left,        self.button2bottom_max - (data_category_idx + 1) * self.button_plot_step, self.button_width, self.button_height])
        check_buttons_pos = np.array([self.check_buttons2left, self.check_buttons2bottom_max - (data_category_idx + 1) * self.check_buttons_plot_step + 0.04, self.check_buttons_width, self.check_buttons_height])

        return subplot_pos, button_pos, check_buttons_pos

    def plot(self) -> None:
        self.fig = plt.figure(self.title)

        for i in range(self.data_category_num):
            subplot = self.subplots[i]

            plot_pos, button_pos, check_buttons_pos = self.cal_ax_poses(i)
            subplot.plot(
                fig=self.fig,
                plot_ax_pos=plot_pos,
                button_ax_pos=button_pos,
                check_buttons_ax_pos=check_buttons_pos,
            )
            subplot.plot_ax.set_xlim(subplot.x_axis_data.min(), subplot.x_axis_data.max())
            subplot.plot_ax.legend(fontsize=8)
            subplot.plot_ax.grid()
            subplot.plot_ax.set_xticks(np.linspace(subplot.x_axis_data.min(), subplot.x_axis_data.max(), 30))
            subplot.plot_ax.tick_params(axis='x', rotation=20)
            subplot.plot_ax.ticklabel_format(axis='x', style='plain')
            subplot.button.on_clicked(self.button_toggle_subplot)
            if i >= 2:
                subplot.visible = False

    def button_toggle_subplot(self, event) -> None:
        for i in range(self.data_category_num):
            subplot = self.subplots[i]
            if event.inaxes == subplot.button_ax:
                if False == subplot.visible: # 若当前为不可见, 需要反转状态, 则期望可见, 子图数+1
                    self.subplot_num += 1
                    self.visible_subplots_dq.append(subplot)
                else:
                    self.subplot_num -= 1
                    self.visible_subplots_dq.remove(subplot)
                subplot.visible = not subplot.visible

        for i in range(self.data_category_num):
            subplot = self.subplots[i]
            if subplot in self.visible_subplots_dq:
                plot_pos, button_pos, check_buttons_pos = self.cal_ax_poses(self.visible_subplots_dq.index(subplot))
            else:
                plot_pos, button_pos, check_buttons_pos = self.cal_ax_poses(4)
            subplot.plot_ax.set_position(plot_pos)
            #subplot.button_ax.set_position(button_pos)
            subplot.check_buttons_ax.set_position(check_buttons_pos)

        self.fig.canvas.draw_idle()