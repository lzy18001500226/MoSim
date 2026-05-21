#version 330
#extension GL_EXT_gpu_shader4 : enable


layout (location = 0) in vec3 position;
layout (location = 1) in float len;
layout (location = 2) in vec3 left;
layout (location = 3) in vec3 right;

uniform mat4 objectToWorld;

out vec3 position0;
out float length0;
out vec3 left0;
out vec3 right0;


void main() 
{
    position0 = (objectToWorld * vec4(position, 1)).xyz;
	vec3 len_vec = vec3(len, 0, 0);
    length0 = length((objectToWorld * vec4(len_vec, 0)).xyz);
	left0 = (objectToWorld * vec4(left, 0)).xyz;
	right0 = (objectToWorld * vec4(right, 0)).xyz;
}


