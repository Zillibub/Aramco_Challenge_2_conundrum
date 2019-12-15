# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'visualizer.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!
import os
import pickle
from time import sleep

import matplotlib.pyplot as plt
import utm
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtTest
from PyQt5 import QtWidgets
from scipy.interpolate import griddata
import numpy as np
import pandas as pd
from typing import List

plt.style.use('ggplot')
import sys

sys.path.append('../')
CLUSTER_NAMES = ['gas', 'production', 'rock']


def set_ax_style(ax: plt.Axes, title, x_label, y_label, font='Tahoma', label_font_size=14, title_font_size=20):
    ax.set_title(title, fontfamily=font, fontsize=title_font_size)
    ax.set_xlabel(x_label, fontfamily=font, fontsize=label_font_size)
    ax.set_ylabel(y_label, fontfamily=font, fontsize=label_font_size)


class MPLCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=8, dpi=100, nrows_sub=1, ncols_sub=1):
        self.fig = Figure(figsize=(width, height))

        self.axes: List[plt.Axes] = []
        for i in range(nrows_sub * ncols_sub):
            self.axes.append(self.fig.add_subplot('{}{}{}'.format(nrows_sub, ncols_sub, i + 1)))

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def clear(self):
        for ax in self.axes:
            ax.clear()


def plot_contour(x, y, z, resolution=50, contour_method='linear'):
    resolution = str(resolution) + 'j'
    X, Y = np.mgrid[min(x):max(x):complex(resolution), min(y):max(y):complex(resolution)]
    points = [[a, b] for a, b in zip(x, y)]
    Z = griddata(points, z, (X, Y), method=contour_method)
    return X, Y, Z


def read_prod_data():
    production = pd.read_csv('./data/CNS_Field_Production.csv')
    dates_to_plot = np.load(os.path.abspath('data/date_to_plot.npy'), allow_pickle=True)

    x, y = production.X.values, production.Y.values

    for i, (x_, y_) in enumerate(zip(x, y)):
        x[i], y[i], _, _ = utm.from_latlon(y_, x_, force_zone_number=31, force_zone_letter='V')

    production['X'] = x
    production['Y'] = y
    production['block'] = production['WELLREGNO'].str.extract('(\d\d\/\d\d\w?)').iloc[:, 0].str.lower()
    production['oil'] = production['OILPRODMAS']
    production['gas'] = production['AGASPRODMA']
    production['gas/oil'] = production.gas / production.oil

    return production, dates_to_plot


def read_cluster_data():
    res = {}

    for feats_type in CLUSTER_NAMES:
        df = pd.read_csv(f'./data/{feats_type}_labels.csv')
        df.dropna(inplace=True)
        x, y = df.WH_LONG.values, df.WH_LAT.values
        for i, (x_, y_) in enumerate(zip(x, y)):
            y[i], x[i], _, _ = utm.from_latlon(y_, x_, force_zone_number=31, force_zone_letter='V')

        df.WH_LONG = x
        df.WH_LAT = y
        res[feats_type] = df

    return res


