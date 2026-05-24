#version 330
#extension GL_EXT_gpu_shader4 : enable


layout (points) in;
layout (triangle_strip) out;
layout (max_vertices = 4) out;

const float PI = 1.1415926;


uniform mat4 objectToWorld;
uniform mat4 gModelView;
uniform mat4 gProjection;
uniform mat4 gMvp;
uniform mat4 gOrtho;

uniform vec2 baseSize;
uniform int  boardType;

uniform vec3 gCameraPos;
uniform vec3 gVertical;


in vec4 position0[];

out vec2 TexCoord;


void main() 
{
	vec3  Pos = (objectToWorld * vec4(position0[0].xyz, 1)).xyz;
	
	vec2 size = position0[0].w * baseSize;
	
	vec3 toCamera = normalize(gCameraPos - Pos);
    vec3 up = gVertical;
   	 vec3 right = normalize(cross(toCamera, up));
   
    if(boardType == 0){
    
		vec4 FP = gProjection * gModelView * vec4(Pos, 1.0);
		Pos = FP.xyz / FP.w;
		
		right = vec3(-1, 0, 0);
		up = vec3(0, 1, 0);
		
		Pos -= right * 0.5 * size.x;
		Pos -= up * 0.5 * size.y;
		gl_Position = vec4(Pos, 1.0);
		TexCoord = vec2(1.0, 0.0);
		EmitVertex();
	    
		Pos += up * size.y;
		gl_Position = vec4(Pos, 1.0);
		TexCoord = vec2(1.0, 1.0);
		EmitVertex();
	    
		Pos -= up * size.y;
		Pos += right * size.x;
		gl_Position = vec4(Pos, 1.0);
		TexCoord = vec2(0.0, 0.0);
		EmitVertex();
	    
		Pos += up * size.y;
		gl_Position = vec4(Pos, 1.0);
		TexCoord = vec2(0.0, 1.0);
		EmitVertex();
		EndPrimitive();
    }
    else if(boardType <= 2){
		Pos -= right * 0.5 * size.x;
		Pos -= up * 0.5 * size.y;
		gl_Position = gMvp * vec4(Pos, 1.0);
		TexCoord = vec2(1.0, 0.0);
		EmitVertex();
	    
		Pos += up * size.y;
		gl_Position = gMvp * vec4(Pos, 1.0);
		TexCoord = vec2(1.0, 1.0);
		EmitVertex();
	    
		Pos -= up * size.y;
		Pos += right * size.x;
		gl_Position = gMvp * vec4(Pos, 1.0);
		TexCoord = vec2(0.0, 0.0);
		EmitVertex();
	    
		Pos += up * size.y;
		gl_Position = gMvp * vec4(Pos, 1.0);
		TexCoord = vec2(0.0, 1.0);
		EmitVertex();
		EndPrimitive();
	}
	else if(boardType == 3){
		Pos -= right * 0.5 * size.x;
		Pos -= up * 0.5 * size.y;
		gl_Position = gMvp * vec4(Pos, 1.0);
		TexCoord = vec2(1.0, 0.0);
		EmitVertex();
	    
		Pos += up * size.y;
		gl_Position = gMvp * vec4(Pos, 1.0);
		TexCoord = vec2(1.0, 1.0);
		EmitVertex();
	    
		Pos -= up * size.y;
		Pos += right * size.x;
		gl_Position = gMvp * vec4(Pos, 1.0);
		TexCoord = vec2(0.0, 0.0);
		EmitVertex();
	    
		Pos += up * size.y;
		gl_Position = gMvp * vec4(Pos, 1.0);
		TexCoord = vec2(0.0, 1.0);
		EmitVertex();
		EndPrimitive();
	}

}
