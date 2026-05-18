// #version 330

uniform mat4 modelview;
uniform mat4 projection;
uniform mat4 modelToWorld;

varying vec3 ViewPos;

void main() {
  gl_Position = projection * modelview * modelToWorld * vec4(gl_Vertex.xyz, 1.0);
  ViewPos = (modelview * modelToWorld * vec4(gl_Vertex.xyz, 1.0)).xyz;
}
