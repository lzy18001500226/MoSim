#version 430
#extension GL_NV_shader_buffer_load : enable
#extension GL_EXT_texture_array : enable

layout (location = 0) out vec4 gFragColor;

uniform sampler2DArray particleSamplers;

uniform sampler2D gFourierALight;
uniform sampler2D gFourierBLight;

uniform int screenWidth;
uniform int screenHeight;


uniform vec2 gNearFar;
uniform float gAspect;
uniform float gNearHeight;

uniform float exposure;
uniform float life;
uniform float life2;

uniform int texArraySize;


uniform mat4 gModelViewLight;
uniform mat4 gProjectionLight;
uniform mat4 gModelViewInv;

uniform vec3 gMainLightPos;

in float age;
in vec2 TexCoord;
in float transparency;
in vec3 Color;
in vec3 CenterPos;
in float Radius;
in float RandVal;


const float PI = 3.1415926535897932384626433832795;

vec3 WorldPosToScreen(vec3 worldP, mat4 modelView, mat4 projection)
{
	//vec3 viewPos = (modelView * vec4(worldP, 1)).xyz;
	//vec4 projPos = projection * vec4(viewPos, 1);

	vec4 projPos = projection * modelView * vec4(worldP, 1);

	projPos.xyz /= projPos.w; // 透视划分
	projPos.xyz = projPos.xyz * 0.5 + 0.5; // 变换到0.0 - 1.0的值域

	return projPos.xyz;
}

//裁剪空间转换为眼空间
vec3 UVToEyePos(vec2 uv, float linear_depth)
{    
	vec2 deltaUV = (2.0 * uv - vec2(1.0)) * vec2(gAspect, 1.0);    
	//计算近平面的平移向量    
	vec2 deltaView = gNearHeight * deltaUV * linear_depth/gNearFar.x;    
	
	return vec3(vec2(deltaView), -linear_depth);
} 

vec3 ScreenToWorldPos(vec3 projPos, mat4 modelViewInv)
{
	vec3 viewPos = UVToEyePos(projPos.xy, projPos.z);
	vec4 worldP = (modelViewInv * vec4(viewPos, 1));

	worldP.xyz /= worldP.w;

	return worldP.xyz;
}


float LinearizeDepth(float depth)
{
    float z = depth * 2.0 - 1.0; // 回到NDC
    return (2.0 * gNearFar.x * gNearFar.y) / (gNearFar.y + gNearFar.x - z * (gNearFar.y - gNearFar.x));    
}


float CalcTransmittance(sampler2D FourierA, sampler2D FourierB, ivec2 pos_xy, float depth)
{
	vec4 fourierOne = texelFetch(FourierA, pos_xy, 0);
	vec4 fourierTwo = texelFetch(FourierB, pos_xy, 0);

	float a0 = fourierOne.y;
	float a1 = fourierOne.z;
	float b1 = fourierOne.w;
	float a2 = fourierTwo.x;
	float b2 = fourierTwo.y;
	float a3 = fourierTwo.z;
	float b3 = fourierTwo.w;

	float sin2, cos2, sin4, cos4, sin6, cos6, sin8, cos8, sin10, cos10, sin12, cos12, sin14, cos14;
	cos2 = cos(2 * PI * depth);
	sin2 = sin(2 * PI * depth);
	cos4 = cos2 * cos2 - sin2 * sin2;
	sin4 = 2 * cos2 * sin2;
	cos6 = cos4 * cos2 - sin4 * sin2;
	sin6 = sin4 * cos2 + cos4 * sin2;

	float opticalDepth = 0.5 * a0 * depth;
	opticalDepth += (a1 / (2 * PI)) * sin2;
	opticalDepth += (b1 / (2 * PI)) * (1 - cos2);
	opticalDepth += (a2 / (4 * PI)) * sin4 ;
	opticalDepth += (b2 / (4 * PI)) * (1 - cos4);
	opticalDepth += (a3 / (6 * PI)) * sin6;
	opticalDepth += (b3 / (6 * PI)) * (1 - cos6);

	return exp(-opticalDepth);
}


void main() 
{
	vec4 DiffuseColor = texture2DArray(particleSamplers, vec3(TexCoord, age/life*(texArraySize-1)));
    DiffuseColor.a *= transparency;

	if(DiffuseColor.a < 0.0001) discard;


	float depth = LinearizeDepth(gl_FragCoord.z);

	vec3 worldP = ScreenToWorldPos( vec3(gl_FragCoord.xy/vec2(screenWidth, screenHeight), depth), gModelViewInv );

	vec3 samplePos = WorldPosToScreen(worldP, gModelViewLight, gProjectionLight);
	float depth_light = LinearizeDepth(samplePos.z);

	float transmittance_light = CalcTransmittance(gFourierALight, gFourierBLight, ivec2(samplePos.xy * vec2(screenWidth, screenHeight)), depth_light);
	

	DiffuseColor.rgb *= Color * exposure * min(transmittance_light * 3 + 0.3, 1.0);

	gFragColor = DiffuseColor;
}


