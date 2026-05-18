#version 130

uniform sampler2D srcImage;
uniform sampler2D dstImage;
uniform int mode;

varying vec2 vUv;

void main()
{

	vec4 result = vec4(1, 0, 0, 1);
	if(mode == 0){
		result.rgb = texture(srcImage, vUv).rgb * (vec3(1.0) - texture(dstImage, vUv).rgb);
	}
	else if(mode == 1){
		result.rgb = texture(srcImage, vUv).rgb + texture(dstImage, vUv).rgb;
	}
	else if(mode == 2){
		vec4 dstColor = texture(dstImage, vUv);
		result.rgb = texture(srcImage, vUv).rgb * (1 - dstColor.a) + dstColor.rgb*dstColor.a;
	}
	else if(mode == 3){
		result = texture(srcImage, vUv);
		result.rgb *= 1.0 - texture(dstImage, vUv).r;
	}
	
	gl_FragColor = result;
}

	
	
		