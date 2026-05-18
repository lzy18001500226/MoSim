#version 330 core

layout (triangles) in;
layout (triangle_strip, max_vertices = 3) out;


uniform mat4 gMvp;
uniform mat4 modelToWorld;

in vec2 oTexcoord0[];

in vec3 worldP0[];

in vec3 vColor0[];
in vec3 vPosition0[];
in vec3 vNormal0[];
in vec3 vibration[];

out vec2 oTexcoord[];

out vec3 worldP[];

out vec3 vColor[];
out vec3 vPosition[];
out vec3 vNormal[];


void main() {

    gl_Position = gl_in[0].gl_Position + vec4(vibration[0], 0);
	oTexcoord[0] = oTexcoord0[0];
	worldP[0] = worldP0[0];
	vColor[0] = vColor0[0];
	vPosition[0] = vPosition0[0];
	vNormal[0] = vNormal0[0];
    EmitVertex();
 
	gl_Position = gl_in[1].gl_Position + vec4(vibration[1], 0);
	oTexcoord[1] = oTexcoord0[1];
	worldP[1] = worldP0[1];
	vColor[1] = vColor0[1];
	vPosition[1] = vPosition0[1];
	vNormal[1] = vNormal0[1];
    EmitVertex();

	gl_Position = gl_in[2].gl_Position + vec4(vibration[2], 0);
	oTexcoord[2] = oTexcoord0[2];
	worldP[2] = worldP0[2];
	vColor[2] = vColor0[2];
	vPosition[2] = vPosition0[2];
	vNormal[2] = vNormal0[2];
    EmitVertex();
  
	EndPrimitive();
}
