
varying vec2 vUv;

void main()
{
	gl_TexCoord[0] = gl_MultiTexCoord0;  
	gl_Position = ftransform();  	
	vUv = gl_TexCoord[0].st;
}
