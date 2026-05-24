#version 330 core

layout (location = 0) out vec4 gMainColor;
//layout (location = 1) out vec4 gRSMPrevColor;


uniform sampler2D gScene;
uniform sampler2D gPositionDepth;

uniform sampler2D gRSMColor;
//uniform sampler2D gHistory;
//uniform sampler2D gMotionVector;

uniform vec2 screenSize;

uniform float gGIFactor;
uniform float gGIRange;

uniform vec3 gCameraPos;


uniform vec2 jitter;

varying vec2 vUv;



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


vec4 GetGaussColor(sampler2D Color, vec2 uv)
{
    const int size = 7;

    vec4 finalColor = vec4(0);
    
    vec2 texSize = textureSize(Color, 0);

    int idx = 0;

    for(int i = -3;i <= 3;i++)
    {
        for(int j = -3; j <= 3;j++)
        {
            vec2 offset_uv = uv + vec2(5.0 * i /texSize.x, 5.0 * j /texSize.y);

            vec4 color = texture2D(Color, offset_uv);

            float weight = gauss[idx++];

            finalColor = finalColor + weight * color;

        }

    }

    return finalColor;
}

vec2 GetJitterUV(vec2 uv)
{
	return uv + jitter / 2;
}


vec2 GetMinDepthUV(vec2 uv)
{
	vec2 size = textureSize(gPositionDepth, 0);

	vec2 min_depth_uv = uv;
	float min_depth = texture(gPositionDepth, min_depth_uv).w;
	
	for(int i=-2; i<=2; i++){
		for(int j=-2; j<=2; j++){
			if(i==0 &&j==0) continue;
			
			vec2 cur_uv = uv + vec2(float(i), float(j))/size;
			float depth = texture(gPositionDepth, cur_uv).w;
			if(min_depth > depth ){	min_depth = depth;	min_depth_uv = cur_uv; }
		}
	}
	
	return min_depth_uv;
}


/*
vec4 BlendHistory()
{
	///混合时帧不能再抖动
	vec2 uv = vUv;
	//vec2 jitter_uv = GetJitterUV(vUv);
	
	vec4 rsmColor = texture(gRSMColor, uv);
	
	
	vec2 min_depth_uv = GetMinDepthUV(uv);
	vec2 MotionVector = texture(gMotionVector, min_depth_uv).xy / 2;
	
	
	vec2 uv_prev = uv - MotionVector;
	vec4 History = texture(gHistory, uv_prev);
	
	///注意必须包含alpha分量
	vec4 NearColor0 = texture(gRSMColor, uv + vec2(1, 0)/screenSize );
	vec4 NearColor1 = texture(gRSMColor, uv + vec2(0, 1)/screenSize );
	vec4 NearColor2 = texture(gRSMColor, uv + vec2(-1, 0)/screenSize );
	vec4 NearColor3 = texture(gRSMColor, uv + vec2(0, -1)/screenSize );

	vec4 BoxMin = min(rsmColor, min(NearColor0, min(NearColor1, min(NearColor2, NearColor3))));
	vec4 BoxMax = max(rsmColor, max(NearColor0, max(NearColor1, max(NearColor2, NearColor3))));
	
	History = clamp(History, BoxMin, BoxMax);
	
	//rsmColor = (NearColor0 + NearColor1 + NearColor2 + NearColor3) / 4;
	//rsmColor = GetGaussColor(gRSMColor, uv);
	
	
	float factor = 1.0f/16;
	rsmColor = clamp(rsmColor * factor + History * (1 - factor), 0, 1);  ///clamp消除黑点
	
	return rsmColor;
}
*/


void main() 
{
	
	vec4 mainColor = texture(gScene, vUv);
	
	//vec4 rsmColor = BlendHistory();
	vec4 rsmColor = texture(gRSMColor, vUv);
	
	//vec3 worldP = texture(gPositionDepth, vUv).xyz;
	//float dis = distance(worldP, gCameraPos);
	float dis = texture(gPositionDepth, vUv).w;
	
	gMainColor.rgb = mainColor.rgb + rsmColor.rgb * gGIFactor * clamp(1.0 - (dis-4*gGIRange) / (4*gGIRange), 0, 1);
	gMainColor.a = mainColor.a;
	
	//gRSMPrevColor = rsmColor;
}