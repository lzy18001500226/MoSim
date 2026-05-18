

struct Material
{
	vec3 Ke, Ka, Kd, Ks;
	float shininess;
  	float alpha;
};

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

struct TextureLight
{
	vec3 position;
	vec3 size;
	float strength;
	sampler2D texture;
};

uniform vec3 tl_n;
uniform vec3 tl_u;
uniform vec3 tl_v;

uniform float sun_exposure;

uniform Material material;

uniform Light lights[16];
uniform int lightCount;
uniform vec3 worldSunDir;

uniform vec3 globalAmbient;
uniform vec3 gCameraPos;

uniform mat4 modelToWorld;

uniform int flag;

uniform vec3 gVertical;

uniform vec4 clipPlanes[3];
uniform int clipPlaneCount;

struct ColorSetting
{
	float value;
	vec4 color;
};


uniform ColorSetting colorSettings[32];
uniform	int colorSettingCount;


vec4 GetVColor(float val)
{

	if(colorSettingCount == 0) return vec4(0);

	vec4 VColor;

	int i;
	for(i=0; i<colorSettingCount; i++){
		if( val < colorSettings[i].value) break;
	}

	if( i==0 ) 
		VColor = colorSettings[0].color;
	else if(i == colorSettingCount) 
		VColor = colorSettings[colorSettingCount-1].color;
	else{
		float factor = (val - colorSettings[i-1].value) / (colorSettings[i].value - colorSettings[i-1].value);

		VColor = colorSettings[i-1].color*(1-factor) + colorSettings[i].color*factor;
	}

	return VColor;
}



uniform float fogDensity;
uniform float fogHeight;
uniform vec3 fogColor;

float CalcFogBlend(vec3 worldP)
{
	float fogBlend = 1.0;
	const float EPSON = 0.0000001;

	if(fogDensity > EPSON){
     	 float dis = distance(gCameraPos, worldP);
		 vec3 viewDir = normalize(worldP - gCameraPos);

		float density = fogDensity;// * 0.5 + fogDensity * 0.5 * GetFogNoise(worldP);  /// worldP no use

		vec3 up = gVertical;
		density *= (1 - dot(up, viewDir)) / 2;
        
		fogBlend = clamp(exp(-density * dis ), 0, 1);

		if( fogHeight > EPSON){
			float H = dot(worldP - vec3(0), gVertical);
			float factor = 1.0 - min( max( H - fogHeight, 0) / (fogHeight*5), 1.0);
			fogBlend = fogBlend*factor + 1.0*(1 - factor);
		}
    }

	return fogBlend;
}

varying vec3 vPosition;
varying vec3 vNormal;
varying vec3 worldP;

varying float vValue;

uniform int textureLightCount;
uniform TextureLight textureLights[8];
	
vec3 calcTextureLights(vec3 P, vec3 N, vec3 baseColor, vec3 ambColor)
{
	vec3 lightColor = vec3(0, 0, 0);

	int index;
	for(index = 0; index < textureLightCount; index++){
	
		float l = textureLights[index].size.x;
		float w = textureLights[index].size.y;
		float h = textureLights[index].size.z;
		float step = w>l?w/32:l/32;

		for(float wi = 0; wi <= w; wi+=step){
			for(float li=0; li<=l; li+=step){
				//vec3 lightPosition = textureLights[index].position + vec3(wi-w/2, 0, li-l/2);
				vec3 lightPosition = textureLights[index].position + tl_u*(wi-w/2) + tl_v*(li-l/2);
				vec3 lightDiffuse = texture2D(textureLights[index].texture, vec2(li/l, wi/w)).xyz;

				float coeff;
				vec3 Len = lightPosition - P;
	
				//float len2 = (Len.x*Len.x + Len.y*Len.y*step*step/h/h + Len.z*Len.z);
				float nf = 	abs(dot(Len, tl_n))/h;
				float uf = abs(dot(Len, tl_u))/step;
				float vf = 	abs(dot(Len, tl_v))/step;

				coeff = clamp(1 - (nf*nf + uf*uf + vf*vf), 0, 1);

				if(coeff > 0){
    					vec3 L = normalize(lightPosition - P);
    					float diffuseLight = max(dot(N, L), 0);
    					lightColor += (ambColor+baseColor) * lightDiffuse * diffuseLight * coeff * textureLights[index].strength;
				}
			}
		}
	}

	return lightColor;
}


bool bit_and(int val, int ref) {
  if(val == 0) return false;

  return (val/ref) % 2 != 0;
}

vec3 expand(vec3 v) {
  return (v - 0.5) * 2;
}

float R(float original_value, float original_min, float original_max, 
            float new_min, float new_max)
{
	//if(original_value <= original_min) return 0;
	
    return new_min + ((( original_value - original_min) / (original_max - original_min))
            * (new_max - new_min));
}


float weight(float z, float a) 
{
	return clamp(pow(min(1.0, a * 10.0) + 0.01, 3.0) * 1e8 * pow(1.0 - z * 0.9, 3.0), 1e-2, 3e3);
}





