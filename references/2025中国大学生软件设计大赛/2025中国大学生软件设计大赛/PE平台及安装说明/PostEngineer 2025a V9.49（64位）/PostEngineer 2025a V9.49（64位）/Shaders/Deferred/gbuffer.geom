#version 330
#extension GL_EXT_gpu_shader4 : enable


layout (triangles) in;
layout (triangle_strip) out;
layout (max_vertices = 3) out;


uniform int isFaceNormal;
//uniform mat4 gMvpInv;

in vec3 vPosition_0[];
in vec3 vNormal_0[];
in vec3 vColor_0[];
in vec3 vVertex_0[];

in vec4 ClipSpacePos0_0[];
in vec4 PrevClipSpacePos0_0[];

in vec2 vTexcoordPrimitive_0[];
in vec2 vTexcoord_0[];
in vec2 vTexcoord2_0[];
in vec2 vTexcoord3_0[];
in vec2 vTexcoordSpec_0[];
in vec2 vTexcoordNorm_0[];
in vec2 vTexcoordAO_0[];


out vec3 vPosition;
out vec3 vNormal;
out vec3 vColor;

out vec4 ClipSpacePos0;
out vec4 PrevClipSpacePos0;

out vec2 vTexcoordPrimitive;
out vec2 vTexcoord;
out vec2 vTexcoord2;
out vec2 vTexcoord3;
out vec2 vTexcoordSpec;
out vec2 vTexcoordNorm;
out vec2 vTexcoordAO;


void main() 
{
	vec3 faceNormal;
	//vec3 a = vec3(gl_in[0].gl_Position) - vec3(gl_in[1].gl_Position);
	//vec3 b = vec3(gl_in[2].gl_Position) - vec3(gl_in[1].gl_Position);
	//faceNormal = -(gMvpInv * vec4(normalize(cross(b,a)), 0)).xyz;

	if(isFaceNormal == 1){
		vec3 a = vec3(vVertex_0[0]) - vec3(vVertex_0[1]);
		vec3 b = vec3(vVertex_0[2]) - vec3(vVertex_0[1]);
		faceNormal = normalize(cross(b,a));
	}


	vPosition = vPosition_0[0];
	vNormal = isFaceNormal == 1? faceNormal : vNormal_0[0];
	vColor = vColor_0[0];

	ClipSpacePos0 = ClipSpacePos0_0[0];
	PrevClipSpacePos0 = PrevClipSpacePos0_0[0];

	vTexcoordPrimitive = vTexcoordPrimitive_0[0];
	vTexcoord = vTexcoord_0[0];
	vTexcoord2 = vTexcoord2_0[0];
	vTexcoord3= vTexcoord3_0[0];
	vTexcoordSpec = vTexcoordSpec_0[0];;
	vTexcoordNorm = vTexcoordNorm_0[0];;
	vTexcoordAO = vTexcoordAO_0[0];;

	gl_Position = gl_in[0].gl_Position;
	EmitVertex();

    
	vPosition = vPosition_0[1];
	vNormal = isFaceNormal == 1? faceNormal : vNormal_0[1];
	vColor = vColor_0[1];

	ClipSpacePos0 = ClipSpacePos0_0[1];
	PrevClipSpacePos0 = PrevClipSpacePos0_0[1];

	vTexcoordPrimitive = vTexcoordPrimitive_0[1];
	vTexcoord = vTexcoord_0[1];
	vTexcoord2 = vTexcoord2_0[1];
	vTexcoord3= vTexcoord3_0[1];
	vTexcoordSpec = vTexcoordSpec_0[1];
	vTexcoordNorm = vTexcoordNorm_0[1];
	vTexcoordAO = vTexcoordAO_0[1];

	gl_Position = gl_in[1].gl_Position;
	EmitVertex();

    
	vPosition = vPosition_0[2];
	vNormal = isFaceNormal == 1? faceNormal : vNormal_0[2];
	vColor = vColor_0[2];

	ClipSpacePos0 = ClipSpacePos0_0[2];
	PrevClipSpacePos0 = PrevClipSpacePos0_0[2];

	vTexcoordPrimitive = vTexcoordPrimitive_0[2];
	vTexcoord = vTexcoord_0[2];
	vTexcoord2 = vTexcoord2_0[2];
	vTexcoord3= vTexcoord3_0[2];
	vTexcoordSpec = vTexcoordSpec_0[2];
	vTexcoordNorm = vTexcoordNorm_0[2];
	vTexcoordAO = vTexcoordAO_0[2];

	gl_Position = gl_in[2].gl_Position;
	EmitVertex();

	EndPrimitive();
    
}
