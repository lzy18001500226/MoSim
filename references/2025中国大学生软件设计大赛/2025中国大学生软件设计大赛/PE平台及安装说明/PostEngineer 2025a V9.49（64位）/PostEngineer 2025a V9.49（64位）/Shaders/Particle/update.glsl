//#version 330
#extension GL_EXT_gpu_shader4 : enable


#ifdef _VERTEX_

layout (location = 0) in int type;
layout (location = 1) in vec3 position;
layout (location = 2) in vec3 velocity;
layout (location = 3) in float age;

out int type0;
out vec3 position0;
out vec3 velocity0;
out float age0;

void main() 
{
	type0 = type;
	position0 = position;
	velocity0 = velocity;
	age0 = age;
}

#endif


#ifdef _GEOMETRY_

layout (points) in;
layout (points) out;
layout (max_vertices = 30) out;

in int type0[];
in vec3 position0[];
in vec3 velocity0[];
in float age0[];


out int type1;
out vec3 position1;
out vec3 velocity1;
out float age1;
out float dir1;

uniform float time;
uniform float delta_time;
uniform float life;
uniform float life2;
uniform float launchLife;

uniform vec3 cameraDir;

uniform vec3 iniPos;
uniform vec3 iniVelo;

uniform vec3 fieldForce;
uniform float mass;
uniform float resistFactor;
uniform float randFactor;

uniform sampler1D randSampler;


vec3 GetRandomDir(float texCoord)
{
	vec3 dir = texture(randSampler, texCoord).xyz;
	dir -= vec3(0.5, 0.5, 0.5);
	return dir;
}

void main() 
{
	vec3 randDir = GetRandomDir(time*1000);
	
    if(type0[0] == 1)
    {
		///·¢ÉäÁ£×Ó
		if(age0[0] >= launchLife){
		
			type1 = 2;
			position1 = iniPos;
			velocity1 = iniVelo;
			age1 = 0;
			
			EmitVertex();
			EndPrimitive();
		
			type1 = type0[0];
			position1 = position0[0];
			velocity1 = velocity0[0];
			age1 = 0;
			EmitVertex();
			EndPrimitive();
		}
		else if(age0[0] >= 0){
			type1 = type0[0];
			position1 = position0[0];
			velocity1 = velocity0[0];
			age1 = age0[0] + delta_time;
			EmitVertex();
			EndPrimitive();
		}
    }
    else if(type0[0] == 2 && age0[0] < life){
		
		vec3 randForce = length(fieldForce) * randFactor * (randDir.x + 0.5) * randDir;
		vec3 resistForce = -resistFactor * velocity0[0] * length(velocity0[0]);
		vec3 acc = (fieldForce + randForce + resistForce) / mass + vec3(0, -1, 0)*0.98;
			
		type1 = type0[0];
		position1 = position0[0] + velocity0[0] * delta_time;
		velocity1 = velocity0[0] + acc * delta_time;
		age1 = age0[0] + delta_time;
		vec3 velo_dir = normalzie(velocity0[0]);
		dir1 = velo_dir - cameraDir * dot(velo_dir, cameraDir);
		
		EmitVertex();
		EndPrimitive();
    }
}

#endif

#ifdef _FRAGMENT_

void main() 
{
    
}

#endif