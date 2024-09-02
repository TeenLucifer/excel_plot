#·绘图相关模块
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
#·计算相关模块
import numpy as np
from collections import deque

class CursorInfo:
    def __init__(self) -> None:
        self.info_num = 0
        self.info_name_list: list[str] = []
        self.info_data_list: list = []
    def add_info(self, name: str, data: list) -> None:
        self.info_name_list.append(name)
        self.info_data_list.append(data)
        self.info_num += 1

class DebugFigureCurve:
    def __init__(
        self,
        y_axis_data: np.ndarray,
        label: str,
        color: str,
        visible: bool | None = True,
        cursor_info: CursorInfo = None,
    ) -> None:
        self.y_axis_data = y_axis_data
        self.label = label
        self.color = color
        self.visible = visible
        self.line: matplotlib.lines.Line2D
        self.cursor: mplcursors.cursor.Cursor
        self.cursor_info: CursorInfo = cursor_info

    def plot(
        self,
        plot_ax: matplotlib.axes.Axes,
        x_axis_data: np.ndarray,
    ) -> None:
        self.line = plot_ax.plot(
            x_axis_data,
            self.y_axis_data,
            label=self.label,
            color=self.color,
            visible=self.visible,
        )[0]
        
        self.cursor = mplcursors.cursor(self.line, multiple=True)
        self.cursor.connect("add", self.update_cursor_annotation)

    def set_visible(self, visible):
        self.visible = visible
        self.line.set_visible(visible)

    def update_cursor_annotation(self, cursor):
        cursor_text = f'{cursor.artist.get_label()}:{cursor.target[1]:.2f}'
        index = round(cursor.index)
        info = ''
        if self.cursor_info is not None:
            for i in range(self.cursor_info.info_num):
                name = self.cursor_info.info_name_list[i]
                data = self.cursor_info.info_data_list[i][index]
                info = f'\n{name}:{data}'
                cursor_text += info
        cursor.annotation.set_text(cursor_text)

