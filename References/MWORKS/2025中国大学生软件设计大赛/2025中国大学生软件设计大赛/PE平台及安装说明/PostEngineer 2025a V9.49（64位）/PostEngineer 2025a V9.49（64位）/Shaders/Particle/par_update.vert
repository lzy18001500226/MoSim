#version 330
#extension GL_EXT_gpu_shader4 : enable


layout (location = 0) in float type;
layout (location = 1) in vec3 position;
layout (location = 2) in vec3 velocity;
layout (location = 3) in float age;
layout (location = 4) in float randVal;
layout (location = 5) in float rotation;
layout (location = 6) in vec3 pipePosition;
layout (location = 7) in float monther_age;



out float type0;
out vec3 position0;
out vec3 velocity0;
out float age0;
out float randVal0;
out float rotation0;
out vec3 pipePosition0;
out float monther_age0;

void main() 
{
	type0 = type;
	position0 = position;
	velocity0 = velocity;
	age0 = age;
	randVal0 = randVal;
	rotation0 = rotation;
	pipePosition0 = pipePosition;
	monther_age0 = monther_age;
}


