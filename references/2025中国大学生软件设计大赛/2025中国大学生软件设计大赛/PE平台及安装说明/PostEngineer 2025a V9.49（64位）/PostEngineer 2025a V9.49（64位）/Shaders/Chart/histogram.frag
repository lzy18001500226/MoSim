
uniform int width;
uniform int height;
uniform int glowSize;

varying vec3 vPosition;
varying vec3 vColor;

void main()
{         
	gl_FragColor.xyz = vColor;
	gl_FragColor.w = 1;

/*	float glowStrength = 0.8;
	if(vPosition.x < glowSize) {
		float s1 = (vPosition.x)/glowSize;
		float s2 = 1;
		if(vPosition.y < glowSize) s2 = 0.5 + vPosition.y/glowSize*0.5;
		else if(vPosition.y > height) s2 = 0.5+ (1 - (vPosition.y - height) / glowSize)*0.5;

		gl_FragColor.w = 0;//s1*s2 * glowStrength;
	}
	else if(vPosition.x > width+glowSize) {
		float s1 = 1 - (vPosition.x - width - glowSize)/glowSize;
		float s2 = 1;
		if(vPosition.y < glowSize)  s2 = 0.5 + vPosition.y/glowSize*0.5;
		else if(vPosition.y > height) s2 = 0.5+ (1 - (vPosition.y - height) / glowSize)*0.5;

		gl_FragColor.w = 0;//s1*s2 * glowStrength;
	}
	
	if(vPosition.y > height) {
		float s1 = 1 - (vPosition.y - height)/glowSize;
		float s2 = 1;
		float s3 = (vPosition.x - (glowSize + width/2))/(glowSize + width/2);
		if(vPosition.x < glowSize)  s2 = 1 - (glowSize - vPosition.x)/glowSize;
		else if(vPosition.x > width+glowSize) s2 = (1 - (vPosition.x - width-glowSize) / glowSize);

		gl_FragColor.w = 0;//s1 * s2 * glowStrength*(1-s3*s3);
	}

	if((vPosition.y > height - glowSize) && ( vPosition.x < glowSize || vPosition.x > width+glowSize ||  vPosition.y > height)) {
		//gl_FragColor.w *= 0.8 + (1 - (vPosition.y - height+glowSize)/glowSize)*0.2;
	}*/
	
}

	
	
		