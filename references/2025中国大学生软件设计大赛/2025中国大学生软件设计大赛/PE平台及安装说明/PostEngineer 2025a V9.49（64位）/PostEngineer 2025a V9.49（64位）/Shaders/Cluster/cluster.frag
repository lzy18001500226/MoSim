#version 330
#extension GL_NV_shader_buffer_load : enable
#extension GL_EXT_texture_array : enable

layout (location = 0) out vec4 gColor;
layout (location = 1) out vec4 gAlpha;

uniform sampler2DArray particleSamplers;

//uniform float exposure;
uniform vec4 color;

in vec2 TexCoord;
in float transparency;
in float texIndex;
in float brightness;

//out vec4 FragColor;

float weight(float z, float a) 
{
	return clamp(pow(min(1.0, a * 10.0) + 0.01, 3.0) * 1e8 * pow(1.0 - z * 0.9, 3.0), 1e-2, 3e3);
}


void main() 
{
	vec4 FragColor = texture2DArray(particleSamplers, vec3(TexCoord, texIndex)) ;
    FragColor.a *= transparency;
    FragColor.rgb *= brightness;
    
    //FragColor.rgb *= Color * exposure;
	FragColor.rgb *= color.rgb * color.a;
    
	float w = weight(gl_FragCoord.z, FragColor.a);

    gColor = vec4(FragColor.rgb * FragColor.a * w, FragColor.a);  

	gAlpha.r = FragColor.a * w;
}


