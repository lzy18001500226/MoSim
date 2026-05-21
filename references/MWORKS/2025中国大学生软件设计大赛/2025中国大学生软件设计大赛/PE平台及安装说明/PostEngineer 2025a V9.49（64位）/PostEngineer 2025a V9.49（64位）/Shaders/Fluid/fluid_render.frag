#version 330

//#extension GL_NV_shadow_samplers_cube : enable

//版权声明：本文为CSDN博主「0小龙虾0」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
//原文链接：https://blog.csdn.net/qq_39300235/article/details/110183675

out vec4 FragColor; 

in vec2 vUv; 

uniform float NEAR;
uniform float FAR;

uniform float maxThickness;

uniform float aspect;//近平面高:宽
uniform float nearHeight;//近平面高

uniform float shininess;//高光参数

uniform sampler2D gPositionDepth;
uniform sampler2D gScene;

uniform sampler2D gDepthMap;
uniform sampler2D gThicknessMap;
uniform sampler2D gNormalMap;
uniform samplerCube gEnvironmentMap;

uniform vec3 gMainLightPos;//仅考虑主光源

uniform mat4 gView; 

const vec3 diffuseColor=vec3(0.5,0.5,0.5);
const vec3 specularColor=vec3(0.5f);
const vec3 waterRefrectColor=vec3(0.05,0.5,0.8);
const float epo=1e-2;

const vec3 waterF0=vec3(0.001f);
const float refrectScale=0.05;
const float waterK=0.5; 

//裁剪空间转换为眼空间
vec3 uvToEye(vec2 texCoord,float depth)
{    
	vec2 deltaUV=(2.0*texCoord-vec2(1.0))*vec2(aspect,1.0);    
	//计算近平面的平移向量    
	vec2 deltaView=0.5*nearHeight*deltaUV*depth/NEAR;    
	
	return vec3(vec2(deltaView),-depth);
} 

vec3 culFresnel(vec3 f0,float cosTheta)
{    
	return f0+(1.0-f0)*pow(1.0-cosTheta,50.0);
} 


//眼空间光照计算

void main()
{    
	vec3 lightDir = normalize((mat3(gView)*gMainLightPos));    
	float depth = texture(gDepthMap,vUv).r;  
	
	//FragColor = vec4(depth, 0, 0, 1);
	//return;
	
	if ( depth >= texture(gPositionDepth, vUv).w  || depth < 1e-6) {        
		//discard; 
		FragColor = texture(gScene,vUv);
		return;
	} 
	       
	
	//vec2 texSize=vec2(1.0)/textureSize(gNormalMap,0).st;
	vec3 normal = texture(gNormalMap,vUv).xyz;  
	normal = normalize(normal);    
	float thickness = texture(gThicknessMap,vUv).r;  
	      
	//phong漫反射（钳制后）    
	vec3 ambient = diffuseColor*0.1;    
	vec3 diffuse = ambient+diffuseColor*(max(dot(normal,lightDir),0.0)); 
	
	   
	vec3 eyePos = uvToEye(vUv,depth);    
	vec3 veiwDir = normalize(-eyePos);    
	
	//blinn-phong镜面反射    
	vec3 halfDir = normalize(veiwDir+lightDir);    
	vec3 specular = specularColor*pow(max(dot(normal, halfDir), 0.0), shininess);        
	//fresnel反射分量    
	vec3 Rfresnel = culFresnel(waterF0,max(dot(normal,veiwDir),0.0));    
	
	vec3 RreflectDir = normalize( mat3(inverse(gView))*normal);//世界空间    
	//vec3 cubeReflectColor = textureCube(gEnvironmentMap, RreflectDir).rgb; 
	vec3 cubeReflectColor = texture(gEnvironmentMap, RreflectDir).rgb; 
	
	//折射分量（t=p-b(N*P)）    
	vec3 RefrectColor = texture(gScene, vUv - normal.xy*thickness/maxThickness*refrectScale).xyz;    
	
	//透射率    
	float transparency = exp(-thickness/maxThickness*waterK);    
	RefrectColor = mix(waterRefrectColor, RefrectColor, transparency);        
	
	FragColor = clamp( vec4(diffuse*0.3 + specular + mix(RefrectColor, cubeReflectColor, Rfresnel*0.5), 1.0), 0, 1.0);    
}
