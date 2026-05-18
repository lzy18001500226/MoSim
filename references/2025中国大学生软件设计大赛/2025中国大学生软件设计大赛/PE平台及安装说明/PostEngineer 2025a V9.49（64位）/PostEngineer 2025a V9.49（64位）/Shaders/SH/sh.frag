#version 330 core

//#extension GL_NV_shadow_samplers_cube : enable

layout (location = 0) out vec4 gSHResult1;
layout (location = 1) out vec4 gSHResult2;
layout (location = 2) out vec4 gSHResult3;


uniform samplerCube gCubeMap;

uniform sampler2D gRandSample;
uniform sampler2D gSHSample;

uniform float gExposure;


varying vec2 vUv;

void main()
{
	vec2 theta_phi = texture(gRandSample, vUv).xy;
	vec3 normal = vec3( sin(theta_phi.x)*cos(theta_phi.y), cos(theta_phi.x), sin(theta_phi.x)*sin(theta_phi.y));
	
	//vec3 color = textureCube(gCubeMap, normal).rgb * gExposure;
	vec3 color = texture(gCubeMap, normal).rgb * gExposure;
	
	vec3 s = texture(gSHSample, vUv).xyz;
	
	gSHResult1.xyz = color * s.x;
	gSHResult2.xyz = color * s.y;
	gSHResult3.xyz = color * s.z;
	
}

	
	
		