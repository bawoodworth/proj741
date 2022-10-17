# -*- coding: utf-8 -*-
import numpy as np
import pyvista
import glob
import os
import time
import pyvistaqt


def get_mesh(filename):
    reader = pyvista.get_reader(filename)
    # print(f"Number of point arrays: {reader.number_point_arrays}")
    # print(f"Available point data:   {reader.point_array_names}")
    # print(f"Number of cell arrays:  {reader.number_cell_arrays}")
    # print(f"Available cell data:    {reader.cell_array_names}")
    mesh = reader.read()
    # print(f"Read arrays:        {mesh.array_names}")
    return mesh


def plot_mesh(plotter, mesh):
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
    

def main():
    data_dir = './data'
    data_files = glob.glob(os.path.join(data_dir, '*.vtp'))
    plotter = pyvistaqt.BackgroundPlotter()
    plotter.show()
    for data_file in data_files:
        print(data_file)
        mesh = get_mesh(data_file)
        plotter = plot_mesh(plotter, mesh)
        time.sleep(1)


if __name__ == '__main__':
    main()
    
    