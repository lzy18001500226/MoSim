#version 330 core

layout (location = 0) out vec4 gMainColor;


uniform sampler2D gScene;
uniform sampler2D gSSRBlend;


varying vec2 vUv;



void main() 
{
	vec4 mainColor = texture(gScene, vUv);
	
	vec4 ssrColor = texture(gSSRBlend, vUv);
	
	float factor = clamp((pow(ssrColor.a, 3) - 0.05), 0, 0.8);
	vec3 blendColor = mainColor.rgb * (1 - factor) + ssrColor.rgb * factor;
	mainColor.rgb = mainColor.rgb*mainColor.rgb + blendColor * ( vec3(1) - mainColor.rgb );
	
	gMainColor = mainColor;

}