#version 330

layout (location = 0) in vec3 Vertex;

uniform mat4 modelview;
uniform mat4 projection;
uniform mat4 objectToWorld;

out vec3 direction;
out vec3 worldP;

void main()
{
	vec4 P = (objectToWorld * vec4(Vertex.xyz, 1.0));
	gl_Position = projection * modelview * P;
	direction = Vertex;
	worldP = P.xyz;
}
