#version 130

uniform sampler2D gTanspImage;
uniform sampler2D gFourierA;
uniform sampler2D gOpacity;


void main()
{
	gl_FragColor = vec4(0, 0, 0, 1);
	
	vec4  transpColor = texelFetch(gTanspImage, ivec2(gl_FragCoord.xy), 0).rgba;

	float sumDepth = 0.5 * texelFetch(gFourierA, ivec2(gl_FragCoord.xy), 0).y;
	float transmittance = exp(-sumDepth);

	//vec3 finalColor = transpColor.rgb / transpColor.a * (1.0 - transmittance) + backColor * transmittance;
	vec3 finalColor = transpColor.rgb / transpColor.a;
	
	if(isnan(finalColor.x))
		finalColor = texelFetch(gOpacity, ivec2(gl_FragCoord.xy), 0).rgb;

	gl_FragColor = vec4(finalColor, 1.0 - transmittance);

	
}

	
		