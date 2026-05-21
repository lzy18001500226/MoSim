#version 330

uniform sampler2D sceneImage;
uniform sampler2D bloomImage;

uniform sampler2D gLightVolume;
uniform sampler2D gVolume;
uniform sampler2D gCloud;   /// gCloud与gVolume不共存

uniform sampler2D gShadow;
uniform sampler2D gNormal;
uniform sampler2D gPosition;
uniform sampler2D gDepth;

uniform sampler2D gSystem;

uniform sampler2D gSSR;


uniform sampler2D gForward;

//uniform sampler2D gAtmosphere;

uniform sampler2D gMotionVector;

uniform sampler2D gPrevFrame;

uniform vec4 lightPosition;

uniform float shadowColor;
uniform float exposure;
uniform int flag;

uniform vec3 fogColor;

in vec2 vUv;

bool bit_and(int val, int ref) {
  if(val == 0) return false;
  return (val/ref) % 2 != 0;
}


vec3 hdr(vec3 L, float expo) {
    L = L * expo;
    L.r = L.r < 1.413 ? pow(L.r * 0.38317, 1.0 / 2.2) : 1.0 - exp(-L.r);
    L.g = L.g < 1.413 ? pow(L.g * 0.38317, 1.0 / 2.2) : 1.0 - exp(-L.g);
    L.b = L.b < 1.413 ? pow(L.b * 0.38317, 1.0 / 2.2) : 1.0 - exp(-L.b);
    return L;
}



