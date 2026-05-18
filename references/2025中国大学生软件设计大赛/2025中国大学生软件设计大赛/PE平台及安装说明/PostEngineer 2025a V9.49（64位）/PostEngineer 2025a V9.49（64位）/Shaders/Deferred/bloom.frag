#version 130

uniform sampler2D ColorBuffer;
uniform float threshold;

varying vec2 vUv;

void main()
{
	vec3 color = texture(ColorBuffer, vUv).rgb;
/*	float brightness = dot(color, vec3(threshold));
	if(brightness > 3.0 && brightness < 15.0)
		gl_FragColor = vec4(color, 1.0);
	else
		gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);*/
		
	float brightness = dot(color, vec3(1.0));  ///超越白色的程度
		if(brightness > threshold*3 && brightness < 100.0)
			gl_FragColor = vec4(color, 1.0);
		else
			gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);

}

	
	
		