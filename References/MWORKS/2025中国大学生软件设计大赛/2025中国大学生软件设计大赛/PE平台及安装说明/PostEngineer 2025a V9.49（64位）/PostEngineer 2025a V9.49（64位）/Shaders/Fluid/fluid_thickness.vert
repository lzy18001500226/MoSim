#version 330
#extension GL_EXT_gpu_shader4 : enable


layout (location = 0) in vec3 position;

out vec3 viewPos;
out mat4 projection0;

uniform mat4 modelview;
uniform mat4 projection;


void main() 
{
    viewPos = (modelview * vec4(position, 1.0)).xyz;
    projection0 = projection;
}


