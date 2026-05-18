#version 330 core

layout (location = 0) in vec3 Vertex;
layout (location = 1) in vec3 Normal;
layout (location = 2) in vec3 Color;
layout (location = 3) in vec2 TexCoord;


uniform mat4 gMvp;
uniform mat4 modelToWorld;

out vec2 oTexcoord0;

out vec3 worldP0;

out vec3 vColor0;
out vec3 vPosition0;
out vec3 vNormal0;

out vec3 vibration;


struct VolumeTexture
{
	vec3 boundMin;
	vec3 boundMax;
	float blend;
	sampler3D texture;
};

uniform VolumeTexture volumeTex;

vec4 GetVolumeData(vec3 P, VolumeTexture vt)
{
	vec3 len = vt.boundMax - vt.boundMin;
	vec3 uvw = (P - vt.boundMin) / len;
	if( abs(uvw.x) > 1 || abs(uvw.y) > 1 || abs(uvw.z) > 1 ) return vec4(0);

	return texture(vt.texture, uvw);
}


void main() 
{

	vec3 dP = GetVolumeData(Vertex, volumeTex).xyz;
   vibration = vec3(0);//((gMvp * modelToWorld) * vec4(dP, 0.0)).xyz;

  gl_Position = (gMvp * modelToWorld) * vec4(Vertex.xyz+dP, 1.0);
 
  oTexcoord0 = TexCoord;

  vPosition0 = Vertex+dP;
  vNormal0 = Normal;
  vColor0 = Color;

   worldP0 = (modelToWorld * vec4(Vertex+dP, 1.0)).xyz;

   
}