vec3 gamma(vec3 color) {
    color.r = pow(color.r, 1.0 / 2.2);
    color.g = pow(color.g, 1.0 / 2.2);
    color.b = pow(color.b, 1.0 / 2.2);
    return color;
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


vec4 GaussBlur(sampler2D Color, vec2 uv)
{
    float step = 1.0;

    vec4 result = vec4(0);
    
    vec2 texSize = textureSize(Color, 0);

    int idx = 0;

    for(int i = -3;i <= 3;i++)
    {
        for(int j = -3; j <= 3;j++)
        {
            vec2 offset_uv = uv + vec2(step * i /texSize.x, step * j /texSize.y);

            vec4 s = texture2D(Color, offset_uv);

            float weight = gauss[idx++];

            result += weight * s;

        }

    }

    return result;
}



vec4 GetColor(vec2 uv)
{
	vec3 result = vec3(0.0);
	vec4 mainColor = texture(sceneImage, uv);

	vec4 bloomColor = texture(bloomImage, uv);
	
	if(bit_and(flag, 0x0001)) result += mainColor.rgb;
	if(bit_and(flag, 0x0002)){
		result += bloomColor.rgb;
		//vec3 bloom = texture(bloomImage, uv).rgb;
		//result = result + max(1-result, 0.0)*bloom;
	}
	
	if(bit_and(flag, 0x0008)){
		vec4 lightVolume = texture(gLightVolume, uv);
		float alpha = GaussBlur(gLightVolume, uv).a;
		vec3 color = lightVolume.rgb * alpha;
		float brightness = 0.2126*color.r + 0.7152*color.g + 0.0722*color.b;
		result = result  + color;
	}
	if(bit_and(flag, 0x00200)){
		vec4 volumeColor = texture(gVolume, uv);
		//float brightness = 0.2126*volumeColor.r + 0.7152*volumeColor.g + 0.0722*volumeColor.b;
		//result = result*clamp(1 - brightness*volumeColor.a, 0, 1) + volumeColor.rgb;
		result = result*(1 - volumeColor.a) + volumeColor.rgb;
	}
	if(bit_and(flag, 0x0400)){
		vec4 cloudColor = texture(gCloud, uv);
		result = result*(1-cloudColor.a) + cloudColor.rgb*cloudColor.a;
	}
	if(bit_and(flag, 0x0100)){
		vec4 clr = texture(gSystem, uv);
		result = result*(1 - clr.a) + clr.rgb*clr.a;
	}
	
	
	if(bit_and(flag, 0x0080)){
		vec4 ssrColor = texture(gSSR, uv);
		float factor = clamp((pow(ssrColor.a, 3) - 0.01), 0, 0.9);
		vec3 blendColor = result * (1 - factor) + ssrColor.rgb * factor;
		result = result*result + blendColor*( vec3(1) - result );
	}

	
	if(bit_and(flag, 0x0004)){
	
		vec4 shadowFactor = texture(gShadow, uv);
		
				/*	float f = max(shadowFactor.r-0.2, 0) * 1.25;
					//f = clamp(1 - min( (1-f) * 1.0, 1.0), 0.0, 1.0);
					shadowFactor.r = mix(shadowColor, 1, shadowFactor.r );
	
					vec3 worldN = texture2D(gNormal, uv).xyz;
					vec3 worldP = texture2D(gPosition, uv).xyz;
		
					float dotOfFace = 0;
					if(lightPosition.w < 0.5){
						dotOfFace = -dot(worldN, lightPosition.xyz);
					}
					else{
						dotOfFace = -dot(worldN,  normalize(worldP - lightPosition.xyz));
					}
		
					dotOfFace = clamp(dotOfFace*2, 0, 1);		
					float shadow = mix(1, shadowFactor.r, dotOfFace);
		
					result *= shadow;*/
		
		///排除剪切断面
		if(bloomColor.a > -0.5)
			result *= shadowFactor.w;  ///SSAO
	}
	
	
	///2023/9/21, 大气放在雾之前
	/*if(bit_and(flag, 0x0010)){   ///延迟渲染部分添加大气
		vec4 atmos = texture2D(gAtmosphere, uv);
		result = result * (1 - (atmos.a-1)*0.05) * (1 - atmos.b) + atmos.rgb;
		//result = hdr(result, 1);
		//result = result * (1 - atmos.b) + atmos.rgb * atmos.b;
		//result += atmos.rgb * 0.6;
	}*/
	
	return vec4(result, mainColor.a);
}




vec3 ClipAABB(vec3 aabbMin, vec3 aabbMax, vec3 prevSample, vec3 avg)

{

#ifdef CLIP_TO_CENTER

	// note: only clips towards aabb center (but fast!)

	vec3 p_clip = 0.5 * (aabbMax + aabbMin);

	vec3 e_clip = 0.5 * (aabbMax - aabbMin);



	vec3 v_clip = prevSample - p_clip;

	vec3 v_unit = v_clip.xyz / e_clip;

	vec3 a_unit = abs(v_unit);

	float ma_unit = max(a_unit.x, max(a_unit.y, a_unit.z));



	if (ma_unit > 1.0)

		return p_clip + v_clip / ma_unit;

	else

		return prevSample;// point inside aabb

#else

	vec3 r = prevSample - avg;

	vec3 rmax = aabbMax - avg.xyz;

	vec3 rmin = aabbMin - avg.xyz;



	const float eps = 0.000001f;



	if (r.x > rmax.x + eps)

		r *= (rmax.x / r.x);

	if (r.y > rmax.y + eps)

		r *= (rmax.y / r.y);

	if (r.z > rmax.z + eps)

		r *= (rmax.z / r.z);



	if (r.x < rmin.x - eps)

		r *= (rmin.x / r.x);

	if (r.y < rmin.y - eps)

		r *= (rmin.y / r.y);

	if (r.z < rmin.z - eps)

		r *= (rmin.z / r.z);



	return avg + r;

#endif

}


vec2 GetMinDepthUV(vec2 uv)
{
	vec2 size = textureSize(gDepth, 0);

	vec2 min_depth_uv = uv;
	float min_depth = texture(gDepth, min_depth_uv).x;
	
	for(int i=-2; i<=2; i++){
		for(int j=-2; j<=2; j++){
			if(i==0 &&j==0) continue;
			
			vec2 cur_uv = uv + vec2(float(i), float(j))/size;
			float depth = texture(gDepth, cur_uv).x;
			if(min_depth > depth ){	min_depth = depth;	min_depth_uv = cur_uv; }
		}
	}
	
	return min_depth_uv;
}



void main()
{
    
	vec2 min_depth_uv = vUv;//GetMinDepthUV(vUv);
	
	vec2 MotionVector = texture(gMotionVector, min_depth_uv).xy / 2;

	
	vec4 Color = vec4(0.0);
	vec2 uv = vUv;
	
	Color = GetColor(uv);

	vec3 CurrentSubpixel = Color.rgb;
		
	///用alpha分量-1来区分延迟渲染像素，同时把透明像素分离出来
	//if(bit_and(flag, 0x0040) && (texture(gForward, uv).a < -0.5 )){ 
	if(bit_and(flag, 0x0040)){ 
	
		vec2 size = textureSize(sceneImage, 0);
		
		vec3 NearColor0 = GetColor(uv + vec2(1, 0)/size ).xyz;
		vec3 NearColor1 = GetColor(uv + vec2(0, 1)/size ).xyz;
		vec3 NearColor2 = GetColor(uv + vec2(-1, 0)/size ).xyz;
		vec3 NearColor3 = GetColor(uv + vec2(0, -1)/size ).xyz;

		vec2 uv_prev = uv - MotionVector;
		vec3 History = texture(gPrevFrame, uv_prev).xyz;

		if(true){   ///运动海面会有拖影
			vec3 BoxMin = min(Color.xyz, min(NearColor0, min(NearColor1, min(NearColor2, NearColor3))));
			vec3 BoxMax = max(Color.xyz, max(NearColor0, max(NearColor1, max(NearColor2, NearColor3))));
			History = clamp(History, BoxMin, BoxMax);
		}
		if(length(MotionVector) > 1e-6){      ///闪烁明显
			const float VARIANCE_CLIPPING_GAMMA = 1.0;
			// Compute the two moments
			vec3 M1 = CurrentSubpixel + NearColor0 + NearColor1 + NearColor2 + NearColor3;
			vec3 M2 = CurrentSubpixel * CurrentSubpixel + NearColor0 * NearColor0 + NearColor1 * NearColor1 
				+ NearColor2 * NearColor2 + NearColor3 * NearColor3;

			vec3 MU = M1 / 5.0;
			vec3 Sigma = sqrt(M2 / 5.0 - MU * MU);

			vec3 BoxMin = MU - VARIANCE_CLIPPING_GAMMA * Sigma;
			vec3 BoxMax = MU + VARIANCE_CLIPPING_GAMMA * Sigma;

			History = ClipAABB(BoxMin, BoxMax, History, MU);
		}
		
	
		float factor = 1.0f/16;
		Color.rgb = clamp(CurrentSubpixel * factor + History * (1 - factor), 0.0, 1.0);
	}

	//Color.rgb = hdr(Color.rgb, 1.2);
	
	//gl_FragColor = clamp(Color, 0, 1);
	gl_FragColor = max(Color, 0);
	gl_FragColor.a = Color.a;

	if(bit_and(flag, 0x0040) &&  gl_FragColor.a < -0.5) gl_FragColor.a = 1.0;
}

	
	
		