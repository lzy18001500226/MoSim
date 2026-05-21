//#version 330


varying vec3 ViewPos;

void main()
{
    vec3 Normal = normalize(ViewPos);
  /*  vec3 T = get_ortho(Normal);
    vec3 B = cross(Normal, T);*/
    gl_FragColor = vec4(Normal, 1);
}
