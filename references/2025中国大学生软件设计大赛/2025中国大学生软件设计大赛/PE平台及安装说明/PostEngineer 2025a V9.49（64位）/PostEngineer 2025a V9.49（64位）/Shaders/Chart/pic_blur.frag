#version 130

uniform sampler2D ColorBuffer;
uniform int blurSize;
uniform float blurStrength;

varying vec2 vUv;

void main()
{
	vec2 tex_size = vec2(textureSize(ColorBuffer, 0));
  	if(blurSize == 0){
		float Offsets[4] = float[]( -2, -1, 1, 2 );
		vec3 Color = vec3(0.0, 0.0, 0.0);
   		 for (int i = 0 ; i < 4 ; i++) {
        		for (int j = 0 ; j < 4 ; j++) {
           		 vec2 tc = vUv;
           		 tc.x = vUv.x + Offsets[j] / tex_size.x;
           		 tc.y = vUv.y + Offsets[i] / tex_size.y;
           		 Color += texture(ColorBuffer, tc).xyz;
       		 }
    		}
    		Color /= 16.0;
    		gl_FragColor = vec4(Color, 1.0);
	}  
           	
	else{
		int count = 0;
		vec3 result = vec3(0, 0, 0);
		int step = blurSize/16;
		if(step == 0) step = 1;

		float D = blurSize*blurSize*2;

		for(float m = -blurSize; m<=blurSize; m+=step){
		for(float n = -blurSize; n<=blurSize; n+=step){
			vec2 uv = vUv+vec2( m/tex_size.x,  n/tex_size.y);
			result += texture(ColorBuffer, uv).rgb;// * (1 - (m*m+n*n)/D);
			count++;
		}}
		result /= count;
		result *= blurStrength;
		result = clamp(result, 0.0, 1.0);
		gl_FragColor = vec4(result, 1.0);
	}
}

	
	
		