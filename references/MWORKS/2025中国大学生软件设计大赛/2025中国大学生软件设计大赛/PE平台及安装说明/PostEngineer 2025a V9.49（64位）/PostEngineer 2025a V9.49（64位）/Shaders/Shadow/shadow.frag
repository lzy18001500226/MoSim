

uniform sampler2D depthMap;
uniform float shadowColor;

uniform float lightSize;
uniform mat4 shadowProjection;

uniform vec4 lightPosition;

varying vec4 lightSpacePos;
varying vec3 vPosition;
varying vec3 vNormal;


float random(vec3 seed, int i)
{
	float dot_product = dot(vec4(seed, i), vec4(12.9898, 78.233, 45.164, 94.673));
	return fract( sin(dot_product) * 43758.5453 );
}

float calcZFromDepth(float depth)
{
	float A = shadowProjection[2][2];
	float B = shadowProjection[3][2];

	float zn = 2*depth - 1;
	return B / ( A + zn );
}

float calcShadowFactor(float dis, float bias)
{
  ///计算阴影
  vec3 projCoord = lightSpacePos.xyz / lightSpacePos.w;
  vec2 UV = vec2(  projCoord.x*0.5+0.5, projCoord.y*0.5+0.5);
  if(UV.x < 0.001 || UV.x > 1-0.001 || UV.y < 0.001 || UV.y > 1-0.001) return 1.0;

  float Factor = 0.0;
  vec2 mapSize = vec2(textureSize(depthMap, 0));
  float Z = projCoord.z*0.5+0.5;
  
   float xOffset = 1.0/mapSize.x;
    float yOffset = 1.0/mapSize.y;
    int count = 0;

    float step = clamp(dis/5, 1.0, 20.0);
   
    for (float y = -dis/2 ; y <= dis/2 ; y+=step) {
        for (float x = -dis/2 ; x <= dis/2 ; x+=step) {
            vec2 UVOffset = UV + vec2(x * xOffset * random(gl_FragCoord.xyy, x) , y * yOffset * random(gl_FragCoord.xyy, y) );
            count++;
            if(UVOffset.x < 0.001 || UVOffset.x > 1-0.001 || UVOffset.y < 0.001 || UVOffset.y > 1-0.001) Factor += 1.0;
            else{
              float depth= texture(depthMap, UVOffset);
              if(depth > Z-bias) Factor += 1.0;
            }
        }
    }

  return shadowColor+Factor/count *(1-shadowColor);
}

float calcBlockerDis(float bias)
{
	vec3 projCoord = lightSpacePos.xyz / lightSpacePos.w;
  	vec2 UV = vec2(  projCoord.x*0.5+0.5, projCoord.y*0.5+0.5);
	float Z = projCoord.z*0.5+0.5;
            /*    float depth= texture(depthMap, UV);
	if(depth < Z-0.00001){
		return calcZFromDepth(depth);
	}
	else return 0;*/

	int blockers_count = 0;
	float blockers_depth = 0;
	float step = 2;
	vec2 mapSize = vec2(textureSize(depthMap, 0));
	float xOffset = 1.0/mapSize.x;
    	float yOffset = 1.0/mapSize.y;

	for (float y = -step ; y <= step ; y+=1.0) {
   		for (float x = -step ; x <= step ; x+=1.0) {
			vec2 UVOffset = UV + vec2(x * xOffset, y * yOffset);
            			if(UVOffset.x < 0.001 || UVOffset.x > 1-0.001 || UVOffset.y < 0.001 || UVOffset.y > 1-0.001) continue;
			float depth= texture(depthMap, UVOffset);
			if(depth < Z-bias){
				blockers_count++;
				blockers_depth += depth;
			}
		}
	}

	if(blockers_count == 0) return 0;
	return calcZFromDepth(blockers_depth / blockers_count);
}

void main() 
{

 /*   float theta;
    if(lightPosition.w < 0.5){
	theta = dot(vNormal, lightPosition.xyz);
    }
    else{
	theta = dot(vNormal,  vPosition - lightPosition.xyz);
    }

   theta = clamp(theta, 0.0, 1.0);

    float bias = 0.001 * tan(acos(theta));*/
    float bias = 0;//clamp(bias, 0.0, 0.01);

    if(lightPosition.w < 0.5){
	float shadowFactor = clamp(calcShadowFactor(4.0, bias) , 0.0, 1.0) ;
	gl_FragColor.rgb = vec3( shadowFactor );
    }
    else{
    	///使用PCSS计算采样步长
  	  float block_dis = calcBlockerDis(bias);
   	 if(block_dis < 0.000001){
		gl_FragColor.rgb = vec3(1.0);
  	  }
   	 else{
    		float step = 50* (lightSpacePos.z -  block_dis) / block_dis;
		step = clamp(step, 2, 200);

		float strength = (lightSpacePos.z -  block_dis)/lightSpacePos.z;
    		float shadowFactor = clamp(calcShadowFactor(step, bias) * (1 + strength), 0.0, 1.0) ;
		gl_FragColor.rgb = vec3( shadowFactor );
    	}
    }
}
