#version 330 core

layout (location = 0) out vec4 gFragColor; 

uniform int isPointColor;

uniform vec4 color;

in vec3 vColor;

void main() 
{
	gFragColor = isPointColor == 1? vec4(vColor, 1.0): color;
}
