struct Material
{
	vec3 Ke, Ka, Kd, Ks;
	float shininess;
  	float alpha;
};

struct Light
{
	vec4 position;
	vec3 diffuse_color;
	vec3 specular_color;
	vec3 ambient_color;
	float range;
	float strength;
};


uniform float box_bottom;
uniform float box_top;

uniform Material material;

uniform Light lights[8];
uniform int lightCount;

uniform vec3 globalAmbient;
uniform vec3 eyePositionLocal;


varying vec3 vPosition;
varying vec3 vNormal;


void main() {
 
  float fff = (vPosition.y - box_bottom) / (box_top - box_bottom);
  if(fff < 0) fff = 0;
  if(fff > 1) fff = 1;


  vec3 emissive = material.Ke * fff;  
  vec3 ambient = material.Ka * globalAmbient * fff;
  vec3 diffuse = vec3(0, 0, 0);
  vec3 specular = vec3(0, 0, 0);
  vec3 Kd = material.Kd *fff;
  vec3 Ks = material.Ks *fff;
  vec3 Ka = material.Ka *fff;

  float shininess = material.shininess;
  vec3 P = vPosition;
  vec3 N;
  N = normalize(vNormal);
  vec3 baseColor = vec3(1, 1, 1)*Kd;
  
  vec3 V = normalize(eyePositionLocal - P);
  
  for (int lightIndex = 0; lightIndex < lightCount; lightIndex++) {
  
	float coeff= 1.0;
	if(lights[lightIndex].position.w > 0.5 && lights[lightIndex].range > 1e-6){
		vec3 Len = lights[lightIndex].position.xyz - P;
		float len2 = (Len.x*Len.x + Len.y*Len.y + Len.z*Len.z);	
		coeff = clamp( 1.1-len2/(lights[lightIndex].range*lights[lightIndex].range), 0.0, 1.0);
	}
	
    	ambient += Ka * lights[lightIndex].ambient_color * coeff;

    	vec3 lightPosition = lights[lightIndex].position.xyz;
    	vec3 L = (lights[lightIndex].position.w > 0.5 ? normalize(lightPosition - P) : normalize(lightPosition));
   	 float diffuseLight = max(dot(N, L), 0);
   	 diffuse += baseColor * lights[lightIndex].diffuse_color * diffuseLight * coeff;
    
    	vec3 H = normalize(L + V);
   	 float specularLight = pow(max(dot(N, H), 0), shininess);
   	 if (diffuseLight <= 0) specularLight = 0;
   	 specular += Ks * lights[lightIndex].specular_color * specularLight * coeff;
  }

  vec3 finalColor = emissive*baseColor + ambient + diffuse + specular;  

  gl_FragColor.rgb = finalColor;
  gl_FragColor.a = material.alpha;
}
