#version 330
#extension GL_EXT_gpu_shader4 : enable


layout (points) in;
layout (triangle_strip) out;
layout (max_vertices = 4) out;

const float PI = 3.1415926;

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

uniform mat4 modelview;
uniform mat4 VP;

uniform float baseSize;
uniform vec3 cameraPos;
uniform int  boardType;

uniform AgeParamSettings sizeSettings;
uniform AgeParamSettings colorSettings;
uniform AgeParamSettings transparencySettings;


in vec3 position0[];
in float age0[];
in float randVal0[];
in float rotation0[];
in vec3 velocity0[];

in mat4 projection0[];

out vec2 TexCoord;
out float transparency;
out vec3 Color;



out float disCP;
out vec3 viewCenterPos;
out vec3 fragPos;
out mat4 projection;


void main() 
{
	float age = age0[0];
	vec3  Pos = (modelview * vec4(position0[0],1)).xyz;
	float randVal = randVal0[0];
	
	projection = projection0[0];
	
	//·¢ÉäÁ£×Ó
	if(randVal < 0) return;
	
	float sizeFactor;
	if(sizeSettings.m_count == 0) sizeFactor = 1.0;
	else sizeFactor = GetParamSettinsValue(sizeSettings, age, randVal).x;
	
	if(transparencySettings.m_count == 0) transparency = 1.0;
	else transparency = GetParamSettinsValue(transparencySettings, age, randVal).x;
	
	
	if(colorSettings.m_count == 0) Color = vec3(1.0, 1.0, 1.0);
	else Color = GetParamSettinsValue(colorSettings, age, randVal);

	
	float particleRadius = baseSize * sizeFactor / 2;
	
	disCP = particleRadius;
   
		
	viewCenterPos = Pos;
	
	fragPos = Pos + vec3(-particleRadius, -particleRadius, 0);
	gl_Position = projection * vec4(fragPos, 1.0);
	TexCoord = vec2(1.0, 0.0);
	EmitVertex();
    
	fragPos = Pos + vec3(particleRadius, -particleRadius, 0);
	gl_Position = projection * vec4(fragPos, 1.0);
	TexCoord = vec2(1.0, 1.0);
	EmitVertex();
    
	fragPos = Pos + vec3(-particleRadius, particleRadius, 0);
	gl_Position = projection * vec4(fragPos, 1.0);
	TexCoord = vec2(0.0, 0.0);
	EmitVertex();
    
	fragPos = Pos + vec3(particleRadius, particleRadius, 0);
	gl_Position = projection * vec4(fragPos, 1.0);
	TexCoord = vec2(0.0, 1.0);
	EmitVertex();
	EndPrimitive();

}
