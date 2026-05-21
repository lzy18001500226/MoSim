
#extension GL_EXT_gpu_shader4 : enable

uniform sampler2DArray fftWavesSampler;
uniform vec4 GRID_SIZES;


uniform mat4 screenToCamera; // screen space to camera space
uniform mat4 cameraToWorld; // camera space to world space
uniform vec3 worldCamera; // camera position in world space
uniform mat4 worldToScreen; // world space to screen space
uniform vec2 gridSize;



flat varying vec3 P; 


#ifdef _VERTEX_

attribute vec2 pos;


vec2 oceanPos(vec4 vertex) {
    vec3 cameraDir = normalize((screenToCamera * vertex).xyz);
    vec3 worldDir = (cameraToWorld * vec4(cameraDir, 0.0)).xyz;
    float t = -worldCamera.z / worldDir.z;
    return worldCamera.xy + t * worldDir.xy;
}

void main() {
    gl_Position = gl_Vertex;
    
    vec2 u;
    u = pos;
    
    vec4 u_s = worldToScreen * vec4(u, 0, 1);
    
    vec2 ux = oceanPos(u_s + vec4(gridSize.x, 0.0, 0.0, 0.0));
    vec2 uy = oceanPos(u_s + vec4(0.0, gridSize.y, 0.0, 0.0));
    vec2 dux = abs(ux - u) * 2.0;
    vec2 duy = abs(uy - u) * 2.0;
    
    vec3 dP = vec3(0.0);
    dP.z += texture2DArrayGrad(fftWavesSampler, vec3(u / GRID_SIZES.x, 0.0), dux / GRID_SIZES.x, duy / GRID_SIZES.x).x;
    dP.z += texture2DArrayGrad(fftWavesSampler, vec3(u / GRID_SIZES.y, 0.0), dux / GRID_SIZES.y, duy / GRID_SIZES.y).y;
    dP.z += texture2DArrayGrad(fftWavesSampler, vec3(u / GRID_SIZES.z, 0.0), dux / GRID_SIZES.z, duy / GRID_SIZES.z).z;
    dP.z += texture2DArrayGrad(fftWavesSampler, vec3(u / GRID_SIZES.w, 0.0), dux / GRID_SIZES.w, duy / GRID_SIZES.w).w;
     
    P = vec3(u, dP.z);
}

#endif

#ifdef _FRAGMENT_

void main() {
    
    gl_FragColor = vec4(P, 1);
}

#endif
