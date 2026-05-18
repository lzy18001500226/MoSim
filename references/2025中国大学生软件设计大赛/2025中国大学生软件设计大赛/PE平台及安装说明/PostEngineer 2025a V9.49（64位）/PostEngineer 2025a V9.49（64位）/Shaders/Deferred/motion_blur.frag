#version 330

uniform sampler2D sceneImage;
uniform sampler2D gPositionDepth;
uniform sampler2D gMotionVector;

uniform vec2 gJitter;

uniform float gMaxDepth;
uniform float gBlurFactor;

in vec2 vUv;

vec2 GetJitterUV(vec2 uv)
{
	return uv + gJitter / 2;
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



void main()
{
	//vec2 jitterUv = GetJitterUV(vUv);
	vec2 minUv = vUv;//GetMinDepthUV(vUv);

	vec2 MotionVector = texture(gMotionVector, minUv).xy / 2 * gBlurFactor;
	float len = length(MotionVector);

	vec4 Color = vec4(0.0);
	if(len > 0.00001){

		 ///要叠加上一帧的像素残影，而上一帧的像素当前已经位于 minUv + MotionVector 处
		
		float max_delta_depth = gMaxDepth;
		vec2 uv0 = minUv;
		float depth0 = texture(gPositionDepth, uv0).w;
		vec4 clr0 = texture(sceneImage, uv0);

		vec2 uv1 = uv0 + MotionVector;
		float depth1 = texture(gPositionDepth, uv1).w;
		float delta_depth = depth1 - depth0;

		if( abs(delta_depth) > max_delta_depth ){
			Color = clr0;
		}
		else{
			vec4 clr1 = texture(sceneImage, uv1);

			vec2 uv2 = uv1 + MotionVector;
			float depth2 = texture(gPositionDepth, uv2).w;
			delta_depth = depth2 - depth0;

			if( abs(delta_depth) > max_delta_depth ){
				Color = clr0 * 0.8 + clr1*0.2;
			}
			else{
				vec4 clr2 = texture(sceneImage, uv2);

				vec2 uv3 = uv2 + MotionVector;
				float depth3 = texture(gPositionDepth, uv3).w;
				delta_depth = depth3 - depth0;

				if( abs(delta_depth) > max_delta_depth ){
					Color = clr0 * 0.6 + clr1*0.3 + clr2*0.1;
				}
				else{
					vec4 clr3 = texture(sceneImage, uv3);

					Color = clr0 * 0.5 + clr1*0.25 + clr2*0.15 + clr3*0.1;
				}
			}
		}
	}
	else
		Color = texture(sceneImage, minUv);
		
	gl_FragColor = Color;
}

	
	
		