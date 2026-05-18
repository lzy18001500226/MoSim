

uniform vec3 eyePositionLocal;
uniform vec3 gCameraPos;


uniform int flag;


uniform sampler2D diffuseMap0;
uniform sampler2D diffuseMap1;
uniform sampler2D diffuseMap2;



varying vec3 vPosition;
varying vec3 vNormal;
varying vec3 worldP;



bool bit_and(int val, int ref) {
  if(val == 0) return false;

  return (val/ref) % 2 != 0;
}

vec3 expand(vec3 v) {
  return (v - 0.5) * 2;
}



void main() {


  gl_FragColor = vec4(1, 0, 0, 0);


}

