#version 430
#extension GL_NV_shader_buffer_load : enable
#extension GL_EXT_texture_array : enable
#extension GL_ARB_fragment_shader_interlock : enable



uniform sampler2DArray particleSamplers;

uniform sampler2D gForwardDepth;


uniform vec2 gNearFar;
uniform float gAspect;
uniform float gNearHeight;

uniform float exposure;
uniform float life;
uniform float life2;

uniform int texArraySize;

uniform int screenWidth;
uniform int screenHeight;

in float age;
in vec2 TexCoord;
in float transparency;
in vec3 Color;

in float disToCenter;
in vec3 viewCenterPos;
in mat4 projection;
in vec3 fragPos;



float weight(float z, float a) 
{
	return clamp(pow(min(1.0, a * 10.0) + 0.01, 3.0) * 1e8 * pow(1.0 - z * 0.9, 3.0), 1e-2, 3e3);
}


vec3 WorldPosToScreen(vec3 worldP, mat4 modelView, mat4 projection)
{
	vec3 viewPos = (modelView * vec4(worldP, 1)).xyz;
	vec4 projPos = projection * vec4(viewPos, 1);

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
	vec3 worldP = (modelViewInv * vec4(viewPos, 1)).xyz;

	return worldP;
}


float LinearizeDepth(float depth)
{
    float z = depth * 2.0 - 1.0; // 回到NDC
    return (2.0 * gNearFar.x * gNearFar.y) / (gNearFar.y + gNearFar.x - z * (gNearFar.y - gNearFar.x));    
}


//版权声明：本文为博主原创文章，遵循 CC 4.0 BY-SA 版权协议，转载请附上原文出处链接和本声明。
//原文链接：https://blog.csdn.net/ONE_SIX_MIX/article/details/113803362

struct OitTransmit
{
	float transmit;
	float depth;
};


layout(set=0, binding=3, std430) buffer _oit_pixels
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

/*
// 压缩像素
OitTransmit pack_oit_pix(OitTransmit p)
{
	OitTransmit d;

	d.parmas = packSnorm4x8(p.parmas);
	
	return d;
}

// 解压缩像素
OitTransmit unpack_oit_pix(OitTransmit p)
{
	OitPixel d;

	d.parmas = unpackSnorm4x8(p.parmas);

	return d;
}
*/

// 将像素体压入
void insert_pixels(OitTransmit pix,		// 待插入元素
				   uvec2 pos_xy,			// 待插入位置
				   uvec2 scn_wh,			// 屏幕大小
				   uint max_oit_layer		// 最大透明层数
				   )
{
	// 得到当前像素体的位置
	uint pix_addr = calc_pixel_addr(uvec3(pos_xy, 0), scn_wh, max_oit_layer);

	OitTransmit temp_pixels[10];
	for(int i=0; i<max_oit_layer + 1; i++){
		if(i < max_oit_layer)temp_pixels[i] = oit_pixels[pix_addr + i];
		else{
			temp_pixels[i].transmit = 0.0;
			temp_pixels[i].depth = gNearFar.y;
		}

		if(temp_pixels[i].depth < 0.000001) temp_pixels[i].depth = gNearFar.y;
	}


	int pos = -1;

	for (int i = 0; i < max_oit_layer; ++i)
	{
		if (pix.depth < temp_pixels[i].depth)
		{
			pos = i;
			break;
		}
	}

	if (pos != -1)
	{
		// 找到了插入位置，从最右边开始，将待插入位置右边的有效数据往右移动
		for (int i=int(max_oit_layer)-1; pos < i; --i)
		{
			// 发现有效数据，往右移动
			temp_pixels[i] = temp_pixels[i - 1];
		}
		// 移动完成，插入数据
		temp_pixels[pos] = pix;
	}

	///从中间删除一个差异最小的，保留最后一个有效值
	if(temp_pixels[max_oit_layer].depth < gNearFar.y - 0.00001){

		float min_val = 1.0;
		int min_i = 1;
		for(int i=1; i<max_oit_layer; i++){
			float scale = (temp_pixels[i].depth  - temp_pixels[i-1].depth) / (temp_pixels[i+1].depth  - temp_pixels[i-1].depth);
			float even_val = temp_pixels[i-1].transmit + scale * (temp_pixels[i+1].transmit - temp_pixels[i-1].transmit);
			float delta = abs( temp_pixels[i].transmit - even_val);

			if(min_val > delta){
				min_val = delta;
				min_i = i;
			}
		}

		for(int i=min_i; i<max_oit_layer; i++){
			temp_pixels[i] = temp_pixels[i+1];
		}
	}

	for(int i=0; i<max_oit_layer; i++){
		oit_pixels[pix_addr + i] = temp_pixels[i];
	}

}



void main() 
{
	vec4 FragColor = texture2DArray(particleSamplers, vec3(TexCoord, age/life*(texArraySize-1)));
    FragColor.a *= transparency;
    
    FragColor.rgb *= Color * exposure;


	float dis = distance(viewCenterPos, fragPos);
	float height = disToCenter;
	uvec2 pos_xy = uvec2(gl_FragCoord.xy);

	OitTransmit pix;
 
    if(dis > disToCenter){        
		gl_FragDepth = 1.0;
		pix.transmit = 0.0;
		pix.depth = gNearFar.y;
		//return;   
	}
	else{
	
		//pos_xy = uvec2((projection*vec4(vec3(fragPos),1.0)).xy*0.5 + 0.5);
	
		height = sqrt(disToCenter*disToCenter - dis*dis);
	
		//深度    
		float depthView = fragPos.z + height;    
		vec4 clip_space_pos = projection*vec4(vec3(fragPos.xy, depthView),1.0);    
		clip_space_pos.xyz = (clip_space_pos.xyz/clip_space_pos.w)*0.5 + 0.5;
		//pos_xy = uvec2(clip_space_pos.xy) * uvec2(screenWidth, screenHeight);

		float depth = clip_space_pos.z;
		gl_FragDepth = depth;

		
		//float brightness = 0.2126*FragColor.r + 0.7152*FragColor.g + 0.0722*FragColor.b;
		//pix.transmit = 1.0 - height / disToCenter * transparency * 0.3 ;
		//pix.transmit = 1.0 - FragColor.a;
		pix.transmit = 1.0 - transparency;
		pix.depth = LinearizeDepth(gl_FragDepth); 
	}


	const uint max_oit_layer = 4;



	// 插入像素
	// 像素锁开始
	beginInvocationInterlockARB();

	// 将像素体压入延迟缓冲区
	insert_pixels(pix,
				pos_xy,
				uvec2(screenWidth, screenHeight),
				max_oit_layer);

	endInvocationInterlockARB();

}


