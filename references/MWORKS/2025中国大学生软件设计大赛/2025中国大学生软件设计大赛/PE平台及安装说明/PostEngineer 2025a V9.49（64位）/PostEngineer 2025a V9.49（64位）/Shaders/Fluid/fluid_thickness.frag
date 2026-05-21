#version 330


in float disCP;
in vec3 viewCenterPos;
in mat4 Projectionf;
in vec3 fragPos;


uniform float NEAR;
uniform float FAR;


out float gThickness;


void main() 
{
	
    float discp=distance(viewCenterPos,fragPos);
    vec4 fColor;
    
    if(discp>disCP){
		discard;
	}
	
	float height=sqrt(disCP*disCP-discp*discp);
	gThickness=2.0*height;
}


