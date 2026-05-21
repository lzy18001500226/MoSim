// #version 330

//layout (location = 0) in vec3 Position;

uniform mat4 modelview;
uniform mat4 projection;
uniform mat4 modelToWorld;

varying vec3 ViewPos;

void main() {
  
  gl_Position = projection * modelview * modelToWorld * vec4(gl_Vertex.xyz, 1.0);
  vec4 P = (modelToWorld * vec4(gl_Normal.xyz, 0.0));
  ViewPos = normalize(P.xyz);
  //TexCoord = (gl_Position.xy/gl_Position.w + vec2(1.0)) / 2.0;
}
