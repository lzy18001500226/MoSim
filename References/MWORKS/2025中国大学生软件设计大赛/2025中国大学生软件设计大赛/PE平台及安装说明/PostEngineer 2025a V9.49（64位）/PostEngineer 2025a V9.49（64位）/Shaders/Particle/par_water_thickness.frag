#version 330


in float disCP;
in vec3 viewCenterPos;
in mat4 Projectionf;
in vec3 fragPos;


uniform float NEAR;
uniform float FAR;


out float FragColor;


void main() 
{
	
    float discp=distance(viewCenterPos,fragPos);
    
    if(discp>disCP){
		discard;
	}
	
	float height=sqrt(disCP*disCP-discp*discp);
	FragColor=2.0*height;
}


