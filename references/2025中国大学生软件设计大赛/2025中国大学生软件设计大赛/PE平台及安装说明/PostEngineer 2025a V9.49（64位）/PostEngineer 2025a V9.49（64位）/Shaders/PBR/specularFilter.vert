#version 330

layout (location = 0) in vec3 Vertex;
layout (location = 1) in vec2 TexCoord;

out vec2 vs_TexCoord;

void main() {

    gl_Position = vec4(Vertex, 1.0);

    vs_TexCoord = TexCoord;

}
