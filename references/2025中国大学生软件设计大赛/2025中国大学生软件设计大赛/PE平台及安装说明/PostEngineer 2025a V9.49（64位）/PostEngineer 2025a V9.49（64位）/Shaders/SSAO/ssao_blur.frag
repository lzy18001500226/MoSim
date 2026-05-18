#version 130


#define _SigmaS 10.0
#define _SigmaR 0.1
#define _Radius 4


uniform sampler2D image;

varying vec2 vUv;

float Luminance(vec3 color)
{
	return dot(color, vec3(0.2125, 0.7154, 0.0721));
}	

vec3 BilateralFilter(vec2 uv)
{
	float i = uv.x;
	float j = uv.y;
	float sigmaSSquareMult2 = (2*_SigmaS*_SigmaS);
	float sigmaRSquareMult2 = (2*_SigmaR*_SigmaR);

	vec3 centerCol = texture(image, uv).rgb;					// 中心点像素的颜色 //
	float centerLum = Luminance(centerCol);						// 中心点像素的亮度 //
	
	vec2 texelSize = 1.0 / vec2(textureSize(image, 0));

	vec3 sum_up;												// 分子 //
	vec3 sum_down;												// 分母 //
	for(int k=-_Radius; k<=_Radius; k++)
	{
		for(int l=-_Radius; l<=_Radius; l++)
		{
			vec2 uv_new = uv + texelSize*vec2(k,l);
			vec3 curCol = texture(image, uv_new).rgb;		// 当前像素的颜色 //
			float curLum = Luminance(curCol);						// 当前像素的亮度 //
			vec3 deltaColor = curCol-centerCol;
			float len = dot(deltaColor, deltaColor);
			// float exponent = -((i-k)*(i-k)+(j-l)*(j-l))/sigmaSSquareMult2 - (curLum-centerLum)*(curLum-centerLum)/sigmaRSquareMult2;
			float exponent = -((i-k)*(i-k)+(j-l)*(j-l))/sigmaSSquareMult2 - len/sigmaRSquareMult2;
			float weight = exp(exponent);
			sum_up += curCol*weight;
			sum_down += weight;
		}
	}

	return sum_up/sum_down;
}

vec4 BilateralFilter4D(vec2 uv)
{
	float i = uv.x;
	float j = uv.y;
	float sigmaSSquareMult2 = (2*_SigmaS*_SigmaS);
	float sigmaRSquareMult2 = (2*_SigmaR*_SigmaR);

	vec3 centerCol = texture(image, uv).rgb;					// 中心点像素的颜色 //
	float centerLum = Luminance(centerCol);						// 中心点像素的亮度 //
	
	vec2 texelSize = 1.0 / vec2(textureSize(image, 0));

	vec4 sum_up;												// 分子 //
	vec4 sum_down;												// 分母 //
	for(int k=-_Radius; k<=_Radius; k++)
	{
		for(int l=-_Radius; l<=_Radius; l++)
		{
			vec2 uv_new = uv + texelSize*vec2(k,l);
			vec4 curCol = texture(image, uv_new).rgba;		// 当前像素的颜色 //
			float curLum = Luminance(curCol.rgb);						// 当前像素的亮度 //
			vec3 deltaColor = curCol.rgb - centerCol;
			float len = dot(deltaColor, deltaColor);
			// float exponent = -((i-k)*(i-k)+(j-l)*(j-l))/sigmaSSquareMult2 - (curLum-centerLum)*(curLum-centerLum)/sigmaRSquareMult2;
			float exponent = -((i-k)*(i-k)+(j-l)*(j-l))/sigmaSSquareMult2 - len/sigmaRSquareMult2;
			float weight = exp(exponent);
			sum_up += curCol*weight;
			sum_down += weight;
		}
	}

	return sum_up/sum_down;
}

