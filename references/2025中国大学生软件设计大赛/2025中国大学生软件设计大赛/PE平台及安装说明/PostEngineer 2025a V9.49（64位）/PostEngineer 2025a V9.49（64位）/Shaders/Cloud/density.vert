
varying vec2 uv;

void main()
{
	gl_TexCoord[0] = gl_MultiTexCoord0;  
	gl_Position = ftransform();  	
	uv = gl_TexCoord[0].st;
}
