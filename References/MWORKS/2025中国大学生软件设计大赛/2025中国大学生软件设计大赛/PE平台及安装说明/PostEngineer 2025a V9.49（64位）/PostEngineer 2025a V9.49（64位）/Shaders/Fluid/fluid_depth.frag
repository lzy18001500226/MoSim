#version 330


in float disCP;
in vec3 viewCenterPos;
in mat4 projection;
in vec3 fragPos;

uniform float NEAR;
uniform float FAR;


out float gDepth;


void main() 
{
	
    float discp = distance(viewCenterPos,fragPos);
 
    if(discp>disCP){ 
        discard;       
		//gDepth = FAR;
		//gl_FragDepth = 1.0;
		//return;   
	}    
	
	float height = sqrt(disCP*disCP-discp*discp);
	
	//…Ó∂»    
	float depthView = (fragPos.z+height);    
	vec4 clip_space_pos = projection*vec4(vec3(depthView),1.0);    
	gl_FragDepth = (clip_space_pos.z/clip_space_pos.w)*0.5 + 0.5;    
	 
	gDepth = -depthView;
}


