#version 330 core
//#extension GL_NV_shadow_samplers_cube : enable
#extension GL_NV_shader_buffer_load : enable

layout (location = 0) out vec4 gMainColor;

const float M_PI = 3.1415926535897932384626433832795;

//uniform float sun_exposure;
uniform vec4 gEnviromentParam;

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
	float angle;
};


uniform sampler2D gPositionDepth;
uniform sampler2D gNormal;
uniform sampler2D gDiffuse;
uniform sampler2D gSpecular;
uniform sampler2D gMaterial;
uniform sampler2D gIrradiance;

uniform sampler2D gBentNormal;


uniform sampler2D gRand;

uniform sampler2D gNoise;


uniform int shadow_level_count;
uniform sampler2DArray VSMMaps;
uniform mat4 shadowWVP[3];
uniform vec3 lightPosForShadow[3];
uniform float shadowRange[3];
uniform vec3 lightShadowDirection;


uniform float gSampleRad;
uniform mat4 gProj;
uniform mat4 gModelView;
uniform float AOFactor;
const int MAX_KERNEL_SIZE = 64;
uniform vec4 gKernel[MAX_KERNEL_SIZE];

uniform vec2 jitter;


uniform float bloomThreshold;


uniform Light lights[16];
uniform int lightCount;
uniform vec3 worldSunDir;

uniform float gParticleDensity;

uniform vec4 clipPlane;


uniform vec3 gCameraPos;

uniform int flag;

varying vec2 vUv;

//uniform sampler2D enviromentMap2;
//uniform samplerCube pbrIrradianceMap;
uniform samplerCube pbrSpecularMap;
uniform sampler2D pbrBRDFMap;


uniform float mirrorRatio;
uniform sampler2D mirrorMap;
//uniform vec3 mirrorCenter;
uniform vec3 mirrorDirection;
//uniform float mirrorDepth;

uniform float gAttenuationDistance;

uniform vec2 screenSize;


const float environment_rotation = 0.0;
const float environment_exposure = 2.0;
const float EPSILON_COEF = 1e-4;


uniform float		gLightProbeGIFactor;

uniform vec3		gReflectProbePos;
uniform int			gReflectProbeIndex;



bool bit_and(int val, int ref) {
  if(val == 0) return false;

  return (val/ref) % 2 != 0;
}

vec3 expand(vec3 v) {
  return (v - 0.5) * 2;
}



/* CODE-BEGIN add by yub */
/*vec3 envIrradiance(vec3 dir)
{	
	float rot = environment_rotation * M_2PI;
	float crot = cos(rot);
	float srot = sin(rot);
	vec4 shDir = vec4(dir.xzy, 1.0);
	shDir = vec4(
		shDir.x * crot - shDir.y * srot,
		shDir.x * srot + shDir.y * crot,
		shDir.z,
		1.0);
	return max(vec3(0.0), vec3(
		dot(shDir, irrad_mat_red * shDir),
		dot(shDir, irrad_mat_green * shDir),
		dot(shDir, irrad_mat_blue * shDir)
	)) * environment_exposure;
}*/



/* CODE-END */

vec3 importanceSampleGGX(vec2 Xi, vec3 A, vec3 B, vec3 C, float roughness) {
  float a = roughness * roughness;
  float cosT = sqrt((1.0 - Xi.y)/(1.0 + (a * a - 1.0) * Xi.y));
  float sinT = sqrt(1.0 - cosT * cosT);
  float phi = 2.0 * 3.14159 * Xi.x;
  return (sinT * cos(phi)) * A + (sinT * sin(phi)) * B + cosT * C;
}

vec3 fresnel(float vdh, vec3 F0) {
  /* Schlick with Spherical Gaussian approximation
     cf http://blog.selfshadow.com/publications/s2013-shading-course/karis/s2013_pbs_epic_notes_v2.pdf p3
  */
  float sphg = pow(2.0, (-5.55473 * vdh - 6.98316) * vdh);
  return F0 + (vec3(1.0, 1.0, 1.0) - F0) * sphg;
}

float G1(float ndw, float k) {
  return 1.0 / (ndw * (1.0 - k) +  k);
}

float visibility(float ndl, float ndv, float Roughness) {
  /* Schlick with Smith-like choice of k
     cf http://blog.selfshadow.com/publications/s2013-shading-course/karis/s2013_pbs_epic_notes_v2.pdf p3
     visibility is a Cook-Torrance geometry function divided by (n.l)*(n.v)
  */
  float k = max(Roughness * Roughness * 0.5, 1e-5);
  return G1(ndl, k) * G1(ndv, k);
}

