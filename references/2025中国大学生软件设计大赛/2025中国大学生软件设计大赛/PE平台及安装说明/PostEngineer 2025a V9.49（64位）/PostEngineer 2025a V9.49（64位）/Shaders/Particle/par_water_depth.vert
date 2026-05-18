#version 330
#extension GL_EXT_gpu_shader4 : enable


layout (location = 0) in vec3 position;
layout (location = 1) in float age;
layout (location = 2) in float randVal;
layout (location = 3) in float rotation;
layout (location = 4) in vec3 velocity;
layout (location = 5) in vec2 pipePos;
layout (location = 6) in float type;

uniform mat4 objectToWorld;
uniform mat4 projection;

out vec3 position0;
out float age0;
out float randVal0;
out float rotation0;
out vec3 velocity0;
out vec2 pipePos0;
out float type0;

out mat4 projection0;


void main() 
{
    
    position0 = (objectToWorld * vec4(position, 1)).xyz;
    age0 = age;
    randVal0 = randVal;
    rotation0 = rotation;
	velocity0 = (objectToWorld * vec4(velocity, 0)).xyz;
	pipePos0 = pipePos;
	type0 = type;
	
	projection0 = projection;
}


