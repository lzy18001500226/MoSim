#version 430
#extension GL_NV_shader_buffer_load : enable
#extension GL_EXT_texture_array : enable

layout (location = 0) out vec4 gColor;
layout (location = 1) out vec4 gAlpha;
layout (location = 2) out vec4 gShadow;   // for test

uniform sampler2DArray particleSamplers;

uniform sampler2D transmit1;
uniform sampler2D transmit2;

uniform vec2 gNearFar;
uniform float gAspect;
uniform float gNearHeight;

uniform float exposure;
uniform float life;
uniform float life2;

uniform int texArraySize;

uniform int screenWidth;
uniform int screenHeight;

uniform int flag;

uniform mat4 gModelViewLight;
uniform mat4 gProjectionLight;
uniform mat4 gModelViewInv;

uniform vec3 gMainLightPos;

in float age;
in vec2 TexCoord;
in float transparency;
in vec3 Color;
in vec3 CenterPos;
in float Radius;
in float RandVal;

struct OitTransmit
{
	float transmit;
	float depth;
};


layout(binding=3, std430) buffer _oit_pixels
{
	// 屏幕分辨率为 1920x1080
	// 最多支持4个透明层，最后一层将固定为不透明像素
	//OitTransmit	oit_pixels[1920*1080*5];
	OitTransmit	oit_pixels[];
};

// 计算当前像素坐标
uint calc_pixel_addr(uvec3 xyz, uvec2 scn_wh, uint max_oit_layer)
{
	uint line_size = max_oit_layer * scn_wh[0];
	uint elem_size = max_oit_layer;
	uint addr = xyz[1] * line_size + xyz[0] * elem_size + xyz[2];
	return addr;
}


float weight(float z, float a) 
{
	return clamp(pow(min(1.0, a * 10.0) + 0.01, 3.0) * 1e8 * pow(1.0 - z * 0.9, 3.0), 1e-2, 3e3);
}


vec3 WorldPosToScreen(vec3 worldP, mat4 modelView, mat4 projection)
{
	//vec3 viewPos = (modelView * vec4(worldP, 1)).xyz;
	//vec4 projPos = projection * vec4(viewPos, 1);

	vec4 projPos = projection * modelView * vec4(worldP, 1);

	projPos.xyz /= projPos.w; // 透视划分
	projPos.xyz = projPos.xyz * 0.5 + 0.5; // 变换到0.0 - 1.0的值域

	return projPos.xyz;
}

//裁剪空间转换为眼空间
vec3 UVToEyePos(vec2 uv, float linear_depth)
{    
	vec2 deltaUV = (2.0 * uv - vec2(1.0)) * vec2(gAspect, 1.0);    
	//计算近平面的平移向量    
	vec2 deltaView = gNearHeight * deltaUV * linear_depth/gNearFar.x;    
	
	return vec3(vec2(deltaView), -linear_depth);
} 

vec3 ScreenToWorldPos(vec3 projPos, mat4 modelViewInv)
{
	vec3 viewPos = UVToEyePos(projPos.xy, projPos.z);
	vec4 worldP = (modelViewInv * vec4(viewPos, 1));

	worldP.xyz /= worldP.w;

	return worldP.xyz;
}


float LinearizeDepth(float depth)
{
    float z = depth * 2.0 - 1.0; // 回到NDC
    return (2.0 * gNearFar.x * gNearFar.y) / (gNearFar.y + gNearFar.x - z * (gNearFar.y - gNearFar.x));    
}


