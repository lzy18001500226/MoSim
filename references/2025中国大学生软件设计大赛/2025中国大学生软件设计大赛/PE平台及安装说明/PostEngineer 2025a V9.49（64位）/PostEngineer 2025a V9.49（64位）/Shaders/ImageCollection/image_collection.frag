#version 330

layout (location = 0) out vec4 FragColor;

uniform sampler2D image;


in vec2 TexCoord;


void main() 
{
	FragColor = texture(image, TexCoord);
}


