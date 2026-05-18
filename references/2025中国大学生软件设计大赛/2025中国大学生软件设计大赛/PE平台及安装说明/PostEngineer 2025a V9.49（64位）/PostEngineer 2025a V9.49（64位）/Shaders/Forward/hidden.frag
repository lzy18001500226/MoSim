#version 330 core

layout (location = 0) out vec4 gPositionDepth;   ///位置+线性深度


uniform int flag;

in vec3 vPosition;


bool bit_and(int val, int ref) {
  if(val == 0) return false;
  return (val/ref) % 2 != 0;
}



uniform vec2 gNearFar; // 投影矩阵的远近平面

float LinearizeDepth(float depth)
{
    float z = depth * 2.0 - 1.0; // 回到NDC
    return (2.0 * gNearFar.x * gNearFar.y) / (gNearFar.y + gNearFar.x - z * (gNearFar.y - gNearFar.x));    
}


void main() 
{

	gPositionDepth.xyz = vPosition;
	gPositionDepth.w = LinearizeDepth(gl_FragCoord.z);  //注意gl_FragCoord.z与gl_FragDepth的一致性
}
