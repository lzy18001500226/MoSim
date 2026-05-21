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
	mat4 modelToWorldPrev;

	mat4 gMvp;
	mat4 gMvpPrev;

	mat4 gMvpNoJitter;
	mat4 gMvpPrevNoJitter;

	mat4 texMatrix;
	mat4 texMatrixSpec;
	mat4 texMatrixNorm;
	mat4 texMatrixAO;

	int texCoordIndexSpec;
	int texCoordIndexNorm;
	int texCoordIndexAO;
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

out vec3 vPosition;
out vec3 vNormal;
out vec3 vColor;

out vec4 ClipSpacePos0;
out vec4 PrevClipSpacePos0;

out vec2 vTexcoord;
out vec2 vTexcoordSpec;
out vec2 vTexcoordNorm;
out vec2 vTexcoordAO;


void main() 
{
  
  ClipSpacePos0 = ((gMvpNoJitter * modelToWorld) * vec4(Vertex.xyz, 1.0));
  PrevClipSpacePos0 = ((gMvpPrevNoJitter * modelToWorldPrev) * vec4(Vertex.xyz, 1.0));
  
  gl_Position = ((gMvp * modelToWorld) * vec4(Vertex.xyz, 1.0));
 
  
  vTexcoord = (texMatrix * vec4(TexCoord.xy, 0, 1)).xy;
  
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
 
  vPosition = (modelToWorld * vec4(Vertex, 1.0)).xyz;
  
  ///变换矩阵可能存在缩放，所以需要归一化
  vNormal = normalize((modelToWorld * vec4(Normal, 0)).xyz);
  vColor = Color;
}
