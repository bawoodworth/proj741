# -*- coding: utf-8 -*-
"""
Created on Sat Oct  8 01:50:37 2022

@author: Brian Woodworrth
"""

import numpy as np
import pyvista

filename = 'test.vtp'

reader = pyvista.get_reader(filename)

print(f"Number of point arrays: {reader.number_point_arrays}")
print(f"Available point data:   {reader.point_array_names}")
print(f"Number of cell arrays:  {reader.number_cell_arrays}")
print(f"Available cell data:    {reader.cell_array_names}")


mesh = reader.read()

print(f"Read arrays:        {mesh.array_names}")


plotter = pyvista.Plotter()

# plotter.subplot(0)
plotter.add_mesh(mesh, scalars='T', show_scalar_bar=True)
plotter.show()