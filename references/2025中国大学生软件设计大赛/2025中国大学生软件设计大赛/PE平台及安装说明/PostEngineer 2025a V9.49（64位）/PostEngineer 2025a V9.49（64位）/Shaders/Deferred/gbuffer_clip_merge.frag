#version 330 core

layout (location = 0) out vec4 gPositionDepth;   ///位置+线性深度
layout (location = 1) out vec4 gNormal;     ///原始法线+发光亮度
layout (location = 2) out vec4 gDiffuse;    ///漫发射+全局环境亮度
layout (location = 3) out vec4 gSpecular;    ///高光+shininess
layout (location = 4) out vec4 gMaterial;   ///pbr+AO系数或环境系数

uniform sampler2D old_gPositionDepth;
uniform sampler2D old_gNormal;
uniform sampler2D old_gDiffuse;
uniform sampler2D old_gSpecular;
uniform sampler2D old_gMaterial;

uniform sampler2D new_gPositionDepth;
uniform sampler2D new_gNormal;
uniform sampler2D new_gDiffuse;
uniform sampler2D new_gSpecular;
uniform sampler2D new_gMaterial;


in vec2 vUv;



void main() 
{
	vec4 newNormalColor = texture(new_gNormal, vUv);
	if(newNormalColor.w > -0.5){
		gPositionDepth = texture(old_gPositionDepth, vUv);
		gNormal = texture(old_gNormal, vUv);
		gDiffuse = texture(old_gDiffuse, vUv);
		gSpecular = texture(old_gSpecular, vUv);
		gMaterial = texture(old_gMaterial, vUv);
	}
	else{
		gPositionDepth = texture(new_gPositionDepth, vUv);
		gNormal = newNormalColor;
		gDiffuse = texture(new_gDiffuse, vUv);
		gSpecular = texture(new_gSpecular, vUv);
		gMaterial = texture(new_gMaterial, vUv);
	}
}