class DebugFigureSubplot:
    def __init__(self, name: str, x_axis_data: np.ndarray) -> None:
        self.name = name
        self.x_axis_data = x_axis_data
        self.xticks_density = 30

        self.fig = matplotlib.figure.Figure
        self.plot_ax = matplotlib.axes.Axes
        self.button_ax = matplotlib.axes.Axes
        self.button = matplotlib.widgets.Button
        self.check_buttons_ax = matplotlib.axes.Axes
        self.check_buttons = matplotlib.widgets.CheckButtons

        self.curve_num = 0
        self.curves: list[DebugFigureCurve] = []

        self.visible = True

        self.mouse_event_callback = None
        self.mouse_press = False
        self.mouse_move_start_x = 0
        self.mouse_move_start_y = 0
        self.mouse_move_rx = 0.0
        self.mouse_move_ry = 0.0
        self.mouse_scroll_rx = 1.0
        self.mouse_scroll_ry = 1.0
        self.vline: matplotlib.lines.Line2D = None

        self.button_event_callback = None

    def add_curve(
        self,
        curve: DebugFigureCurve,
    ) -> None:
        self.curves.append(curve)
        self.curve_num += 1

    def plot(
        self,
        fig: matplotlib.figure.Figure,
        plot_ax_pos: np.ndarray,
        button_ax_pos: np.ndarray,
        check_buttons_ax_pos: np.ndarray,
        default_visible: bool = True,
        mouse_event_callback = None,
        button_event_callback = None,
    ) -> None:
        self.fig = fig
        self.plot_ax: matplotlib.axes.Axes = self.fig.add_axes(plot_ax_pos)
        self.button_ax: matplotlib.axes.Axes = self.fig.add_axes(button_ax_pos)
        self.check_buttons_ax: matplotlib.axes.Axes = self.fig.add_axes(check_buttons_ax_pos)

        self.fig.canvas.mpl_connect('scroll_event',         self.mouse_toggle_event)
        self.fig.canvas.mpl_connect('button_press_event',   self.mouse_toggle_event)
        self.fig.canvas.mpl_connect('button_release_event', self.mouse_toggle_event)
        self.fig.canvas.mpl_connect('motion_notify_event',  self.mouse_toggle_event)

        self.mouse_event_callback = mouse_event_callback

        self.button_event_callback = button_event_callback

        for curve in self.curves:
            curve.plot(self.plot_ax, self.x_axis_data)

        self.button = Button(ax=self.button_ax, label=self.name)
        self.button.on_clicked(self.button_toggle_event)

        labels = [curve.label for curve in self.curves]
        visibility = [curve.visible for curve in self.curves]
        self.check_buttons = CheckButtons(
            ax=self.check_buttons_ax,
            labels=labels,
            actives=visibility,
        )
        self.check_buttons.on_clicked(self.checkbuttons_toggle_event)

        self.plot_ax.set_xlim(self.x_axis_data.min(), self.x_axis_data.max())
        self.plot_ax.legend(fontsize=8)
        self.plot_ax.grid()
        self.plot_ax.set_xticks(np.linspace(self.x_axis_data.min(), self.x_axis_data.max(), self.xticks_density))
        self.plot_ax.tick_params(axis='x', rotation=20)
        self.plot_ax.ticklabel_format(axis='x', style='plain')

        for curve in self.curves:
            curve.set_visible(curve.visible)

    def checkbuttons_toggle_event(self, label: str) -> None:
        index = [curve.label for curve in self.curves].index(label)
        self.curves[index].visible = not self.curves[index].visible
        self.curves[index].line.set_visible(self.curves[index].visible)
        self.fig.canvas.draw_idle()

    def mouse_toggle_event(self, event: matplotlib.backend_bases.MouseEvent) -> None:
        if self.plot_ax == event.inaxes and \
           (event.name == 'button_press_event' or event.name == 'scroll_event' or\
            event.name == 'button_press_event' or event.name == 'button_release_event' or \
            event.name == 'motion_notify_event' and event.button == 3 and self.mouse_press == True):

            x_min, x_max = self.plot_ax.get_xlim()
            y_min, y_max = self.plot_ax.get_ylim()
            subplot_width = x_max - x_min
            subplot_height = y_max - y_min
            updated_x_min = x_min
            updated_x_max = x_max
            updated_y_min = y_min
            updated_y_max = y_max

            if event.name == 'button_press_event' and event.button == 1:
                for curve in self.curves:
                    for sel in curve.cursor.selection:
                        annotation = sel.annotation
                        bbox = annotation.get_window_extent()
                        if bbox.contains(event.x, event.y):
                            return
                if self.vline is not None:
                    self.vline.remove()
                self.vline = self.plot_ax.axvline(x=event.xdata, color='black', linewidth=1, visible=True)

            if event.name == 'scroll_event':
                scale_factor = 0.9 if event.button == 'up' else 1.1
                fig_width_px, fig_height_px = self.fig.canvas.get_width_height()

                if event.x > fig_height_px / 5.0:
                    self.mouse_scroll_rx = scale_factor
                    self.mouse_scroll_ry = 1.0

                    x_mid = (x_max + x_min) / 2.0
                    updated_x_min = x_mid - (x_mid - x_min) * self.mouse_scroll_rx
                    updated_x_max = x_mid + (x_max - x_mid) * self.mouse_scroll_rx
                else:
                    self.mouse_scroll_rx = 1.0
                    self.mouse_scroll_ry = scale_factor

                    y_mid = (y_max + y_min) / 2.0
                    updated_y_min = y_mid - (y_mid - y_min) * self.mouse_scroll_ry
                    updated_y_max = y_mid + (y_max - y_mid) * self.mouse_scroll_ry

            if event.name == 'button_press_event' and event.button == 3:
                self.mouse_press = True
                self.mouse_move_start_x = event.x
                self.mouse_move_start_y = event.y
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

            if (event.name == 'scroll_event' or (event.name == 'motion_notify_event' and self.mouse_press) or\
                (event.name == 'button_press_event' and event.button == 1) and self.mouse_event_callback is not None):
                self.mouse_event_callback(self, event)

            self.fig.canvas.draw_idle()

    def button_toggle_event(self, event) -> None:
        if (self.button_event_callback is not None):
            self.button_event_callback(self)


