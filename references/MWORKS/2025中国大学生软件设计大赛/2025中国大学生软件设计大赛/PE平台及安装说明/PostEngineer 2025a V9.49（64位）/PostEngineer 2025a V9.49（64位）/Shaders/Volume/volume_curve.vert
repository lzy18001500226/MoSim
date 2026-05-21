#version 330
#extension GL_EXT_gpu_shader4 : enable


layout (location = 0) in vec3 Vertex;

out vec3 vertex0;


void main() 
{
	vertex0 = Vertex;
}
