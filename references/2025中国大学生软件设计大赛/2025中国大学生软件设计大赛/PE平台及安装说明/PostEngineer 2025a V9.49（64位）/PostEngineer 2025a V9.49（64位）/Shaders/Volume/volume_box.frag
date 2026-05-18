#version 330 core

layout (location = 0) out vec4 gPositionDepth;   ///位置+线性深度


in vec3 vPosition;

uniform vec2 jitter;
uniform vec2 gNearFar;

float LinearizeDepth(float depth)
{
    float z = depth * 2.0 - 1.0; // 回到NDC
    return (2.0 * gNearFar.x* gNearFar.y)/ (gNearFar.y + gNearFar.x - z * (gNearFar.y - gNearFar.x));    
}

vec2 GetJitterUV(vec2 uv)
{
	return uv + jitter / 2;
}


void main() 
{
	gPositionDepth.xyz = vPosition;
	gPositionDepth.w = LinearizeDepth(gl_FragCoord.z);  //注意gl_FragCoord.z与gl_FragDepth的一致性
}
