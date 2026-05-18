#version 330

out vec4 FragColor;

in vec2 vUv; 
uniform sampler2D gDepthMap;

uniform sampler2D gNoiseMap;

uniform float NEAR;
uniform float FAR;

uniform float aspect;//近平面高:宽
uniform float nearHeight;//近平面高 

const float epo=1e-7; 

//裁剪空间转换为眼空间
vec3 uvToEye(vec2 texCoord,float depth)
{
	vec2 deltaUV=(2.0*texCoord-vec2(1.0))*vec2(aspect,1.0);    
	
	//计算近平面的平移向量    
	vec2 deltaView=nearHeight*deltaUV*depth/NEAR;    
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
	float depthV=(texture(gDepthMap,vUv).r);    
	if (depthV>=FAR-FAR/1000.0) 
	{        
		discard;    
	}    
	
	//获得当前点的view空间位置    
	vec3 posEye=uvToEye(vUv,depthV);        
	
	//计算微分    
	vec2 uv_plus = vUv+vec2(texSize.x,0);
	vec2 uv_minus = vUv-vec2(texSize.x,0);
	float depth_plus = texture(gDepthMap, uv_plus).r;
	float depth_minus = texture(gDepthMap, uv_minus).r;
	
	vec3 ddu;
/*	if( depth_plus > FAR-FAR/1000){
		ddu = posEye - getEyePos(gDepthMap, uv_minus);
	}
	else if(depth_minus > FAR-FAR/1000){
		ddu = getEyePos(gDepthMap, uv_plus) - posEye; 
	}
	else{*/
		ddu = getEyePos(gDepthMap, uv_plus) - posEye; 
		vec3 ddub = posEye - getEyePos(gDepthMap, uv_minus);
		
		if (abs(ddu.z)<abs(ddub.z) && length(ddub) > epo) {        
			ddu=ddub;  
		} 
	//}
	
	
	uv_plus = vUv+vec2(0, texSize.y);
	uv_minus = vUv-vec2(0, texSize.y);
	depth_plus = texture(gDepthMap, uv_plus).r;
	depth_minus = texture(gDepthMap, uv_minus).r;
	
	vec3 ddv;
/*	if( depth_plus > FAR-FAR/1000){
		ddv = posEye - getEyePos(gDepthMap, uv_minus);
	}
	else if(depth_minus > FAR-FAR/1000){
		ddv = getEyePos(gDepthMap, uv_plus) - posEye; 
	}
	else{*/
		ddv = getEyePos(gDepthMap, uv_plus) - posEye; 
		vec3 ddvb = posEye - getEyePos(gDepthMap, uv_minus);
		
		if (abs(ddv.z)<abs(ddvb.z) && length(ddvb) > epo) {        
			ddv=ddvb;  
		} 
	//}

	
	//计算法线    
	vec3 N = cross(ddu,ddv);
	N = normalize(N) + vec3(texture(gNoiseMap, vUv).xy, 0) * 0.0002 ;
	N = normalize(N);  
	FragColor = vec4(N,1.0);
}
