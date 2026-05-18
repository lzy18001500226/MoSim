#version 330 core

layout (location = 0) out vec4 gPosition;


in vec3 vWorldPos;


void main() 
{
	gPosition.xyz = vWorldPos;
	gPosition.w = 1.0;
}
