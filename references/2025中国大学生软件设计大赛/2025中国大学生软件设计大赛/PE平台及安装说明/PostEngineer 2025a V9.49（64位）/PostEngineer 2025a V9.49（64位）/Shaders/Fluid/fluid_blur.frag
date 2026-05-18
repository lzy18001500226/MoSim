/*版权声明：本文为CSDN博主「0小龙虾0」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
原文链接：https://blog.csdn.net/qq_39300235/article/details/110183675*/

#version 330

layout (location = 0) out float Fdepth;
layout (location = 1) out float Fthickness; 

in vec2 vUv; 

uniform sampler2D depthMap;

uniform sampler2D thickMap;

uniform vec2 blurDir;

uniform float filterRadius;

uniform float spatialScale;

uniform float rangeScale; 

uniform float NEAR;

uniform float FAR; 

void main()
{    
	vec2 depTexSize=textureSize(depthMap,0);
	vec2 thickTexSize=textureSize(thickMap,0);    
	
	float depth=texture(depthMap,vUv).r;    
	float thickness=texture(thickMap,vUv).r;  
	
	
	if(depth < 1e-6 || depth > FAR - FAR/1000) {
		Fdepth=depth;    
		Fthickness=thickness;
		return;
	}
	      
	float sumDep=0.0f,sumThick=0.0f;    
	float wsumDep=0.0f,wsumThick=0.0f;    
	for (float x=-filterRadius; x<=filterRadius; x+=1.0) {        
		float sampleDepth=texture(depthMap,vUv+x*blurDir).r;  
		
		if(sampleDepth < 1e-6 || sampleDepth > FAR - FAR/1000){
			continue;
		} 
			
		      
		float sampleThick=texture(thickMap,vUv+x*blurDir).r;
		                
		//空域        
		float r=x*spatialScale;        
		float w=exp(-r*r);                
		//值域        
		float r2Dep=(sampleDepth-depth)*rangeScale;        
		float gDep=exp(-r2Dep*r2Dep);                
		
		//深度采用双边滤波，厚度只使用高斯滤波        
		sumDep+=sampleDepth*w*gDep;        
		sumThick+=sampleThick*w;        
		wsumDep+=w*gDep;        
		wsumThick+=w;    
	}    
	
	
	sumDep/=wsumDep;    
	sumThick/=wsumThick; 
	    
	Fdepth = max(sumDep, 0);
	Fthickness = max(sumThick, 0);
}


