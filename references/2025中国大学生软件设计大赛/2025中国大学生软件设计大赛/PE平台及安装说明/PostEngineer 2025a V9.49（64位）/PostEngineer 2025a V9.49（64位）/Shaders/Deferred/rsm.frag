#version 330 core

layout (location = 0) out vec4 gMainColor;


const float PI = 3.1415926;

uniform sampler2D gPositionDepth;
uniform sampler2D gNormal;
uniform sampler2D gDiffuse;


uniform sampler2D gLowColor;
uniform sampler2D gLowPosition;
uniform sampler2D gLowNormal;



uniform sampler2D gRSMPositionDepth;
uniform sampler2D gRSMNormal;
uniform sampler2D gRSMDiffuse;

uniform sampler1D gWeight;

uniform float gGIRange;


uniform mat4 gRSMMVP;

uniform vec2 screenSize;

uniform vec2 jitter;

varying vec2 vUv;


vec2 NormalizedDeviceCoordToScreenCoord(vec2 ndc, vec2 screenSize)
{
	vec2 screenCoord;

	screenCoord.x = screenSize.x * (0.5 * ndc.x + 0.5);

	screenCoord.y = screenSize.y * (-0.5 * ndc.y + 0.5);

	return screenCoord;

}


float gauss[] = float[]
(
    0.00000067, 0.00002292, 0.00019117, 0.00038771, 0.00019117, 0.00002292, 0.00000067,

    0.00002292, 0.00078633, 0.00655965, 0.01330373, 0.00655965, 0.00078633, 0.00002292,

    0.00019117, 0.00655965, 0.05472157, 0.11098164, 0.05472157, 0.00655965, 0.00019117,

    0.00038771, 0.01330373, 0.11098164, 0.22508352, 0.11098164, 0.01330373, 0.00038771,

    0.00019117, 0.00655965, 0.05472157, 0.11098164, 0.05472157, 0.00655965, 0.00019117,

    0.00002292, 0.00078633, 0.00655965, 0.01330373, 0.00655965, 0.00078633, 0.00002292,

    0.00000067, 0.00002292, 0.00019117, 0.00038771, 0.00019117, 0.00002292, 0.00000067

);


vec3 GetGaussColor(sampler2D Color, vec2 uv)
{
    const int size = 7;

    vec3 finalColor = vec3(0,0,0);
    
    vec2 texSize = textureSize(Color, 0);

    int idx = 0;

    for(int i = -3;i <= 3;i++)
    {
        for(int j = -3; j <= 3;j++)
        {
            vec2 offset_uv = uv + vec2(5.0 * i /texSize.x, 5.0 * j /texSize.y);

            vec3 color = texture2D(Color, offset_uv).xyz;

            float weight = gauss[idx++];

            finalColor = finalColor + weight * color;

        }

    }

    return finalColor;
}


vec3 CalcVPL(vec2 uv, vec3 P, vec3 N)
{
	vec3 VP = texture(gRSMPositionDepth, uv).xyz;
	vec3 VN = texture(gRSMNormal, uv).xyz;
	vec3 VE = texture(gRSMDiffuse, uv).rgb;
	vec3 D = P - VP;
	float len = dot(D, D);
	if(len < 1e-6) return vec3(0.0);
	
	float coeff = clamp(1.0 - len / (gGIRange*gGIRange), 0, 1);
	
	return VE * max( dot(VN, D), 0 ) * max( dot(N, -D), 0 ) / len * coeff;
}



vec2 GetJitterUV(vec2 uv)
{
	return uv + jitter / 2;
}


int IsSimilar(vec3 P, vec3 N, vec2 uv)
{
	return (dot(N, texture(gLowNormal, uv).xyz) > 0.9 && distance(P, texture(gLowPosition, uv).xyz) < 0.1)? 1: 0;
}



void main() 
{
	///将当前点变换到光源空间，在光源的屏幕空间寻找邻近点作为虚拟光源
			
	vec2 jitUv = GetJitterUV(vUv);
	
	vec3 worldN = texture(gNormal, jitUv).xyz;
	vec3 worldP = texture(gPositionDepth, jitUv).xyz; 
	
	int similar_count = 0;
	similar_count += IsSimilar(worldP, worldN, vUv);
	similar_count += IsSimilar(worldP, worldN, vUv + vec2(0, 1.0/screenSize.y));
	similar_count += IsSimilar(worldP, worldN, vUv + vec2(1/screenSize.x, 0));
	similar_count += IsSimilar(worldP, worldN, vUv + vec2(0, -1/screenSize.y));
	similar_count += IsSimilar(worldP, worldN, vUv + vec2(-1/screenSize.x, 0));
	
	if(similar_count > 2){
		//gMainColor.rgb = GetGaussColor(gLowColor, vUv);
		gMainColor.rgb = texture2D(gLowColor, vUv).rgb;
		return;
	}
	

	vec4 lightSpacePos = gRSMMVP * vec4(worldP, 1.0);
	
	lightSpacePos.xy /= lightSpacePos.w; // 透视划分
	lightSpacePos.xy = lightSpacePos.xy * 0.5 + vec2(0.5); // 变换到0.0 - 1.0的值域
	
	///判断点是否已经位于反射阴影贴图上
	vec3 VP = texture(gRSMPositionDepth, lightSpacePos.xy).xyz;
	if( distance(VP, worldP) < 1e-3 ){
		gMainColor.rgb = vec3(0);
		return;
	}
	
	const int num = 100;
	vec3 E = vec3(0);
	vec2 st = lightSpacePos.xy;
	float maxRadius = 0.2;
	
	for(int k=0; k<num; k++){
		///采样，计算，加权
		vec3 weight = texture(gWeight, float(k)/num).xyz;
		vec2 vpl_uv = st + maxRadius * weight.xy;
		
		E += CalcVPL(vpl_uv, worldP, worldN) * weight.z;
	}
	
/*	for(int i=-5; i<5; i++)
	for(int j=-5; j<5; j++)
	{
		vec2 vpl_uv = st + vec2( float(i)/screenSize.x*10, float(j)/screenSize.y*10 );
		E += CalcVPL(vpl_uv, worldP, worldN);
	}*/
	
	vec3 materialDiffuse = texture(gDiffuse, jitUv).rgb;
	
	gMainColor.rgb = clamp(E/PI * materialDiffuse, 0, 2);

}