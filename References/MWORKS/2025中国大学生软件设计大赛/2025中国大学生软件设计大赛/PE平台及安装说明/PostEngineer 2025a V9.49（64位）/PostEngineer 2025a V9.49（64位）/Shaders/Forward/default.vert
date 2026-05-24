#version 330 core

layout (location = 0) in vec3 Vertex;
layout (location = 1) in vec3 Normal;
layout (location = 2) in vec3 Color;
layout (location = 3) in vec2 TexCoord;
layout (location = 4) in vec2 TexCoord2;
layout (location = 5) in vec2 TexCoord3;

//uniform mat4 modelview;
//uniform mat4 projection;
uniform mat4 gMvp;
uniform mat4 modelToWorld;


uniform mat4 texMatrix;
uniform mat4 texMatrix1;
uniform mat4 texMatrix2;


uniform mat4 texMatrixSpec;
uniform mat4 texMatrixNorm;
uniform mat4 texMatrixAO;

uniform int multiTexCount;

uniform int projectorEnable;
uniform mat4 projectorProjMatrix;
varying vec4 projectorTexCoord_0;


uniform int flag;

uniform int texCoordIndexSpec;
uniform int texCoordIndexNorm;
uniform int texCoordIndexAO;



out vec2 oTexcoord0_0;
out vec2 oTexcoord1_0;
out vec2 oTexcoord2_0;

out vec2 oTexcoordSpec_0;
out vec2 oTexcoordNorm_0;
out vec2 oTexcoordAO_0;


out vec3 worldP_0;
out vec3 worldP_no_offset_0;

out vec3 vColor_0;
out vec3 vPosition_0;
out vec3 vNormal_0;


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

uniform VolumeTexture volumeTexVector;

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


bool bit_and(int val, int ref) {
  if(val == 0) return false;

  return (val/ref) % 2 != 0;
}


void main() {
  //gl_Position = projection * modelview * modelToWorld * vec4(Vertex.xyz, 1.0);

  vec3 dP = vec3(0);
  
  if (bit_and(flag, 0x40000) == true && volumeTexVector.dimension >= 3) {
	vec4 pos = modelToWorld * vec4(Vertex.xyz, 1.0);
	dP = GetVolumeData(pos.xyz, volumeTexVector).xyz;
  }

  gl_Position = (gMvp * modelToWorld) * vec4(Vertex.xyz+dP, 1.0);
 
  oTexcoord0_0 = (texMatrix * vec4(TexCoord.xy, 0, 1)).xy;

  if(texCoordIndexNorm == 0) oTexcoordNorm_0 = (texMatrixNorm * vec4(TexCoord.xy, 0, 1)).xy;
  if(texCoordIndexNorm == 1) oTexcoordNorm_0 = (texMatrixNorm * vec4(TexCoord2.xy, 0, 1)).xy;
  if(texCoordIndexNorm == 2) oTexcoordNorm_0 = (texMatrixNorm * vec4(TexCoord3.xy, 0, 1)).xy;

  if(texCoordIndexSpec == 0) oTexcoordSpec_0 = (texMatrixSpec * vec4(TexCoord.xy, 0, 1)).xy;
  if(texCoordIndexSpec == 1) oTexcoordSpec_0 = (texMatrixSpec * vec4(TexCoord2.xy, 0, 1)).xy;
  if(texCoordIndexSpec == 2) oTexcoordSpec_0 = (texMatrixSpec * vec4(TexCoord3.xy, 0, 1)).xy;

  if(texCoordIndexAO == 0) oTexcoordAO_0 = (texMatrixAO * vec4(TexCoord.xy, 0, 1)).xy;
  if(texCoordIndexAO == 1) oTexcoordAO_0 = (texMatrixAO * vec4(TexCoord2.xy, 0, 1)).xy;
  if(texCoordIndexAO == 2) oTexcoordAO_0 = (texMatrixAO * vec4(TexCoord3.xy, 0, 1)).xy;
  
  if(projectorEnable != 0){
	projectorTexCoord_0 = projectorProjMatrix * (modelToWorld * vec4(Vertex.xyz, 1.0));

	projectorTexCoord_0.x /= projectorTexCoord_0.w;
	projectorTexCoord_0.y /= projectorTexCoord_0.w;
	projectorTexCoord_0.z /= projectorTexCoord_0.w;

	projectorTexCoord_0.w = 1.0;

  }	
  

  vPosition_0 = Vertex+dP;
  vNormal_0 = normalize(Normal);
  vColor_0 = Color;

  worldP_0 = (modelToWorld * vec4(Vertex+dP, 1.0)).xyz;
  worldP_no_offset_0 = (modelToWorld * vec4(Vertex, 1.0)).xyz;
}
