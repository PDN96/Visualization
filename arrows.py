import random
import math
# import math
from scipy.spatial import Delaunay
import numpy as np
from fury import window, actor, ui
import dipy.io.vtk as io_vtk
import dipy.viz.utils as ut_vtk
from dipy.utils.optpkg import optional_package
import itertools
from fury import window, utils
from fury.utils import vtk

def arrow(start_point, end_point, length):
    USER_MATRIX = False

    # Create an arrow.
    arrowSource = vtk.vtkArrowSource()

    # Generate a random start and end point
    # random.seed(8775070)
    startPoint = start_point
    endPoint = end_point

    # Compute a basis
    normalizedX = [0 for i in range(3)]
    normalizedY = [0 for i in range(3)]
    normalizedZ = [0 for i in range(3)]

    # The X axis is a vector from start to end
    math = vtk.vtkMath()
    print(normalizedX)
    math.Subtract(endPoint, startPoint, normalizedX)
    l = math.Norm(normalizedX)
    print(l)
    math.Normalize(normalizedX)
    print(normalizedX)

    # The Z axis is an arbitrary vector cross X
    arbitrary = [0 for i in range(3)]
    arbitrary[0] = random.uniform(-10, 10)
    arbitrary[1] = random.uniform(-10, 10)
    arbitrary[2] = random.uniform(-10, 10)
    math.Cross(normalizedX, arbitrary, normalizedZ)
    math.Normalize(normalizedZ)

    # The Y axis is Z cross X
    math.Cross(normalizedZ, normalizedX, normalizedY)
    matrix = vtk.vtkMatrix4x4()

    # Create the direction cosine matrix
    matrix.Identity()
    for i in range(3):
        matrix.SetElement(i, 0, normalizedX[i])
        matrix.SetElement(i, 1, normalizedY[i])
        matrix.SetElement(i, 2, normalizedZ[i])

    # Apply the transforms
    transform = vtk.vtkTransform()
    transform.Translate(startPoint)
    transform.Concatenate(matrix)
    transform.Scale(length, length, length)

    # Transform the polydata
    transformPD = vtk.vtkTransformPolyDataFilter()
    transformPD.SetTransform(transform)
    transformPD.SetInputConnection(arrowSource.GetOutputPort())

    # Create a mapper and actor for the arrow
    mapper = vtk.vtkPolyDataMapper()
    arrow_actor = vtk.vtkActor()

    if USER_MATRIX:
        mapper.SetInputConnection(arrowSource.GetOutputPort())
        arrow_actor.SetUserMatrix(transform.GetMatrix())
    else:
        mapper.SetInputConnection(transformPD.GetOutputPort())

    arrow_actor.SetMapper(mapper)
    return arrow_actor


start = [5, 5, 5]
end = [12, 12, 12]
arrow_actor = arrow(start, end, 5)

sphereStartSource = vtk.vtkSphereSource()
sphereStartSource.SetCenter(start)
sphereStartMapper = vtk.vtkPolyDataMapper()
sphereStartMapper.SetInputConnection(sphereStartSource.GetOutputPort())
sphereStart = vtk.vtkActor()
sphereStart.SetMapper(sphereStartMapper)
sphereStart.GetProperty().SetColor(1.0, 1.0, .3)

sphereEndSource = vtk.vtkSphereSource()
sphereEndSource.SetCenter(end)
sphereEndMapper = vtk.vtkPolyDataMapper()
sphereEndMapper.SetInputConnection(sphereEndSource.GetOutputPort())
sphereEnd = vtk.vtkActor()
sphereEnd.SetMapper(sphereEndMapper)
sphereEnd.GetProperty().SetColor(1.0, .3, .3)

#Create a renderer, render window, and interactor
renderer = window.Renderer()

renderer.add(arrow_actor)
renderer.add(sphereStart)
renderer.add(sphereEnd)

renderer.SetBackground(.1, .2, .3) # Background color dark blue

axes_actor = actor.axes(scale=(18,18,18))
renderer.add(axes_actor)
#Render and interact
window.show(renderer, size=(600, 600), reset_camera=False)