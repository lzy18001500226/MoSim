#version 330 core

layout (location = 0) in vec3 Vertex;


uniform mat4 modelToWorld;
uniform mat4 gMvp;

out vec3 vPosition;

void main() 
{
    
  gl_Position = ((gMvp * modelToWorld) * vec4(Vertex.xyz, 1.0));
 
  vPosition = (modelToWorld * vec4(Vertex, 1.0)).xyz;

}
