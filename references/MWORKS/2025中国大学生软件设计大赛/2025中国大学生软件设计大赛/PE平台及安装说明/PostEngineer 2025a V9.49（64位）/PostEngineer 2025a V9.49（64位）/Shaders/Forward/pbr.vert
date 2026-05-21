#version 330 core

layout (location = 0) in vec3 Vertex;
layout (location = 1) in vec3 Normal;
layout (location = 2) in vec3 Color;
layout (location = 3) in vec2 TexCoord;
layout (location = 4) in vec2 TexCoord2;
layout (location = 5) in vec2 TexCoord3;

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



uniform mat4 gMvp;
uniform mat4 modelToWorld;

//uniform vec3 globalAmbient;
//uniform vec3 eyePositionLocal;
//uniform vec3 eyePositionW;

uniform mat4 texMatrix;
uniform mat4 texMatrix1;
uniform mat4 texMatrix2;


uniform mat4 texMatrixSpec;
uniform mat4 texMatrixNorm;
uniform mat4 texMatrixAO;

//uniform int multiTexCount;

//uniform int shadowMapEnable;
//uniform mat4 shadowProjMatrix;
//out vec4 lightSpacePos;

uniform int flag;

//uniform int reflectMapEnable;
//uniform mat4 reflectProjMatrix;
//out vec4 reflectTexCoord;


//uniform int projectorEnable;
//uniform mat4 projectorProjMatrix;
//out vec4 projectorTexCoord;



//out vec2 oTexcoordOrigin;
out vec2 oTexcoord0;
//out vec2 oTexcoord1;
//out vec2 oTexcoord2;


uniform int texCoordIndexSpec;
uniform int texCoordIndexNorm;
uniform int texCoordIndexAO;


out vec2 oTexcoordSpec;
out vec2 oTexcoordNorm;
//out vec2 oTexcoordAO;

//out vec3 halfAngle;
//out vec3 normalLocal;
//out vec3 normalWorld;

//out vec3 I_World;
//out vec3 I_Local;
/*out vec3 tangent;
out vec3 binormal;*/

out vec4 oColor;

out vec3 worldP;
out vec3 worldN;
out vec3 worldP_no_offset;


/*uniform float heightFactor;
uniform sampler2D heightMap1;
uniform sampler2D heightMap2;
uniform sampler2D normalMap1;
uniform sampler2D normalMap2;*/

out vec3 vPosition;
out vec3 vNormal;
//out vec3 vTangent;

void main() {
  
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

  //if(texCoordIndexAO == 0) oTexcoordAO = (texMatrixAO * vec4(TexCoord.xy, 0, 1)).xy;
  //if(texCoordIndexAO == 1) oTexcoordAO = (texMatrixAO * vec4(TexCoord2.xy, 0, 1)).xy;
  //if(texCoordIndexAO == 2) oTexcoordAO = (texMatrixAO * vec4(TexCoord3.xy, 0, 1)).xy;
 
   worldP = (modelToWorld * vec4(Vertex+dP, 1.0)).xyz;
   worldP_no_offset = (modelToWorld * vec4(Vertex, 1.0)).xyz;

  vPosition = Vertex;
  vNormal = Normal;
  oColor.rgb = Color;
  
  worldN = normalize((modelToWorld * vec4(Normal, 0)).xyz);
}
