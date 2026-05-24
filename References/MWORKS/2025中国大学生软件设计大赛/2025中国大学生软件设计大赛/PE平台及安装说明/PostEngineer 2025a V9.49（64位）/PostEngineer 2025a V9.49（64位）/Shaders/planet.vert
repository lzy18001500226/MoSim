#version 330 core

layout (location = 0) in vec3 Vertex;
layout (location = 1) in vec3 Normal;
layout (location = 2) in vec3 Color;
layout (location = 3) in vec2 TexCoord;
layout (location = 4) in vec2 TexCoord2;
layout (location = 5) in vec2 TexCoord3;


uniform vec3 eyePositionLocal;
uniform vec3 v3SunPos;
uniform mat4 worldToModel;
uniform mat4 modelToWorld;
uniform mat4 texMatrix;
uniform mat4 texMatrix1;

uniform mat4 cameraConvertMatrixInverse;

uniform mat4 gMvp;

varying vec3 v3Pos;
varying float fCameraHeight;
varying float fCameraHeight2;
varying vec3 v3Direction;
varying vec3 v3LightDirection;
varying vec2 oTexcoord0;
varying vec2 oTexcoord1;

void main()
{
	v3Pos = Vertex;//gl_Vertex.xyz;
	fCameraHeight = length(eyePositionLocal);
	fCameraHeight2 = fCameraHeight * fCameraHeight;
	v3Direction = normalize(Vertex);
	v3LightDirection = normalize((worldToModel * cameraConvertMatrixInverse * vec4(v3SunPos, 1)).xyz);
	oTexcoord0 = (texMatrix * vec4(TexCoord, 0, 1)).xy;
	oTexcoord1 = (texMatrix1 * vec4(TexCoord2, 0, 1)).xy;
	
	//gl_Position = ftransform();
	gl_Position = (gMvp * modelToWorld) * vec4(Vertex.xyz, 1.0);
} 
