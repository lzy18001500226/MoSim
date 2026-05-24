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

uniform int shadowMapEnable;
uniform mat4 shadowProjMatrix;
varying vec4 lightSpacePos;

uniform int reflectMapEnable;
uniform mat4 reflectProjMatrix;
varying vec4 reflectTexCoord;


uniform int projectorEnable;
uniform mat4 projectorProjMatrix;
varying vec4 projectorTexCoord;


uniform int flag;


varying vec2 oTexcoordOrigin;
varying vec2 oTexcoord0;
varying vec2 oTexcoord1;
varying vec2 oTexcoord2;


uniform int texCoordIndexSpec;
uniform int texCoordIndexNorm;
uniform int texCoordIndexAO;

varying vec2 oTexcoordSpec;
varying vec2 oTexcoordNorm;
varying vec2 oTexcoordAO;

varying vec3 halfAngle;
varying vec3 normalLocal;
varying vec3 normalWorld;

varying vec3 I_World;
varying vec3 I_Local;
/*varying vec3 tangent;
varying vec3 binormal;*/


varying vec3 worldP;
varying vec3 worldP_no_offset;

varying vec3 vColor;
varying vec3 vPosition;
varying vec3 vNormal;


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
  
  if (bit_and(flag, 0x40000) == true && volumeTex.dimension >= 3) {
	vec4 pos = modelToWorld * vec4(Vertex.xyz, 1.0);
	dP = GetVolumeData(pos.xyz, volumeTex).xyz;
  }

  gl_Position = (gMvp * modelToWorld) * vec4(Vertex.xyz+dP, 1.0);
 
  oTexcoord0 = (texMatrix * vec4(TexCoord.xy, 0, 1)).xy;

  if(texCoordIndexNorm == 0) oTexcoordNorm = (texMatrixNorm * vec4(TexCoord.xy, 0, 1)).xy;
  if(texCoordIndexNorm == 1) oTexcoordNorm = (texMatrixNorm * vec4(TexCoord2.xy, 0, 1)).xy;
  if(texCoordIndexNorm == 2) oTexcoordNorm = (texMatrixNorm * vec4(TexCoord3.xy, 0, 1)).xy;

  if(texCoordIndexSpec == 0) oTexcoordSpec = (texMatrixSpec * vec4(TexCoord.xy, 0, 1)).xy;
  if(texCoordIndexSpec == 1) oTexcoordSpec = (texMatrixSpec * vec4(TexCoord2.xy, 0, 1)).xy;
  if(texCoordIndexSpec == 2) oTexcoordSpec = (texMatrixSpec * vec4(TexCoord3.xy, 0, 1)).xy;

  if(texCoordIndexAO == 0) oTexcoordAO = (texMatrixAO * vec4(TexCoord.xy, 0, 1)).xy;
  if(texCoordIndexAO == 1) oTexcoordAO = (texMatrixAO * vec4(TexCoord2.xy, 0, 1)).xy;
  if(texCoordIndexAO == 2) oTexcoordAO = (texMatrixAO * vec4(TexCoord3.xy, 0, 1)).xy;
  
  if(projectorEnable != 0){
	projectorTexCoord = projectorProjMatrix * (modelToWorld * vec4(Vertex.xyz, 1.0));

	projectorTexCoord.x /= projectorTexCoord.w;
	projectorTexCoord.y /= projectorTexCoord.w;
	projectorTexCoord.z /= projectorTexCoord.w;

	projectorTexCoord.w = 1.0;

  }	
  

  vPosition = Vertex+dP;
  vNormal = normalize(Normal);
  vColor = Color;

  worldP = (modelToWorld * vec4(Vertex+dP, 1.0)).xyz;
  worldP_no_offset = (modelToWorld * vec4(Vertex, 1.0)).xyz;
}
