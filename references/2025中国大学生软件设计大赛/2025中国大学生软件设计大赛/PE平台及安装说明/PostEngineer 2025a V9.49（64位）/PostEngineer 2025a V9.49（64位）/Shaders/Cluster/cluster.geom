#version 330
#extension GL_EXT_gpu_shader4 : enable


layout (points) in;
layout (triangle_strip) out;
layout (max_vertices = 4) out;

const float PI = 3.1415926;


uniform mat4 objectToWorld;
uniform mat4 modelview;
uniform mat4 projection;
uniform mat4 VP;

uniform vec3 cameraPos;
uniform int  boardType;


in vec4 position0[];
in vec4 shape0[];


out vec2 TexCoord;
out float transparency;
out float texIndex;
out float brightness;



void main() 
{
	
	vec3  Pos = (objectToWorld * vec4(position0[0].xyz, 1)).xyz;
	
	float angle = position0[0].w;
	transparency = shape0[0].z;
	texIndex = shape0[0].w;
	
	//if(colorSettings.m_count == 0) Color = vec3(1.0, 1.0, 1.0);
	//else Color = GetParamSettinsValue(colorSettings, age, pipePosition0[0].y, randVal);

	vec2 size = shape0[0].xx;
 	brightness = shape0[0].y;
	
	vec3 toCamera = normalize(cameraPos - Pos);
    vec3 up = vec3(0.0, 1.0, 0.0);
    vec3 right = normalize(cross(toCamera, up));
 
   
    if(boardType == 0){
    
		mat4 rotMat;
		float angleRad = angle*PI / 180.0;
		rotMat[0] = vec4( cos(angleRad), sin(angleRad), 0.0, 0 );
		rotMat[1] = vec4( -sin(angleRad), cos(angleRad), 0.0,0 );
		rotMat[2] = vec4( 0.0, 0.0, 1.0, 0 );
		rotMat[3] = vec4( 0.0, 0.0, 0.0, 1.0 );
   
		Pos = (modelview * vec4(Pos, 1.0)).xyz;
		
		right = (rotMat * vec4(-1, 0, 0, 1)).xyz;
		up = (rotMat * vec4(0, 1, 0, 1)).xyz;
		
		Pos -= right * 0.5 * size.x;
		Pos -= up * 0.5 * size.y;
		gl_Position = projection * vec4(Pos, 1.0);
		TexCoord = vec2(1.0, 0.0);
		EmitVertex();
	    
		Pos += up * size.y;
		gl_Position = projection * vec4(Pos, 1.0);
		TexCoord = vec2(1.0, 1.0);
		EmitVertex();
	    
		Pos -= up * size.y;
		Pos += right * size.x;
		gl_Position = projection * vec4(Pos, 1.0);
		TexCoord = vec2(0.0, 0.0);
		EmitVertex();
	    
		Pos += up * size.y;
		gl_Position = projection * vec4(Pos, 1.0);
		TexCoord = vec2(0.0, 1.0);
		EmitVertex();
		EndPrimitive();
    }
    else {
		Pos -= right * 0.5 * size.x;
		Pos -= up * 0.5 * size.y;
		gl_Position = VP * vec4(Pos, 1.0);
		TexCoord = vec2(1.0, 0.0);
		EmitVertex();
	    
		Pos += up * size.y;
		gl_Position = VP * vec4(Pos, 1.0);
		TexCoord = vec2(1.0, 1.0);
		EmitVertex();
	    
		Pos -= up * size.y;
		Pos += right * size.x;
		gl_Position = VP * vec4(Pos, 1.0);
		TexCoord = vec2(0.0, 0.0);
		EmitVertex();
	    
		Pos += up * size.y;
		gl_Position = VP * vec4(Pos, 1.0);
		TexCoord = vec2(0.0, 1.0);
		EmitVertex();
		EndPrimitive();
	}

}
