#version 130

uniform sampler2D image;
uniform bool hori;
uniform int width;

const float weight[15] = float[](0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216, 0.101487, 0.0983644, 0.0895618, 0.0766063, 0.0615549, 0.0464641, 0.032948, 0.0219481, 0.0137348, 0.00807424 );

varying vec2 vUv;

vec3 getColorX(int direction, int i, vec2 tex_offset, vec3 mainColor)
{
	vec3 color;
	vec2 uv = vUv + vec2(tex_offset.x * i, 0.0) * direction;
	if( texture(image, uv).b < 0.5 ) color = mainColor;
	else color = texture(image, uv).rgb;
	
	return color;
}

vec3 getColorY(int direction, int i, vec2 tex_offset, vec3 mainColor)
{
	vec3 color;
	vec2 uv = vUv + vec2(0.0, tex_offset.y * i) * direction;
	if( texture(image, uv).b < 0.5 ) color = mainColor;
	else color = texture(image, uv).rgb;
	
	return color;
}


void main()
{
	int base_index = 0;
	if(width > 5) base_index = 5;
	
	vec2 tex_offset = 1.0 / textureSize(image, 0);
	vec3 mainColor = texture(image, vUv).rgb;
	vec3 color;
	
	if(texture(image, vUv).b < 0.5){
		gl_FragColor = vec4(mainColor, 1.0);
		return;
	}
	
	vec3 result = mainColor * weight[base_index+0];
	
  	if(hori){
		for(int i = 1; i < base_index + 5; ++i)

        {
			result += getColorX(-1, i, tex_offset, mainColor) * weight[base_index+i];
			result += getColorX(1, i, tex_offset, mainColor) * weight[base_index+i];

        }
	}  
           	
	else{
		for(int i = 1; i < base_index + 5; ++i)
        {        
            result += getColorY(-1, i, tex_offset, mainColor) * weight[base_index+i];
			result += getColorY(1, i, tex_offset, mainColor) * weight[base_index+i];

        }
	}
	
	gl_FragColor = vec4(result, 1.0);
}

	
	
		