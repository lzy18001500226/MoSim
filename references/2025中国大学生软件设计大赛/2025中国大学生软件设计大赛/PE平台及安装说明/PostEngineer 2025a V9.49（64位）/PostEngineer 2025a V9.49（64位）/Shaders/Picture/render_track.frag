#version 330
#extension GL_NV_shader_buffer_load : enable
#extension GL_EXT_texture_array : enable

uniform sampler2D gBackground;

uniform sampler2DArray gFrames;
uniform int count;

uniform int flag;

in vec2 vUv;

void main()
{	
	vec4 color = vec4(0);

	if(flag == 0){
		float d = 6.0 / (count + 1) / (count*2 + 1);
		for(int k=0; k<count; k++){
			color.rgb += texture2DArray(gFrames, vec3(vUv, k)).rgb * (k+1)*(k+1)*d;
		}
		color.rgb /= count;
	}
	else{
		vec4 backColor = texture2D(gBackground, vUv);
		for(int k=0; k<count; k++){
			float factor = 1.0;//( 0.3 + (k+1) * 0.7/count );
			color += texture2DArray(gFrames, vec3(vUv, k)) * factor + backColor*(1 - factor);
		}
		//color.rgb = texture2D(gBackground, vUv).rgb * (1 - color.a) + color.rgb * color.a;
		//float len = min(length(color.rgb) * 3, 1);
		float brightness = 0.2126*color.r + 0.7152*color.g + 0.0722*color.b;
		brightness = min(brightness * 5, 1);
		color.rgb += backColor.rgb * (1 - brightness);
	}

	gl_FragColor.rgb = color.rgb;
	gl_FragColor.a = 1.0;
}

	
	
		