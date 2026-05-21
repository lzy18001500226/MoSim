#version 330
#extension GL_EXT_gpu_shader4 : enable

#ifdef _VERTEX_

uniform mat4 modelview;
uniform mat4 projection;

layout (location = 0) in vec3 position;

void main() 
{
    gl_Position = modelview * projection * vec4(position, 1);
}

#endif



#ifdef _GEOMETRY_

layout (points) in;
layout (points) out;
layout (max_vertices = 3) out;

in vec3 position0[];
out vec3 position1;

void main() 
{
	position1 = position0[0];
	EmitVertex();
	EndPrimitive();
}

#endif



#ifdef _FRAGMENT_
uniform sampler2D particleSampler;

void main() 
{
    gl_FragColor.rgba = vec4(1, 0, 0, 1); //texture2D(particleSampler, gl_PointCoord.xy);
}

#endif
