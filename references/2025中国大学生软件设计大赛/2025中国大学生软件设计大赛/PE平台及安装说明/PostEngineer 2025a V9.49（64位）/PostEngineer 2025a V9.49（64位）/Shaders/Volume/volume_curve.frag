#version 330 core

layout (location = 0) out vec4 gMainColor;


in vec4 vertexColor;

void main() 
{	
	if(vertexColor.a < 0.001) discard;

	gMainColor = vertexColor;
	//gMainColor.a = 1.0;
	
}