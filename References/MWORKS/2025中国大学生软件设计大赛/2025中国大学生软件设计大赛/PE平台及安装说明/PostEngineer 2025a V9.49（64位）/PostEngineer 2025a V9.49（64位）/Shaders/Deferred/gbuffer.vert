#version 330 core

layout (location = 0) in vec3 Vertex;
layout (location = 1) in vec3 Normal;
layout (location = 2) in vec3 Color;
layout (location = 3) in vec2 TexCoord;
layout (location = 4) in vec2 TexCoord2;
layout (location = 5) in vec2 TexCoord3;



layout(std140) uniform GBufferMatrix
{
	mat4 modelToWorld;
	vec3 modelToWorld_extra;
	mat4 modelToWorldPrev;
	vec3 modelToWorldPrev_extra;

	mat4 gMvp;
	vec3 gMvp_extra;
	mat4 gMvpPrev;
	vec3 gMvpPrev_extra;

	mat4 gMvpNoJitter;
	vec3 gMvpNoJitter_extra;
	mat4 gMvpPrevNoJitter;
	vec3 gMvpPrevNoJitter_extra;

	mat4 texMatrix;
	mat4 texMatrixSpec;
	mat4 texMatrixNorm;
	mat4 texMatrixAO;

	int texCoordIndexSpec;
	int texCoordIndexNorm;
	int texCoordIndexAO;
	int texCoordIndex2;
	int texCoordIndex3;
	mat4 texMatrix2;
	mat4 texMatrix3;
};


//uniform mat4 texMatrix;
/*uniform mat4 texMatrixSpec;
uniform mat4 texMatrixNorm;
uniform mat4 texMatrixAO;

uniform int texCoordIndexSpec;
uniform int texCoordIndexNorm;
uniform int texCoordIndexAO;*/


/*
uniform mat4 modelToWorld;
uniform mat4 modelToWorldPrev;

uniform mat4 gMvp;
uniform mat4 gMvpPrev;

uniform mat4 gMvpNoJitter;
uniform mat4 gMvpPrevNoJitter;*/

out vec3 vPosition_0;
out vec3 vNormal_0;
out vec3 vColor_0;
out vec3 vVertex_0;

out vec4 ClipSpacePos0_0;
out vec4 PrevClipSpacePos0_0;

out vec2 vTexcoordPrimitive_0;
out vec2 vTexcoord_0;
out vec2 vTexcoord2_0;
out vec2 vTexcoord3_0;
out vec2 vTexcoordSpec_0;
out vec2 vTexcoordNorm_0;
out vec2 vTexcoordAO_0;

