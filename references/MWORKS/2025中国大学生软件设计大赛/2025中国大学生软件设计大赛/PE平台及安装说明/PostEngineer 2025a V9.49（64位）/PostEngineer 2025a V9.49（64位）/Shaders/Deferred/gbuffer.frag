#version 330 core

layout (location = 0) out vec4 gPositionDepth;   ///位置+线性深度
layout (location = 1) out vec4 gNormal;     ///原始法线+发光亮度
layout (location = 2) out vec4 gDiffuse;    ///漫发射+全局环境亮度
layout (location = 3) out vec4 gSpecular;   ///高光+shininess
layout (location = 4) out vec4 gMaterial;   ///pbr+AO系数或环境系数
//layout (location = 5) out vec4 gNormalMap;  ///法线贴图
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

	int materialID;
};

uniform sampler2D diffuseMap;
uniform sampler2D diffuseMap2;
uniform sampler2D diffuseMap3;
uniform sampler2D diffuseMap4;

uniform sampler2D maskMap;
uniform sampler2D maskMap2;
uniform int mapBlendType;

uniform int diffuseMapCount;
uniform float diffuseRange;

uniform sampler2D normalMap;
uniform sampler2D AOMap;  //同时也作为pbr map
uniform sampler2D specularMap;

uniform float normalStrength;

uniform sampler2D clingColorMap;
uniform sampler2D clingAlphaMap;

uniform vec3 mirrorCenter;
uniform vec3 mirrorDirection;
uniform float mirrorDepth;

uniform vec2 screenSize;

uniform vec4 clipPlanes[3];
uniform int clipPlaneCount;

in vec3 vPosition;
in vec3 vNormal;
in vec3 vColor;

in vec2 vTexcoordPrimitive;
in vec2 vTexcoord;
in vec2 vTexcoord2;
in vec2 vTexcoord3;

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
	float near_1 = 1.0/ClipNear;
	float far_1 = 1.0/ClipFar;
    //return (2.0 * ClipNear * ClipFar) / (ClipFar + ClipNear - z * (ClipFar - ClipNear));    
	return 2.0 / ( (1 - z)*near_1 + (1 + z)*far_1 );
}



vec3 CalcByNormalMap(vec2 uv, vec3 worldP, vec3 worldN, float strengthFactor)
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
  
	vec3 In = texture2D(normalMap, uv).xyz * 2.0 - 1.0;
	In = vec3(In.rg * normalStrength*strengthFactor, mix(1.0, In.b, clamp(normalStrength*strengthFactor, 0.0, 1.0)));

	vec3 mapN = In;
	return normalize(tsn * mapN);
}


 


