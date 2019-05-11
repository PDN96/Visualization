import vtk
import math
import random
from scipy.spatial import Delaunay
import numpy as np
from fury import utils, window
from vtk.util import numpy_support


scene = window.Scene()


reader = vtk.vtkPLYReader()
reader.SetFileName("horse.ply")

norms = vtk.vtkPolyDataNormals()

norms.SetInputConnection(reader.GetOutputPort())


texture = vtk.vtkTexture()
texture.CubeMapOn()
files = ["skybox-px.jpg", "skybox-nx.jpg", "skybox-py.jpg", "skybox-ny.jpg", "skybox-pz.jpg", "skybox-nz.jpg"]
# files = ["wall1.jpg", "wall1.jpg", "wall1.jpg", "wall1.jpg", "wall1.jpg", "wall1.jpg"]

for i in range(6):
    imgReader = vtk.vtkJPEGReader()
    imgReader.SetFileName(files[i])

    flip = vtk.vtkImageFlip()
    flip.SetInputConnection(imgReader.GetOutputPort())
    flip.SetFilteredAxis(1)
    texture.SetInputConnection(i, flip.GetOutputPort())

# imgReader = vtk.vtkJPEGReader()
# imgReader.SetFileName(file)
# texture.SetInputConnection(0, imgReader.GetOutputPort())

s_mapper = vtk.vtkOpenGLPolyDataMapper()
s_mapper.SetInputConnection(norms.GetOutputPort())

h_actor = vtk.vtkActor()
scene.add(h_actor)
h_actor.SetTexture(texture)
h_actor.SetMapper(s_mapper)


# // Add new code in default VTK vertex shader
s_mapper.AddShaderReplacement(
      vtk.vtkShader.Vertex,
      "//VTK::PositionVC::Dec",  #// replace the normal block
      True,                      #// before the standard replacements
      "//VTK::PositionVC::Dec\n" #// we still want the default
      "out vec3 TexCoords;\n",
      False #// only do it once
  )
s_mapper.AddShaderReplacement(
    vtk.vtkShader.Vertex,
      "//VTK::PositionVC::Impl",  #// replace the normal block
      True,                       #// before the standard replacements
      "//VTK::PositionVC::Impl\n" #// we still want the default
      "vec3 camPos = -MCVCMatrix[3].xyz * mat3(MCVCMatrix);\n"
      "TexCoords.xyz = reflect(vertexMC.xyz - camPos, normalize(normalMC));\n",
      False # // only do it once
  )

s_mapper.SetFragmentShaderCode(
    "//VTK::System::Dec\n" #// always start with this line
      "//VTK::Output::Dec\n" #// always have this line in your FS
      "in vec3 TexCoords;\n"
      "uniform samplerCube texture_0;\n"
      "void main () {\n"
      "  gl_FragData[0] = texture(texture_0, TexCoords);\n"
      "}\n")


window.show(scene)

