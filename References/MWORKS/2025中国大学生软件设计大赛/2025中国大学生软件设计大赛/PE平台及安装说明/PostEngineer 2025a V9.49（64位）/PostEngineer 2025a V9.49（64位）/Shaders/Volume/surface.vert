#version 330 core

layout (location = 0) in vec3 Vertex;
layout (location = 1) in vec3 Normal;
layout (location = 2) in float Value;


uniform mat4 gMvp;
uniform mat4 modelToWorld;


uniform int flag;



varying vec3 halfAngle;
varying vec3 normalLocal;
varying vec3 normalWorld;

varying vec3 I_World;
varying vec3 I_Local;


varying vec3 worldP;

varying float vValue;
varying vec3 vPosition;
varying vec3 vNormal;


bool bit_and(int val, int ref) {
  if(val == 0) return false;

  return (val/ref) % 2 != 0;
}


void main() {

  gl_Position = (gMvp * modelToWorld) * vec4(Vertex.xyz, 1.0);

  vPosition = Vertex;
  vNormal = normalize(Normal);
  vValue = Value;

   worldP = (modelToWorld * vec4(Vertex, 1.0)).xyz;
}
