#version 330

uniform sampler2D gImage;

uniform vec2 offset;

in vec2 vUv;

void main()
{	
	vec2 uv = texture(gImage, vUv).xy;
	gl_FragDepth = texture(gImage, uv).z;
	gl_FragColor = vec4((gl_FragDepth-0.98)*50, 0, 0, 1);
}

	
	
		