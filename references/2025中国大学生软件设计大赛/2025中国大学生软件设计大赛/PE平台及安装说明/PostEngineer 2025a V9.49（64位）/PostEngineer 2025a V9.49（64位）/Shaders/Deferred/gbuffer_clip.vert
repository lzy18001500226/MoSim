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


out vec3 vPosition_0;
out vec3 vNormal_0;
out vec3 vColor_0;


void main() 
{
 
  vec4 worldPos = modelToWorld * vec4(Vertex.xyz, 1.0) + vec4(modelToWorld_extra, 0);
  vec4 worldPosPrev = modelToWorldPrev * vec4(Vertex.xyz, 1.0) + vec4(modelToWorldPrev_extra, 0);

  gl_Position = gMvp * worldPos + vec4(gMvp_extra, 0);
 
  vPosition_0 = worldPos.xyz;
  
  ///变换矩阵可能存在缩放，所以需要归一化
  vNormal_0 = normalize((modelToWorld * vec4(Normal, 0)).xyz);

  vColor_0 = Color;
}
