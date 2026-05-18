#version 330

layout (location = 0) in vec3 Vertex;

uniform mat4 modelview;
uniform mat4 projection;
uniform mat4 modelToWorld;

out vec3 direction;

void main()
{
	gl_Position = projection * modelview * modelToWorld * vec4(Vertex.xyz, 1.0);
	direction = Vertex;
}
