

#version 330

layout (location = 0) out vec4 gBlurColor;


in vec2 vUv; 

uniform sampler2D gImage;


uniform vec2  gBlurDir;
uniform float gFilterRadius;
uniform float gSpatialScale;
uniform float gRangeScale; 


void main()
{    

	vec4 color = texture(gImage, vUv);    	
	
	vec4 sumColor = vec4(0.0f);    
	vec4 sumWeight = vec4(0.0f); 
	
	vec2 scale = 1.0 / textureSize(gImage, 0);
	   
	for (float x=-gFilterRadius; x<=gFilterRadius; x+=1.0) 
	{        
		vec4 sampleColor = texture(gImage, vUv + x*gBlurDir*scale);  
		                
		//空域        
		float r = x*gSpatialScale;        
		float w = exp(-r*r);    
		            
		//值域        
		vec4 c = (sampleColor - color) * gRangeScale*0.01;        
		vec4 g = exp(-c*c);                
		
  
		sumColor += sampleColor*w*g;              
		sumWeight += w*g;  
		
		//sumColor += sampleColor;
		//sumWeight += 1;       
	}    	
	
	sumColor /= sumWeight; 
	    
	gBlurColor = sumColor;
}


