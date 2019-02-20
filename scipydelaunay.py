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
        z = -abs(fact1 * fact2)
        vertices.append([i, j, z])


random.shuffle(vertices)
vertices = np.array(vertices)
xy = list()
for coordinate in vertices:
    xy.append([coordinate[0], coordinate[1]])

tri = Delaunay(xy)
faces = np.array(tri.simplices,dtype='i8')

c_arr = np.random.rand(len(vertices),3)

def surface(vertices, faces=None, colors=None, smooth=None, subdivision=3):

    """Generates a surface actor from an array of vertices
        The color and smoothness of the surface can be customized.

        Parameters
        ----------
        vertices : array, shape (X, Y, Z)
            The point cloud defining the surface.
        faces : array
            An array of precomputed triangulation for the point cloud. It is an optional parameter, it is computed
            locally if None
        colors : (N, 3) array
            Specifies the colors associated with each vertex in the vertices array. Optional parameter, if not passed,
            all vertices are colored white
        smooth : string - "loop" or "butterfly"
            Defines the type of subdivision to be used for smoothing the surface
        subdivision : integer, default = 3
            Defines the number of subdivisions to do for each triangulation of the point cloud. The higher the value,
            smoother the surface but at the cost of higher computation

        Returns
        -------
        surface_actor : vtkActor
            A vtkActor visualizing the final surface computed from the point cloud is returned.

    """
    points = vtk.vtkPoints()
    points.SetData(numpy_support.numpy_to_vtk(vertices))
    triangle_poly_data = vtk.vtkPolyData()
    triangle_poly_data.SetPoints(points)

    if colors is not None:
        triangle_poly_data.GetPointData().SetScalars(numpy_support.numpy_to_vtk(colors))

    if faces is None:
        tri = Delaunay(vertices[:, [0, 1]])
        faces = np.array(tri.simplices, dtype='i8')

    if faces.shape[1] == 3:
        triangles = np.empty((faces.shape[0], 4), dtype=np.int64)
        triangles[:, -3:] = faces
        triangles[:, 0] = 3
    else:
        triangles = faces

    if not triangles.flags['C_CONTIGUOUS'] or triangles.dtype != 'int64':
        triangles = np.ascontiguousarray(triangles, 'int64')

    cells = vtk.vtkCellArray()
    cells.SetCells(triangles.shape[0], numpy_support.numpy_to_vtkIdTypeArray(triangles, deep=True))
    triangle_poly_data.SetPolys(cells)

    clean_poly_data = vtk.vtkCleanPolyData()
    clean_poly_data.SetInputData(triangle_poly_data)

    mapper = vtk.vtkPolyDataMapper()
    surface_actor = vtk.vtkActor()

    if smooth is None:
        mapper.SetInputData(triangle_poly_data)
        surface_actor.SetMapper(mapper)

    elif smooth == "loop":
        smooth_loop = vtk.vtkLoopSubdivisionFilter()
        smooth_loop.SetNumberOfSubdivisions(subdivision)
        smooth_loop.SetInputConnection(clean_poly_data.GetOutputPort())
        mapper.SetInputConnection(smooth_loop.GetOutputPort())
        surface_actor.SetMapper(mapper)

    elif smooth == "butterfly":
        smooth_butterfly = vtk.vtkButterflySubdivisionFilter()
        smooth_butterfly.SetNumberOfSubdivisions(subdivision)
        smooth_butterfly.SetInputConnection(clean_poly_data.GetOutputPort())
        mapper.SetInputConnection(smooth_butterfly.GetOutputPort())
        surface_actor.SetMapper(mapper)

    return surface_actor
surface_actor = surface(vertices, colors=c_arr, smooth = "loop")
renderer = window.renderer(background=(1,1,1))
renderer.add(surface_actor)
window.show(renderer, size=(600, 600), reset_camera=False)

