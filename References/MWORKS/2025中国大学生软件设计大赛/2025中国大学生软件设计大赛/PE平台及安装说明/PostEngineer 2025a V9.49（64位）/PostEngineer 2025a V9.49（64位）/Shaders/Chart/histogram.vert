
varying vec3 vPosition;
varying vec3 vColor;

void main()
{
	gl_Position = ftransform();  
	vPosition = gl_Vertex.xyz;
	vColor = gl_Color.xyz;
}
