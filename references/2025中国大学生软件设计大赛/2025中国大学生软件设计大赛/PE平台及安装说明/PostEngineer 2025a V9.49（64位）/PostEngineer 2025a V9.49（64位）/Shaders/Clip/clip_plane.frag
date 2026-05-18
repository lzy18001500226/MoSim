#version 430

layout (location = 0) out vec4 gMainColor; 

uniform sampler2D gClipImage;


in vec3 vPosition;
in vec3 vNormal;
in vec3 worldP;


void main() {

  vec2 screenSize = textureSize(gClipImage, 0);
  gMainColor.rgb = texture(gClipImage, clamp(gl_FragCoord.xy/screenSize, 0.0, 1.0)).rgb;
  //gMainColor.rgb = vec3(0, 0, 1);
  gMainColor.a = 1.0;
  
}

