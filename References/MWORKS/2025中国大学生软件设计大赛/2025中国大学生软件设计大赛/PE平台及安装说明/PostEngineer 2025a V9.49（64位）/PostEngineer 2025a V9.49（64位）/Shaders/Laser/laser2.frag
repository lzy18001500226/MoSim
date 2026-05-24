#version 330 core

layout (location = 0) out vec4  FragColor;   

uniform int drawBack;
uniform vec2 gNearFar;
uniform sampler2D backDepthTexture;
uniform float maxThickness;
uniform vec3 laserColor;

uniform float width1;
uniform float height1;
uniform float width2;
uniform float height2;

uniform vec2 exposure;

uniform vec3 start;
uniform vec3 end;
uniform vec3 right;

uniform vec3 normal1;
uniform vec3 normal2;

uniform vec3 boundNormal1;
uniform vec3 boundNormal2;
uniform vec2 boundOffset;

uniform int sectionType;


in vec3 pos;

float LinearizeDepth(float depth)
{
    float z = depth * 2.0 - 1.0; // 回到NDC
    return (2.0 * gNearFar.x * gNearFar.y) / (gNearFar.y + gNearFar.x - z * (gNearFar.y - gNearFar.x));    
}

void main()
{	

	if(drawBack == 1){
		FragColor.r = LinearizeDepth(gl_FragCoord.z);
	}
	else{
		vec2 screenSize = textureSize(backDepthTexture, 0);
		vec2 uv = gl_FragCoord.xy / screenSize;

		float depth = texture(backDepthTexture, uv).x - LinearizeDepth(gl_FragCoord.z);
		float alpha = depth/maxThickness;

		if(alpha < 0) discard;

		vec3 forward = normalize(end - start);
		vec3 up = cross(right, forward);

		float E = max(height1, max(height2, max(width1, width2))) * 0.0001;

		
		if( length(boundNormal1) > 1e-6 && dot(pos - start, -boundNormal1)  > boundOffset.x + E) discard;

		if( length(boundNormal2) > 1e-6 && dot(pos - end, -boundNormal2)  > boundOffset.y +  E) discard;

		if( dot(pos - start, normal1)  > E  ||  dot(pos - end, normal2)  > E ) discard;

		float len_scale = dot(pos - start, forward) / distance(start, end);

		//无明显高光
		if(sectionType == 0)
			alpha = clamp(pow(alpha, 2) * 10, 0.0, 1.0);
		else
			alpha = clamp(pow(alpha, 2) * 1.2 , 0.0, 1.2);

		//有明显高光
		//if(sectionType == 0)  alpha += 0.1;


		//float sqr = sqrt(2.0);
		float d1 = dot( pos - start, right );
		float d2 = dot( pos - start, up );

		float dis2 = d1*d1 + d2*d2;

		float elen1 = (width1*width1 + height1*height1)/4;
		float elen2 = (width2*width2 + height2*height2)/4;

		float elen = elen1 + (elen2 - elen1) * len_scale;
		
		float edge = max(dis2/elen - 0.8, 0);

		float scale = clamp(len_scale, 0, 1);
		float e = exposure.x + (exposure.y - exposure.x) * scale;

		vec3 newLaserColor = laserColor * (edge + 1.0) * e * alpha;
		if(newLaserColor.x > 1.0){
			newLaserColor.y += (newLaserColor.x - 1.0) * 0.8;
			newLaserColor.z += (newLaserColor.x - 1.0) * 0.8;
			newLaserColor.x = 1.0;
		}
		/*if(newLaserColor.y > 1.0){
			newLaserColor.z += (newLaserColor.y - 1.0) * 0.8;
			newLaserColor.y = 1.0;
		}*/
		if(newLaserColor.z > 1.0){
			newLaserColor.x += (newLaserColor.z - 1.0) * 0.8;
			newLaserColor.y += (newLaserColor.z - 1.0) * 0.8;
			newLaserColor.z = 1.0;
		}

		//FragColor = vec4(newLaserColor,  min(pow(alpha, 2) * f1 * f2 * 4, 1.0)) * e;
		FragColor = vec4(newLaserColor,  min((alpha + edge), 1.0));
	}	


}