void main() 
{
  
  //ClipSpacePos0 = ((gMvpNoJitter * modelToWorld) * vec4(Vertex.xyz, 1.0));
  //PrevClipSpacePos0 = ((gMvpPrevNoJitter * modelToWorldPrev) * vec4(Vertex.xyz, 1.0));

  vec4 worldPos = modelToWorld * vec4(Vertex.xyz, 1.0) + vec4(modelToWorld_extra, 0);
  vec4 worldPosPrev = modelToWorldPrev * vec4(Vertex.xyz, 1.0) + vec4(modelToWorldPrev_extra, 0);

  ClipSpacePos0_0 = gMvpNoJitter * worldPos + vec4(gMvpNoJitter_extra, 0);
  PrevClipSpacePos0_0 = gMvpPrevNoJitter * worldPosPrev + vec4(gMvpPrevNoJitter_extra, 0);
  
  //gl_Position = ((gMvp * modelToWorld) * vec4(Vertex.xyz, 1.0));

  gl_Position = gMvp * worldPos + vec4(gMvp_extra, 0);
 

	///2023-2-25, wxg
  
  /*vTexcoord = (texMatrix * vec4(TexCoord.xy, 0, 1)).xy;
  
 // vTexcoordNorm = vTexcoord;

  if(texCoordIndexNorm == 0) vTexcoordNorm = (texMatrixNorm * vec4(TexCoord.xy, 0, 1)).xy;
  if(texCoordIndexNorm == 1) vTexcoordNorm = (texMatrixNorm * vec4(TexCoord2.xy, 0, 1)).xy;
  if(texCoordIndexNorm == 2) vTexcoordNorm = (texMatrixNorm * vec4(TexCoord3.xy, 0, 1)).xy;

  if(texCoordIndexSpec == 0) vTexcoordSpec = (texMatrixSpec * vec4(TexCoord.xy, 0, 1)).xy;
  if(texCoordIndexSpec == 1) vTexcoordSpec = (texMatrixSpec * vec4(TexCoord2.xy, 0, 1)).xy;
  if(texCoordIndexSpec == 2) vTexcoordSpec = (texMatrixSpec * vec4(TexCoord3.xy, 0, 1)).xy;

  if(texCoordIndexAO == 0) vTexcoordAO = (texMatrixAO * vec4(TexCoord.xy, 0, 1)).xy;
  if(texCoordIndexAO == 1) vTexcoordAO = (texMatrixAO * vec4(TexCoord2.xy, 0, 1)).xy;
  if(texCoordIndexAO == 2) vTexcoordAO = (texMatrixAO * vec4(TexCoord3.xy, 0, 1)).xy;
  */

  vTexcoordPrimitive_0 = TexCoord;

  vTexcoord_0 = (texMatrix * vec4(TexCoord.xy, 0, 1)).xy;

  if(texCoordIndex2 == 0)vTexcoord2_0 = (texMatrix2 * vec4(TexCoord.xy, 0, 1)).xy;
  else if(texCoordIndex2 == 1)vTexcoord2_0 = (texMatrix2 * vec4(TexCoord2.xy, 0, 1)).xy;
  else if(texCoordIndex2 == 2)vTexcoord2_0 = (texMatrix2 * vec4(TexCoord3.xy, 0, 1)).xy;

  if(texCoordIndex3 == 0)vTexcoord3_0 = (texMatrix3 * vec4(TexCoord.xy, 0, 1)).xy;
  else if(texCoordIndex3 == 1)vTexcoord3_0 = (texMatrix3 * vec4(TexCoord2.xy, 0, 1)).xy;
  else if(texCoordIndex3 == 2)vTexcoord3_0 = (texMatrix3 * vec4(TexCoord3.xy, 0, 1)).xy;
  

  if(texCoordIndexNorm == 0) vTexcoordNorm_0 = (texMatrixNorm * vec4(TexCoord.xy, 0, 1)).xy;
  else if(texCoordIndexNorm == 1) vTexcoordNorm_0 = (texMatrixNorm * vec4(TexCoord2.xy, 0, 1)).xy;
  else if(texCoordIndexNorm == 2) vTexcoordNorm_0 = (texMatrixNorm * vec4(TexCoord3.xy, 0, 1)).xy;

  if(texCoordIndexSpec == 0) vTexcoordSpec_0 = TexCoord.xy;
  else if(texCoordIndexSpec == 1) vTexcoordSpec_0 = TexCoord2.xy;
  else if(texCoordIndexSpec == 2) vTexcoordSpec_0 = TexCoord3.xy;

  if(texCoordIndexAO == 0) vTexcoordAO_0 = TexCoord.xy;
  else if(texCoordIndexAO == 1) vTexcoordAO_0 = TexCoord2.xy;
  else if(texCoordIndexAO == 2) vTexcoordAO_0 = TexCoord3.xy;
 
  //vPosition = (modelToWorld * vec4(Vertex, 1.0)).xyz;
  vPosition_0 = worldPos.xyz;
  vVertex_0 = Vertex.xyz;

  vNormal_0 = normalize((modelToWorld * vec4(Normal, 0)).xyz);

  vColor_0 = Color;
}
