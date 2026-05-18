#extension GL_EXT_gpu_shader4 : enable

uniform sampler2DArray fftWavesSampler;
uniform vec4 GRID_SIZES;
uniform vec2 basePt;
uniform vec2 rectSize;

varying vec3 P; 

#ifdef _VERTEX_

void main() {
    
    vec2 u;
    u.x = basePt.x + gl_Vertex.x*rectSize.x;
    u.y = basePt.y + gl_Vertex.y*rectSize.y;
    
    vec3 dP = vec3(0.0);
 /*   dP.z += texture2DArray(fftWavesSampler, vec3(u / GRID_SIZES.x, 0.0)).x;
    dP.z += texture2DArray(fftWavesSampler, vec3(u / GRID_SIZES.y, 0.0)).y;
    dP.z += texture2DArray(fftWavesSampler, vec3(u / GRID_SIZES.z, 0.0)).z;
    dP.z += texture2DArray(fftWavesSampler, vec3(u / GRID_SIZES.w, 0.0)).w;*/

    P = gl_Vertex.xyz;    
}

#endif

#ifdef _FRAGMENT_

void main() {
    gl_FragColor = vec4(0.1, 0.5, 0.9, 1);
}

#endif
