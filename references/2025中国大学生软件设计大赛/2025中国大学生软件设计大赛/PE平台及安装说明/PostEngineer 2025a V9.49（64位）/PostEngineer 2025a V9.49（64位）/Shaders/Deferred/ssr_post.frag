#version 330 core

layout (location = 0) out vec4 gMainColor;
layout (location = 1) out vec4 gSSRColor;


//uniform sampler2D gScene;
uniform sampler2D gNormal;
uniform sampler2D gSpecular;
uniform sampler2D gMaterial;
uniform sampler2D gSSR;
uniform sampler2D gHistory;
uniform sampler2D gMotionVector;


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


vec4 BlendHistory()
{
	vec2 screenSize = textureSize(gSSR, 0);
	vec2 refrectUv = vUv - texture(gNormal, vUv).xy * 8.0/screenSize;
	
	vec4 ssrColor = texture(gSSR, refrectUv);
	
	
	vec2 MotionVector = texture(gMotionVector, vUv).xy / 2;
	
	
	vec2 uv_prev = vUv + MotionVector;
	vec4 History = texture(gHistory, uv_prev);
	
	///注意必须包含alpha分量
	vec4 NearColor0 = texture(gSSR, vUv + vec2(1, 0)/screenSize );
	vec4 NearColor1 = texture(gSSR, vUv + vec2(0, 1)/screenSize );
	vec4 NearColor2 = texture(gSSR, vUv + vec2(-1, 0)/screenSize );
	vec4 NearColor3 = texture(gSSR, vUv + vec2(0, -1)/screenSize );

	vec4 BoxMin = min(ssrColor, min(NearColor0, min(NearColor1, min(NearColor2, NearColor3))));
	vec4 BoxMax = max(ssrColor, max(NearColor0, max(NearColor1, max(NearColor2, NearColor3))));
	
	History = clamp(History, BoxMin, BoxMax);
	
	//ssrColor = (NearColor0 + NearColor1 + NearColor2 + NearColor3) / 4;
	//ssrColor = GetGaussColor(gSSR, vUv);
	
	
	float factor = 1.0f/16;
	ssrColor = clamp(ssrColor * factor + History * (1 - factor), 0, 1);  ///clamp消除黑点
	
	return ssrColor;
}


void main() 
{
	//vec4 mainColor = texture(gScene, vUv);
	
	//vec4 ssrColor = BlendHistory();
	vec4 ssrColor = texture(gSSR, vUv);
	
/*	float factor = clamp((pow(ssrColor.a, 3) - 0.01)*1.5, 0, 0.8);
	mainColor.rgb = clamp(mainColor.rgb * (1 - factor) + ssrColor.rgb * factor, 0, 1);*/
	
	gMainColor = ssrColor;
	gSSRColor = ssrColor;
}