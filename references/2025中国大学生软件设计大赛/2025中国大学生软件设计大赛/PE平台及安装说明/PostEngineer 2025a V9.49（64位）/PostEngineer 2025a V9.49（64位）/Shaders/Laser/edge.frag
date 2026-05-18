#version 330

uniform sampler2D image;

in vec2 vUv;


void main()
{
    
	vec4 color = texture(image, vUv);
	vec2 texSize = textureSize(image, 0);
	
	if(color.a > 0.5)
	{
		vec4 NearColor0 = texture(image, vUv + vec2(1, 0)/texSize );
		vec4 NearColor1 = texture(image, vUv + vec2(0, 1)/texSize );
		vec4 NearColor2 = texture(image, vUv + vec2(-1, 0)/texSize );
		vec4 NearColor3 = texture(image, vUv + vec2(0, -1)/texSize );
		
		if( NearColor0.a < 0.1 || NearColor1.a < 0.1 || NearColor2.a < 0.1 || NearColor3.a < 0.1 ){
			color.a = 2;
		}
	}
		
	gl_FragColor = color;
}

	
	
		