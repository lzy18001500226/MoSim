#version 330


layout (location = 0) out vec4 gFragColor; 


uniform sampler2D gScene;
uniform sampler2D gStencil;

uniform vec3 clipColor;

in vec2 vUv;

void main()
{
	
	vec4 result = texture(gScene, vUv);
	
	result.rgb = result.rgb + texture(gStencil, vUv).g * (clipColor - result.rgb);
	
	gFragColor = result;
}

	
	
		