#version 330 core

layout (location = 0) out vec4 gMainColor;

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
	vec4 position;
	vec3 diffuse_color;
	vec3 specular_color;
	vec3 ambient_color;
	float range;
};


uniform sampler2D gPosition;
uniform sampler2D gNormal;
uniform sampler2D gDiffuse;
uniform sampler2D gSpecular;
uniform sampler2D gMaterial;
uniform sampler2D gNormalMap;

uniform sampler2D depthMap;
uniform mat4 shadowWVP;
uniform mat4 shadowProjection;


uniform float gSampleRad;
uniform mat4 gProj;
uniform mat4 gModelView;
uniform float AOFactor;
const int MAX_KERNEL_SIZE = 128;
uniform vec3 gKernel[MAX_KERNEL_SIZE];


uniform float bloomThreshold;


uniform Light lights[16];
uniform int lightCount;
uniform vec3 worldSunDir;

uniform float hdrExposure;


uniform vec3 gCameraPos;

uniform int flag;

varying vec2 vUv;

uniform sampler2D enviromentMap2;


uniform mat4 irrad_mat_red;
uniform mat4 irrad_mat_green;
uniform mat4 irrad_mat_blue;


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


const float M_PI = 3.1415926535897932384626433832795;
const float M_2PI = 2.0 * M_PI;
const float M_INV_PI = 0.31830988618379067153776752674503;
const float M_INV_LOG2 = 1.4426950408889634073599246810019;


/* CODE-BEGIN add by yub */
vec3 envIrradiance(vec3 dir)
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
}

vec3 envSample(vec3 dir)
{
  vec2 pos = M_INV_PI * vec2(atan(-dir.z, -1.0 * dir.x), 2.0 * asin(dir.y));
  pos = 0.5 * pos + vec2(0.5);
  pos.x += environment_rotation;
  return texture2D(enviromentMap2, pos).rgb * environment_exposure;
}


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

float calcZFromDepth(float depth)
{
	float A = shadowProjection[2][2];
	float B = shadowProjection[3][2];

	float zn = 2*depth - 1;
	return B / ( A + zn );
}

float calcShadowFactor(vec4 lightSpacePos, float dis, float bias)
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
            vec2 UVOffset = UV + vec2(x * xOffset * random(projCoord, x) , y * yOffset * random(projCoord, y) );
            count++;
            if(UVOffset.x < 0.001 || UVOffset.x > 1-0.001 || UVOffset.y < 0.001 || UVOffset.y > 1-0.001) Factor += 1.0;
            else{
              float depth= texture(depthMap, UVOffset).r;
              if(depth > Z-bias) Factor += 1.0;
            }
        }
    }
    
 /*   if(Factor > count - 0.000001) return 1.0;
    return shadowColor;*/

  return Factor/count;
}

float calcBlockerDis(vec4 lightSpacePos, float bias)
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
			float depth= texture(depthMap, UVOffset).r;
			if(depth < Z-bias){
				blockers_count++;
				blockers_depth += depth;
			}
		}
	}

	if(blockers_count == 0) return 0.f;
	return calcZFromDepth(blockers_depth / blockers_count);
}




