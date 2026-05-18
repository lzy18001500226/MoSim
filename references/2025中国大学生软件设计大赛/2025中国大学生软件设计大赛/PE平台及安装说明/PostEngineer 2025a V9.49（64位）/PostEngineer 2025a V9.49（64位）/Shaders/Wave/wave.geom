#version 330
#extension GL_EXT_gpu_shader4 : enable


layout (lines) in;
layout (triangle_strip) out;
layout (max_vertices = 10) out;

const float PI = 1.1415926;

uniform mat4 modelview;
uniform mat4 projection;
uniform mat4 VP;

uniform float width;
uniform float ratio;
uniform float scale;

uniform float totalLength;

uniform float displace;

uniform vec3 cameraPos;
uniform vec3 normal;


in vec3 position0[];
in float length0[];
in vec3 left0[];
in vec3 right0[];


out vec3 vPos;

flat out vec3 oPos1;
flat out float oLen;
flat out vec3 oDir;
flat out vec3 oRight;
flat out vec2 oWidth;
flat out float oBaseCoord;


out vec4 TexCoord;
out float age;


vec3 MakeOrtho(vec3 n)
{
	vec3 v;
	float maxv = abs(n[0]);
	int mi=0;
	for(int i=1; i<3; i++)
	{
		if(abs(n[i]) > maxv)
		{
			maxv = abs(n[i]);
			mi = i;
		}
	}

	if(mi == 0)
	{
		v[0] = -n[1]/n[0] - n[2]/n[0];
    	v[1] = 1.0;
    	v[2] = 1.0;
	}
	else if(mi == 1)
	{
		v[1] = -n[0]/n[1] - n[2]/n[1];
    	v[0] = 1.0;
    	v[2] = 1.0;
	}
	else if(mi == 2)
	{
		v[2] = -n[0]/n[2] - n[1]/n[2];
    	v[0] = 1.0;
    	v[1] = 1.0;
	}
	
	return normalize(v);
}

void main() 
{
	
	vec3  Pos1 = position0[0].xyz;
	vec3  Pos2 = position0[1].xyz;
	vec3  center = (Pos1+Pos2) / 2;
	vec3 dir = normalize(Pos2 - Pos1);

	float L1 = length0[0];
	float L2 = length0[1];

	///计算相机到直线的垂线
			/*vec3 cameraToPos1 = cameraPos - Pos1;
			vec3 cameraToPos2 = cameraPos - Pos2;

			float dotv1 = dot(cameraToPos1, dir);
			float dotv2 = dot(cameraToPos2, dir);

			vec3 proj;
			if( dotv1 * dotv2 > 0 ){
				if( abs(dotv1) < abs(dotv2) )  proj = Pos1;
				else proj = Pos2;
			}
			else{
				proj = Pos1 + dotv1 * dir;
			}

	
			vec3 toCamera = cameraPos - proj;

			vec3 normal = normalize(toCamera);*/

			/*vec3 cameraToPos1 = cameraPos - Pos1;
			float dotv1 = dot(cameraToPos1, dir);
			vec3 proj = Pos1 + dotv1 * dir;
			vec3 normal = normalize(cameraPos - proj);*/

	float ndv = dot(normal, dir);
	vec3 local_normal = normalize(normal - ndv*dir);

	vec3 binormal = normalize(cross(local_normal, dir));

	oPos1 = Pos1;
	oDir = dir;
	oRight = -binormal;
	oLen = L2 - L1;

	///左边计算left到绘图平面的投影，再计算中分线
	vec3 middle1, middle2;
	float mdv1 = 1, mdv2 = 1;

	if( length(left0[0]) < 0.0001 ){
		middle1 = binormal;
	}
	else{
		float dv = dot(left0[0], local_normal);
		vec3 left_proj = normalize(left0[0] - dv*local_normal);
		middle1 = normalize( (-left_proj + dir) / 2);

		mdv1 = dot(middle1, binormal);
		if( mdv1 < 0 ){
			middle1 = -middle1;
			mdv1 = - mdv1;
		}
	}

	if( length(right0[1]) < 0.0001 ){
		middle2 = binormal;
	}
	else{
		float dv = dot(right0[1], local_normal);
		vec3 right_proj = normalize(right0[1] - dv*local_normal);
		middle2 = normalize( (-dir + right_proj) / 2);

		mdv2 = dot(middle2, binormal);
		if( mdv2 < 0 ){
			middle2 = -middle2;
			mdv2 = - mdv2;
		}
	}

			//middle1 = binormal;
			//middle2 = binormal;
			//mdv1 = 1;
			//mdv2 = 1;


	mdv1 = max(mdv1, 0.0001);
	mdv2 = max(mdv2, 0.0001);

	float s1 = ( 1.0 + L1/width * (scale - 1.0) );
	float s2 = ( 1.0 + L2/width * (scale - 1.0) );

	float width1 = width * s1;
	float width2 = width * s2;

	oWidth = vec2(width1, width2);

	vec3 W1b = binormal * width1/2;
	vec3 W2b = binormal * width2/2;

	vec3 W1 = middle1 * width1/2 / mdv1;
	vec3 W2 = middle2 * width2/2 / mdv2;

	float dW1 = dot(W1 - W1b, dir);
	float dW2 = dot(W2 - W2b, dir);

	vec3 dL = dir * (L2 - L1) / 2;

	float baseCoord = (displace + L1)/(width*ratio);
	float newCoord = (displace + L2)/(width*ratio);

	oBaseCoord = baseCoord;

	float age1 = L1 / totalLength;
	float age2 = L2 / totalLength;
	

	///P2
	age = age2;
	vec3 newPos = center + W2 + dL;
	vPos = newPos;

	newPos = (modelview * vec4(newPos, 1.0)).xyz;
	gl_Position = projection * vec4(newPos, 1.0);
	TexCoord = vec4(newCoord + dW2/width2/ratio, 1.0,  0.0, 1.0);
	EmitVertex();


	///P0
	age = age1;
	newPos = center + W1 - dL;
	vPos = newPos;
	newPos = (modelview * vec4(newPos, 1.0)).xyz;
	gl_Position = projection * vec4(newPos, 1.0);

	TexCoord = vec4(baseCoord + dW1/width1/ratio, 1.0,  0.0, 1.0);
	EmitVertex();


	///P4 : M1->
	age = age2;
	newPos = center + dL;
	vPos = newPos;
	newPos = (modelview * vec4(newPos, 1.0)).xyz;
	gl_Position = projection * vec4(newPos, 1.0);

	TexCoord = vec4(newCoord + width2, 0.5*width2,  0.0, width2);
	EmitVertex();


	////P1
	age = age1;
	newPos = center - W1 - dL;
	vPos = newPos;
	newPos = (modelview * vec4(newPos, 1.0)).xyz;
	gl_Position = projection * vec4(newPos, 1.0);

	TexCoord = vec4(baseCoord - dW1/width1/ratio, 0.0,  0.0, 1.0);
	EmitVertex();


	///P3
	age = age2;
	newPos = center - W2 + dL;
	vPos = newPos;
	newPos = (modelview * vec4(newPos, 1.0)).xyz;
	gl_Position = projection * vec4(newPos, 1.0);

	TexCoord = vec4(newCoord - dW2/width2/ratio, 0,  0.0, 1.0);
	EmitVertex();
	

}