void main() {

	vec4 FragColor = vec4(0, 0, 0, 1);
   
  if(bit_and(flag, 0x0200) == true ){
	
		for(int k=0; k<clipPlaneCount; k++){
			float d = dot(clipPlanes[k].xyz, worldP) + clipPlanes[k].w;
			if(d < 0){
				discard;
				return;
			}
		}
	}
 

  vec3 ambient = material.Ka * globalAmbient;
  vec3 diffuse = vec3(0, 0, 0);
  vec3 specular = vec3(0, 0, 0);
  vec3 Kd = material.Kd;
  vec3 Ks = material.Ks;
  vec3 Ka = material.Ka;
  vec3 Ke = material.Ke;
  float shininess = material.shininess;
  vec3 P = vPosition;
  vec3 N;
  
  N = normalize(vNormal);

  vec3 worldN = normalize(modelToWorld * vec4(N, 0)).xyz;
  
  
  vec3 baseColor = Kd;

  vec3 V = normalize(gCameraPos - worldP);
 
  for (int lightIndex = 0; lightIndex < lightCount; lightIndex++) {
  
    if (bit_and(flag, 0x0100) == true && lightIndex == 0) continue;
  
	if(lights[lightIndex].type == 0){
		float coeff= 1.0;
		if(lights[lightIndex].position.w > 0.5 && lights[lightIndex].range > 1e-6){
			vec3 Len = lights[lightIndex].position.xyz - P;
			float len2 = (Len.x*Len.x + Len.y*Len.y + Len.z*Len.z);	
			coeff = clamp( 1.1-len2/(lights[lightIndex].range*lights[lightIndex].range), 0.0, 1.0);
		}
		
		ambient += Ka * lights[lightIndex].ambient_color * coeff;

		vec3 lightPosition = lights[lightIndex].position.xyz;
		vec3 L = -(lights[lightIndex].position.w > 0.5 ? normalize(worldP - lightPosition) : normalize(lightPosition));
		float diffuseLight = max(dot(worldN, L), 0);
		diffuse += baseColor * lights[lightIndex].diffuse_color * diffuseLight * coeff;
	    
		vec3 H = normalize(L + V);
		float specularLight = pow(max(dot(worldN, H), 0), shininess);
		if (diffuseLight <= 0) specularLight = 0;
		specular += Ks * lights[lightIndex].specular_color * specularLight * coeff;
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
		
		ambient += Ka * lights[lightIndex].ambient_color * coeff;

		float diffuseLight = max(dot(worldN, L), 0);
		diffuse += baseColor * lights[lightIndex].diffuse_color * diffuseLight * coeff;
	    
		vec3 H = normalize(L + V);
		float specularLight = pow(max(dot(worldN, H), 0), shininess);
		if (diffuseLight <= 0) specularLight = 0;
		specular += Ks * lights[lightIndex].specular_color * specularLight * coeff;   
	}
  }
  
  if (bit_and(flag, 0x0100) == true) {
    float coeff = abs(dot(worldSunDir, vec3(0, 1, 0)));
   
    //vec3 sunColor = mix(vec3(1, 0.8, 0.5), vec3(0.9, 0.9, 0.8), coeff) * clamp(hdrExposure * 1.5, 0, 1);
    //vec3 sunColor = mix(vec3(1.0, 0.7, 0.4), vec3(1.3, 1.1, 1.0), verticle_angle) * clamp(hdrExposure, 0, 2);
    vec3 sunColor = mix(vec3(1, 0.8, 0.5), vec3(1.1, 1.05, 1.0), coeff) * sun_exposure * 2;// * clamp(hdrExposure * 1.5, 0, 1);
    
    //追加阳光的颜色
    vec3 worldL = -worldSunDir;
    float diffuseLight = max(dot(worldN, worldL), 0);
    diffuse += baseColor * sunColor * diffuseLight;
    
    ambient += Ka * sunColor * (coeff*coeff+0.1) *0.5;
    
    vec3 worldV = normalize(gCameraPos - worldP);
    vec3 worldH = normalize(worldL + worldV);
    float specularLight = pow(max(dot(worldN, worldH), 0), shininess);
    if (diffuseLight <= 0) specularLight = 0;
    specular += Ks * vec3(1, 1, 1) * specularLight;

  }
 

  vec3 finalColor = ambient*baseColor + diffuse + specular; 
  
  float transparencySetting = material.alpha;
  
  finalColor += calcTextureLights( P, N, baseColor, material.Ka);
  
  if(Ke.r > 0.99 && Ke.g > 0.99 && Ke.b > 0.99)
	finalColor = Ke*baseColor;
  else
	finalColor += Ke;

	
  vec4 VColor = GetVColor(vValue);
    
  ///改为光源只影响强度
  //FragColor.rgb = finalColor * VColor.rgb;
  float brightness = 0.2126*finalColor.r + 0.7152*finalColor.g + 0.0722*finalColor.b; 
  FragColor.rgb = brightness * VColor.rgb;

  FragColor.a = transparencySetting;
  
  if(bit_and(flag, 0x0400) == true) {
	float alpha = (baseColor.r + baseColor.g + baseColor.b) / 3;
	if(alpha < 0.1) FragColor.a *= alpha*0.1;
	//else FragColor.a = 1;
  }
  

  //雾
  float fogBlend = CalcFogBlend(worldP);
  FragColor.rgb = FragColor.rgb*fogBlend + fogColor*(1-fogBlend);

  if( transparencySetting < 0.9-1e-6 )
  {
		float transparency = FragColor.a;
		//获得要输出的颜色，把rgb乘上透明度，加到Color这张纹理上
		//gl_FragData[0] = vec4(FragColor.rgb * FragColor.a, FragColor.a);
		//在记录累加次数的纹理上加1
		//gl_FragData[1] = vec4(1.0);

		vec3 viewDir = worldP - gCameraPos;
		vec3 v = normalize(viewDir);
		float nv = abs(dot(v, N));

		FragColor.a += (1 - nv) * ( 1 - FragColor.a) * 0.8; 
		if(transparency < 0.25){
			FragColor.a = FragColor.a * (transparency * 4);
		}
	
		float w = weight(gl_FragCoord.z, FragColor.a);

		gl_FragData[0] = vec4(FragColor.rgb * FragColor.a * w, FragColor.a);  
		gl_FragData[1] = vec4(FragColor.a * w);
  }
  else{
	gl_FragData[0] = FragColor;
	gl_FragData[1] = vec4(1.0);
  }

}

