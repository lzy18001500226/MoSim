//#version 330
varying vec3 ViewPos;

void main()
{
    gl_FragColor = vec4(ViewPos, 1);
}
