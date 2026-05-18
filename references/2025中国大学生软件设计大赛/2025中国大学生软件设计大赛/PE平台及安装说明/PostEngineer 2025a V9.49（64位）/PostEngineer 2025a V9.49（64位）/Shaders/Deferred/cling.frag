#version 330 core

layout (location = 0) out vec4 gMainColor;
layout (location = 1) out vec3 gAlphaAndID; 


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

uniform int diffuseMapCount;
uniform float diffuseRange;

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
in vec2 vTexcoord2;
in vec2 vTexcoord3;

in vec2 vTexcoordSpec;
in vec2 vTexcoordNorm;
in vec2 vTexcoordAO;



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


float weight(float z, float a) 
{
	return clamp(pow(min(1.0, a * 10.0) + 0.01, 3.0) * 1e8 * pow(1.0 - z * 0.9, 3.0), 1e-2, 3e3);
}


void main() 
{
	vec4 FragColor = vec4(0, 0, 0, 1);

	///镜面以下的部分丢弃
	if ( bit_and(flag, 0x0020) == true && dot(vPosition - (mirrorCenter - mirrorDirection * 1), mirrorDirection) < 0 ) {
		discard;
		return;
	}

	
	vec4 baseColor;
	baseColor.rgb = Kd;
	baseColor.a = alpha;

	if (bit_and(flag, 0x0002) == true) {
		vec4 diffColor = texture2D(diffuseMap, vTexcoord.xy);
		/*if(diffuseMapCount > 1){
			float camera_dis = LinearizeDepth(gl_FragCoord.z);
			vec4 diffColor2 = texture2D(diffuseMap2, vTexcoord2.xy);

			if(diffuseMapCount > 2){
				vec4 diffColor3 = texture2D(diffuseMap3, vTexcoord3.xy);
				
				if(camera_dis < diffuseRange*5){
					float factor = clamp((camera_dis - diffuseRange)/diffuseRange, 0, 1);
					diffColor = diffColor * (1 - factor) + diffColor2 * factor;
				}
				else{
					float factor = clamp((camera_dis - 5*diffuseRange)/diffuseRange/2, 0, 1);
					diffColor = diffColor2 * (1 - factor) + diffColor3 * factor;
				}
			}
			else{
				float factor = clamp((camera_dis - diffuseRange)/diffuseRange, 0, 1);
				diffColor = diffColor * (1 - factor) + diffColor2 * factor;
			}
		}*/

		baseColor *= diffColor;
	} 

	if(baseColor.a < 0.0001){
		discard;
		return;
	}
	
	FragColor = baseColor;
	
   
	if(bit_and(flag, 0x8000) == true){
		FragColor.rgb = lineColor;
	}
	
	if (bit_and(flag, 0x10000) == true) 
	{
		FragColor.rgb = vColor;
	} 
	
	///透明度随颜色减退
	FragColor.a *= 1 - (0.2126*FragColor.r + 0.7152*FragColor.g + 0.0722*FragColor.b);

	if(vColor.r < -0.5){
		float alpha = -(vColor.r + 1.0);
		FragColor.a *= alpha; 
	}

	float w = weight(gl_FragCoord.z, FragColor.a);
	gMainColor = vec4(FragColor.rgb * FragColor.a * w, FragColor.a);  
	gAlphaAndID = vec3(1, materialID, FragColor.a * w);
}
