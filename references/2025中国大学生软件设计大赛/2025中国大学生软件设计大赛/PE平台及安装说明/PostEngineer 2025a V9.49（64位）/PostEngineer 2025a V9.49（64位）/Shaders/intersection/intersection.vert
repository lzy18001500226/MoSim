#version 330 core

layout (location = 0) in vec3 Vertex;
layout (location = 1) in vec3 Normal;



uniform mat4 gModelView;
uniform mat4 gProjection;

uniform mat4 modelToWorld;

out vec3 vWorldPos0;



void main() 
{

  vec4 worldPos = modelToWorld * vec4(Vertex.xyz, 1.0);
 
  gl_Position = gProjection * gModelView * worldPos;
  
  vWorldPos0 = worldPos.xyz;
}