void main() 
{

	///镜面以下的部分丢弃
	if ( bit_and(flag, 0x0020) == true && dot(vPosition - (mirrorCenter - mirrorDirection * 1), mirrorDirection) < 0 ) {
		discard;
		return;
	}

	if(bit_and(flag, 0x0200) == true ){
	
		for(int k=0; k<clipPlaneCount; k++){
			float d = dot(clipPlanes[k].xyz, vPosition) + clipPlanes[k].w;
			if(d < 0){
				discard;
				return;
			}
		}
	}

	//位置，法矢
	//漫反射材质+亮度，高光反射材质+高光强度，环境遮挡系数+粗糙度系数+金属系数
	
	
	///注意经过插值之后必须要单位化，否则大三角形中的插值点法矢可能闪烁
	gNormal.xyz = normalize(vNormal);  
	
	float option = 0;
	if(bit_and(flag, 0x1000000)) option = 1.0;

	gNormal.w = materBrightness + 100.0*option;
	
	//gNormalMap = vec4(0, 0, 1, 0);
	
	
	if (bit_and(flag, 0x0001) == true) 
	{
		//gNormalMap.xyz = texture2D(normalMap, vTexcoord.xy).xyz * 2.0 - 1.0;
		gNormal.xyz = CalcByNormalMap(vTexcoordNorm.xy, vPosition, gNormal.xyz, 1.0);
	} 

	vec3 lKs = Ks;
	if(bit_and(flag, 0x0008) == true) {	
	    lKs *= texture2D(specularMap, vTexcoordSpec.xy).r;
	}
	
	
	vec3 baseColor = Kd;
	if (bit_and(flag, 0x0002) == true) {
		vec4 diffColor = texture2D(diffuseMap, vTexcoord.xy);
		if(mapBlendType == 0){
			if(diffuseMapCount > 1){
				float camera_dis = LinearizeDepth(gl_FragCoord.z);
				vec4 diffColor2 = texture2D(diffuseMap2, vTexcoord2.xy);

				if(diffuseMapCount > 2){
					vec4 diffColor3 = texture2D(diffuseMap3, vTexcoord3.xy);
					
					if(camera_dis < diffuseRange*5){
						float factor = clamp((camera_dis - diffuseRange)/diffuseRange, 0, 1);
						diffColor.rgb = diffColor.rgb * (1 - factor) + diffColor2.rgb * factor;
					}
					else{
						float factor = clamp((camera_dis - 5*diffuseRange)/diffuseRange/2, 0, 1);
						diffColor.rgb = diffColor2.rgb * (1 - factor) + diffColor3.rgb * factor;
					}
				}
				else{
					float factor = clamp((camera_dis - diffuseRange)/diffuseRange, 0, 1);
					diffColor.rgb = diffColor.rgb * (1 - factor) + diffColor2.rgb * factor;
				}
			}
		}
		else if(mapBlendType == 1 || mapBlendType == 2 && diffuseMapCount < 4){
			if(diffuseMapCount > 1){
				vec4 maskColor = texture2D(maskMap, vTexcoordPrimitive.xy);
				vec4 maskColor2 = texture2D(maskMap2, vTexcoordPrimitive.xy);
				lKs *= maskColor2.r;

				if (bit_and(flag, 0x0001) == true) 
				{
					gNormal.xyz = normalize(vNormal);  
					gNormal.xyz = CalcByNormalMap(vTexcoordNorm.xy, vPosition, gNormal.xyz, maskColor2.g);
				} 

				vec4 diffColor2 = texture2D(diffuseMap2, vTexcoord2.xy);
				if(diffuseMapCount > 2){
					vec4 diffColor3 = texture2D(diffuseMap3, vTexcoord3.xy);
					//float alphaSum = diffColor.a + diffColor2.a + diffColor3.a;
					//diffColor.rgb = diffColor.rgb * diffColor.a + diffColor2.rgb * diffColor2.a  + diffColor3.rgb * diffColor3.a;
					//diffColor.rgb /= alphaSum;
					float alphaSum = maskColor.r + maskColor.g + maskColor.b;
					diffColor.rgb = diffColor.rgb *  maskColor.r + diffColor2.rgb *  maskColor.g  + diffColor3.rgb *  maskColor.b;
					diffColor.rgb /= alphaSum;
				}
				else{
					//float alphaSum = diffColor.a + diffColor2.a;
					//diffColor.rgb = diffColor.rgb * diffColor.a + diffColor2.rgb * diffColor2.a;
					//diffColor.rgb /= alphaSum;
					float alphaSum = maskColor.r + maskColor.g;
					diffColor.rgb = diffColor.rgb *  maskColor.r + diffColor2.rgb *  maskColor.g;
					diffColor.rgb /= alphaSum;
				}
			}
		}
		else if(mapBlendType == 2){
			
				vec4 maskColor = texture2D(maskMap, vTexcoordPrimitive.xy);
				vec4 maskColor2 = texture2D(maskMap2, vTexcoordPrimitive.xy);
				lKs *= maskColor2.r;

				if (bit_and(flag, 0x0001) == true) 
				{
					gNormal.xyz = normalize(vNormal);  
					gNormal.xyz = CalcByNormalMap(vTexcoordNorm.xy, vPosition, gNormal.xyz, maskColor2.g);
				} 

				float camera_dis = LinearizeDepth(gl_FragCoord.z);
				if(camera_dis > diffuseRange)
				{
					vec4 diffColor4 = texture2D(diffuseMap4, vTexcoordPrimitive.xy);
					float factor = clamp((camera_dis - diffuseRange)/diffuseRange, 0, 1);
					diffColor.rgb = diffColor.rgb * (1 - factor) + diffColor4.rgb * factor;
				}

				vec4 diffColor2 = texture2D(diffuseMap2, vTexcoord2.xy);

				
					vec4 diffColor3 = texture2D(diffuseMap3, vTexcoord3.xy);

					float alphaSum = maskColor.r + maskColor.g + maskColor.b;
					diffColor.rgb = diffColor.rgb *  maskColor.r + diffColor2.rgb *  maskColor.g  + diffColor3.rgb *  maskColor.b;
					diffColor.rgb /= alphaSum;
				

		}

		baseColor *= diffColor.rgb;
	} 

	if(materialID > 0){
		vec4 SumColor = texture2D(clingColorMap, gl_FragCoord.xy / screenSize);
		vec4 SumAlpha = texture2D(clingAlphaMap, gl_FragCoord.xy / screenSize);
		int clingID = int(SumAlpha.g / SumAlpha.r + 0.1); ///消除积累
		
		vec4 clingColor = vec4( SumColor.rgb / clamp(SumAlpha.b, 0.000001, 5000000.0), SumColor.a);
		clingColor.a = 1 - clingColor.a;

		if(clingID == materialID){
			baseColor = baseColor*(1 - clingColor.a) + clingColor.rgb * clingColor.a;
		}
	}

	
	gDiffuse.rgb = baseColor;
	gDiffuse.a = max(Ka.r, max(Ka.g, Ka.b));	 ///保存环境亮度系数
	
   
	gMaterial = vec4(1, 1, 1, 1);
	float shininessFactor = 1.0;
	if(bit_and(flag, 0x0004) == true) {	
		
		if(bit_and(flag, 0x0080) == true) {	 ///Speclur/Glossiness流程
			vec3 orm = texture2D(AOMap, vTexcoordAO.xy).rgb;
			gMaterial.r = 1.0;
  			gMaterial.g = clamp((1 - orm.y) * pbrFactors.y, 0.0, 10.0);
  			gMaterial.b = clamp(orm.z * pbrFactors.z, 0.0, 10.0);
		}
		else{  ///metalness/roughness流程
			vec3 orm = texture2D(AOMap, vTexcoordAO.xy).rgb;
			gMaterial.r = clamp(1*(1-pbrFactors.x) + orm.x * pbrFactors.x, 0.0, 10.0);
			gMaterial.g = clamp(orm.y * pbrFactors.y, 0.0, 10.0);
			gMaterial.b = clamp(orm.z * pbrFactors.z, 0.0, 10.0);
		}
	}
	else{
        gMaterial.r = clamp(pbrFactors.x, 0.0, 10.0);
  		gMaterial.g = clamp(pbrFactors.y, 0.0, 10.0);
  		gMaterial.b = clamp(pbrFactors.z, 0.0, 10.0);
  		 
	}

	gSpecular = vec4(lKs, shininess * shininessFactor);
	
	///保存渲染类型
	if(bit_and(flag, 0x1000) == true) {
		gMaterial.a = 10 + clamp(pbrFactors.w, 0, 9);
	}
	else if(bit_and(flag, 0x8000) == true){
		gDiffuse.rgb = lineColor;
		gMaterial.a = 1.0;
	}
	else{
		gMaterial.rgb = Ke; ///对于普通材质则保存发光属性
		
		gMaterial.b += float(int(pbrFactors.w*10))*100;
		
		gMaterial.a = 21;
		if (bit_and(flag, 0x0040) == true) {
		  gMaterial.a = 20 + texture2D(AOMap, vTexcoordAO).r;
		} 
	}
	
	if (bit_and(flag, 0x10000) == true) 
	{
		gDiffuse.rgb = vColor;
		gMaterial.rgb = vColor * 0.2; //增强环境亮度
	} 
	
	//float screenMirrorDepth = 0.0;

	// 处于绘制倒影阶段
	if (bit_and(flag, 0x0020) == true) {
		float height = max(dot(vPosition - mirrorCenter, mirrorDirection), 0);
		float screenMirrorDepth = max(1.0 - max((height - mirrorDepth ) / mirrorDepth, 0), 0);
		screenMirrorDepth = float(int(screenMirrorDepth*10));
		gMaterial.a += screenMirrorDepth*1000;
	}
	// 正式绘制阶段，镜子材质，需要设置标志
	else if (bit_and(flag, 0x4000) == true) {
		float screenMirrorDepth = 1.0;
		screenMirrorDepth = float(int(screenMirrorDepth*10));
		gMaterial.a += screenMirrorDepth*1000;
	}
	//else{
	//	screenMirrorDepth = 0.0;   //雾的效果不好且影响倒影， 去掉 //gl_FragCoord.z/gl_FragCoord.w;  //到相机的距离，用于雾浓度的计算
	//}

	
	vec3 NDCPos = ( ClipSpacePos0 / ClipSpacePos0.w ).xyz;
	vec3 PrevNDCPos = ( PrevClipSpacePos0 / PrevClipSpacePos0.w ).xyz;
	gMotionVector.xy = (NDCPos - PrevNDCPos).xy;
	gMotionVector.z = NDCPos.z*0.5 + 0.5;
	//gl_FragDepth = NDCPos.z*0.5 + 0.5;
	
	gPositionDepth.xyz = vPosition;
	gPositionDepth.w = LinearizeDepth(gl_FragCoord.z);  //注意gl_FragCoord.z与gl_FragDepth的一致性
}
