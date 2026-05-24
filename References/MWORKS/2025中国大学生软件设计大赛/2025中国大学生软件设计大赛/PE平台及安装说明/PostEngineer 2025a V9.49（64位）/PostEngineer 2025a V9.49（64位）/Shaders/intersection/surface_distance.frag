#version 330 core

layout (location = 0) out vec3 oDistance;

uniform vec3 uCenter;
uniform vec2 uScreenSize;


in vec3 vWorldPos;


void main() 
{
	oDistance.x = distance(vWorldPos, uCenter);
}
