//#version 330 core

//layout (location = 0) in vec3 Vertex;
//layout (location = 1) in vec3 Color;


uniform mat4 modelToWorld;

uniform mat4 gMvp;

varying vec3 vColor;

void main() 
{
  
  //gl_Position = ((gMvp * modelToWorld) * vec4(Vertex.xyz, 1.0));
  //vColor = Color;

  gl_Position = ((gMvp * modelToWorld) * vec4(gl_Vertex.xyz, 1.0));
  vColor = gl_Color.xyz;
}
