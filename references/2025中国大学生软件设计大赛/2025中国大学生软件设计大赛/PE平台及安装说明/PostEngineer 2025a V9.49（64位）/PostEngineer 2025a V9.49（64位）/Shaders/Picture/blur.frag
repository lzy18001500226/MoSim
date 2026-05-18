#version 130

uniform sampler2D gImage;

uniform bool hori;
uniform int width;
uniform int component;

const float weight[15] = float[](0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216, 0.101487, 0.0983644, 0.0895618, 0.0766063, 0.0615549, 0.0464641, 0.032948, 0.0219481, 0.0137348, 0.00807424 );

varying vec2 vUv;

vec4 GetColor(vec2 uv)
{
	//return vec4(1.0) - texture(gImage, uv);
	return texture(gImage, uv);
}

void main()
{
	int base_index = 0;
	if(width > 5) base_index = 5;
	
	vec4 Color = GetColor(vUv);
	
	vec2 tex_offset = 1.0 / textureSize(gImage, 0);// * max(width/10, 1);
	vec4 result = Color * weight[base_index+0];
	
  	if(hori){
		for(int i = 1; i < base_index + 5; ++i)
        {

            result += GetColor(vUv + vec2(tex_offset.x * i, 0.0)) * weight[base_index+i];
            result += GetColor(vUv - vec2(tex_offset.x * i, 0.0)) * weight[base_index+i];

        }
	}  
           	
	else{
		for(int i = 1; i < base_index + 5; ++i)
        {

            result += GetColor(vUv + vec2(0.0, tex_offset.y * i)) * weight[base_index+i];
            result += GetColor(vUv - vec2(0.0, tex_offset.y * i)) * weight[base_index+i];

        }
	}
	
	gl_FragColor = vec4(result);
	//gl_FragColor.a = Color.a;
}

	
	
		