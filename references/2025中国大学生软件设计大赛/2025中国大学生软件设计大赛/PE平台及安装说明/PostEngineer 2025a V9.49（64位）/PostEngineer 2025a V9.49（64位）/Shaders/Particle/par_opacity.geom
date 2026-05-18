#version 330
#extension GL_EXT_gpu_shader4 : enable


layout (points) in;
layout (triangle_strip) out;
layout (max_vertices = 4) out;

const float PI = 1.1415926;

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

vec3 GetParamSettinsValue(AgeParamSettings settings, float age, float radialPos, float randVal)
{
	if(settings.m_count == 0)  return vec3(0);
	
	//float extent = 1.0 - min(abs(radialPos/0.1), 1.0);
	//age *= 1 + extent*0.5;
	
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

uniform mat4 objectToWorld;
uniform mat4 modelview;
uniform mat4 projection;
uniform mat4 VP;

uniform float baseSize;
uniform vec3 faceNormal;
uniform int  boardType;

uniform vec3 gCameraPos;
uniform vec3 gVertical;

uniform int  showHead;
uniform float life2;

uniform AgeParamSettings sizeSettings;
uniform AgeParamSettings colorSettings;
uniform AgeParamSettings transparencySettings;


in vec3 position0[];
in float age0[];
in float randVal0[];
in float rotation0[];
in vec3 velocity0[];
in vec3 pipePosition0[];
in float type0[];
in float monther_age0[];

out float age;
out vec2 TexCoord;
out float transparency;
out vec3 Color;
out vec3 CenterPos;
out float Radius;
out float RandVal;


void main() 
{
	int par_type = int(type0[0]/10000+0.001);
	if(par_type == 0) par_type = 1;
	
	//·¢ÉäÁ£×Ó
	if(par_type == 1 || par_type == 2 && showHead == 0 && life2 > 1e-6) return;
	
	age = age0[0];
	vec3  Pos = (objectToWorld * vec4(position0[0], 1)).xyz;
	float randVal = randVal0[0];
	vec3 velo = (objectToWorld * vec4(velocity0[0], 0)).xyz;

	RandVal = randVal0[0];
	
	
	float sizeFactor;
	if(sizeSettings.m_count == 0) sizeFactor = 1.0;
	else sizeFactor = GetParamSettinsValue(sizeSettings, age, pipePosition0[0].y, randVal).x;
	
	if(transparencySettings.m_count == 0) transparency = 1.0;
	else transparency = GetParamSettinsValue(transparencySettings, age, pipePosition0[0].y, randVal).x;

	if(par_type == 3){
		transparency = GetParamSettinsValue(transparencySettings, monther_age0[0] + age, pipePosition0[0].y, randVal).x;
	}
	
	
	if(colorSettings.m_count == 0) Color = vec3(1.0, 1.0, 1.0);
	else Color = GetParamSettinsValue(colorSettings, age, pipePosition0[0].y, randVal);

	
	float size = baseSize * sizeFactor;

	CenterPos = Pos;
	Radius = size;
	
	vec3 toCamera = normalize(gCameraPos - Pos);
    vec3 up = gVertical;
    vec3 right = normalize(cross(toCamera, up));
    
    if(boardType == 2) up = -normalize(velo) * 1.0;
   
    if(boardType == 0){
    
		mat4 rotMat;
		float angleRad = rotation0[0]*PI / 180.0;
		rotMat[0] = vec4( cos(angleRad), sin(angleRad), 0.0, 0 );
		rotMat[1] = vec4( -sin(angleRad), cos(angleRad), 0.0,0 );
		rotMat[2] = vec4( 0.0, 0.0, 1.0, 0 );
		rotMat[3] = vec4( 0.0, 0.0, 0.0, 1.0 );
   
		Pos = (modelview * vec4(Pos, 1.0)).xyz;
		
		right = normalize((rotMat * vec4(-1, 0, 0, 0)).xyz);
		up = normalize((rotMat * vec4(0, 1, 0, 0)).xyz);
		
		Pos -= right * 0.5 * size;
		Pos -= up * 0.5 * size;
		gl_Position = projection * vec4(Pos, 1.0);
		TexCoord = vec2(1.0, 0.0);
		EmitVertex();
	    
		Pos += up * size;
		gl_Position = projection * vec4(Pos, 1.0);
		TexCoord = vec2(1.0, 1.0);
		EmitVertex();
	    
		Pos -= up * size;
		Pos += right * size;
		gl_Position = projection * vec4(Pos, 1.0);
		TexCoord = vec2(0.0, 0.0);
		EmitVertex();
	    
		Pos += up * size;
		gl_Position = projection * vec4(Pos, 1.0);
		TexCoord = vec2(0.0, 1.0);
		EmitVertex();
		EndPrimitive();
    }
    else if(boardType <= 2){
		Pos -= right * 0.5 * size;
		Pos -= up * 0.5 * size;
		gl_Position = VP * vec4(Pos, 1.0);
		TexCoord = vec2(1.0, 0.0);
		EmitVertex();
	    
		Pos += up * size * 10;
		gl_Position = VP * vec4(Pos, 1.0);
		TexCoord = vec2(1.0, 1.0);
		EmitVertex();
	    
		Pos -= up * size * 10;
		Pos += right * size;
		gl_Position = VP * vec4(Pos, 1.0);
		TexCoord = vec2(0.0, 0.0);
		EmitVertex();
	    
		Pos += up * size * 10;
		gl_Position = VP * vec4(Pos, 1.0);
		TexCoord = vec2(0.0, 1.0);
		EmitVertex();
		EndPrimitive();
	}
	else if(boardType == 3){
		Pos -= right * 0.5 * size;
		Pos -= up * 0.5 * size;
		gl_Position = VP * vec4(Pos, 1.0);
		TexCoord = vec2(1.0, 0.0);
		EmitVertex();
	    
		Pos += up * size;
		gl_Position = VP * vec4(Pos, 1.0);
		TexCoord = vec2(1.0, 1.0);
		EmitVertex();
	    
		Pos -= up * size;
		Pos += right * size;
		gl_Position = VP * vec4(Pos, 1.0);
		TexCoord = vec2(0.0, 0.0);
		EmitVertex();
	    
		Pos += up * size;
		gl_Position = VP * vec4(Pos, 1.0);
		TexCoord = vec2(0.0, 1.0);
		EmitVertex();
		EndPrimitive();
	}

}