float BilateralFilter1D(vec2 uv)
{
	float i = uv.x;
	float j = uv.y;
	float sigmaSSquareMult2 = (2*_SigmaS*_SigmaS);
	float sigmaRSquareMult2 = (2*_SigmaR*_SigmaR);

	float centerCol = texture(image, uv).w;					// 中心点像素的颜色 //
	float centerLum = centerCol;						// 中心点像素的亮度 //
	
	vec2 texelSize = 1.0 / vec2(textureSize(image, 0));

	float sum_up;												// 分子 //
	float sum_down;												// 分母 //
	for(int k=-_Radius; k<=_Radius; k++)
	{
		for(int l=-_Radius; l<=_Radius; l++)
		{
			vec2 uv_new = uv + texelSize*vec2(k,l);
			float curCol = texture(image, uv_new).w;		// 当前像素的颜色 //
			float curLum = curCol;						// 当前像素的亮度 //
			float deltaColor = curCol-centerCol;
			float len = deltaColor * deltaColor;
			// float exponent = -((i-k)*(i-k)+(j-l)*(j-l))/sigmaSSquareMult2 - (curLum-centerLum)*(curLum-centerLum)/sigmaRSquareMult2;
			float exponent = -((i-k)*(i-k)+(j-l)*(j-l))/sigmaSSquareMult2 - len/sigmaRSquareMult2;
			float weight = exp(exponent);
			sum_up += curCol*weight;
			sum_down += weight;
		}
	}

	return sum_up/sum_down;
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


vec3 GaussNormal(sampler2D Color, vec2 uv)
{
    const int size = 7;

    vec3 result = vec3(0);
    
    vec2 texSize = textureSize(Color, 0);

    int idx = 0;

    for(int i = -3;i <= 3;i++)
    {
        for(int j = -3; j <= 3;j++)
        {
            vec2 offset_uv = uv + vec2(5.0 * i /texSize.x, 5.0 * j /texSize.y);

            vec3 n = texture2D(Color, offset_uv).xyz;

            float weight = gauss[idx++];

            result += weight * n;

        }

    }

    return result;
}

 
 

void main() {

    vec2 texelSize = 1.0 / vec2(textureSize(image, 0));

    ///不对体积的遮蔽作模糊，否则会产生伴影
	//float volume_shadow = GaussVolumeShadow(image, vUv);
    
    //gl_FragColor = texture(image, vUv);
    gl_FragColor.w = clamp(BilateralFilter1D(vUv), 0, 1);

	//gl_FragColor.xyz = normalize(BilateralFilter(vUv));

	//gl_FragColor.xyz = normalize(gl_FragColor.xyz);

			vec3 normal = texture(image, vUv).xyz;
			gl_FragColor.xyz = normal;

			const float F = 0.5;
			vec3 normal2 = texture(image, vUv + vec2(-texelSize.y, 0)).xyz;
			gl_FragColor.xyz += dot(normal, normal2) > F? normal2: vec3(0);

			normal2 = texture(image, vUv + vec2(texelSize.y, 0)).xyz;
			gl_FragColor.xyz += dot(normal, normal2) > F? normal2: vec3(0);

			normal2 = texture(image, vUv + vec2(0, -texelSize.y)).xyz;
			gl_FragColor.xyz += dot(normal, normal2) > F? normal2: vec3(0);

			normal2 = texture(image, vUv + vec2(0, texelSize.y)).xyz;
			gl_FragColor.xyz += dot(normal, normal2) > F? normal2: vec3(0);

			normal2 = texture(image, vUv + vec2(-texelSize.y, texelSize.y)).xyz;
			gl_FragColor.xyz += dot(normal, normal2) > F? normal2: vec3(0);

			normal2 = texture(image, vUv + vec2(-texelSize.y, -texelSize.y)).xyz;
			gl_FragColor.xyz += dot(normal, normal2) > F? normal2: vec3(0);

			normal2 = texture(image, vUv + vec2(texelSize.y, texelSize.y)).xyz;
			gl_FragColor.xyz += dot(normal, normal2) > F? normal2: vec3(0);

			normal2 = texture(image, vUv + vec2(texelSize.y, -texelSize.y)).xyz;
			gl_FragColor.xyz += dot(normal, normal2) > F? normal2: vec3(0);

			gl_FragColor.xyz = normalize(gl_FragColor.xyz);


}
	
		