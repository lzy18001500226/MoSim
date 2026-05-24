

uniform sampler2D textureMap;

varying vec2 vUv;

void main() 
{
  //gl_FragColor.rgb = texture( textureMap, vUv).rgb;
   float Depth = texture(textureMap, vUv).x;
    //Depth = 1.0 - (1.0 - Depth) * 25.0;
    Depth = 1.0 - (1.0 - Depth)*1000;
    gl_FragColor.rgb = vec3(Depth);

}
