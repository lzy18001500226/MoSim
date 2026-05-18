
uniform float density;

void main() {

 float dis = gl_FragCoord.z / gl_FragCoord.w;
 gl_FragColor = vec4(dis,  density, 0, 1);

}
