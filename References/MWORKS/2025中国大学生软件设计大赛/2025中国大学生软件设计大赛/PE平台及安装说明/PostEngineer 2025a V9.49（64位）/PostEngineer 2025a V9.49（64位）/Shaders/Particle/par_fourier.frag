#version 430
#extension GL_NV_shader_buffer_load : enable
#extension GL_EXT_texture_array : enable

layout (location = 0) out vec4 gFourierA;
layout (location = 1) out vec4 gFourierB;


uniform sampler2DArray particleSamplers;


uniform vec2 gNearFar;
uniform float gAspect;
uniform float gNearHeight;

uniform float exposure;
uniform float life;
uniform float life2;

uniform int texArraySize;



in float age;
in vec2 TexCoord;
in float transparency;
in vec3 Color;
in vec3 CenterPos;
in float Radius;
in float RandVal;

const float PI = 3.1415926535897932384626433832795;

float LinearizeDepth(float depth)
{
    float z = depth * 2.0 - 1.0; // »Øµ½NDC
    return (2.0 * gNearFar.x * gNearFar.y) / (gNearFar.y + gNearFar.x - z * (gNearFar.y - gNearFar.x));    
}



void main() 
{
	vec4 FragColor = texture2DArray(particleSamplers, vec3(TexCoord, age/life*(texArraySize-1)));
    FragColor.a *= transparency;
    
    FragColor.rgb *= Color * exposure;

	float a0 = -log(1.0 - FragColor.a + 1e-5);
	float depth = LinearizeDepth(gl_FragCoord.z);

	float sin2, cos2, sin4, cos4, sin6, cos6, sin8, cos8, sin10, cos10, sin12, cos12, sin14, cos14;
	cos2 = cos(2 * PI * depth);
	sin2 = sin(2 * PI * depth);
	cos4 = cos2 * cos2 - sin2 * sin2;
	sin4 = 2 * cos2 * sin2;
	cos6 = cos4 * cos2 - sin4 * sin2;
	sin6 = sin4 * cos2 + cos4 * sin2;
	float a1 = a0 * cos2;
	float b1 = a0 * sin2;
	float a2 = a0 * cos4;
	float b2 = a0 * sin4;
	float a3 = a0 * cos6;
	float b3 = a0 * sin6;

	gFourierA = vec4(1,a0,a1,b1);
	gFourierB = vec4(a2,b2,a3,b3);

}


