import os
import sys
import matplotlib.pyplot as plt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from excel_plot.excel_plot import ExcelPlotUiMini

TOOL_VERSION = "ANY_PLOT_TOOL 241010"

def main():
    # 创建mpl画布
    plt.rcParams['toolbar'] = 'None'
    fig = plt.figure()
    fig.set_size_inches(18, 9)
    # 创建绘图ui
    excel_plot_ui = ExcelPlotUiMini(TOOL_VERSION, fig)
    excel_plot_ui.open_file()
    plt.show()

if __name__ == '__main__':
    main()