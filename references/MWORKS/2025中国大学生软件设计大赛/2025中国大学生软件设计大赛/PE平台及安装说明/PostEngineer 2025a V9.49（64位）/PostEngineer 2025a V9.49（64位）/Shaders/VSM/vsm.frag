#version 130

uniform float shadow_distance_scale;
uniform int shadow_c_count;

varying vec3 ViewPos;
varying vec4 v_pos; 

void main()
{
	//float depth =  v_pos.z / v_pos.w;
	//depth = depth*0.5 + 0.5;
	float depth = length(ViewPos) * shadow_distance_scale;
	float moment1 = exp(shadow_c_count*depth);
	float moment2 = exp(2*shadow_c_count*depth);
	//float dx = dFdx(depth);
	//float dy = dFdy(depth);
	//moment2 += 0.25*(dx*dx + dy*dy);

	gl_FragColor = vec4( moment1,  moment2,  1.0,  1.0  );
}

	
	
		