from calc import Calc
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import matplotlib.ticker as ticker
from matplotlib.widgets import RangeSlider, CheckButtons
from globalData import GlobalData
import colorsys
from mpl_toolkits.axes_grid1 import make_axes_locatable

class View():
    def __init__(self, path, topic_field_pairs):
        self.calc = Calc(path)
        self.topic_field_pairs = topic_field_pairs
        self.cn_field = ''
        self.lines = []
        pass
    def show(self):
        print("通用版可视化开始喽")
        fig = plt.figure(figsize=(7, 5), dpi=100)
        ax = fig.subplots()
        #plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
        plt.rcParams['axes.unicode_minus'] = False  
        plt.subplots_adjust(left=0.185,bottom=0.2)
        plt.xlabel('时间')
        if len(self.topic_field_pairs) >= 2 :
            plt.ylabel("数据字段")
        else:
            tmp_field = self.topic_field_pairs[0][1]
            status = GlobalData.param_dict.get(tmp_field)
            if status is not None:
                self.cn_field = status
            else:
                self.cn_field = tmp_field
            plt.ylabel(self.cn_field)
        divider = make_axes_locatable(ax)
        checkbox_ax = divider.append_axes("right", size="10%", pad=0.05, frameon=False)
        checkbox = CheckButtons(checkbox_ax, [field for topic, field in self.topic_field_pairs],
                                [True for _ in range(len(self.topic_field_pairs))])

        def update_checkbox(label):
            idx = [i for i,(topic, field) in enumerate(self.topic_field_pairs) if field == label][0]
            print("-----------------------")
            self.lines[idx].set_visible(not self.lines[idx].get_visible())
            plt.draw()

        checkbox.on_clicked(update_checkbox)
        for topic,field in self.topic_field_pairs:
            list_param_r1, list_param_r2 = self.calc.getData(topic,field)
            self.cn_field = GlobalData.param_dict.get(field)
            data = {
                'xa': list_param_r1,
                'ya': list_param_r2,
            }
            df = pd.DataFrame(data)
            sns.lineplot(
                data=df,
                x='xa',
                y='ya',
                alpha=0.8,
                errorbar=None,
                label=None,
                ax=ax
            )
        ax.xaxis.set_major_locator(ticker.MultipleLocator(base=26)) 
        ax_slider = plt.axes([0.18, 0.06, 0.65, 0.03])
        slider = RangeSlider(ax_slider, '时间段', 0, 100, valinit=(0,100))
        self.lines = ax.get_lines()
        def update(val):
            start, end = slider.val
            ax.set_xlim(start, end)
            fig.canvas.draw_idle()
        slider.on_changed(update)
        slider.poly.set_visible(True)
        plt.show()