vec3 cook_torrance_contrib(float vdh, float ndh, float ndl, float ndv, vec3 Ks, float Roughness) {
  /* 
    This is the contribution when using importance sampling with the GGX based
    sample distribution. This means ct_contrib = ct_brdf / ggx_probability
  */
  return fresnel(vdh, Ks) * (visibility(ndl, ndv, Roughness) * vdh * ndl / ndh);
}

const vec3  DEFAULT_BASE_COLOR     = vec3(0.5);
const float DEFAULT_ROUGHNESS      = 0.3;
const float DEFAULT_METALLIC       = 0.0;
const float DEFAULT_OPACITY        = 1.0;
const float DEFAULT_AO             = 1.0;
const float DEFAULT_SPECULAR_LEVEL = 0.5;

vec3 getSpecularColor(sampler2D specular_tex, vec2 tex_coord)
{
  vec4 out_color = texture2D(specular_tex, tex_coord).rgba;
  vec3 specColor = out_color.rgb + DEFAULT_BASE_COLOR * (1.0 - out_color.a);
  vec3 defaultF0 = mix(vec3(0.04), specColor, DEFAULT_METALLIC);
  return mix(specColor, defaultF0, (1.0 - out_color.a));
}



float random(vec3 seed, float i)
{
	float dot_product = dot(vec4(seed, i), vec4(12.9898, 78.233, 45.164, 94.673));
	return fract( sin(dot_product) * 43758.5453 );
}

/*
float calcZFromDepth(float depth)
{
	float A = shadowProjection[2][2];
	float B = shadowProjection[3][2];

	float zn = 2*depth - 1;
	return B / ( A + zn );
}
*/

vec3 calc_fresnel_roughness(vec3 n, vec3 v, vec3 F0, float roughness) {

    float ndotv = max(dot(n, v), 0.0);

    return F0 + (max(vec3(1.0 - roughness), F0) - F0) * pow(1.0 - ndotv, 5.0);
}


int CalcShadowLevel(vec3 viewPos)
{
	int k;
	for(k=0; k<3; k++){
		if(-viewPos.z < shadowRange[k]) break;
	}
	
	return k;
}




float InScatter(vec3 start, vec3 rd, vec3 lightPos, vec3 lightDir, float d, float g)
{
    vec3 q = start - lightPos;
    float b = dot(rd, q);
    float c = dot(q, q);
    float iv = 1.0f / sqrt(c - b*b);
    float L = iv * (atan( (d + b) * iv) - atan( b*iv ));
    
    ///散射
    float cosTheta = dot(lightDir,rd);
    float P = 1/(4*M_PI)* (1 - g*g)/ pow(1 + g*g -2*g* cosTheta, 1.5);
    
    ///透光率
    //float T = exp(-c*d);

    return L * P;
}



