'''
This simple example demonstrates how to use shaders to generate geometry in
your scene. We will use the SetGeometryShaderCode() function to inject our own
geometry shader into VTK's shader pipline.
In this example, we will create a cube and use a geometry shader to discard
the cube's vertices and replace them with our own geometry.
This example borrows heavily from the FURY surfaces example.
http://fury.gl/dev/auto_examples/viz_surfaces.html
https://github.com/fury-gl/fury/blob/master/docs/examples/viz_surfaces.py
It also borrows from FURY GSoC student thechargedneutron's examples.
https://github.com/thechargedneutron/GSoC-Codes
Those examples borrow from:
https://learnopengl.com/Advanced-OpenGL/Geometry-Shader
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

my_colors = my_vertices * 255  # transform from [0, 1] to [0, 255]

# use a FURY util to apply the above values to the polydata
utils.set_polydata_vertices(my_polydata, my_vertices)
utils.set_polydata_triangles(my_polydata, my_triangles)
utils.set_polydata_colors(my_polydata, my_colors)

# in VTK, shaders are applied at the mapper level
# set the cube to render in wireframe mode
# get mapper from polydata
cube_actor = utils.get_actor_from_polydata(my_polydata)
cube_actor.GetProperty().SetRepresentationToWireframe()
mapper = cube_actor.GetMapper()

# add the cube to a scene and show it
scene = window.Scene()
scene.add(cube_actor)
window.show(scene, size=(500, 500))

# now we want to write a geometry shader which takes in each line from the
# wireframe cube, discards it, and in it's place inserts a pyramid


mapper.SetGeometryShaderCode('''
    //VTK::System::Dec
    //VTK::PositionVC::Dec
    // declarations below aren't necessary because VTK
    // injects them in the PositionVC template
    //in vec4 vertexVCVSOutput[];
    //out vec4 vertexVCGSOutput;
    // declare coordinate transformation matrices
    uniform mat4 MCDCMatrix;
    uniform mat4 MCVCMatrix;
    //VTK::PrimID::Dec
    // declarations below aren't necessary because VTK
    // injects them in the PrimID template
    //in vec4 vertexColorVSOutput[];
    //out vec4 vertexColorGSOutput;
    //VTK::Color::Dec
    //VTK::Normal::Dec
    //VTK::Light::Dec
    //VTK::TCoord::Dec
    //VTK::Picking::Dec
    //VTK::DepthPeeling::Dec
    //VTK::Clip::Dec
    //VTK::Output::Dec
    // lines come in, triangle strips come out
    layout(lines) in;
    layout(triangle_strip, max_vertices = 6) out;
    // function to construct a pyramid
    void build_pyramid(vec4 position)
    {
        vec4 point1 = vec4(0.0, 0.0, 0.0, 0.0);
        vec4 point2 = vec4(0.3, 0.0, 0.0, 0.0);
        vec4 point3 = vec4(0.0, 0.0, 0.3, 0.0);
        vec4 point4 = vec4(0.0, 0.3, 0.0, 0.0);
        gl_Position = position + (MCDCMatrix * point1);
        vertexVCGSOutput = vertexVCVSOutput[0] + (MCVCMatrix * point1);
        EmitVertex();
        gl_Position = position + (MCDCMatrix * point2);
        vertexVCGSOutput = vertexVCVSOutput[0] + (MCVCMatrix * point2);
        EmitVertex();
        gl_Position = position + (MCDCMatrix * point3);
        vertexVCGSOutput = vertexVCVSOutput[0] + (MCVCMatrix * point3);
        EmitVertex();
        gl_Position = position + (MCDCMatrix * point4);
        vertexVCGSOutput = vertexVCVSOutput[0] + (MCVCMatrix * point4);
        EmitVertex();
        gl_Position = position + (MCDCMatrix * point1);
        vertexVCGSOutput = vertexVCVSOutput[0] + (MCVCMatrix * point1);
        EmitVertex();
        gl_Position = position + (MCDCMatrix * point2);
        vertexVCGSOutput = vertexVCVSOutput[0] + (MCVCMatrix * point2);
        EmitVertex();
        EndPrimitive();
    }
    void main() {
        // pass color information through to frag shader
        vertexColorGSOutput = vertexColorVSOutput[0];
        build_pyramid(gl_in[0].gl_Position);
    }
''')

# debug block
# uncomment this to force the shader code to print so you can see how your
# replacements are being inserted into the template
# mapper.AddShaderReplacement(
#     vtk.vtkShader.Fragment,
#     '//VTK::Coincident::Impl',
#     True,
#     '''
#     //VTK::Coincident::Impl
#     foo = bar;
#     ''',
#     False
# )

window.show(scene, size=(500, 500))