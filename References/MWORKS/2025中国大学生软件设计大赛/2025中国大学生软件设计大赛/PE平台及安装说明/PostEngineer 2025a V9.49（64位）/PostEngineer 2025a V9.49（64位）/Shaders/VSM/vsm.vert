#version 130

//layout (location = 0) in vec3 Position;

uniform mat4 modelview;
uniform mat4 projection;
uniform mat4 modelToWorld;

varying vec4 v_pos; 
varying vec3 ViewPos;

void main() {
  gl_Position = projection * modelview * modelToWorld * vec4(gl_Vertex.xyz, 1.0);
  v_pos = gl_Position;
  ViewPos = (modelview * modelToWorld * vec4(gl_Vertex.xyz, 1.0)).xyz;
}
