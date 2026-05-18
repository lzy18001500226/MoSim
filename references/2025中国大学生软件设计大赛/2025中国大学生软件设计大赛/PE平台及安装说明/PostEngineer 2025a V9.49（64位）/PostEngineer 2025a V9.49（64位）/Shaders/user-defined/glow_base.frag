#version 120

uniform sampler2D tDiffuse;

void main()
{
	// gl_FragColor = texture2D(tDiffuse, gl_TexCoord[0].st);
	gl_FragColor = vec4(1, 0 ,0, 1);
	// gl_FragColor.w = 0;
}
