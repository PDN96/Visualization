import numpy as np
import math
import dipy.io.vtk as io_vtk
import dipy.viz.utils as ut_vtk
from dipy.viz import window
import random
from scipy.spatial import Delaunay
from vtk.util import numpy_support

from dipy.utils.optpkg import optional_package
vtk, have_vtk, setup_module = optional_package('vtk')

size = 12
vertices = list()
for i in range(-size, size):
    for j in range(-size, size):
        fact1 = - math.sin(i) * math.cos(j)
        fact2 = - math.exp(abs(1 - math.sqrt(i ** 2 + j ** 2) / math.pi))
        z =  -abs(fact1 * fact2)
        vertices.append([i, j, z])


random.shuffle(vertices)
vertices = np.array(vertices)
xy = list()
for coordinate in vertices:
    xy.append([coordinate[0], coordinate[1]])



tri = Delaunay(xy)
faces = np.array(tri.simplices,dtype='i8')

c_arr = np.random.rand(len(vertices),3)


def surface(vertices, faces = None, colors = None, smooth = None, subdivision = 3):

    points = vtk.vtkPoints()
    points.SetData(numpy_support.numpy_to_vtk(vertices))

    sourcePolyData = vtk.vtkPolyData()
    sourcePolyData.SetPoints(points)

    targetCellArray = vtk.vtkCellArray()
    targetPolyData = vtk.vtkPolyData()
    targetPolyData.SetPoints(sourcePolyData.GetPoints())

    cleanPolyData = vtk.vtkCleanPolyData()

    if faces is None:
        targetPolyData.SetPolys(targetCellArray)
        if colors is not None:
            sourcePolyData.GetPointData().SetScalars(numpy_support.numpy_to_vtk(colors))
        delaunay = vtk.vtkDelaunay2D()
        delaunay.SetInputData(sourcePolyData)
        delaunay.SetSourceData(targetPolyData)
        delaunay.Update()

        cleanPolyData.SetInputConnection(delaunay.GetOutputPort())

    else:
        if faces.shape[1] == 3:
            triangles = np.empty((faces.shape[0], 4), dtype=np.int64)
            triangles[:, -3:] = faces
            triangles[:, 0] = 3

        else:
            triangles = faces

        if not triangles.flags['C_CONTIGUOUS'] or triangles.dtype != 'int64':
            triangles = np.ascontiguousarray(triangles, 'int64')

        targetCellArray.SetCells(triangles.shape[0], numpy_support.numpy_to_vtkIdTypeArray(triangles, deep=True))
        targetPolyData.SetPolys(targetCellArray)
        if colors is not None:
            targetPolyData.GetPointData().SetScalars(numpy_support.numpy_to_vtk(colors))

        cleanPolyData.SetInputData(targetPolyData)



    mapper = vtk.vtkPolyDataMapper()
    surface_actor = vtk.vtkActor()

    if smooth is None:
        mapper.SetInputData(targetPolyData)
        surface_actor.SetMapper(mapper)

    elif smooth == "loop":
        smooth_loop = vtk.vtkLoopSubdivisionFilter()
        smooth_loop.SetNumberOfSubdivisions(subdivision)
        smooth_loop.SetInputConnection(cleanPolyData.GetOutputPort())
        mapper.SetInputConnection(smooth_loop.GetOutputPort())
        surface_actor.SetMapper(mapper)

    elif smooth == "butterfly":
        smooth_butterfly = vtk.vtkButterflySubdivisionFilter()
        smooth_butterfly.SetNumberOfSubdivisions(subdivision)
        smooth_butterfly.SetInputConnection(cleanPolyData.GetOutputPort())
        mapper.SetInputConnection(smooth_butterfly.GetOutputPort())
        surface_actor.SetMapper(mapper)

    return surface_actor

surface_actor = surface(vertices,faces = faces, colors=c_arr, smooth="butterfly", subdivision=5)
renderer = window.Renderer()
renderer.add(surface_actor)
window.show(renderer, size=(600, 600), reset_camera=False)