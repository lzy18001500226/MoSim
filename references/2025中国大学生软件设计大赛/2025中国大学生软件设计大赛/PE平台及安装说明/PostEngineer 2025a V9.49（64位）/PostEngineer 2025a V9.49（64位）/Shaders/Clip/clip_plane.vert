#version 330 core

layout (location = 0) in vec3 Vertex;
layout (location = 1) in vec3 Normal;


uniform mat4 gMvp;
//uniform mat4 modelToWorld;

out vec3 worldP;
out vec3 vPosition;
out vec3 vNormal;


void main() {

  //gl_Position = (gMvp * modelToWorld) * vec4(Vertex.xyz, 1.0);  
  gl_Position = gMvp * vec4(Vertex.xyz, 1.0);  

  vPosition = Vertex;
  vNormal = normalize(Normal);

  //worldP = (modelToWorld * vec4(Vertex, 1.0)).xyz;
  worldP = vec4(Vertex, 1.0).xyz;
}
