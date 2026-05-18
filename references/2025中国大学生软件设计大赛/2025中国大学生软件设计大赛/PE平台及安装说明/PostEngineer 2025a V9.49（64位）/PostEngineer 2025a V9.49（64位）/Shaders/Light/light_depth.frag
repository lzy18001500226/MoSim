#version 130

varying vec3 ViewPos;

void main()
{
	float depth = length(ViewPos);
	gl_FragColor = vec4( depth,  0,  0.0,  1.0  );
}

	
	
		