vec3 CalcLightsContribute(vec3 worldP, vec3 worldN, vec3 worldNBent, vec3 V, vec3 albedo, vec3 specColor, vec3 F0, vec2 dfg, float shininess, vec3 ambient, float amb_factor, vec3 diffuse, vec3 specular, float occlusion, float shadow)
{
	for (int lightIndex = 0; lightIndex < lightCount; lightIndex++) {
			  
			if (bit_and(flag, 0x0100) == true && lightIndex == 0) continue;
			  
			if(lights[lightIndex].type == 0){
				float coeff= 1.0;
				if(lights[lightIndex].position.w > 0.5 && lights[lightIndex].range > 1e-6){
					vec3 Len = worldP - lights[lightIndex].position.xyz;
					float len2 = (Len.x*Len.x + Len.y*Len.y + Len.z*Len.z);	
					coeff = clamp( 1.1-len2/(lights[lightIndex].range*lights[lightIndex].range), 0.0, 1.0);
				}
					
				ambient += albedo * amb_factor * lights[lightIndex].ambient_color * coeff;// * min(0.02 + shadow, 1);

				vec3 lightPosition = lights[lightIndex].position.xyz;
				vec3 L = -(lights[lightIndex].position.w > 0.5 ? normalize(worldP - lightPosition) : normalize(lightPosition));

				float diffuseLight;
				diffuseLight = max(dot(worldNBent, L), 0); ///有太阳光时辅助灯不产生阴影
				if (bit_and(flag, 0x0100) != true) diffuseLight *= min(amb_factor*0.5 + shadow, 1);

				diffuse += albedo * lights[lightIndex].diffuse_color * diffuseLight * coeff * 1.5;
				    
				vec3 H = normalize(L + V);
				float specularLight = pow(max(dot(worldN, H), 0), shininess);
				if (bit_and(flag, 0x0100) != true) specularLight *= min(amb_factor*0.5 + shadow, 1);

				//if (diffuseLight <= 0) specularLight = 0;
				///2021-11-11,wxg,没有高光
				//specular += specColor * lights[lightIndex].specular_color * specularLight * coeff * (F0 * dfg.x + dfg.y);    
				specular += specColor * lights[lightIndex].specular_color * specularLight * coeff; 
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
					
				///在点光源的基础上根据角度计算聚光范围
				float dot1 = dot( -L, lights[lightIndex].direction );
				float d = 1.0 / ( 1.0 - lights[lightIndex].cos_angle );
				coeff *= clamp(1.0 - (1.0 - dot1) * d, 0.0, 1.0);
					
				ambient += albedo * amb_factor * lights[lightIndex].ambient_color * coeff;// * min(0.02 + shadow, 1);

				float diffuseLight;
				diffuseLight = max(dot(worldNBent, L), 0);
				if (bit_and(flag, 0x0100) != true) diffuseLight *= min(amb_factor*0.5 + shadow, 1);

				diffuse += albedo * lights[lightIndex].diffuse_color * diffuseLight * coeff * 1.5;
				    
				vec3 H = normalize(L + V);
				float specularLight = pow(max(dot(worldN, H), 0), shininess);
				if (bit_and(flag, 0x0100) != true) specularLight *= min(amb_factor*0.5 + shadow, 1);

				//if (diffuseLight <= 0) specularLight = 0;
				///2021-11-11,wxg,没有高光
				//specular += specColor * lights[lightIndex].specular_color * specularLight * coeff * (F0 * dfg.x + dfg.y);   
				specular += specColor * lights[lightIndex].specular_color * specularLight * coeff;  
			}
		    
	  }
	  
	  if (bit_and(flag, 0x0100) == true) {
	  
			float coeff = abs(dot(worldSunDir, vec3(0, 1, 0)));
	
			coeff = pow(coeff, 0.5);
			vec3 sunColor = mix(vec3(1, 0.8, 0.5), vec3(1.1, 1.05, 1.0), coeff)*gEnviromentParam.y*2;// * clamp(hdrExposure * 1.5, 0, 1);
			//vec3 sunColor = mix(vec3(1.0, 0.7, 0.4), vec3(1.3, 1.1, 1.0), verticle_angle) * clamp(hdrExposure, 0, 2);
		    
			//追加阳光的颜色
			vec3 worldL = -worldSunDir;
			float diffuseLight = max(dot(worldNBent, worldL), 0)  * min(amb_factor*0.5 + shadow, 1);
			diffuse += albedo * sunColor * diffuseLight;
			
			//ambient += albedo * amb_factor * (1 - diffuseLight) * coeff;
			ambient += amb_factor * sunColor * 0.3 * (coeff*coeff+0.1);// * min(0.02 + shadow, 1);
		    
			vec3 worldV = normalize(gCameraPos - worldP);
			vec3 worldH = normalize(worldL + worldV);
			float specularLight = pow(max(dot(worldN, worldH), 0), shininess) * min(amb_factor*0.5 + shadow, 1);
			//if (diffuseLight <= 0) specularLight = 0;
			///2021-11-11,wxg,没有高光
			//specular += specColor * vec3(1, 1, 1) * specularLight * (F0 * dfg.x + dfg.y);
			specular += specColor * vec3(1, 1, 1) * specularLight;

	  }
		
	  return (ambient*albedo + diffuse + specular) * occlusion;
}



vec3 MakeOrtho(vec3 n)
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