class DebugFigure:
    def __init__(self, title: str,) -> None:
        self.title = title
        self.fig = matplotlib.figure.Figure
        self.subplot_num = 0
        self.subplots: list[DebugFigureSubplot] = []
        self.data_category_num = 0
        self.default_visible_subplot_num = 2
        self.visible_subplot_num_max = 3
        self.visible_subplots_dq = deque(maxlen=self.visible_subplot_num_max)

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

        self.y_sync = False
    
    def add_subplot(self, subplot: DebugFigureSubplot) -> None:
        self.subplots.append(subplot)
        self.data_category_num += 1
        self.subplot_num += 1
        self.visible_subplots_dq.append(subplot)
        if self.data_category_num > self.default_visible_subplot_num:
            subplot.visible = False
            self.visible_subplots_dq.remove(subplot)
        if self.subplot_num > self.default_visible_subplot_num:
            self.subplot_num = self.default_visible_subplot_num

    def cal_ax_poses(self, data_category_idx):
        self.subplot_plot_step = 1.0 / self.subplot_num
        self.subplot_height = 1.0 / self.subplot_num
        self.check_buttons_plot_step = 1.0 / self.subplot_num

        subplot_pos       = np.array([self.subplot2left,       self.subplot2bottom_max - (data_category_idx + 1) * self.subplot_plot_step + 0.04, self.subplot_width, self.subplot_height - 0.04])
        button_pos        = np.array([self.button2left,        self.button2bottom_max - (data_category_idx + 1) * self.button_plot_step, self.button_width, self.button_height])
        check_buttons_pos = np.array([self.check_buttons2left, self.check_buttons2bottom_max - (data_category_idx + 1) * self.check_buttons_plot_step + 0.04, self.check_buttons_width, self.check_buttons_height])

        return subplot_pos, button_pos, check_buttons_pos

    def plot(self, suptitle: str) -> None:
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
                default_visible=subplot_default_visibile,
                mouse_event_callback=self.subplot_mouse_toggle_event,
                button_event_callback=self.subplot_button_toggle_event,
            )
        plt.show()

    def subplot_button_toggle_event(self, major_subplot: DebugFigureSubplot) -> None:
        if self.subplot_num <= 1 and True == major_subplot.visible:
            pass
        else:
            major_subplot.visible = not major_subplot.visible
            if False == major_subplot.visible:
                self.subplot_num -= 1
                self.visible_subplots_dq.remove(major_subplot)
            else:
                self.subplot_num += 1
                if self.subplot_num > self.visible_subplot_num_max:
                    self.subplot_num = self.visible_subplot_num_max
                    subplot_miss: DebugFigureSubplot = self.visible_subplots_dq.pop()
                    subplot_miss.visible = False
                self.visible_subplots_dq.append(major_subplot)

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

    def subplot_mouse_toggle_event(
        self,
        major_subplot: DebugFigureSubplot,
        mouse_event: matplotlib.backend_bases.MouseEvent
    ) -> None:
        for other_subplot in self.subplots:
            if other_subplot is major_subplot:
                continue

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
                x_mid = (x_max + x_min) / 2.0
                y_mid = (y_max + y_min) / 2.0
                updated_x_min = x_mid - (subplot_width  / 2.0) * major_subplot.mouse_scroll_rx
                updated_x_max = x_mid + (subplot_width  / 2.0) * major_subplot.mouse_scroll_rx
                updated_y_min = y_mid - (subplot_height / 2.0) * major_subplot.mouse_scroll_ry
                updated_y_max = y_mid + (subplot_height / 2.0) * major_subplot.mouse_scroll_ry
            
            elif mouse_event.name == 'motion_notify_event':
                mx = subplot_width  * major_subplot.mouse_move_rx
                my = subplot_height * major_subplot.mouse_move_ry
                updated_x_min = x_min - mx
                updated_x_max = x_min - mx + subplot_width

                updated_y_min = y_min - my
                updated_y_max = y_min - my + subplot_height

            other_subplot.plot_ax.set_xlim(updated_x_min, updated_x_max)
            if True == self.y_sync:
                other_subplot.plot_ax.set_y_lim(updated_y_min, updated_y_max)
            other_subplot.plot_ax.set_xticks(np.linspace(self.x_axis_data.min(), self.x_axis_data.max(), self.xticks_density))

        self.fig.canvas.draw_idle()