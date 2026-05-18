#version 330



struct AgeParamSetting
{
	float age;
	vec3 minVal;
	vec3 maxVal;
};

class AgeParamSettings
{
	AgeParamSetting m_paramSettings[8];
	int m_count;
};

vec3 GetParamSettinsValue(AgeParamSettings settings, float age, float randVal)
{
	if(settings.m_count == 0)  return vec3(0);
	
	int k;
	for(k=1; k<settings.m_count; k++){
		if(age < settings.m_paramSettings[k].age) break;
	}
	
	if(k == settings.m_count){
		return settings.m_paramSettings[k-1].minVal*randVal + settings.m_paramSettings[k-1].maxVal*(1 - randVal);
	}
	else{
		float scale = (age - settings.m_paramSettings[k-1].age) / (settings.m_paramSettings[k].age - settings.m_paramSettings[k-1].age);
		vec3 minV = settings.m_paramSettings[k-1].minVal + scale * (settings.m_paramSettings[k].minVal - settings.m_paramSettings[k-1].minVal);
		vec3 maxV = settings.m_paramSettings[k-1].maxVal + scale * (settings.m_paramSettings[k].maxVal - settings.m_paramSettings[k-1].maxVal);
		
		return minV*randVal + maxV*(1 - randVal);
	}
}

uniform AgeParamSettings colorSettings;


in float disCP;
in vec3 viewCenterPos;
in mat4 projection;
in vec3 fragPos;

in vec3 Color;


uniform float NEAR;
uniform float FAR;


uniform float life;
uniform float totalDistance;

in float pipeX;

uniform sampler2D gNoiseMap;

out vec4 fragColor;


void main() 
{
	fragColor.gba = Color;
	//if(colorSettings.m_count == 0) fragColor.gba = vec3(1.0, 1.0, 1.0);
	//else fragColor.gba = GetParamSettinsValue(colorSettings, pipeX * life/totalDistance, 0.5/*randVal*/);
	
    float discp = distance(viewCenterPos,fragPos);
 
    if(discp>disCP){        
		//discard;
		///2023/9/10, 需要被剔除的深度值可以设为0
		//fragColor.r = FAR;
		fragColor.r = 0;
		gl_FragDepth = 1.0;
		return;   
	}    
	
	vec2 uv = (projection*vec4(vec3(fragPos),1.0)).xy*0.5+ 0.5;
	
	float height = sqrt(disCP*disCP-discp*discp);
	//height *= 0.5 + texture(gNoiseMap, uv*0.1 ).x*0.5;
	
	//深度    
	float depthView = (fragPos.z+height);    
	vec4 clip_space_pos = projection*vec4(vec3(depthView),1.0);    
	gl_FragDepth = (clip_space_pos.z/clip_space_pos.w)*0.5 + 0.5;     
	 
	fragColor.r = -depthView;
}


