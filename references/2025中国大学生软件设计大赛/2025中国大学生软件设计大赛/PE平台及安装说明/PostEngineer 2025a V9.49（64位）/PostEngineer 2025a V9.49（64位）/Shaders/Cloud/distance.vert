
uniform mat4 modelview;
uniform mat4 projection;
uniform mat4 modelToWorld;

void main() {
  
  gl_Position = projection * modelview * modelToWorld * vec4(gl_Vertex.xyz, 1.0);

}