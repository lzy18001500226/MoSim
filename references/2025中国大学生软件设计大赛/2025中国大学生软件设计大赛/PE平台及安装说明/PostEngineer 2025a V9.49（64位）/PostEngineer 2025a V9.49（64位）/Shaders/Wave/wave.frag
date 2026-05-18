#version 330
#extension GL_NV_shader_buffer_load : enable
#extension GL_EXT_texture_array : enable

layout (location = 0) out vec4 gMainColor;
layout (location = 1) out vec4 gAlpha;


uniform sampler2D waveTexture;

uniform float transparency;
uniform float exposure;

uniform float ageThreshold;

uniform vec2 segment;

uniform float width;
uniform float ratio;
uniform float scale;

uniform float totalLength;


in vec4 TexCoord;
in float age;

in vec3 vPos;

flat in vec3 oPos1;
flat in float oLen;
flat in vec3 oDir;
flat in vec3 oRight;
flat in vec2 oWidth;
flat in float oBaseCoord;

float weight(float z, float a) 
{
	return clamp(pow(min(1.0, a * 10.0) + 0.01, 3.0) * 1e8 * pow(1.0 - z * 0.9, 3.0), 1e-2, 3e3);
}


///计算点在方向梯形上的纹理坐标
vec2 CalaTexCoord()
{
	float t = dot(vPos - oPos1, oDir) / oLen;
	float w = oWidth.x + t *( oWidth.y - oWidth.x );

	float s = 0.5 + dot(vPos - oPos1, oRight) / w;

	float coord_t;
	if( abs(oWidth.y - oWidth.x) > 0.0001 ){
		coord_t = ( log2(w) - log2(oWidth.x) ) * oLen / ((oWidth.y - oWidth.x) * ratio);
	}
	else
		coord_t = t * oLen / (width * ratio);

	return vec2(oBaseCoord + coord_t, s);
}


void main() 
{
	vec4 FragColor = texture(waveTexture, CalaTexCoord());
    //FragColor.a *= transparency;
	FragColor.rgb *= exposure;

	float total_scale = 1 + totalLength / (width*ratio) * (scale - 1.0);
	float scaled_ageThreshold = ageThreshold * total_scale;
	if(scaled_ageThreshold > 0.5) scaled_ageThreshold = 0.5;

	FragColor.a = age<ageThreshold? FragColor.a * age/ageThreshold : FragColor.a;
	FragColor.a = age>(1 - scaled_ageThreshold)? FragColor.a * (1-age)/scaled_ageThreshold : FragColor.a;

	if(segment.y > 0){
		FragColor.a = age < segment.x || age > segment.y? 0: FragColor.a;
	}

	float w = weight(gl_FragCoord.z, FragColor.a);

	gMainColor = vec4(FragColor.rgb * FragColor.a * w, FragColor.a);  
	gAlpha = vec4(FragColor.a * w);
}


