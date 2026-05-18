#version 330

out vec4 FragColor;

in vec2 vUv; 

uniform float NEAR;
uniform float FAR;

uniform float aspect;//近平面高:宽
uniform float nearHeight;//近平面高 

uniform sampler2D gDepthMap;

const float epo=1e-7; 

//裁剪空间转换为眼空间
vec3 uvToEye(vec2 texCoord,float depth)
{
	vec2 deltaUV=(2.0*texCoord-vec2(1.0))*vec2(aspect,1.0);    
	
	//计算近平面的平移向量    
	vec2 deltaView=0.5*nearHeight*deltaUV*depth/NEAR;    
	return vec3(vec2(deltaView),-depth);
}  

vec3 getEyePos(sampler2D depthTex,vec2 texCoord)
{    
	float depth=(texture(depthTex,texCoord).r);    
	return uvToEye(texCoord,depth);
} 

void main()
{   
		 
	vec2 texSize=vec2(1.0/textureSize(gDepthMap,0).s,1.0/textureSize(gDepthMap,0).t);  
	
		
	//深度    
	vec4 depthColor = texture(gDepthMap,vUv);
	float depthV = depthColor.r;    
	if (depthV >= FAR-epo || depthV < epo) 
	{        
		//discard; 
		FragColor = vec4(0, 0, 0, 1);
		return;   
	}    
	
	//获得当前点的view空间位置    
	vec3 posEye=uvToEye(vUv,depthV);        
	
	//计算微分    
	vec3 ddu=getEyePos(gDepthMap,vUv+vec2(texSize.x,0))-posEye;    
	vec3 ddub=posEye-getEyePos(gDepthMap,vUv-vec2(texSize.x,0));    
	
	if (abs(ddu.z)>abs(ddub.z)) {        
		ddu=ddub;  
	}    
	
	vec3 ddv=getEyePos(gDepthMap,vUv+vec2(0,texSize.y))-posEye;    
	vec3 ddvb=posEye-getEyePos(gDepthMap,vUv-vec2(0,texSize.y));    
	
	if (abs(ddv.z)>abs(ddvb.z)) {        
		ddv=ddvb;    
	}
	
	//计算法线    
	vec3 N=cross(ddu,ddv);    
	N=normalize(N);    
	FragColor=vec4(N,1.0);
}
