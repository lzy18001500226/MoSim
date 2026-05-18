#version 330
#extension GL_EXT_gpu_shader4 : enable


layout (points) in;
layout (line_strip) out;
layout (max_vertices = 1000) out;

#define MAX_VALUE 1073741824

in vec3 vertex0[];

out vec4 vertexColor;

uniform mat4 objectToWorld;
uniform mat4 gMVP;

uniform float gStep;

uniform vec4 clipPlanes[3];
uniform int clipPlaneCount;

struct ColorSetting
{
	float value;
	vec4 color;
};


uniform ColorSetting colorSettings[32];
uniform	int colorSettingCount;

/*struct VolumeTexture
{
	vec3 boundMin;
	vec3 boundMax;
	float blend;
	sampler3D texture;
	int dimension;
};*/

struct VolumeTexture
{
	vec3 boundMin;
	vec3 boundMax;
	float factor;
	mat4 transform;
	mat4 transformToObject;
	sampler3D texture;
	sampler3D textureOld;
	int dimension;
};

uniform VolumeTexture volumeTex;

/*vec3 GetVolumeData(vec3 P, VolumeTexture vt)
{
	vec3 len = vt.boundMax - vt.boundMin;
	vec3 uvw = (P - vt.boundMin) / len;
	if( uvw.x > 1 || uvw.y > 1 || uvw.z > 1 || uvw.x < 0  || uvw.y < 0 || uvw.z < 0 ) return vec3(0);

	return texture(vt.texture, uvw).xyz;
}*/

vec4 GetVolumeData(vec3 P, VolumeTexture vt)
{
	vec3 localP = (vt.transform * vec4(P, 1)).xyz;

	vec3 len = vt.boundMax - vt.boundMin;
	vec3 uvw = (localP - vt.boundMin) / len;

	if( uvw.x > 1 || uvw.y > 1 || uvw.z > 1 || uvw.x < 0  || uvw.y < 0 || uvw.z < 0 ) return vec4(0);

	vec4 dP;
	if(vt.factor > -0.000001){
		dP = texture(vt.textureOld, uvw) *(1 - vt.factor) + texture(vt.texture, uvw) * vt.factor;
	}
	else
		dP = texture(vt.texture, uvw);

	return vt.transformToObject * vec4(dP.xyz, 0);
}


vec4 GetVolumeDataLocal(vec3 localP, VolumeTexture vt)
{
	vec3 len = vt.boundMax - vt.boundMin;
	vec3 uvw = (localP - vt.boundMin) / len;

	if( uvw.x > 1 || uvw.y > 1 || uvw.z > 1 || uvw.x < 0  || uvw.y < 0 || uvw.z < 0 ) return vec4(0);

	vec4 dP;
	if(vt.factor > -0.000001){
		dP = texture(vt.textureOld, uvw) *(1 - vt.factor) + texture(vt.texture, uvw) * vt.factor;
	}
	else
		dP = texture(vt.texture, uvw);

	if(dP.x < -MAX_VALUE/10000) return vec4(0);

	return vec4(dP.xyz, 0);
}

vec4 GetVolumeColor(vec3 P, VolumeTexture vt)
{
	if(colorSettingCount == 0) return vec4(0);

	vec3 len = vt.boundMax - vt.boundMin;
	vec3 uvw = (P - vt.boundMin) / len;
	if( uvw.x > 1 || uvw.y > 1 || uvw.z > 1 || uvw.x < 0  || uvw.y < 0 || uvw.z < 0 ) return vec4(0);

	//vec3 data = texture(vt.texture, uvw).xyz;
	vec3 data = GetVolumeDataLocal(P, vt).xyz;
	float data_val = length(data);

	int i;
	for(i=0; i<colorSettingCount; i++){
		if( data_val < colorSettings[i].value) break;
	}

	if( i==0 ) 
		return colorSettings[0].color;
	else if(i == colorSettingCount) 
		return colorSettings[colorSettingCount-1].color;
	else{
		float factor = (data_val - colorSettings[i-1].value) / (colorSettings[i].value - colorSettings[i-1].value);

		return colorSettings[i-1].color*(1-factor) + colorSettings[i].color*factor;
	}
}


float TestPlane(vec3 point, vec4 plane)
{
	return dot(point, plane.xyz) + plane.w;
}



void main() 
{
	const float EPS = 1e-12;
	vec3 P = vertex0[0];
	for(int k=0; k<100; k++){

		vec3 D = GetVolumeDataLocal(P, volumeTex).xyz;
		vec4 worldP = objectToWorld * vec4(P, 1.0);

		if(clipPlaneCount > 0){
			if(TestPlane(P, clipPlanes[0]) < 0){
				float len = length(D);
				if( len < EPS ) break;

				//if(len < gStep)
				if(abs(gStep) > 1e-6)
					P += normalize(D) * gStep;
				else
					P += D;

				EndPrimitive();
				continue;
			}
		}
	
		gl_Position = gMVP * worldP;	
		vertexColor = GetVolumeColor(P, volumeTex);
		EmitVertex();

		float len = length(D);
		if( len < EPS ) break;

		//if(len < gStep)
		if(abs(gStep) > 1e-6)
			P += normalize(D) * gStep;
		else
			P += D;
	}

	EndPrimitive();
}

