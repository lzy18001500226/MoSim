#version 330 core

layout (location = 0) out vec4 gPositionDepth;   ///位置+线性深度
layout (location = 1) out vec4 gNormal;     ///原始法线+发光亮度


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

uniform sampler2D gbufferPositionMap;
uniform sampler2D gbufferNormalMap;


uniform vec3 mirrorCenter;
uniform vec3 mirrorDirection;
uniform float mirrorDepth;

uniform vec2 screenSize;

in vec3 vPosition;
in vec3 vNormal;

in vec2 vTexcoord;



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
	///镜面以下的部分丢弃
	if ( bit_and(flag, 0x0020) == true && dot(vPosition - (mirrorCenter - mirrorDirection * 1), mirrorDirection) < 0 ) {
		discard;
		return;
	}

	vec2 uv = gl_FragCoord.xy / screenSize;
	vec4 gbufferPos = texture(gbufferPositionMap, uv);
	gPositionDepth.w = LinearizeDepth(gl_FragCoord.z);  //注意gl_FragCoord.z与gl_FragDepth的一致性

	/*if(gbufferPos.w <= gPositionDepth.w && gbufferPos.w > 0.000001){
		discard;
		return;
	}*/

	gPositionDepth.xyz = vPosition;
	
	
	///注意经过插值之后必须要单位化，否则大三角形中的插值点法矢可能闪烁
	gNormal.xyz = normalize(vNormal);  
	
	gNormal.w = materBrightness;
	
	if (bit_and(flag, 0x0001) == true) 
	{
		gNormal.xyz = CalcByNormalMap(vTexcoord.xy, vPosition, gNormal.xyz);
	} 

}
