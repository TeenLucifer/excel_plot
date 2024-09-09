import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
from debug_figure import CursorInfo, DebugFigureCurve, DebugFigureSubplot, DebugFigure
from debug_figure import DebugFigureBasePlot
from debug_figure import DebugFigureSubplot_
from debug_figure import DebugFigureAnyPlot

TOOL_VERSION = "ANY_PLOT_TOOL 240907"

def main():
    plt.rcParams['toolbar'] = 'None'

    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    data_frame: pd.DataFrame
    try:
        data_frame = pd.read_csv(file_path)
        print("Read file successfully!")
    except:
        print("Read file failed!")
        sys.exit(1)

    label_list = data_frame.columns
    color_tab: list[str] = ['tab:blue', 'tab:red', 'tab:green', 'tab:orange', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
    button_ax_pos        = [0.005, 0.95, 0.10, 0.03]
    check_buttons_ax_pos = [0.005, 0.05, 0.10, 0.89]
    plot_ax_pos          = [0.130, 0.05, 0.80, 0.89]

    fig = plt.figure(TOOL_VERSION)
    any_plot = DebugFigureAnyPlot(name="Open File", fig=fig, data_frame=data_frame)
    any_plot.set_widgets(
        plot_ax_pos=plot_ax_pos,
        button_ax_pos=button_ax_pos,
        check_buttons_ax_pos=check_buttons_ax_pos
    )

    plt.show()

if __name__ == '__main__':
    main()