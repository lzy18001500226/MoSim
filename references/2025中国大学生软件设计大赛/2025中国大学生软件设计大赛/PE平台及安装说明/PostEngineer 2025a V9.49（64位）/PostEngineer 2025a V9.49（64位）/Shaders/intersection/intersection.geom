#version 330 core


layout (triangles) in;
layout (triangle_strip, max_vertices = 3) out;


uniform vec4 clipPlanes[3];
uniform int clipPlaneCount;

uniform int flag;

in vec3 vWorldPos0[];
out vec3 vWorldPos;

void main() 
{
	if(flag == 0x0200){
	
		int iOutside = 0;
		for(int i=0; i<3; i++){
			for(int k=0; k<clipPlaneCount; k++){
				float d = dot(clipPlanes[k].xyz, vWorldPos0[i]) + clipPlanes[k].w;
				if(d < 0){
					iOutside++;
				}
			}
		}

		if(iOutside == 3) return;
	}
   
    gl_Position = gl_in[0].gl_Position;
	vWorldPos = vWorldPos0[0];
	EmitVertex();

	gl_Position = gl_in[1].gl_Position;
	vWorldPos = vWorldPos0[1];
	EmitVertex();

	gl_Position = gl_in[2].gl_Position;
	vWorldPos = vWorldPos0[2];
	EmitVertex();

	EndPrimitive();
}
