# -*- coding: utf-8 -*-
import numpy as np
import pyvista
import sys
import glob
import os
import time
import pyvistaqt
from collections import OrderedDict
from pyvistaqt import QtInteractor
from PyQt5 import QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtCore import *

# if orientation changes, need to maintain that view through animation sequence

# global variables
DATA_DIR = './soj_test'
DATA_FILES = glob.glob(os.path.join(DATA_DIR, '*.vtp'))

# sort data files
def sort_criteria(e):
    return float(e.split('_')[-1].split('.vtp')[0])
DATA_FILES.sort(key=sort_criteria)

        
# background thread worker to animate without blocking main thread        
class Worker(QObject):
    finished = pyqtSignal()
    def __init__(self, target, args):
        super().__init__()
        self.t = target
        self.args = args
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.__task)
            
    def __task(self):
        self.t(*self.args)
        
    @pyqtSlot()    
    def start_task(self):
        self.timer.start(500)
        
    @pyqtSlot()
    def stop_task(self):
        self.timer.stop()
        

class MainWindow(pyvistaqt.MainWindow):
    worker_start = pyqtSignal()
    worker_pause = pyqtSignal()
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        loadUi('main_window.ui', self)
        self.__setup_signals()
        self.show()
        self.__load_data()
        self.__show_plot()
        
        
    def __setup_signals(self):
        self.animate_button = self.findChild(QtWidgets.QPushButton, 'animate_button')
        self.animate_button.clicked.connect(self.__animate_button)
        self.reset_button = self.findChild(QtWidgets.QPushButton, 'reset_button')
        self.reset_button.clicked.connect(self.__reset_button)
        self.prev_button = self.findChild(QtWidgets.QPushButton, 'prev_button')
        self.prev_button.clicked.connect(self.__prev_button)
        self.next_button = self.findChild(QtWidgets.QPushButton, 'next_button')
        self.next_button.clicked.connect(self.__next_button)
        self.xy_button = self.findChild(QtWidgets.QPushButton, 'xy_button')
        self.xy_button.clicked.connect(self.__xy_button)
        self.xz_button = self.findChild(QtWidgets.QPushButton, 'xz_button')
        self.xz_button.clicked.connect(self.__xz_button)
        self.yz_button = self.findChild(QtWidgets.QPushButton, 'yz_button')
        self.yz_button.clicked.connect(self.__yz_button)
        self.axes_button = self.findChild(QtWidgets.QRadioButton, 'axes_button')
        self.axes_button.toggled.connect(self.__axes_button)
        # self.time_slider = self.findChild(QtWidgets.QSlider, 'time_slider')
        # self.time_slider.sliderMoved.connect(self.__slider_update)
        
        
    def __setup_slider(self):
        self.time_slider.setMinimum(0)
        self.time_slider.setMaximum(len(self.time_state_dict)-1)
        self.time_slider.setValue(0)
        
    def __slider_update(self):
        print('slider update...')
        self.plotter = self.__plot_mesh(
            self.plotter, 
            self.time_state_dict[self.time_slider.value()][1]
            )
        self.current_time_idx = self.time_slider.value()
        self.__set_time_text(self.time_state_dict[self.current_time_idx][0])
        
    def __xy_button(self):
        self.plotter.camera_position = 'xy'
    
    def __xz_button(self):
        self.plotter.camera_position = 'xz'
    
    def __yz_button(self):
        self.plotter.camera_position = 'yz'
    
    def __axes_button(self):
        if self.axes_button.isChecked():
            self.plotter.show_bounds(location='outer')
        else:
            self.plotter.remove_bounds_axes()
        
    def __save_camera_position(self, position):
        self.camera_position = position
    
    def __reset_button(self):
        self.__reset_animation_button()
        self.plotter = self.__plot_mesh(
            self.plotter, 
            self.time_state_dict[0][1]
            )
        self.current_time_idx = 0
        self.__set_time_text(self.time_state_dict[0][0])
        pass
    
    def __prev_button(self):
        self.__reset_animation_button()
        self.__prev()
        
    def __prev(self):
        if self.current_time_idx > 0:
            prev_idx = self.current_time_idx - 1
        else:
            prev_idx = self.final_time_idx
        self.plotter = self.__plot_mesh(
            self.plotter, 
            self.time_state_dict[prev_idx][1]
            )
        self.current_time_idx = prev_idx
        self.__set_time_text(self.time_state_dict[prev_idx][0])
    
    def __next_button(self):
        self.__reset_animation_button()
        self.__next()
        
    def __next(self):
        if self.current_time_idx < self.final_time_idx:
            next_idx = self.current_time_idx + 1
        else:
            next_idx = 0
        self.plotter = self.__plot_mesh(
            self.plotter, 
            self.time_state_dict[next_idx][1]
            )
        self.current_time_idx = next_idx
        self.__set_time_text(self.time_state_dict[next_idx][0])
    
    def __set_time_text(self, time_str):
        self.text_actor.SetText(3, 'Time: {}s'.format(time_str))
    
    def __load_data(self):
        self.time_state_dict = OrderedDict()
        for idx, data_file in enumerate(DATA_FILES):
            time_state = data_file.split('_')[-1].split('.vtp')[0]
            reader = pyvista.get_reader(data_file)
            mesh = reader.read()
            self.time_state_dict[idx] = (time_state, mesh)
            if idx > self.final_time_idx:
                self.final_time_idx = idx
            
            
    def __show_plot(self):
        self.frame      = QtWidgets.QFrame()
        self.plotter    = QtInteractor(self.frame)
        self.v_layout   = self.findChild(QtWidgets.QVBoxLayout, 'verticalLayout')
        self.v_layout.addWidget(self.plotter.interactor)
        self.signal_close.connect(self.plotter.close)        
        # plot initial mesh
        mesh = self.time_state_dict[0][1]
        self.current_time_idx = 0
        self.plotter    = self.__plot_mesh(self.plotter, mesh)
        self.text_actor = self.plotter.add_text('Time: 0.0s', position='upper_right')
        self.plotter.show()

    # def __get_mesh(self, filename):
    #     reader = pyvista.get_reader(filename)
    #     mesh = reader.read()
    #     return mesh

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
        self.actor = plotter.add_mesh(mesh, clim=[0,500], cmap="jet", lighting=True, scalar_bar_args=bar_args)
        plotter.camera.view_angle = 30
        if self.first_plot:
            plotter.view_vector([-.3,-.5,.2])
            self.first_plot = False
        return plotter
    
    def __animate_button(self):
        print('animating....')
        self.animate_button.clicked.disconnect()
        self.animate_button.clicked.connect(self.__pause)
        self.animate_button.setText('Pause')
        self.thread = QThread()
        self.worker = Worker(target=self.__next, args=())
        self.worker.moveToThread(self.thread)
        self.worker_start.connect(self.worker.start_task)
        self.worker_pause.connect(self.worker.stop_task)
        self.thread.start()
        self.worker_start.emit()        
        
    def __pause(self):
        print('pause animation...')
        self.__reset_animation_button()
        self.worker_pause.emit()
        self.thread.quit()
        self.thread.wait()
        
    def __reset_animation_button(self):
        self.animate_button.setText('Play')
        self.animate_button.clicked.disconnect()
        self.animate_button.clicked.connect(self.__animate_button)
    
            
    # class members
    actor = None
    first_plot = True
    data_files = []
    current_time_idx = -1
    final_time_idx = 0
    loading_screen = None
    
    # button members
    animate_button = None
    
class LoadWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        loadUi('load_window.ui', self)
        self.show()
        


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    app.exec_()
    