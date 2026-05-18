#version 330
#extension GL_EXT_gpu_shader4 : enable

const float PI = 3.1415926535897932384626433832795;

#define MAX_VALUE 1073741824

layout (points) in;
layout (triangle_strip, max_vertices = 100) out;


in vec3 vertex0[];

out vec4 vertexColor;

uniform mat4 objectToWorld;
uniform mat4 gMVP;

uniform float gStep;
uniform float gArrowSize;

struct ColorSetting
{
	float value;
	vec4 color;
};


uniform ColorSetting colorSettings[32];
uniform	int colorSettingCount;


uniform vec4 clipPlanes[3];
uniform int clipPlaneCount;

struct VolumeTexture
{
	vec3 boundMin;
	vec3 boundMax;
	float blend;
	sampler3D texture;
	int dimension;
};

uniform VolumeTexture volumeTex;

vec3 GetVolumeData(vec3 P, VolumeTexture vt)
{
	vec3 len = vt.boundMax - vt.boundMin;
	vec3 uvw = (P - vt.boundMin) / len;
	if( uvw.x > 1 || uvw.y > 1 || uvw.z > 1 || uvw.x < 0  || uvw.y < 0 || uvw.z < 0 ) return vec3(0);

	vec3 dP = texture(vt.texture, uvw).xyz;

	if(dP.x < -MAX_VALUE/10000) return vec3(0);

	return dP;
}

vec4 GetVolumeColor(vec3 P, VolumeTexture vt)
{
	if(colorSettingCount == 0) return vec4(0);

	vec3 len = vt.boundMax - vt.boundMin;
	vec3 uvw = (P - vt.boundMin) / len;
	if( uvw.x > 1 || uvw.y > 1 || uvw.z > 1 || uvw.x < 0  || uvw.y < 0 || uvw.z < 0 ) return vec4(0);

	vec3 data = texture(vt.texture, uvw).xyz;
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


vec3 erot(vec3 p, vec3 ax, float ro) {

	return mix(dot(ax, p)*ax, p, cos(ro)) + cross(ax, p)*sin(ro);

}

vec3 PointRotateAroudAxis(vec3 point, vec3 pos, vec3 axis, float angle)
{
	vec3 p = point - pos;
	return erot(p, axis, angle) + pos;
}

float TestPlane(vec3 point, vec4 plane)
{
	return dot(point, plane.xyz) + plane.w;
}

vec3 MakeOrtho(vec3 n)
{
	vec3 v;
	float maxv = abs(n[0]);
	int mi=0;
	for(int i=1; i<3; i++)
	{
		if(abs(n[i]) > maxv){
			maxv = abs(n[i]);	mi = i;
		}
	}

	if(mi == 0)	{
		v[0] = -n[1]/n[0] - n[2]/n[0]; 	v[1] = 1.0;   	v[2] = 1.0;
	}
	else if(mi == 1)	{
		v[1] = -n[0]/n[1] - n[2]/n[1];    	v[0] = 1.0;    	v[2] = 1.0;
	}
	else if(mi == 2)	{
		v[2] = -n[0]/n[2] - n[1]/n[2];    	v[0] = 1.0;    	v[1] = 1.0;
	}
	
	return normalize(v);
}


void main() 
{
	vec3 P = vertex0[0];
	for(int k=0; k<100; k++){

		vec3 D = GetVolumeData(P, volumeTex);
		vec3 Di = normalize(D);

		if( k%20 == 0 ){

			vec4 worldP = objectToWorld * vec4(P, 1.0);

			if(clipPlaneCount > 0){
				if(TestPlane(P, clipPlanes[0]) < 0){
					float len = length(D);
					if( len < 0.0001 ) break;
					P += Di * gStep;
					continue;
				}
			}

			vertexColor = GetVolumeColor(P, volumeTex);
			vec3 binormal =	MakeOrtho(Di);

			vec3 O;
			if(gStep < 0)
				//O =  P + Di*gStep;
				O =  P + Di*gArrowSize * 5;
			else
				//O =  P - Di*gStep;
				O =  P - Di*gArrowSize * 5;;

			//vec3 P1 = O + binormal*gStep/5;
			vec3 P1 = O + binormal*gArrowSize;
		
			vec3 P0, P2;

			int num = 4;
			float angle = 360 / num * PI / 180.0;

			for(int i=0; i<num; i++){
				
				P2 = PointRotateAroudAxis(P1, O, Di, angle);

				gl_Position = gMVP * (objectToWorld * vec4(P, 1.0));	
				EmitVertex();
				gl_Position = gMVP * (objectToWorld * vec4(P1, 1.0));	
				EmitVertex();
				gl_Position = gMVP * (objectToWorld * vec4(P2, 1.0));	
				EmitVertex();
				EndPrimitive();

				if(i == 0){
					P0 = P1;
				}
				else {
					gl_Position = gMVP * (objectToWorld * vec4(P2, 1.0));	
					EmitVertex();
					gl_Position = gMVP * (objectToWorld * vec4(P1, 1.0));	
					EmitVertex();
					gl_Position = gMVP * (objectToWorld * vec4(P0, 1.0));	
					EmitVertex();
					EndPrimitive();
				}
				P1 = P2;
			}

			
			
		}

		
		float len = length(D);
		if( len < 0.0001 ) break;

		P += Di * gStep;
	}
}

