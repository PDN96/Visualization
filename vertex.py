'''
This simple example demonstrates how to use shaders to modify the vertices in
your scene. We will use the AddShaderReplacement() function to modify the
vertex shader with VTK's shader template system.
In this example, we will create a cube and use a vertex shader to distort its
shape.
This example borrows heavily from the FURY surfaces example.
http://fury.gl/dev/auto_examples/viz_surfaces.html
https://github.com/fury-gl/fury/blob/master/docs/examples/viz_surfaces.py
'''

import numpy as np
from vtk.util import numpy_support as ns

from fury import utils, window
from fury.utils import vtk

# create a vtkPolyData and the geometry information
my_polydata = vtk.vtkPolyData()

my_vertices = np.array([[0.0,  0.0,  0.0],
                        [0.0,  0.0,  1.0],
                        [0.0,  1.0,  0.0],
                        [0.0,  1.0,  1.0],
                        [1.0,  0.0,  0.0],
                        [1.0,  0.0,  1.0],
                        [1.0,  1.0,  0.0],
                        [1.0, 1.0, 1.0]])

my_triangles = np.array([[0,  6,  4],
                         [0,  2,  6],
                         [0,  3,  2],
                         [0,  1,  3],
                         [2,  7,  6],
                         [2,  3,  7],
                         [4,  6,  7],
                         [4,  7,  5],
                         [0,  4,  5],
                         [0,  5,  1],
                         [1,  5,  7],
                         [1, 7, 3]], dtype='i8')

# use a FURY util to apply the vertices and triangles to the polydata
utils.set_polydata_vertices(my_polydata, my_vertices)
utils.set_polydata_triangles(my_polydata, my_triangles)

# in VTK, shaders are applied at the mapper level
# get mapper from polydata
cube_actor = utils.get_actor_from_polydata(my_polydata)
mapper = cube_actor.GetMapper()

# add the cube to a scene and show it
scene = window.Scene()
scene.add(cube_actor)
# window.show(scene, size=(500, 500))

# let's say we want to distort the vertex positions using some data
# we can pass per-vertex data into the shader in an array which has the same
# length as the vertex array

# make some dummy data, in this case just duplicate the vertex positions
# need to convert it to a VTK object
# give it a name so it can be referred to later
# add it to the polydata's pointdata
# pass it int the shader as a vertex attribute
my_dummy_data = my_vertices
my_dummy_data_vtk = ns.numpy_to_vtk(my_dummy_data,
                                    deep=True,
                                    array_type=vtk.VTK_UNSIGNED_CHAR)
my_dummy_data_vtk.SetName('dummy_array')
my_polydata.GetPointData().AddArray(my_dummy_data_vtk)

mapper.MapDataArrayToVertexAttribute(
    'dummyAttribute',
    'dummy_array',
    vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS,
    -1)

# now we augment VTK's default shaders with our own code
# first, declare the incoming vertex attribute
mapper.AddShaderReplacement(
    vtk.vtkShader.Vertex,
    '//VTK::PositionVC::Dec',  # target the PositionVC block
    True,
    '''
    // include the default
    //VTK::PositionVC::Dec
    // now declare our attribute
    in vec3 dummyAttribute;
    ''',
    False
)

# now calculate the new vertex coordinates
mapper.AddShaderReplacement(
    vtk.vtkShader.Vertex,
    '//VTK::PositionVC::Impl',  # target the PositionVC block
    True,
    '''
    // replace the default
    // copy position in model coordinates
    vec4 myVertexMC = vertexMC;
    // modify coordinates with dummyAttribute
    // just for fun, 'swizzle' the parameters
    // subtract 0.5 so it stays centered
    myVertexMC.xyz = vertexMC.xyz + (dummyAttribute.yzx - 0.5);
    // this is used for lighting in the frag shader
    // need to calculate and include since we replaced the default
    vertexVCVSOutput = MCVCMatrix * myVertexMC;
    // transform from model to display coordinates
    gl_Position = MCDCMatrix * myVertexMC;
    ''',
    False
)

# debug block
# uncomment this to force the shader code to print so you can see how your
# replacements are being inserted into the template
mapper.AddShaderReplacement(
    vtk.vtkShader.Fragment,
    '//VTK::Coincident::Impl',
    True,
    '''
    //VTK::Coincident::Impl
    foo = bar;
    ''',
    False
)

window.show(scene, size=(500, 500))