#version 330 core

layout (location = 0) out vec4 gPositionDepth;   ///Œª÷√+≤ƒ÷ 

uniform mat4 gModelView;
uniform mat4 gProjection;

uniform mat4 modelToWorld;

uniform int gMaterialID;


in vec3 vWorldPos;


void main() 
{
	gPositionDepth.xyz = vWorldPos;
	gPositionDepth.w = gMaterialID;
}
