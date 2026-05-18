#version 120


varying vec3 vPosition;
varying vec3 vNormal;

void main()
{         
	float factor = (vNormal.x+45)/270.0; 

	vec3 color1 = vec3(0, 0.6, 1);
	vec3 color2 = vec3(1, 0.2, 0.0);

	gl_FragColor.xyz = color1*factor + color2*(1-factor);

/*	if(factor > 0.5){
		gl_FragColor.x = (factor-0.5)*2;
		gl_FragColor.y = 1 - (factor-0.5)*2;
		gl_FragColor.z = 1 - (factor-0.5)*2;
	}
	else{
		gl_FragColor.x = 0;
		gl_FragColor.y = 0.2+factor*2*0.8;
		gl_FragColor.z = 0.2+factor*2*0.8;
	}*/

	gl_FragColor.w = 1.0;
	if(vNormal.z < 0.25)
		gl_FragColor.w = 0.5+vNormal.z*2;

	gl_FragColor.w = 0.95;
	
}

	
	
		