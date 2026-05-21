#version 330

uniform sampler2D gScene;
uniform sampler2D gMotionVector;
uniform sampler2D gPrevFrame;

uniform int flag;

in vec2 vUv;


uniform vec2 jitter;



bool bit_and(int val, int ref) {
  if(val == 0) return false;
  return (val/ref) % 2 != 0;
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
	vec2 size = textureSize(gMotionVector, 0);

	vec2 min_depth_uv = uv;
	float min_depth = texture(gMotionVector, min_depth_uv).z;
	
	for(int i=-2; i<=2; i++){
		for(int j=-2; j<=2; j++){
			if(i==0 &&j==0) continue;
			
			vec2 cur_uv = uv + vec2(float(i), float(j))/size;
			float depth = texture(gMotionVector, cur_uv).z;
			if(min_depth > depth ){	min_depth = depth;	min_depth_uv = cur_uv; }
		}
	}
	
	return min_depth_uv;
}


vec4 GetColor(vec2 uv)
{
	return vec4(texture(gScene, uv).rgb, texture(gMotionVector, uv).b);
}



void main()
{
	vec2 size = textureSize(gScene, 0);
	float motion_factor = 1.0;
	
/*	if( bit_and(flag, 0x0001)){
	
		motion_factor = 0;
		motion_factor += texture(gScene, vUv).a < -0.5? 1: 0;
		motion_factor += texture(gScene, vUv + vec2(0, 1)/size ).a < -0.5? 1: 0;
		motion_factor += texture(gScene, vUv + vec2(1, 0)/size ).a < -0.5? 1: 0;
		motion_factor += texture(gScene, vUv + vec2(0, -1)/size ).a < -0.5? 1: 0;
		motion_factor += texture(gScene, vUv + vec2(-1, 0)/size ).a < -0.5? 1: 0;
		
		motion_factor /= 5.0;
		
		if(motion_factor < 1e-6){
			gl_FragColor = texture(gScene, vUv);
			return;
		}
	}*/

	vec2 jitterUv = vUv + jitter/2 * motion_factor;
    
	vec2 min_depth_uv = GetMinDepthUV(jitterUv);
	
	vec2 MotionVector = texture(gMotionVector, min_depth_uv).xy / 2 * motion_factor;
	
	vec4 Color = vec4(0.0);
	vec2 uv = jitterUv;
	
	Color = GetColor(uv);
	vec4 CurrentSubpixel = Color;
	gl_FragColor.a = Color.a;
		
	vec4 NearColor0 = GetColor(uv + vec2(1, 0)/size );
	vec4 NearColor1 = GetColor(uv + vec2(0, 1)/size );
	vec4 NearColor2 = GetColor(uv + vec2(-1, 0)/size );
	vec4 NearColor3 = GetColor(uv + vec2(0, -1)/size );

	vec4 BoxMin = min(Color, min(NearColor0, min(NearColor1, min(NearColor2, NearColor3))));
	vec4 BoxMax = max(Color, max(NearColor0, max(NearColor1, max(NearColor2, NearColor3))));
	
	vec2 uv_prev = vUv - MotionVector;
	vec4 History = texture(gPrevFrame, uv_prev);
	History = clamp(History, BoxMin, BoxMax);
		
/*	const float VARIANCE_CLIPPING_GAMMA = 1.0;

	// Compute the two moments
	vec3 M1 = CurrentSubpixel + NearColor0 + NearColor1 + NearColor2 + NearColor3;
	vec3 M2 = CurrentSubpixel * CurrentSubpixel + NearColor0 * NearColor0 + NearColor1 * NearColor1 
		+ NearColor2 * NearColor2 + NearColor3 * NearColor3;

	vec3 MU = M1 / 5.0;
	vec3 Sigma = sqrt(M2 / 5.0 - MU * MU);

	vec3 BoxMin = MU - VARIANCE_CLIPPING_GAMMA * Sigma;
	vec3 BoxMax = MU + VARIANCE_CLIPPING_GAMMA * Sigma;

	History = ClipAABB(BoxMin, BoxMax, History, MU);*/

	float factor = 1.0f/16;
	Color = clamp(CurrentSubpixel * factor + History * (1 - factor), 0, 1);
		
	gl_FragColor = clamp(Color, 0, 1);
	//gl_FragDepth = gl_FragColor.a;
}

	
	
		