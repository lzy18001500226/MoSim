#version 330 core
#extension GL_NV_shadow_samplers_cube : enable

layout (location = 0) out vec4 gMainColor;


const float M_PI = 3.1415926535897932384626433832795;
const float M_2PI = 2.0 * M_PI;
const float M_INV_PI = 0.31830988618379067153776752674503;
const float M_INV_LOG2 = 1.4426950408889634073599246810019;

vec3 hdr(vec3 L, float expo) {
    L = L * expo;
    L.r = L.r < 1.413 ? pow(L.r * 0.38317, 1.0 / 2.2) : 1.0 - exp(-L.r);
    L.g = L.g < 1.413 ? pow(L.g * 0.38317, 1.0 / 2.2) : 1.0 - exp(-L.g);
    L.b = L.b < 1.413 ? pow(L.b * 0.38317, 1.0 / 2.2) : 1.0 - exp(-L.b);
    return L;
}


vec3 get_ortho(vec3 n)
{
    vec3 v;
	float maxv = abs(n[0]);
	int mi=0;
	for(int i=1; i<3; i++)
	{
		if(abs(n[i]) > maxv)
		{
			maxv = abs(n[i]);
			mi = i;
		}
	}

	if(mi == 0)
	{
		v[0] = -n[1]/n[0] - n[2]/n[0];
    	v[1] = 1.0;
    	v[2] = 1.0;
	}
	else if(mi == 1)
	{
		v[1] = -n[0]/n[1] - n[2]/n[1];
    	v[0] = 1.0;
    	v[2] = 1.0;
	}
	else if(mi == 2)
	{
		v[2] = -n[0]/n[2] - n[1]/n[2];
    	v[0] = 1.0;
    	v[1] = 1.0;
	}
    return normalize(v);
}



struct Light
{
	int type;
	vec4 position;
	vec3 diffuse_color;
	vec3 specular_color;
	vec3 ambient_color;
	float range;
	vec3 direction;
	float cos_angle;
};


uniform sampler2D gPositionDepth;
uniform sampler2D gNormal;
uniform sampler2D gDiffuse;
uniform sampler2D gSpecular;
uniform sampler2D gMaterial;
uniform sampler2D gNormalMap;


uniform sampler2D texNoise;


uniform vec2 jitter;


uniform vec4 clipPlane;


uniform vec3 gCameraPos;

uniform int flag;

varying vec2 vUv;


uniform vec2 screenSize;

uniform Light lights[16];
uniform int lightCount;
uniform vec3 worldSunDir;

uniform float hdrExposure;



const float environment_rotation = 0.0;
const float environment_exposure = 2.0;
const float EPSILON_COEF = 1e-4;

bool bit_and(int val, int ref) {
  if(val == 0) return false;

  return (val/ref) % 2 != 0;
}

vec3 expand(vec3 v) {
  return (v - 0.5) * 2;
}




const vec3  DEFAULT_BASE_COLOR     = vec3(0.5);
const float DEFAULT_ROUGHNESS      = 0.3;
const float DEFAULT_METALLIC       = 0.0;
const float DEFAULT_OPACITY        = 1.0;
const float DEFAULT_AO             = 1.0;
const float DEFAULT_SPECULAR_LEVEL = 0.5;



float random(vec3 seed, float i)
{
	float dot_product = dot(vec4(seed, i), vec4(12.9898, 78.233, 45.164, 94.673));
	return fract( sin(dot_product) * 43758.5453 );
}


vec3 calc_fresnel_roughness(vec3 n, vec3 v, vec3 F0, float roughness) {

    float ndotv = max(dot(n, v), 0.0);

    return F0 + (max(vec3(1.0 - roughness), F0) - F0) * pow(1.0 - ndotv, 5.0);
}




void main() 
{
	vec2 uv = vUv;
	
	vec3 worldN = texture2D(gNormal, uv).xyz;
	vec3 worldP = texture2D(gPositionDepth, uv).xyz;
	
	vec3 albedo = texture2D(gDiffuse, uv).rgb;
	
	gMainColor.rgb = vec3(0);
	
	for (int lightIndex = 0; lightIndex < lightCount; lightIndex++) {
		  
		if (bit_and(flag, 0x0100) == true && lightIndex == 0) continue;
		  
		if(lights[lightIndex].type == 0){
			float coeff= 1.0;
			if(lights[lightIndex].position.w > 0.5 && lights[lightIndex].range > 1e-6){
				vec3 Len = worldP - lights[lightIndex].position.xyz;
				float len2 = (Len.x*Len.x + Len.y*Len.y + Len.z*Len.z);	
				coeff = clamp( 1.1-len2/(lights[lightIndex].range*lights[lightIndex].range), 0.0, 1.0);
			}
				
			//vec3 lightPosition = lights[lightIndex].position.xyz;
			//vec3 L = -(lights[lightIndex].position.w > 0.5 ? normalize(worldP - lightPosition) : normalize(lightPosition));
			//float diffuseLight = max(dot(worldN, L), 0);
			gMainColor.rgb += albedo * lights[lightIndex].diffuse_color * coeff;// * diffuseLight;
			       
		}
		else{
			float coeff= 1.0;
			if(lights[lightIndex].range > 1e-6){
				vec3 Len = worldP - lights[lightIndex].position.xyz;
				float len2 = (Len.x*Len.x + Len.y*Len.y + Len.z*Len.z);	
				coeff = clamp( 1.1-len2/(lights[lightIndex].range*lights[lightIndex].range), 0.0, 1.0);
			}
				
			vec3 lightPosition = lights[lightIndex].position.xyz;
			vec3 L = -(normalize(worldP - lightPosition));
			//float diffuseLight = max(dot(worldN, L), 0);
				
			///在点光源的基础上根据角度计算聚光范围
			float dot1 = dot( -L, lights[lightIndex].direction );
			float d = 1.0 / ( 1.0 - lights[lightIndex].cos_angle );
			coeff *= clamp(1.0 - (1.0 - dot1) * d, 0.0, 1.0);
				
			gMainColor.rgb += albedo * lights[lightIndex].diffuse_color * coeff;// * diffuseLight;
			   
		}
	    
	  }
	  
	  if (bit_and(flag, 0x0100) == true) {
	  
			float coeff = abs(dot(worldSunDir, vec3(0, 1, 0)));
			//vec3 sunColor = mix(vec3(0.8, 0.7, 0.4), vec3(1, 1, 1), coeff) * clamp(hdrExposure * 1.5, 0, 1);
			vec3 sunColor = mix(vec3(1, 0.8, 0.5), vec3(0.9, 0.9, 0.8), coeff) * clamp(hdrExposure * 1.5, 0, 1);
		    
			//追加阳光的颜色
			//vec3 worldL = -worldSunDir;
			//float diffuseLight = max(dot(worldN, worldL), 0);
			gMainColor.rgb += albedo * sunColor;// * diffuseLight;
			
	  }
	
	
	gMainColor.rgb = max( gMainColor.rgb - vec3(0.2), 0 );
	
}