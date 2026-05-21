#version 330
#extension GL_EXT_gpu_shader4 : enable


layout (location = 0) in vec4 position;


out vec4 position0;

void main() 
{
    
    position0 = position;

}


