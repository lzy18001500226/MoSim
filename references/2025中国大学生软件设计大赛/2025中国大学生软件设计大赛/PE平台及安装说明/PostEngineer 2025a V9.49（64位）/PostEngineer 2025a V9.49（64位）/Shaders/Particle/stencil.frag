#version 330 core

layout (location = 0) out vec4  FragColor;   

uniform sampler2D gForwardDepth;

uniform vec2 screenSize;

void main()
{
	vec2 uv = gl_FragCoord.xy / screenSize;	
	float sceneDepth = texture(gForwardDepth, uv).r;
	
	///需要被剔除的深度值可以设为0
	if ( sceneDepth > 0.000001 && sceneDepth < gl_FragCoord.z - 0.000001) {        
		discard; 
		return;
	} 
	
    FragColor = vec4(1.0, 0.0, 0.0,  1.0);
}