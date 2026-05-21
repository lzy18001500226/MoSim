#version 330

layout (location = 0) in vec3 Vertex;
layout (location = 1) in vec3 Normal;

uniform mat4 modelview;
uniform mat4 projection;

uniform mat4 modelToWorld;

out vec3 vertex;
out vec3 normal;
out vec3 viewPos;

void main()
{
	//vec4 Pos = modelview * modelToWorld * vec4(Vertex.xyz, 1.0);
	vec4 Pos = modelview * vec4(Vertex.xyz, 1.0);
	viewPos = Pos.xyz;
	//vertex = (modelToWorld * vec4(Vertex.xyz, 1.0)).xyz;
	//normal = (modelToWorld * vec4(Normal.xyz, 0.0)).xyz;
	vertex = Vertex.xyz;
	normal = Normal.xyz;

	gl_Position = projection * Pos;
}
