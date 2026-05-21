#version 130

uniform sampler2D gSumColorImage;
uniform sampler2D gSumAlphaImage;


varying vec2 vUv;

void main()
{
	gl_FragColor = vec4(0, 0, 0, 1);
	
	vec4 SumColor = texture(gSumColorImage, vUv);
	float SumAlpha = texture(gSumAlphaImage, vUv).r;
	
	vec4 color = vec4( SumColor.rgb / clamp(SumAlpha, 0.000001, 5000000.0), 1.0 - SumColor.a);
	gl_FragColor = color;
	
}

	
		