void main() 
{
	vec2 uv = vUv;
	
	vec4 orm = texture2D(gMaterial, uv);
	
	float screenMirrorDepth = float(int(orm.a / 1000));
	float render_type = orm.a - screenMirrorDepth*1000;
	screenMirrorDepth /= 10.0;
	
	vec4 normalVal = texture2D(gNormal, uv);
	vec3 worldN = normalize(normalVal.xyz);
	vec3 worldNBent = bit_and(flag, 0x0400) == true? texture2D(gBentNormal, uv).xyz: worldN;

	vec3 worldP = texture2D(gPositionDepth, uv).xyz;
	float emissive = normalVal.a; 
	
	gMainColor.rgb = vec3(0.0);

	
	vec4 specularColor = texture2D(gSpecular, uv);
	float shininess = specularColor.w;
  
    float camera_dis = distance(gCameraPos, worldP);
	
	
	vec3 V = normalize(gCameraPos - worldP);
	

	vec3 albedo = texture2D(gDiffuse, uv).rgb;
	float amb_factor = texture2D(gDiffuse, uv).a;
  
	if(render_type >= 10 && render_type < 20)  ///pbr
	{ 
		vec3 specColor = vec3(1.0);
		vec3 emitColor = specularColor.rgb;
		
		float occlusion, roughness, metalic;
		occlusion = orm.r;
		roughness = orm.g;
		metalic  = orm.b;
		float envFactor = render_type - 10;

		vec3 F0 = mix(vec3(0.04, 0.04, 0.04), albedo, metalic);
		vec3 F = calc_fresnel_roughness(worldN, V, F0, roughness);
		
		float ndotv = max(0.0, dot(worldN, V));

		// Diffuse part
		vec3 T = vec3(1.0, 1.0, 1.0) - F;
		vec3 kD = T * (1.0 - metalic);
		
		//vec3 irradianceColor = texture(pbrIrradianceMap, worldN).rgb;
		//vec3 irradianceColor = CalcProbeDiffuse(worldP, worldN) * gLightProbeGIFactor;
		vec3 irradianceColor = texture(gIrradiance, uv).rgb * gLightProbeGIFactor;
		
		vec3 diffuse = kD * albedo * irradianceColor;

		// Specular part
		
		vec3 r = 2.0 * ndotv * worldN - V;
		vec3 ld =  textureLod(pbrSpecularMap, r, roughness*5).rgb * specColor;
		
		//衰减
		float attenuation = 1.0;
		if(gReflectProbeIndex >= 0){
			if(gAttenuationDistance > 1e-6){
				attenuation = distance(worldP, gReflectProbePos) / gAttenuationDistance;
				attenuation = clamp( 1 - attenuation*attenuation, 0, 1 );
			}
		}
		
		vec2 dfg = texture(pbrBRDFMap, vec2(ndotv, roughness)).xy;
		vec3 specular = ld * (F0 * dfg.x + dfg.y)  * gLightProbeGIFactor * min(attenuation * 10, 1);	
		vec3 ambient = vec3(amb_factor * 0.1);
			
		gMainColor.rgb = CalcLightsContribute(worldP, worldN, worldNBent, V, albedo, specColor, F0, dfg, shininess, ambient, amb_factor, diffuse, specular, occlusion, 1.0);
			
	}
	
	else if(render_type >= 20 && render_type < 30)
	{
		//vec3 albedo = texture2D(gDiffuse, uv).rgb;
		vec3 specColor = specularColor.rgb;
		vec3 ambient = vec3(amb_factor * 0.1);
		vec3 specular = vec3(0.0);
		
		vec3 V = normalize(gCameraPos - worldP);
		float ndotv = max(0.0, dot(worldN, V));
			
		///2023-1-9, 非pbr不用环境的颜色，只用亮度
		vec3 irradianceColor = texture(gIrradiance, uv).rgb * gLightProbeGIFactor;
		float brightness = 0.3 * irradianceColor.r + 0.6 * irradianceColor.g + 0.1 * irradianceColor.b;
		vec3 diffuse = albedo * brightness;
					  
		  
		gMainColor.rgb = CalcLightsContribute(worldP, worldN, worldNBent, V, albedo, specColor, vec3(0.0), vec2(0.0, 1.0), shininess, ambient, amb_factor, diffuse, specular, 1.0, 1.0);
		  
		//gMainColor.rgb = ambient*albedo + diffuse + specular; 
		float occlusion = render_type - 20;
		gMainColor.rgb *= occlusion;
		  
		  
		orm.b -= float(int(orm.b/100))*100;
		  
		///orm为emission
		if(orm.r>0.999 && orm.g>0.999 && orm.b>0.999) gMainColor.rgb = orm.rgb*albedo * gEnviromentParam.y;
		else gMainColor.rgb += orm.rgb; 
	}
	
	else{  ///lines
		gMainColor.rgb = albedo*1.5;
	}
	
	
	gMainColor.rgb *= emissive * 0.8;   ///材质发光强度
	

	///2023-1-12, -2表示没有gbuffer绘制像素
	//gMainColor.a = orm.a < 0.0001? -2: -1;
	gMainColor.a = orm.a < 0.0001? -2: screenMirrorDepth;
	//gMainColor.a = orm.a < 0.0001? 0 : screenMirrorDepth;  //影响海面颜色
}