#version 330
#extension GL_EXT_gpu_shader4 : enable


layout (location = 0) in vec4 position;
layout (location = 1) in vec4 shape;



out vec4 position0;
out vec4 shape0;


void main() 
{
    
    position0 = position;
    shape0 = shape;
}


