
varying vec3 vPosition;
varying vec3 vNormal;

void main()
{
	gl_Position = ftransform();  
	vPosition = gl_Vertex.xyz;
  	vNormal = gl_Normal;
}
