#version 330 core
#extension GL_NV_shadow_samplers_cube : enable
#extension GL_NV_shader_buffer_load : enable

layout (location = 0) out vec4 gMainColor;


uniform sampler2D gPositionDepth;
uniform sampler2D gDiffuse;

uniform vec2 jitter;

uniform vec3 worldSunDir;

uniform vec4 clipPlane;


uniform vec3 eyePositionWorld;

uniform int flag;

varying vec2 vUv;


uniform vec2 screenSize;


const float environment_rotation = 0.0;
const float environment_exposure = 2.0;
const float EPSILON_COEF = 1e-4;



bool bit_and(int val, int ref) {
  if(val == 0) return false;

  return (val/ref) % 2 != 0;
}

vec3 expand(vec3 v) {
  return (v - 0.5) * 2;
}




void main() 
{
	vec2 uv = vUv;
	
	vec3 worldP = texture2D(gPositionDepth, uv).xyz;

	gMainColor.rgb = vec3(0.0);
	

	gMainColor.rgb = texture2D(gDiffuse, uv).rgb;

	gMainColor.a = -1;
}