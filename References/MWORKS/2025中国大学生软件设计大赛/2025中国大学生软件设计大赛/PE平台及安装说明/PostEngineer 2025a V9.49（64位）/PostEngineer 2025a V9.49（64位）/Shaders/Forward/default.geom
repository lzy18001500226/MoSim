#version 330
#extension GL_EXT_gpu_shader4 : enable


layout (triangles) in;
layout (triangle_strip) out;
layout (max_vertices = 3) out;


uniform int isFaceNormal;
//uniform mat4 gMvpInv;

in vec4 projectorTexCoord_0[];

in vec2 oTexcoord0_0[];
in vec2 oTexcoord1_0[];
in vec2 oTexcoord2_0[];

in vec2 oTexcoordSpec_0[];
in vec2 oTexcoordNorm_0[];
in vec2 oTexcoordAO_0[];

in vec3 worldP_0[];
in vec3 worldP_no_offset_0[];

in vec3 vColor_0[];
in vec3 vPosition_0[];
in vec3 vNormal_0[];



out vec4 projectorTexCoord;

out vec2 oTexcoord0;
out vec2 oTexcoord1;
out vec2 oTexcoord2;

out vec2 oTexcoordSpec;
out vec2 oTexcoordNorm;
out vec2 oTexcoordAO;

out vec3 worldP;
out vec3 worldP_no_offset;

out vec3 vColor;
out vec3 vPosition;
out vec3 vNormal;


void main() 
{

	vec3 faceNormal;
	//vec3 a = vec3(gl_in[0].gl_Position) - vec3(gl_in[1].gl_Position);
	//vec3 b = vec3(gl_in[2].gl_Position) - vec3(gl_in[1].gl_Position);
	//faceNormal = -(gMvpInv * vec4(normalize(cross(b,a)), 0)).xyz;

	if(isFaceNormal == 1){
		vec3 a = vPosition_0[0] - vPosition_0[1];
		vec3 b = vPosition_0[2] - vPosition_0[1];
		faceNormal = normalize(cross(b,a));
	}

	projectorTexCoord = projectorTexCoord_0[0];

	oTexcoord0 = oTexcoord0_0[0];
	oTexcoord1 = oTexcoord1_0[0];
	oTexcoord2 = oTexcoord2_0[0];

	oTexcoordSpec = oTexcoordSpec_0[0];
	oTexcoordNorm = oTexcoordNorm_0[0];
	oTexcoordAO = oTexcoordAO_0[0];

	worldP = worldP_0[0];
	worldP_no_offset = worldP_no_offset_0[0];

	vColor = vColor_0[0];
	vPosition = vPosition_0[0];
	vNormal = isFaceNormal == 1? faceNormal : vNormal_0[0];

	gl_Position = gl_in[0].gl_Position;
	EmitVertex();

    
	projectorTexCoord = projectorTexCoord_0[1];

	oTexcoord0 = oTexcoord0_0[1];
	oTexcoord1 = oTexcoord1_0[1];
	oTexcoord2 = oTexcoord2_0[1];

	oTexcoordSpec = oTexcoordSpec_0[1];
	oTexcoordNorm = oTexcoordNorm_0[1];
	oTexcoordAO = oTexcoordAO_0[1];

	worldP = worldP_0[1];
	worldP_no_offset = worldP_no_offset_0[1];

	vColor = vColor_0[1];
	vPosition = vPosition_0[1];
	vNormal = isFaceNormal == 1? faceNormal : vNormal_0[1];

	gl_Position = gl_in[1].gl_Position;
	EmitVertex();

    
	projectorTexCoord = projectorTexCoord_0[2];

	oTexcoord0 = oTexcoord0_0[2];
	oTexcoord1 = oTexcoord1_0[2];
	oTexcoord2 = oTexcoord2_0[2];

	oTexcoordSpec = oTexcoordSpec_0[2];
	oTexcoordNorm = oTexcoordNorm_0[2];
	oTexcoordAO = oTexcoordAO_0[2];

	worldP = worldP_0[2];
	worldP_no_offset = worldP_no_offset_0[2];

	vColor = vColor_0[2];
	vPosition = vPosition_0[2];
	vNormal = isFaceNormal == 1? faceNormal : vNormal_0[2];

	gl_Position = gl_in[2].gl_Position;
	EmitVertex();

	EndPrimitive();
    
}
