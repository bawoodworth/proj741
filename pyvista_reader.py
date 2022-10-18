# -*- coding: utf-8 -*-
import numpy as np
import pyvista
import sys
import glob
import os
import time
import pyvistaqt
from pyvistaqt import QtInteractor
from PyQt5 import QtWidgets
from PyQt5.uic import loadUi

# if orientation changes, need to maintain that view through animation sequence


class Window(pyvistaqt.MainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        # super(Window, self).__init__()
        loadUi('main_window.ui', self)
        self.__setup_signals()
        self.__show_plot()
        self.show()
        
    def __setup_signals(self):
        animate_button = self.findChild(QtWidgets.QPushButton, 'animateButton')
        animate_button.clicked.connect(self.__animate)
        pass
    
    def __show_plot(self):
        self.frame = QtWidgets.QFrame()
        self.plotter = pyvistaqt.QtInteractor(self.frame)
        self.v_layout = self.findChild(QtWidgets.QVBoxLayout, 'verticalLayout')
        self.v_layout.addWidget(self.plotter.interactor)
        self.signal_close.connect(self.plotter.close)
        data_dir = './data'
        self.data_files = glob.glob(os.path.join(data_dir, '*.vtp'))
        mesh = self.__get_mesh(self.data_files[0])
        self.plotter = self.__plot_mesh(self.plotter, mesh)
        self.plotter.show()

    def __get_mesh(self, filename):
        reader = pyvista.get_reader(filename)
        mesh = reader.read()
        return mesh

    def __plot_mesh(self, plotter, mesh):
        bar_args = {
            'title': "Temperate \N{DEGREE SIGN}C",
            'height': 0.25,
            'vertical': True,
            'position_x': 0.05,
            'position_y': 0.05,
            'title_font_size':20,
            'label_font_size':14,
            'n_labels':3,
            'use_opacity':True,
            }
        plotter.add_mesh(mesh, clim=[273,350], cmap="jet", lighting=True, scalar_bar_args=bar_args)
        plotter.camera.view_angle = 30
        plotter.view_vector([-.3,-.5,.2])
        return plotter
    
    def __animate(self):
        for data_file in self.data_files[1:]:
            print(data_file)
            mesh = self.__get_mesh(data_file)
            self.plotter = self.__plot_mesh(self.plotter, mesh)
            time.sleep(1)
            
    # class members
    data_files = []



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    app.exec_()
    