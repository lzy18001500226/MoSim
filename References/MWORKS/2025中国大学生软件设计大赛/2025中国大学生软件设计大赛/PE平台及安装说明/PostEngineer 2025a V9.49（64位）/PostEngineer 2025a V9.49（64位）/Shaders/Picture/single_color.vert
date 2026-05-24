#version 330 core

layout (location = 0) in vec3 Vertex;
layout (location = 1) in vec3 Normal;
layout (location = 2) in vec3 Color;
layout (location = 3) in vec2 TexCoord;
layout (location = 4) in vec2 TexCoord2;
layout (location = 5) in vec2 TexCoord3;

uniform mat4 modelview;
uniform mat4 projection;
uniform mat4 modelToWorld;


void main() 
{
  gl_Position = projection * modelview * modelToWorld * vec4(Vertex.xyz, 1.0);

}
