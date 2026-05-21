#version 330 core

layout (location = 0) out vec4 gPositionDepth;   ///位置+线性深度
layout (location = 1) out vec4 gNormal;     ///原始法线+发光亮度
layout (location = 2) out vec4 gDiffuse;    ///漫发射+全局环境亮度
layout (location = 3) out vec4 gSpecular;    ///高光+shininess
layout (location = 4) out vec4 gMaterial;   ///pbr+AO系数或环境系数


uniform int flag;

uniform vec3 gCameraPos;

layout(std140) uniform GBufferMaterial
{
	vec3 Ke, Ka, Kd, Ks;
	float shininess;
	float alpha;
	
	float materBrightness;

	vec3 lineColor;

	vec4 pbrFactors;

	int materialID;
};


uniform sampler2D diffuseMap;
uniform int diffuseMapCount;

uniform vec2 screenSize;

uniform vec4 clipPlanes[3];
uniform int clipPlaneCount;

in vec3 vPosition;
in vec3 vNormal;
in vec3 vColor;



bool bit_and(int val, int ref) {
  if(val == 0) return false;
  return (val/ref) % 2 != 0;
}


uniform float ClipNear; // 投影矩阵的近平面
uniform float ClipFar; // 投影矩阵的远平面

float LinearizeDepth(float depth)
{
    float z = depth * 2.0 - 1.0; // 回到NDC
	float near_1 = 1.0/ClipNear;
	float far_1 = 1.0/ClipFar;
    //return (2.0 * ClipNear * ClipFar) / (ClipFar + ClipNear - z * (ClipFar - ClipNear));    
	return 2.0 / ( (1 - z)*near_1 + (1 + z)*far_1 );
}


vec3 CalcIntersectionOfLineWithPlane(vec3 S, vec3 E, vec3 B, vec3 N)
{
	float l1 = dot(B - S, N);
	float l2 = dot(E - S, N);

	return S + l1/l2 * (E - S);
}


void main() 
{

	int clip_index = 0;
	for(int k=0; k<clipPlaneCount; k++){
		float d = dot(clipPlanes[k].xyz, vPosition) + clipPlanes[k].w;
		if(d < 0){
			discard;
			return;
		}
	}

	gNormal.xyz = -normalize(clipPlanes[clip_index].xyz);  	
	gNormal.w = -1.0;  ///像素分隔标志
	
	vec3 baseColor = Kd;
	if (bit_and(flag, 0x0002) == true) {
		vec3 diffColor = texture2D(diffuseMap, vec2(0.0, 0.0)).rgb;
		baseColor *= diffColor;
	} 
	
	gDiffuse.rgb = baseColor;
	gDiffuse.a = max(Ka.r, max(Ka.g, Ka.b));	 ///保存环境亮度系数

	if (bit_and(flag, 0x10000) == true) 
	{
		gDiffuse.rgb = vColor;
		gMaterial.rgb = vColor * 0.2; //增强环境亮度
	} 
	 
	gMaterial = vec4(1, 1, 1, 1);
	float shininessFactor = 1.0;

	gMaterial.rgb = Ke; ///对于普通材质则保存发光属性
	gMaterial.b += float(int(pbrFactors.w*10))*100;
	gMaterial.a = 21;

	vec3 lKs = Ks;
	gSpecular = vec4(lKs, shininess * shininessFactor);


	///计算视线与剪切面的交点
	vec3 B;

	if(abs(clipPlanes[clip_index].x) > 0.1) B = vec3( -clipPlanes[clip_index].w / clipPlanes[clip_index].x, 0, 0 );
	else if(abs(clipPlanes[clip_index].y) > 0.1) B = vec3(0,  -clipPlanes[clip_index].w / clipPlanes[clip_index].y, 0 );
	else if(abs(clipPlanes[clip_index].z) > 0.1) B = vec3(0,  0, -clipPlanes[clip_index].w / clipPlanes[clip_index].z );

	vec3 I = CalcIntersectionOfLineWithPlane(gCameraPos, vPosition, B, clipPlanes[clip_index].xyz);
	
	gPositionDepth.xyz = I;
	gPositionDepth.w = distance(gCameraPos, I);  //注意gl_FragCoord.z与gl_FragDepth的一致性
}
