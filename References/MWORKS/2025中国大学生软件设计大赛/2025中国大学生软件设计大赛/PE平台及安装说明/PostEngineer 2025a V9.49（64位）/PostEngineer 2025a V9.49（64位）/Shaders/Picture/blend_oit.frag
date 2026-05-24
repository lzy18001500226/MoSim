#version 130

uniform sampler2D srcImage;
uniform sampler2D dstImage;
uniform sampler2D backImage;

varying vec2 vUv;

void main()
{
	gl_FragColor = vec4(0, 0, 0, 1);
	
	vec4 SumColor = texture(srcImage, vUv);
	float SumAlpha = texture(dstImage, vUv).r;
	
	vec3 BackgroundColor = texture(backImage, vUv).rgb;
	
	vec4 color = vec4( SumColor.rgb / clamp(SumAlpha, 0.000001, 5000000.0), SumColor.a);
	//color.rgb = pow(color.rgb, vec3(1.0/2.2));

	gl_FragColor.rgb = mix(color.rgb, BackgroundColor.rgb, color.a);

}

	
	
		