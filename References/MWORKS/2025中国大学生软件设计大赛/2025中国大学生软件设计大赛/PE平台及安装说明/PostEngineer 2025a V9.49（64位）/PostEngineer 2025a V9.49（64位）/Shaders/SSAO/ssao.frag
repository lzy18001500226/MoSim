#version 330


uniform sampler2D gPositionDepth;
uniform sampler2D gNormal;


uniform mat4 gProjection;
uniform mat4 gModelView;
uniform vec3 gCameraPos;

uniform vec3 gVertical;

uniform mat4 cameraConvertMatrix;

//uniform float fogDensity;
//uniform float fogHeight;
uniform vec3 fogParam;
uniform vec3 fogColor;

float CalcFogBlend(vec3 worldP)
{
	float fogBlend = 1.0;
	const float EPSON = 0.0000001;

	float fogDensity = fogParam.x;
	float fogHeight = fogParam.y;
	int fogAtten = int(fogParam.z + 0.001);

	if(fogDensity > EPSON){

		//全部转换到世界坐标系下
		//vec3 worldP0 = (cameraConvertMatrix * vec4(worldP, 1.0)).xyz;
		//vec3 gCameraPos0 = (cameraConvertMatrix * vec4(gCameraPos, 1.0)).xyz;
 
		vec3 view_vec = worldP - gCameraPos;
		vec3 viewDir = normalize(view_vec);

		float dis_in_fog = length(view_vec);

		//if( fogHeight > EPSON){
			float H0 = dot(gCameraPos, gVertical);
			float H1 = dot(worldP, gVertical);

			float h0 = H0 - fogHeight;
			float h1 = H1 - fogHeight;

			if(h0 <= 0 && h1 >= 0) dis_in_fog *= -h0/(-h0+h1);
			else if(h0 >= 0 && h1 <= 0) dis_in_fog *= -h1/(h0-h1);
			else if(h0 >= 0 && h1 >= 0) dis_in_fog = 0.0;
		//}

		float density = fogDensity;

		vec3 up = gVertical;
		//density *= max(1.0 - dot(up, viewDir), 0);
        
		if(fogAtten == 0){
			float maxDis = log(5.0) / density;
			fogBlend = clamp( 1.0 - dis_in_fog/maxDis , 0, 1);
		}
		else if(fogAtten == 1)
			fogBlend = clamp(exp(-density * dis_in_fog ), 0, 1);
		else{
			float ind = pow(density * dis_in_fog, 2);
			fogBlend = clamp(exp(-ind ), 0, 1);
		}

		/*if( fogHeight > EPSON){
			//float H = dot(worldP - vec3(0), gVertical);
			float factor = 1.0 - min( max( H - fogHeight, 0) / (fogHeight*5), 1.0);
			fogBlend = fogBlend*factor + 1.0*(1 - factor);
		}*/
   	 }

	return fogBlend;
}


uniform float gSampleRad;
uniform float AOFactor;
const int MAX_KERNEL_SIZE = 64;
uniform vec4 gKernel[MAX_KERNEL_SIZE];

uniform sampler2D gRand;

in vec2 UV;
out vec4 FragColor;


void main()
{
	vec2 uv = UV;

	vec3 worldN = texture2D(gNormal, uv).xyz;
	vec4 PosDepth = texture2D(gPositionDepth, uv);

	if(PosDepth.a < 0.000001){
		FragColor.xyz = worldN;
		FragColor.w = 1.0;
		return;
	}

	vec3 worldP = PosDepth.xyz;

	float camera_dis = distance(gCameraPos, worldP);
	
	if(AOFactor > 0.01 && camera_dis < gSampleRad*1000){
		
		vec2 texSize = textureSize(gPositionDepth, 0);
		vec2 noiseScale = texSize / 2.0;
		
		vec3 fragPos = (gModelView * vec4(worldP,1)).xyz;
		vec3 normal = (gModelView * vec4(worldN,0)).xyz;
		vec3 randomVec = texture(gRand, uv * noiseScale).xyz;
		
		vec3 tangent = normalize(randomVec - normal * dot(randomVec, normal));
		vec3 bitangent = normalize(cross(normal, tangent));
		mat3 TBN = mat3(tangent, bitangent, normal);
		
		int kernelSize = 64;
		float radius = gSampleRad;
		if(camera_dis > gSampleRad*100) radius *= 10;

		vec3 bendNormal = worldN*64;
		
		float occlusion = 0.0;
		for(int i = 0; i < kernelSize; ++i)
		{
			// 获取样本位置
			vec3 sampleDir = TBN * gKernel[i].xyz; // 切线->观察空间
			
			vec3 samplePoint = fragPos + sampleDir * radius; 
			
			vec4 offset = vec4(samplePoint, 1.0);
			offset = gProjection * offset; // 观察->裁剪空间
			offset.xyz /= offset.w; // 透视划分
			offset.xyz = offset.xyz * 0.5 + 0.5; // 变换到0.0 - 1.0的值域
			vec2 sampleUV = offset.xy;
			
			
			float sampleDepth = texture(gPositionDepth, sampleUV).w;
			vec3 sampleNormal = texture(gNormal, sampleUV).xyz;
			
			float rangeCheck = smoothstep(0.0, 1.0, radius / abs(-fragPos.z - sampleDepth));
			float fc = (sampleDepth > -samplePoint.z - radius/10000 ? 0.0 : 1.0) * rangeCheck; 
			occlusion += fc;   
			
			//有噪声
			bendNormal += sampleNormal*(1-fc);
		}
		
		//有噪声
		FragColor.xyz = normalize(bendNormal);
		
		occlusion *= min(radius * 100 / camera_dis, 1);
		occlusion = 1.0 - (max(occlusion / kernelSize - 0.1, 0));	
		

		float fogBlend = CalcFogBlend(worldP);
		FragColor.w = pow(occlusion, AOFactor);

		FragColor.w = FragColor.w*fogBlend + 1.0*(1 - fogBlend);

					/*if(fogDensity > 0.0000001){
     					 float dis = distance(gCameraPos, worldP);
						 vec3 viewDir = normalize(worldP - gCameraPos);

						float density = fogDensity;// * 0.5 + fogDensity * 0.5 * GetFogNoise(worldP);  /// worldP no use

						vec3 up = gVertical;
						density *= (1 - dot(up, viewDir)) / 2;
        
						float fogBlend = clamp(exp(-density * dis ), 0, 1);
		
						//occlusion = 1.0*fogBlend + occlusion*(1-fogBlend);
						FragColor.w = pow(occlusion, AOFactor * fogBlend);
					}
					else
						FragColor.w = pow(occlusion, AOFactor);*/
	}
	else{
		FragColor.xyz = worldN;
		FragColor.w = 1.0;
	}
}
