#version 130

uniform sampler2D ColorBuffer;


const int SAMPLER_NUMBER = 5; //9*9 = 5*2-1
//float weight[SAMPLER_NUMBER] = float[] (0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216);
float weight[SAMPLER_NUMBER] = float[SAMPLER_NUMBER](0.1633, 0.1531, 0.12245, 0.0918, 0.051);

uniform float blurScale;  
uniform float blurStrength;
uniform int blurDir; 

varying vec2 vUv;

void main()
{             
	vec2 tex_size = vec2(textureSize(ColorBuffer, 0));
    	vec2 tex_offset = blurScale / tex_size;
	vec3 color = texture(ColorBuffer, vUv).rgb ;
    	vec3 result = color * weight[0]; 
	
	if(blurDir == 0) {
		for(int i = 1; i < SAMPLER_NUMBER; ++i) {
			result += texture(ColorBuffer, vUv + vec2(tex_offset.x, 0.0)* i).rgb * weight[i]* blurStrength;
			result += texture(ColorBuffer, vUv - vec2(tex_offset.x, 0.0)* i).rgb * weight[i]* blurStrength;		
		}
	}
	else {
		for(int i = 1; i < SAMPLER_NUMBER; ++i) {
			result += texture(ColorBuffer, vUv + vec2(0.0, tex_offset.y)* i).rgb * weight[i]* blurStrength;
			result += texture(ColorBuffer, vUv - vec2(0.0, tex_offset.y)* i).rgb * weight[i]* blurStrength;
		}
	}

	gl_FragColor = vec4(result, 1.0);
}

	
	
		