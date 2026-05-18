#version 130

uniform sampler2D srcImage;
uniform sampler2D dstImage;
uniform sampler2D backImage;

uniform int type;

varying vec2 vUv;

void main()
{
	gl_FragColor = vec4(0, 0, 0, 1);
	
	vec4 SumColor = texture(srcImage, vUv);
	float SumAlpha = texture(dstImage, vUv).r;
	
	vec4 BackgroundColor = texture(backImage, vUv);
	
	///第一张粒子图
	if(type == 1){	
		vec4 color = vec4( SumColor.rgb / clamp(SumAlpha, 0.000001, 5000000.0), SumColor.a);
		gl_FragColor = color;
	}
	
	///粒子图之间alpha混合
	else if(type == 2){
		vec4 color = vec4( SumColor.rgb / clamp(SumAlpha, 0.000001, 5000000.0), SumColor.a);

		gl_FragColor = mix(color, BackgroundColor, color.a);
		gl_FragColor.a = color.a * 0.0 + color.a * BackgroundColor.a;
	}
	
	///最终与场景混合
	else if(type == 0){
		vec4 color = SumColor;
		//2024-6-2, wxg
		//gl_FragColor.rgb = mix(BackgroundColor.rgb, color.rgb, color.a);
		gl_FragColor.rgb = mix(BackgroundColor.rgb, color.rgb, 1.0 - color.a);
	}
	
}

	
		