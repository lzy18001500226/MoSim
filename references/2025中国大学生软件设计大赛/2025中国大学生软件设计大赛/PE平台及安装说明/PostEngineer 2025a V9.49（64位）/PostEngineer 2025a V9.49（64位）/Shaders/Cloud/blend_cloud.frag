#version 130

uniform sampler2D srcImage;
uniform sampler2D dstImage;
uniform int mode;

varying vec2 vUv;

void main()
{

	vec4 result = texture(srcImage, vUv);
	
	vec4 cloudColor = texture(dstImage, vUv);
	result.rgb = result.rgb * (1-cloudColor.a) + cloudColor.rgb;
	
	gl_FragColor = result;
}

	
	
		