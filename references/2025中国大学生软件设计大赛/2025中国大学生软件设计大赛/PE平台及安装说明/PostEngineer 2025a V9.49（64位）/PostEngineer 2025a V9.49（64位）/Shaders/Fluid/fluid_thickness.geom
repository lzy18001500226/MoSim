#version 330
#extension GL_EXT_gpu_shader4 : enable


layout (points) in;
layout (triangle_strip) out;
layout (max_vertices = 4) out;

const float PI = 3.1415926;



uniform float particleRadius;


in vec3 viewPos[];
in mat4 projection0[];

out vec2 TexCoord;


out float disCP;
out vec3 viewCenterPos;
out vec3 fragPos;
out mat4 projection;


void main() 
{
	vec3 Pos = viewPos[0];	
	
	projection = projection0[0];
	
	disCP = particleRadius;
   
		
	viewCenterPos = Pos;
	
	fragPos = Pos + vec3(-particleRadius, -particleRadius, 0);
	gl_Position = projection * vec4(fragPos, 1.0);
	TexCoord = vec2(1.0, 0.0);
	EmitVertex();
    
	fragPos = Pos + vec3(particleRadius, -particleRadius, 0);
	gl_Position = projection * vec4(fragPos, 1.0);
	TexCoord = vec2(1.0, 1.0);
	EmitVertex();
    
	fragPos = Pos + vec3(-particleRadius, particleRadius, 0);
	gl_Position = projection * vec4(fragPos, 1.0);
	TexCoord = vec2(0.0, 0.0);
	EmitVertex();
    
	fragPos = Pos + vec3(particleRadius, particleRadius, 0);
	gl_Position = projection * vec4(fragPos, 1.0);
	TexCoord = vec2(0.0, 1.0);
	EmitVertex();
	EndPrimitive();
    
}
