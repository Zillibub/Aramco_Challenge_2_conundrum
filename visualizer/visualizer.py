# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'visualizer.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!
from time import sleep

import matplotlib.pyplot as plt
import utm
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5 import QtCore
from PyQt5 import QtTest
from PyQt5 import QtWidgets
from scipy.interpolate import griddata
import numpy as np
import pandas as pd

plt.style.use('ggplot')
import sys

sys.path.append('../')


class MPLCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=8, dpi=100, nrows_sub=1, ncols_sub=1):
        self.fig = Figure(figsize=(width, height))

        self.axes = []
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
    production = pd.read_csv('../../challenge2/Production Data/CNS_Field_Production.csv')
    dates_to_plot = production.groupby(by=['PERIODDATE']).count()[production.groupby(by=['PERIODDATE']).count()['X']
                                                                  > 20].reset_index().iloc[:, 0]
    return production, dates_to_plot


class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi()
        self.prod_data, self.date_to_plot = read_prod_data()
        self.setup_prod_surf()
        self.current_prod = ''

    def setup_prod_surf(self):
        sf = 0.05
        x_min, y_min = self.prod_data['X'].min(), self.prod_data['Y'].min()
        x_max, y_max = self.prod_data['X'].max(), self.prod_data['Y'].max()
        dx = x_max - x_min
        dy = y_max - y_min
        self.prod_surf.axes[0].set_xlim([x_min - dx * sf, x_max + dx * sf])
        self.prod_surf.axes[0].set_ylim([y_min - dy * sf, y_max + dy * sf])

    def set_colorbar(self, surf, prod_name):
        if self.current_prod != prod_name:
            self.current_prod = prod_name
            # ToDo use min max fo sale
            self.prod_surf.fig.colorbar(surf, aspect=20)

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

        # Datetime list begin
        self.date_time_list = QtWidgets.QComboBox(self.centralwidget)
        self.date_time_list.setObjectName("date_time_list")
        # Datetime list end

        self.verticalLayout.addWidget(self.date_time_list)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")

        # Feature importance plot begin
        self.feature_importance = QtWidgets.QWidget(self.centralwidget)
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
        self.og_target_list = QtWidgets.QComboBox(self.centralwidget)
        self.og_target_list.setObjectName("og_target_list")
        # Oil and gas target list end

        self.horizontalLayout.addWidget(self.og_target_list)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)

        # Oil and gas horizons list begin
        self.og_horiz_list = QtWidgets.QComboBox(self.centralwidget)
        self.og_horiz_list.setObjectName("og_horiz_list")
        # Oil and gas horizons list end

        self.horizontalLayout.addWidget(self.og_horiz_list)
        self.verticalLayout_3.addLayout(self.horizontalLayout)

        # Oil and gas surf begin
        self.og_surf = QtWidgets.QWidget(self.centralwidget)
        self.og_surf.setObjectName("og_surf")
        # Oil and gas surf end

        self.verticalLayout_3.addWidget(self.og_surf)
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
        self.well_list.setObjectName("well_list")
        # Well list end

        self.verticalLayout_4.addWidget(self.well_list)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        # Production plot begin
        self.prod_plot = QtWidgets.QWidget(self.centralwidget)
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

    def plot_prod(self, date, product_name):
        self.prod_surf.clear()
        df = self.prod_data[self.prod_data['PERIODDATE']==date]
        x, y, z = df['X'].values, df['Y'].values, df[product_name].values
        for i, (x_, y_) in enumerate(zip(x, y)):
            x[i], y[i], _, _ = utm.from_latlon(y_, x_, force_zone_number=31, force_zone_letter='V')
        X, Y, Z = plot_contour(x, y, z, resolution=300, contour_method='linear')
        surf = self.prod_surf.axes[0].contourf(X, Y, Z, cmap='seismic', levels=30)
        self.set_colorbar(surf, product_name)
        self.prod_surf.draw()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        # self.date_time_list.setTitle(_translate("MainWindow", "ComboBox"))
        # self.og_target_list.setTitle(_translate("MainWindow", "ComboBox"))
        # self.og_horiz_list.setTitle(_translate("MainWindow", "ComboBox"))
        # self.well_list.setTitle(_translate("MainWindow", "ComboBox"))
        self.menuTechnotone.setTitle(_translate("MainWindow", "Technotone"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    self = Ui_MainWindow()
    self.show()
    for date in self.date_to_plot:
        self.plot_prod(date, 'OILPRODM3')
        QtTest.QTest.qWait(1000)
    sys.exit(app.exec_())
