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


out vec3 vPosition;
out vec3 vNormal;
out vec3 vColor;


out vec2 vTexcoord;
out vec2 vTexcoord2;
out vec2 vTexcoord3;
out vec2 vTexcoordSpec;
out vec2 vTexcoordNorm;
out vec2 vTexcoordAO;


void main() 
{
  
  vec4 worldPos = modelToWorld * vec4(Vertex.xyz, 1.0) + vec4(modelToWorld_extra, 0);
  vec4 worldPosPrev = modelToWorldPrev * vec4(Vertex.xyz, 1.0) + vec4(modelToWorldPrev_extra, 0);

  
  gl_Position = gMvp * worldPos + vec4(gMvp_extra, 0);

  //gl_Position = gMvpTest * vec4(Vertex.xyz, 1.0);  // for test
 

	///2023-2-25, wxg, 各纹理可选择不同的通道，共三个通道；同时漫反射纹理还可重复，法线纹理一同重复

  vTexcoord = (texMatrix * vec4(TexCoord.xy, 0, 1)).xy;

  if(texCoordIndex2 == 0)vTexcoord2 = (texMatrix2 * vec4(TexCoord.xy, 0, 1)).xy;
  else if(texCoordIndex2 == 1)vTexcoord2 = (texMatrix2 * vec4(TexCoord2.xy, 0, 1)).xy;
  else if(texCoordIndex2 == 2)vTexcoord2 = (texMatrix2 * vec4(TexCoord3.xy, 0, 1)).xy;

  if(texCoordIndex3 == 0)vTexcoord3 = (texMatrix2 * vec4(TexCoord.xy, 0, 1)).xy;
  else if(texCoordIndex3 == 1)vTexcoord3 = (texMatrix2 * vec4(TexCoord2.xy, 0, 1)).xy;
  else if(texCoordIndex3 == 2)vTexcoord3 = (texMatrix3 * vec4(TexCoord3.xy, 0, 1)).xy;
  

  if(texCoordIndexNorm == 0) vTexcoordNorm = (texMatrix * vec4(TexCoord.xy, 0, 1)).xy;
  else if(texCoordIndexNorm == 1) vTexcoordNorm = (texMatrix * vec4(TexCoord2.xy, 0, 1)).xy;
  else if(texCoordIndexNorm == 2) vTexcoordNorm = (texMatrix * vec4(TexCoord3.xy, 0, 1)).xy;

  if(texCoordIndexSpec == 0) vTexcoordSpec = TexCoord.xy;
  else if(texCoordIndexSpec == 1) vTexcoordSpec = TexCoord2.xy;
  else if(texCoordIndexSpec == 2) vTexcoordSpec = TexCoord3.xy;

  if(texCoordIndexAO == 0) vTexcoordAO = TexCoord.xy;
  else if(texCoordIndexAO == 1) vTexcoordAO = TexCoord2.xy;
  else if(texCoordIndexAO == 2) vTexcoordAO = TexCoord3.xy;
 
  //vPosition = (modelToWorld * vec4(Vertex, 1.0)).xyz;
  vPosition = worldPos.xyz;
  
  ///变换矩阵可能存在缩放，所以需要归一化
  vNormal = normalize((modelToWorld * vec4(Normal, 0)).xyz);

  vColor = Color;
}
