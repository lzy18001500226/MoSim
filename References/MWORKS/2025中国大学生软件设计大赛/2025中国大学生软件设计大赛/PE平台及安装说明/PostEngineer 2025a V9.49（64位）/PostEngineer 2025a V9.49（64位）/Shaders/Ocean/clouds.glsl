uniform mat4 worldToScreen;
uniform vec3 worldCamera;
uniform vec3 worldSunDir;
uniform mat4 cameraToScreen; 
uniform mat4 worldToCamera;
uniform mat4 horizonRotation;

varying vec3 worldP;


uniform vec3 fogColor;
uniform float fogDensity;
uniform float fogHeight;

#ifdef _VERTEX_

void main() {
    gl_Position = cameraToScreen * horizonRotation * worldToCamera * vec4(gl_Vertex.xyz, 1.0);
    worldP = gl_Vertex.xyz;
}

#endif

#ifdef _FRAGMENT_

void main() {
    gl_FragColor = cloudColor(worldP, worldCamera, worldSunDir);
    gl_FragColor.rgb = hdr(gl_FragColor.rgb);
    
    float fogBlend = 1;	
    if(fogDensity > 0.0000001){
  /*      float dis = distance(worldP, worldCamera);
        if(worldP.z > fogHeight && worldCamera.z < fogHeight){
           float f = (fogHeight - worldCamera.z) / (worldP.z - worldCamera.z);
           if( f < 0) f = 0;
           dis *= f;
        }
		fogBlend = exp(-fogDensity * dis );*/
		fogBlend = 0.0;
		
		gl_FragColor.rgb = gl_FragColor.rgb*fogBlend + fogColor*(1-fogBlend);
    }
    
}

#endif
