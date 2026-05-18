#version 330 core

layout (location = 0) in vec3 Vertex;
layout (location = 1) in vec3 Normal;
layout (location = 2) in vec3 Color;


uniform mat4 modelToWorld;
uniform mat4 modelToWorldPrev;

uniform mat4 gMvp;
uniform mat4 gMvpPrev;


out vec3 vPosition;
out vec3 vNormal;
out vec3 vColor;


void main() 
{
  

  gl_Position = ((gMvp * modelToWorld) * vec4(Vertex.xyz, 1.0));
 
 
  vPosition = (modelToWorld * vec4(Vertex, 1.0)).xyz;
  
  ///变换矩阵可能存在缩放，所以需要归一化
  vNormal = normalize((modelToWorld * vec4(Normal, 0)).xyz);
  vColor = Color;
}
