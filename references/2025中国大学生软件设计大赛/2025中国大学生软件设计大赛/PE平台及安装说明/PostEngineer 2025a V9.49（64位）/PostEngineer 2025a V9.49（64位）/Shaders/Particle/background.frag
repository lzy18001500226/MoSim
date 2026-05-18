#version 330

out vec4 FragColor;

in vec2 vUv; 

uniform float NEAR;
uniform float FAR;

void main()
{    
	FragColor = vec4(FAR, FAR, FAR, 0.5);
	gl_FragDepth = 1.0;
}