class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.load_data()
        self.setupUi()
        self.setup_axes()
        self.current_date_idx = 0
        self.tl_stoped = False
        self._gas_cb_seted = False
        self.curr_cb_prod = ''
        self.cb = None
        self.init_all_plots()

    def load_data(self):
        with open('./data/all_model_predicts_with_clusters.pkl', 'rb') as f:
            self.curv_data = pickle.load(f)
        self.prod_data, self.date_to_plot = read_prod_data()
        self.date_to_plot = self.date_to_plot[12:]
        self.selected_curvs = ['21/25', '30/07a', '22/06a', '22/11']
        self.prod_cols = ['oil', 'gas', 'gas/oil']
        self.current_prod = self.prod_cols[0]
        self.clsuster_data = read_cluster_data()

    def setup_axes(self):
        sf = 0.05
        x_min, y_min = self.prod_data['X'].min(), self.prod_data['Y'].min()
        x_max, y_max = self.prod_data['X'].max(), self.prod_data['Y'].max()
        dx = x_max - x_min
        dy = y_max - y_min
        self.prod_surf.axes[0].set_xlim(*[x_min - dx * sf, x_max + dx * sf])
        self.prod_surf.axes[0].set_ylim(*[y_min - dy * sf, y_max + dy * sf])
        self.clusters_plot.axes[0].set_xlim(*[x_min - dx * sf, x_max + dx * sf])
        self.clusters_plot.axes[0].set_ylim(*[y_min - dy * sf, y_max + dy * sf])

    def set_prod_colorbar(self, surf, prod_name):
        pass

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.resize(1435, 885)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout_2.addLayout(self.verticalLayout, 0, 0, 1, 1)

        # product list begin
        self.product_list = QtWidgets.QComboBox(self.centralwidget)
        self.product_list.addItems(self.prod_cols)
        self.product_list.currentIndexChanged.connect(self.change_product)
        self.product_list.setObjectName("date_time_list")
        # product list end

        self.verticalLayout.addWidget(self.product_list)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")

        # Feature importance plot begin
        self.feature_importance = MPLCanvas(self.centralwidget)
        self.feature_importance.setMinimumSize(QtCore.QSize(629, 299))
        self.feature_importance.setObjectName("feature_importance")
        # Feature importance plot end

        self.gridLayout.addWidget(self.feature_importance, 1, 1, 1, 1)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout.setObjectName("horizontalLayout")

        # Oil and gas target list begin
        self.run_button = QtWidgets.QPushButton(self.centralwidget)
        self.run_button.setObjectName("run_button")
        self.run_button.pressed.connect(self.run_time_lapse)
        self.horizontalLayout.addWidget(self.run_button)
        # Oil and gas target list end

        self.stop_button = QtWidgets.QPushButton(self.centralwidget)
        self.stop_button.setObjectName("next_button")
        self.horizontalLayout.addWidget(self.stop_button)
        self.stop_button.pressed.connect(self.stop_time_lapse)

        self.prev_button = QtWidgets.QPushButton(self.centralwidget)
        self.prev_button.setObjectName("prev_button")
        self.prev_button.pressed.connect(self.plot_prev_surf)
        self.horizontalLayout.addWidget(self.prev_button)

        # Oil and gas horizons list begin
        self.next_button = QtWidgets.QPushButton(self.centralwidget)
        self.next_button.setObjectName("next_button")
        self.horizontalLayout.addWidget(self.next_button)
        self.next_button.pressed.connect(self.plot_next_surf)
        # Oil and gas horizons list end

        self.verticalLayout_3.addLayout(self.horizontalLayout)

        # Oil and gas surf begin
        self.clusters_plot = MPLCanvas(self.centralwidget)
        self.clusters_plot.setObjectName("og_surf")
        self.verticalLayout_3.addWidget(self.clusters_plot)
        # Oil and gas surf end

        self.cluster_list = QtWidgets.QComboBox(self.centralwidget)
        self.cluster_list.addItems(CLUSTER_NAMES)
        self.cluster_list.setObjectName("cluster_list")
        self.verticalLayout_3.addWidget(self.cluster_list)
        self.cluster_list.currentIndexChanged.connect(self.plot_clusters)

        self.verticalLayout_3.setStretch(1, 1)
        self.gridLayout.addLayout(self.verticalLayout_3, 1, 0, 1, 1)

        # Production surf begin
        self.prod_surf = MPLCanvas(self.centralwidget)
        self.prod_surf.setMinimumSize(QtCore.QSize(630, 299))
        self.prod_surf.setObjectName("prod_surf")
        # Production surf end

        self.gridLayout.addWidget(self.prod_surf, 0, 0, 1, 1)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")

        # Well list begin
        self.well_list = QtWidgets.QComboBox(self.centralwidget)
        self.well_list.addItems(list(self.selected_curvs))
        self.well_list.currentIndexChanged.connect(self.on_bloc_select)
        self.well_list.setObjectName("well_list")
        # Well list end

        self.verticalLayout_4.addWidget(self.well_list)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        # Production plot begin
        self.prod_plot = MPLCanvas(self.centralwidget)
        self.prod_plot.setObjectName("prod_plot")
        # Production plot end

        self.horizontalLayout_2.addWidget(self.prod_plot)

        # Oil and gas plot begin
        self.og_plot = QtWidgets.QWidget(self.centralwidget)
        self.og_plot.setObjectName("og_plot")
        # Oil and gas plot end

        self.horizontalLayout_2.addWidget(self.og_plot)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.verticalLayout_4.setStretch(1, 1)
        self.gridLayout.addLayout(self.verticalLayout_4, 0, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1435, 40))
        self.menubar.setObjectName("menubar")
        self.menuTechnotone = QtWidgets.QMenu(self.menubar)
        self.menuTechnotone.setObjectName("menuTechnotone")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuTechnotone.menuAction())

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    def plot_prod_surf(self, date, product_name):
        self.prod_surf.clear()
        self.setup_axes()
        set_ax_style(self.prod_surf.axes[0], f'Production map at {date[:7]}', 'X, m', ' Y, m')
        df = self.prod_data[self.prod_data['PERIODDATE'] == date]
        x, y, z = df['X'].values, df['Y'].values, df[product_name].values
        X, Y, Z = plot_contour(x, y, z, resolution=300, contour_method='linear')
        Z = np.clip(Z, 0, np.inf)
        surf = self.prod_surf.axes[0].contourf(X, Y, Z, cmap='seismic', levels=30)
        coors = df[['X', 'Y']].values
        self.prod_surf.axes[0].plot(coors[:, 0], coors[:, 1], 'o', color='green')
        self.set_prod_colorbar(surf, product_name)

        self.prod_surf.draw()

    def plot_clusters(self):
        self.clusters_plot.clear()
        self.setup_axes()
        set_ax_style(self.clusters_plot.axes[0], f'Clustering by {self.cluster_list.currentText()}', 'X, m',
                     'Y, m')
        cluster_data = self.clsuster_data[self.cluster_list.currentText()]

        scatter = self.clusters_plot.axes[0].scatter(cluster_data['WH_LAT'], cluster_data['WH_LONG'],
                                                     c=cluster_data[self.cluster_list.currentText() + '_labels'],
                                                     s=50, cmap='viridis')

        # produce a legend with the unique colors from the scatter
        legend1 = self.clusters_plot.axes[0].legend(*scatter.legend_elements(),
                                                    loc="lower left", title="Labels")
        self.clusters_plot.axes[0].add_artist(legend1)
        self.clusters_plot.draw()

    def plot_prediction_curve(self):
        self.prod_plot.clear()
        set_ax_style(self.prod_plot.axes[0], f'{self.current_prod.title()} production curve', 'Datetime',
                     'Production')
        true, pred, date = self.curv_data[self.current_prod][0][self.well_list.currentText()]
        date = list(map(lambda x: x[:7], date.astype(str)))
        self.prod_plot.axes[0].plot(date, true, label='True values')
        self.prod_plot.axes[0].plot(date, pred, label='Prediction')
        self.prod_plot.axes[0].xaxis.set_tick_params(rotation=70, labelsize=8)
        self.prod_plot.axes[0].legend(fontsize=14)
        self.prod_plot.draw()

    def plot_importance(self):
        self.feature_importance.clear()
        set_ax_style(self.feature_importance.axes[0], 'Feature importance', 'Score', 'Feature name')
        self.importance = self.curv_data[self.current_prod][1][self.well_list.currentText()]

        percentages = pd.Series(self.importance)
        df = pd.DataFrame({
            'feature_importance': percentages
        })
        df = df.sort_values(by='feature_importance')
        df = df.iloc[-10:, :]
        colors = [plt.get_cmap('YlGnBu')(i / float(len(df.values) - 1)) for i in range(len(df.values))]
        self.feature_importance.axes[0].barh(df['feature_importance'].index, df['feature_importance'], color=colors)

        self.feature_importance.draw()

    def on_bloc_select(self):
        self.plot_prediction_curve()
        self.plot_importance()

    def run_time_lapse(self):
        self.tl_stoped = False
        while self.current_date_idx != len(self.date_to_plot) - 1:
            if not self.tl_stoped:
                self.plot_prod_surf(self.date_to_plot[self.current_date_idx], self.current_prod)
                self.current_date_idx += 1
            else:
                break
            QtTest.QTest.qWait(1000)
        self.current_date_idx = 0

    def plot_next_surf(self):
        self.tl_stoped = True
        if self.current_date_idx == len(self.date_to_plot) - 1:
            return
        self.current_date_idx += 1
        self.plot_prod_surf(self.date_to_plot[self.current_date_idx], self.current_prod)

    def plot_prev_surf(self):
        self.tl_stoped = True
        if self.current_date_idx == 0:
            return
        self.current_date_idx -= 1
        self.plot_prod_surf(self.date_to_plot[self.current_date_idx], self.current_prod)

    def change_product(self):
        self.tl_stoped = True
        self.current_date_idx = 0
        self.current_prod = self.product_list.currentText()
        self.init_all_plots()

    def init_all_plots(self):
        self.plot_prod_surf(self.date_to_plot[self.current_date_idx], self.current_prod)
        self.plot_prediction_curve()
        self.plot_importance()
        self.plot_clusters()

    def change_cluster(self):
        self.plot_clusters()

    def stop_time_lapse(self):
        self.tl_stoped = True

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Oil and Gas Deposit Dashboard"))
        self.next_button.setText(_translate("MainWindow", "Next surf"))
        self.prev_button.setText(_translate("MainWindow", "Prev surf"))
        self.run_button.setText(_translate("MainWindow", "Run time-lapse"))
        self.stop_button.setText(_translate("MainWindow", "Stop"))
        self.cluster_list.setFont(QtGui.QFont("Verdana", 12, QtGui.QFont.Normal))
        self.product_list.setFont(QtGui.QFont("Verdana", 12, QtGui.QFont.Normal))
        self.well_list.setFont(QtGui.QFont("Verdana", 12, QtGui.QFont.Normal))
        self.next_button.setFont(QtGui.QFont("Verdana", 12, QtGui.QFont.Normal))
        self.prev_button.setFont(QtGui.QFont("Verdana", 12, QtGui.QFont.Normal))
        self.run_button.setFont(QtGui.QFont("Verdana", 12, QtGui.QFont.Normal))
        self.stop_button.setFont(QtGui.QFont("Verdana", 12, QtGui.QFont.Normal))
        self.menuTechnotone.setTitle(_translate("MainWindow", "AramcoTechnotone"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    self = Ui_MainWindow()
    self.resize(1920, 1080)
    self.show()
    sys.exit(app.exec_())
