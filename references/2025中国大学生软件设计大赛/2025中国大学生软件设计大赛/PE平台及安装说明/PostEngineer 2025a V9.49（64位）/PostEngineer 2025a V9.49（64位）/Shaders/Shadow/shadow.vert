

uniform mat4 modelToWorld;
uniform mat4 shadowWVP;
varying vec4 lightSpacePos;

varying vec3 vPosition;
varying vec3 vNormal;

void main() {
  gl_Position = ftransform();  
  lightSpacePos = shadowWVP * modelToWorld*gl_Vertex;	
  vPosition = gl_Vertex.xyz;
  vNormal = gl_Normal.xyz;
}
