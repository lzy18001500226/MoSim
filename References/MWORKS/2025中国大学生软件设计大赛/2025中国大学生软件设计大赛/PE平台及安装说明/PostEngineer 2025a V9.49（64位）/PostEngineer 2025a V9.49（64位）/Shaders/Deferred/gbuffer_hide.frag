#version 330 core

layout (location = 0) out vec4 gPositionDepth;   ///位置+线性深度
layout (location = 2) out vec4 gDiffuse;    ///漫发射+全局环境亮度
layout (location = 5) out vec4 gMotionVector;  ///运动矢量


/*
struct Material
{
	vec3 Ke, Ka, Kd, Ks;
	float shininess;
	float alpha;
};*/

uniform int flag;

layout(std140) uniform GBufferMaterial
{
	vec3 Ke, Ka, Kd, Ks;
	float shininess;
	float alpha;
	
	float materBrightness;

	vec3 lineColor;

	vec4 pbrFactors;
};

uniform sampler2D diffuseMap;
uniform sampler2D normalMap;
uniform sampler2D AOMap;  //同时也作为pbr map
uniform sampler2D specularMap;


uniform vec3 mirrorCenter;
uniform vec3 mirrorDirection;
uniform float mirrorDepth;



in vec3 vPosition;
in vec3 vNormal;
in vec3 vColor;


in vec2 vTexcoord;
in vec2 vTexcoordTransform;

in vec2 vTexcoordSpec;
in vec2 vTexcoordNorm;
in vec2 vTexcoordAO;


in vec4 ClipSpacePos0;
in vec4 PrevClipSpacePos0;


bool bit_and(int val, int ref) {
  if(val == 0) return false;
  return (val/ref) % 2 != 0;
}



uniform float ClipNear; // 投影矩阵的近平面
uniform float ClipFar; // 投影矩阵的远平面

float LinearizeDepth(float depth)
{
    float z = depth * 2.0 - 1.0; // 回到NDC
    return (2.0 * ClipNear * ClipFar) / (ClipFar + ClipNear - z * (ClipFar - ClipNear));    
}



vec3 CalcByNormalMap(vec2 uv, vec3 worldP, vec3 worldN)
{
	/* Thanks to http://www.thetenthplanet.de/archives/1180 */
	/* get edge vectors of the pixel triangle */
	vec3 dp1 = dFdx(worldP);
	vec3 dp2 = dFdy(worldP);
	vec2 duv1 = dFdx(uv);
	vec2 duv2 = dFdy(uv);

	/* solve the linear system */
	vec3 dp2perp = cross(dp2, worldN);
	vec3 dp1perp = cross(worldN, dp1);
	vec3 tangent = dp2perp * duv1.x + dp1perp * duv2.x;
	vec3 binormal = dp2perp * duv1.y + dp1perp * duv2.y;

	/* construct a scale-invariant frame */
	float invmax = inversesqrt(max(dot(tangent, tangent), dot(binormal, binormal)));
	mat3 tsn = mat3(tangent * invmax, binormal * invmax, worldN);
  
	vec3 mapN = texture2D(normalMap, uv).xyz * 2.0 - 1.0;
	return normalize(tsn * mapN);
}


 


void main() 
{
	
	vec3 baseColor = vec3(1.0, 1.0, 1.0);
	
	gDiffuse.rgb = baseColor;
	gDiffuse.a = 1.0;

	if(bit_and(flag, 0x8000) == true){
		gDiffuse.rgb = vec3(0.0, 0.0, 0.0);
	}
	
	vec3 NDCPos = ( ClipSpacePos0 / ClipSpacePos0.w ).xyz;
	vec3 PrevNDCPos = ( PrevClipSpacePos0 / PrevClipSpacePos0.w ).xyz;
	gMotionVector.xy = (NDCPos - PrevNDCPos).xy;
	gMotionVector.z = NDCPos.z*0.5 + 0.5;
	
	gPositionDepth.xyz = vPosition;
	gPositionDepth.w = LinearizeDepth(gl_FragCoord.z);  //注意gl_FragCoord.z与gl_FragDepth的一致性
}