float CalcShadow(vec3 samplePos)
{
	float shadow = 1.0;	
	const uint max_oit_layer = 4;
	uint pix_addr = calc_pixel_addr(uvec3(samplePos.xy*uvec2(screenWidth, screenHeight), 0), uvec2(screenWidth, screenHeight), max_oit_layer);

	float t1 = oit_pixels[pix_addr + 0].transmit;
	float d1 = oit_pixels[pix_addr + 0].depth;
	float t2 = oit_pixels[pix_addr + 1].transmit;
	float d2 = oit_pixels[pix_addr + 1].depth;

	float t3, d3, t4, d4 = 0;

	if(d1 > 0.000001){
		if(samplePos.z < d1){
			shadow = 1.0;	
		}
		else if(samplePos.z < d2){
			//float t = t1 + (samplePos.z - d1) / (d2 - d1) * ( t2 - t1 );
			float t = 1 + (samplePos.z - d1) / (d2 - d1) * (t2 - 1);
			shadow =  t1 * t;
		
		}
		else{
			t3 = oit_pixels[pix_addr + 2].transmit;
			d3 = oit_pixels[pix_addr + 2].depth;
			t4 = oit_pixels[pix_addr + 3].transmit;
			d4 = oit_pixels[pix_addr + 3].depth;

			float t;
			if(samplePos.z < d3){
				//t = t2 + (samplePos.z - d2) / (d3 - d2) * ( t3 - t2 );
				t = 1 + (samplePos.z - d2) / (d3 - d2) * ( t3 - 1 );
				shadow = t1 * t2 * t;
			}
			else if(samplePos.z < d4){
				//t = t3 + (samplePos.z - d3) / (d4 - d3) * ( t4 - t3 );
				t = 1 + (samplePos.z - d3) / (d4 - d3) * ( t4 - 1 );
				shadow = t1*t2*t3*t;
			}
			else{
				t = t4;
				shadow = t1*t2*t3*t;
			}
		}
	}

	return shadow;
}


void main() 
{
	vec4 FragColor = texture2DArray(particleSamplers, vec3(TexCoord, age/life*(texArraySize-1)));
    FragColor.a *= transparency;
    
    FragColor.rgb *= Color * exposure;

	gShadow = vec4(0.0);  // for test
	
	///计算自阴影
	///当前坐标转换到光源空间
	if(flag == 1){
		float shadow = 1.0;

		//重算深度
		float linear_depth = LinearizeDepth(gl_FragCoord.z);
		vec3 worldP = ScreenToWorldPos( vec3(gl_FragCoord.xy/vec2(screenWidth, screenHeight), linear_depth), gModelViewInv );
		/*float dis = distance(worldP, CenterPos);
		float height = sqrt( Radius*Radius - dis*dis );

		linear_depth += height;

		worldP = ScreenToWorldPos( vec3(gl_FragCoord.xy/vec2(screenWidth, screenHeight), linear_depth), gModelViewInv );*/

		vec3 samplePos = WorldPosToScreen(worldP, gModelViewLight, gProjectionLight);
		samplePos.z = LinearizeDepth(samplePos.z);
		//samplePos.z = distance(worldP, gMainLightPos);

		shadow = 0.0;
		shadow += CalcShadow(samplePos);
		shadow += CalcShadow(samplePos + vec3(vec2(-1.0, 0.0)/vec2(screenWidth, screenHeight), samplePos.z));
		shadow += CalcShadow(samplePos + vec3(vec2(1.0, 0.0)/vec2(screenWidth, screenHeight), samplePos.z));
		shadow += CalcShadow(samplePos + vec3(vec2(0.0, -1.0)/vec2(screenWidth, screenHeight), samplePos.z));
		shadow += CalcShadow(samplePos + vec3(vec2(0.0, 1.0)/vec2(screenWidth, screenHeight), samplePos.z));

		shadow /= 5.0;

		shadow = clamp(shadow + 0.3, 0, 1);

		FragColor.rgb *= shadow;  

		//gShadow = vec4(d1, d4, samplePos.z, shadow);  // for test
		gShadow = vec4(shadow, shadow, shadow, 1.0);  // for test
	}
	
    
	float w = weight(gl_FragCoord.z, FragColor.a);

    gColor = vec4(FragColor.rgb * FragColor.a * w, FragColor.a); 

	gAlpha.r = FragColor.a * w;
}


