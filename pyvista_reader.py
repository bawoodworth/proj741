# -*- coding: utf-8 -*-
import numpy as np
import pyvista


def get_mesh(filename):
    reader = pyvista.get_reader(filename)
    # print(f"Number of point arrays: {reader.number_point_arrays}")
    # print(f"Available point data:   {reader.point_array_names}")
    # print(f"Number of cell arrays:  {reader.number_cell_arrays}")
    # print(f"Available cell data:    {reader.cell_array_names}")
    mesh = reader.read()
    # print(f"Read arrays:        {mesh.array_names}")
    return mesh


def plot_mesh(mesh):
    plotter = pyvista.Plotter()
    bar_args = {
        'title': "Temperate \N{DEGREE SIGN}C",
        'height': 0.25,
        'vertical': True,
        'position_x': 0.05,
        'position_y': 0.05,
        'title_font_size':20,
        'label_font_size':14,
        'n_labels':3
        }
    plotter.add_mesh(mesh, scalars='T', cmap="bmy", lighting=True, scalar_bar_args=bar_args)
    plotter.show()
    

def main():
    filename = './data/test.vtp'
    mesh = get_mesh(filename)
    plot_mesh(mesh)


if __name__ == '__main__':
    main()