void main() 
{
  float hammersley[256] = float[](
 0.000000, 0.003906,
0.500000, 0.011719,
0.250000, 0.019531,
0.750000, 0.027344,
0.125000, 0.035156,
0.625000, 0.042969,
0.375000, 0.050781,
0.875000, 0.058594,
0.062500, 0.066406,
0.562500, 0.074219,
0.312500, 0.082031,
0.812500, 0.089844,
0.187500, 0.097656,
0.687500, 0.105469,
0.437500, 0.113281,
0.937500, 0.121094,
0.031250, 0.128906,
0.531250, 0.136719,
0.281250, 0.144531,
0.781250, 0.152344,
0.156250, 0.160156,
0.656250, 0.167969,
0.406250, 0.175781,
0.906250, 0.183594,
0.093750, 0.191406,
0.593750, 0.199219,
0.343750, 0.207031,
0.843750, 0.214844,
0.218750, 0.222656,
0.718750, 0.230469,
0.468750, 0.238281,
0.968750, 0.246094,
0.015625, 0.253906,
0.515625, 0.261719,
0.265625, 0.269531,
0.765625, 0.277344,
0.140625, 0.285156,
0.640625, 0.292969,
0.390625, 0.300781,
0.890625, 0.308594,
0.078125, 0.316406,
0.578125, 0.324219,
0.328125, 0.332031,
0.828125, 0.339844,
0.203125, 0.347656,
0.703125, 0.355469,
0.453125, 0.363281,
0.953125, 0.371094,
0.046875, 0.378906,
0.546875, 0.386719,
0.296875, 0.394531,
0.796875, 0.402344,
0.171875, 0.410156,
0.671875, 0.417969,
0.421875, 0.425781,
0.921875, 0.433594,
0.109375, 0.441406,
0.609375, 0.449219,
0.359375, 0.457031,
0.859375, 0.464844,
0.234375, 0.472656,
0.734375, 0.480469,
0.484375, 0.488281,
0.984375, 0.496094,
0.007813, 0.503906,
0.507813, 0.511719,
0.257813, 0.519531,
0.757813, 0.527344,
0.132813, 0.535156,
0.632813, 0.542969,
0.382813, 0.550781,
0.882813, 0.558594,
0.070313, 0.566406,
0.570313, 0.574219,
0.320313, 0.582031,
0.820313, 0.589844,
0.195313, 0.597656,
0.695313, 0.605469,
0.445313, 0.613281,
0.945313, 0.621094,
0.039063, 0.628906,
0.539063, 0.636719,
0.289063, 0.644531,
0.789063, 0.652344,
0.164063, 0.660156,
0.664063, 0.667969,
0.414063, 0.675781,
0.914063, 0.683594,
0.101563, 0.691406,
0.601563, 0.699219,
0.351563, 0.707031,
0.851563, 0.714844,
0.226563, 0.722656,
0.726563, 0.730469,
0.476563, 0.738281,
0.976563, 0.746094,
0.023438, 0.753906,
0.523438, 0.761719,
0.273438, 0.769531,
0.773438, 0.777344,
0.148438, 0.785156,
0.648438, 0.792969,
0.398438, 0.800781,
0.898438, 0.808594,
0.085938, 0.816406,
0.585938, 0.824219,
0.335938, 0.832031,
0.835938, 0.839844,
0.210938, 0.847656,
0.710938, 0.855469,
0.460938, 0.863281,
0.960938, 0.871094,
0.054688, 0.878906,
0.554688, 0.886719,
0.304688, 0.894531,
0.804688, 0.902344,
0.179688, 0.910156,
0.679688, 0.917969,
0.429688, 0.925781,
0.929688, 0.933594,
0.117188, 0.941406,
0.617188, 0.949219,
0.367188, 0.957031,
0.867188, 0.964844,
0.242188, 0.972656,
0.742188, 0.980469,
0.492188, 0.988281,
0.992188, 0.996094
  );
	
	vec3 worldN = texture2D(gNormal, vUv).xyz;
	vec3 worldP = texture2D(gPosition, vUv).xyz;
	//float render_type = texture2D(gPosition, vUv).a;
	float emissive = texture2D(gNormal, vUv).a; 
	
	gMainColor.rgb = vec3(0.0);
	
	vec3 Ks = texture2D(gSpecular, vUv).xyz;
	float shininess = texture2D(gSpecular, vUv).w;
  
	/* Thanks to http://www.thetenthplanet.de/archives/1180 */
	/* get edge vectors of the pixel triangle */
	vec3 dp1 = dFdx(worldP);
	vec3 dp2 = dFdy(worldP);
	vec2 duv1 = dFdx(vUv);
	vec2 duv2 = dFdy(vUv);

	/* solve the linear system */
	vec3 dp2perp = cross(dp2, worldN);
	vec3 dp1perp = cross(worldN, dp1);
	vec3 tangent = dp2perp * duv1.x + dp1perp * duv2.x;
	vec3 binormal = dp2perp * duv1.y + dp1perp * duv2.y;

	/* construct a scale-invariant frame */
	float invmax = inversesqrt(max(dot(tangent, tangent), dot(binormal, binormal)));
	mat3 tsn = mat3(tangent * invmax, binormal * invmax, worldN);
  
	vec3 mapN = texture2D(gNormalMap, vUv).xyz;
	worldN = normalize(tsn * mapN);
    
  
	vec3 V = normalize(gCameraPos - worldP);
	float ndv = dot(V, worldN);
	if (ndv < 0) {
		V = reflect(V, worldN);
		ndv = abs(ndv);
	}


	vec3 baseColor = texture2D(gDiffuse, vUv).rgb;
	float amb_factor = texture2D(gDiffuse, vUv).a;

	float occlusion, roughness, metallic;
	vec4 orm = texture2D(gMaterial, vUv);
	occlusion = orm.r;
	roughness = orm.g;
	metallic  = orm.b;

	///2023/7/13
	//float envFactor = orm.a - 10;
	float screenMirrorDepth = float(int(orm.a / 1000));
	float render_type = orm.a - screenMirrorDepth*1000;
	float envFactor = render_type - 10;
	screenMirrorDepth /= 10.0;

  
	if(render_type >= 10 && render_type < 20)  ///pbr
	{ 
		  float glossiness = 1.0 - roughness;
		  vec3 contribS = vec3(0, 0, 0);
		  vec3 contribSpe = vec3(0, 0, 0);
		  vec3 contribLight = vec3(0, 0, 0);
		  
		  for (int i = 0; i < 64; ++i) {
				vec2 Xi = vec2(hammersley[i*2+0], hammersley[i*2+1]);
				vec3 Hn = importanceSampleGGX(Xi, tsn[0], tsn[1], worldN, roughness);
				vec3 Ln = -reflect(V, Hn);
				float ndl = dot(worldN, Ln);

				/* Horizon fading trick from http://marmosetco.tumblr.com/post/81245981087 */
				const float horizonFade = 1.3;
				float horiz = clamp(1.0 + horizonFade * ndl, 0.0, 1.0);
				horiz *= horiz;

				ndl = max(1e-8, abs(ndl));
				float vdh = max(1e-8, dot(V, Hn));
				float ndh = max(1e-8, dot(worldN, Hn));
				
				//float lodS = roughness < 0.01 ? 0.0 : computeLOD(Ln, probabilityGGX(ndh, vdh, roughness));
				//contribS += envSample(Ln) * cook_torrance_contrib(vdh, ndh, ndl, ndv, specularColor, roughness) * horiz;	
				
				/*
				vec2 pos = 0.31831 * vec2(atan(-Ln.z, -1.0 * Ln.x), 2.0 * asin(Ln.y));
				pos = 0.5 * pos + vec2(0.5, 0.5);
				vec3 envColor = texture2D(AOMap, pos).rgb * hdrBlend;
				*/
			    
				vec3 envColor = envSample(Ln);
			    
				vec3 lightColor = vec3(0, 0, 0);
				for(int lightIndex=0; lightIndex<lightCount; lightIndex++){
				
						if (bit_and(flag, 0x0100) == true && lightIndex == 0) continue;
					
						vec3 localColor = vec3(0, 0, 0);
						localColor += baseColor * lights[lightIndex].ambient_color;// * (1-envFactor);

    					vec3 lightPosition = lights[lightIndex].position.xyz;
    					vec3 L = -(lights[lightIndex].position.w > 0.5 ? normalize(worldP - lightPosition) : normalize(lightPosition));
    					float diffuseLight = max(dot(Hn, L), 0);
    					localColor += baseColor * lights[lightIndex].diffuse_color * diffuseLight;
				    
    					vec3 H = normalize(L + V);
    					float specularLight = pow(max(dot(Hn, H), 0), shininess);
    					if (diffuseLight <= 0) specularLight = 0;
    					localColor += Ks * lights[lightIndex].specular_color * specularLight;

						float coeff= 1.0;
						if(lights[lightIndex].position.w > 0.5 && lights[lightIndex].range > 1e-6){
							vec3 Len = lights[lightIndex].position.xyz - worldP;
							float len2 = (Len.x*Len.x + Len.y*Len.y + Len.z*Len.z);	
							//coeff = exp(-len/lights[lightIndex].range*5) * 5;
							coeff = clamp( 1.1-len2/(lights[lightIndex].range*lights[lightIndex].range), 0.0, 1.0);
						}

						lightColor += localColor * coeff;
				}
			 
				contribLight += lightColor;
			    
				float q = pow(vdh, shininess);
				vec3 speColor = baseColor * ndh * vdh * vdh;
				vec3 f = cook_torrance_contrib(vdh, ndh, ndl, ndv*sqrt(vdh), speColor, 0.3);
				contribS += envColor * f * horiz;
				contribSpe += envColor*q * horiz;
		    
		  }
		  
		  
		  float fa = mix(occlusion, 1.0, glossiness * glossiness) / 64.0;
		  contribS *= fa * envFactor;
		  contribSpe *= fa * envFactor;
		  contribLight *= fa;
		  baseColor *= occlusion;
		  
		  
		  if (bit_and(flag, 0x0100) == true) {
		  
				float coeff = abs(dot(worldSunDir, vec3(0, 1, 0)));
				//vec3 sunColor = mix(vec3(0.8, 0.7, 0.4), vec3(1, 1, 1), coeff) * clamp(hdrExposure * 1.5, 0, 1);
				vec3 sunColor = mix(vec3(1, 0.8, 0.5), vec3(0.9, 0.9, 0.8), coeff) * clamp(hdrExposure * 1.5, 0, 1);
		    
				//追加阳光的颜色
				vec3 worldL = -worldSunDir;
				float diffuseLight = max(dot(worldN, worldL), 0);
				contribLight += baseColor * sunColor * diffuseLight;
		    
				contribLight += baseColor * sunColor * (coeff*coeff+0.1);// * (1-envFactor);
		    
				vec3 worldV = normalize(gCameraPos - worldP);
				vec3 worldH = normalize(worldL + worldV);
				float specularLight = pow(max(dot(worldN, worldH), 0), shininess);
				if (diffuseLight <= 0) specularLight = 0;
				contribLight += Ks * sunColor * specularLight;

		  }


		  float baseFactor = 1.0;
		  float spe = max(max(contribSpe.x, contribSpe.y) , contribSpe.z);
		  vec3 metaColor = (baseColor*baseFactor*contribLight*0.5 + contribS + contribLight*0.5)*(1-spe) +contribSpe*1.2;
		    
		  vec3 plasticColor = baseColor*baseFactor*contribLight;

		  
		  float sss = (plasticColor.x + plasticColor.y + plasticColor.z) / 3;
		  plasticColor = plasticColor + (contribS + contribLight)*(1-sss);

		  gMainColor.rgb = metaColor*metallic + plasticColor*(1-metallic);
	}
	
	else
	{
			vec3 baseColor = texture2D(gDiffuse, vUv).rgb;
			vec3 specColor = texture2D(gSpecular, vUv).rgb;
			vec3 ambient = vec3(amb_factor * 0.2);
			vec3 specular = vec3(0.0);
			vec3 diffuse = vec3(0.0);
			
			vec3 V = normalize(gCameraPos - worldP);
		  
		  
		  for (int lightIndex = 0; lightIndex < lightCount; lightIndex++) {
		  
				if (bit_and(flag, 0x0100) == true && lightIndex == 0) continue;
			  
				float coeff= 1.0;
				if(lights[lightIndex].position.w > 0.5 && lights[lightIndex].range > 1e-6){
					vec3 Len = worldP - lights[lightIndex].position.xyz;
					float len2 = (Len.x*Len.x + Len.y*Len.y + Len.z*Len.z);	
					coeff = clamp( 1.1-len2/(lights[lightIndex].range*lights[lightIndex].range), 0.0, 1.0);
				}
				
				ambient += amb_factor * lights[lightIndex].ambient_color * coeff;

				vec3 lightPosition = lights[lightIndex].position.xyz;
				vec3 L = -(lights[lightIndex].position.w > 0.5 ? normalize(worldP - lightPosition) : normalize(lightPosition));
				float diffuseLight = max(dot(worldN, L), 0);
				diffuse += baseColor * lights[lightIndex].diffuse_color * diffuseLight * coeff;
			    
				vec3 H = normalize(L + V);
				float specularLight = pow(max(dot(worldN, H), 0), shininess);
				if (diffuseLight <= 0) specularLight = 0;
				specular += specColor * lights[lightIndex].specular_color * specularLight * coeff;    
		    
		  }
		  
		  if (bit_and(flag, 0x0100) == true) {
		  
				float coeff = abs(dot(worldSunDir, vec3(0, 1, 0)));
				//vec3 sunColor = mix(vec3(0.8, 0.7, 0.4), vec3(1, 1, 1), coeff) * clamp(hdrExposure * 1.5, 0, 1);
				vec3 sunColor = mix(vec3(1, 0.8, 0.5), vec3(0.9, 0.9, 0.8), coeff) * clamp(hdrExposure * 1.5, 0, 1);
			    
				//追加阳光的颜色
				vec3 worldL = -worldSunDir;
				float diffuseLight = max(dot(worldN, worldL), 0);
				diffuse += baseColor * sunColor * diffuseLight;
				
				//ambient += baseColor * amb_factor * (1 - diffuseLight) * coeff;
				ambient += amb_factor * sunColor * (coeff*coeff+0.1) *0.5;
			    
				vec3 worldV = normalize(gCameraPos - worldP);
				vec3 worldH = normalize(worldL + worldV);
				float specularLight = pow(max(dot(worldN, worldH), 0), shininess);
				if (diffuseLight <= 0) specularLight = 0;
				specular += specColor * vec3(1, 1, 1) * specularLight;

		  }
		  

		  gMainColor.rgb = ambient*baseColor + diffuse + specular; 
		  gMainColor.rgb *= orm.r;
	}
	
	
	gMainColor.rgb *= emissive;   ///材质发光强度
	gMainColor.a = 1.0;//screenMirrorDepth;

}