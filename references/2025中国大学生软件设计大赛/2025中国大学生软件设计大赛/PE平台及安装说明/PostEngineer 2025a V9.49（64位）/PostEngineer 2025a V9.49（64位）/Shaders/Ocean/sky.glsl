uniform mat4 screenToCamera;
uniform mat4 cameraToWorld;
uniform mat4 horizonRotation;

uniform mat4 matLocalToSurface;
uniform mat4 matSurfaceToLocal;
uniform mat4 matLocalToEarth;

uniform mat4 cameraToScreen; 
uniform mat4 worldToCamera; 
uniform vec3 worldCamera;
uniform vec3 worldSunDir;
uniform float localDistToEarthCenter;

varying vec3 viewDir;
varying vec3 posToCamera;

uniform vec3 fogColor;
uniform float fogDensity;
uniform float fogHeight;
uniform vec3 gVertical;

uniform sampler2D frontTex;
uniform sampler2D backTex;
uniform vec3 cloudColor2;
uniform float cloudDensity;

uniform vec2 screenSize;

uniform int flag;

#ifdef _VERTEX_

void main() {
    	viewDir = (cameraToWorld * vec4((screenToCamera * gl_Vertex).xyz, 0.0)).xyz;

	vec4 CP = horizonRotation * screenToCamera * vec4(gl_Vertex.xy, 0.999999, 1.0);  ///0.999999不能写为1，会导致闪烁

	vec4 PT = screenToCamera * vec4(gl_Vertex.xy, 0.999999, 1.0);
	posToCamera = PT.xyz / PT.w;
	//posToCamera = CP.xyz / CP.w;

    	gl_Position = cameraToScreen * CP;

    //gl_Position = vec4(gl_Vertex.xy, 0.9999999, 1.0);
}

#endif

#ifdef _FRAGMENT_

bool bit_and(int val, int ref) {
  if(val == 0) return false;

  return (val/ref) % 2 != 0;
}

float CalcFogBlend(vec3 worldP)
{
	float fogBlend = 1.0;
	const float EPSON = 0.0000001;

	int fogAtten = 1;

	if(fogDensity > EPSON){

		//全部转换到世界坐标系下
		vec3 worldP0 = worldP;//(cameraConvertMatrix * vec4(worldP, 1.0)).xyz;
		vec3 gCameraPos0 = worldCamera;//(cameraConvertMatrix * vec4(gCameraPos, 1.0)).xyz;
 
		vec3 view_vec = worldP0 - gCameraPos0;
		vec3 viewDir = normalize(view_vec);
		vec3 gVertical0 = vec3(0, 0, 1);

		float dis_in_fog = length(view_vec);

		float H0, H1;
		if( fogHeight > EPSON){
			if (bit_and(flag, 0x800000) == true){
				H0 = length(gCameraPos0) - localDistToEarthCenter;
				H1 = length(worldP0) - localDistToEarthCenter;
			}
			else{
				H0 = dot(gCameraPos0, gVertical0);
				H1 = dot(worldP0, gVertical0);
			}

			float h0 = H0 - fogHeight;
			float h1 = H1 - fogHeight;

			if(h0 <= 0 && h1 >= 0) dis_in_fog *= -h0/(-h0+h1);
			else if(h0 >= 0 && h1 <= 0) dis_in_fog *= -h1/(h0-h1);
			else if(h0 >= 0 && h1 >= 0) dis_in_fog = 0.0;
		}

		//return H1;

		float density = fogDensity;

		vec3 up = gVertical0;
		//density *= max(1.0 - dot(up, viewDir), 0);
        
		if(fogAtten == 0){
			float maxDis = log(5.0) / density;
			fogBlend = clamp( 1.0 - dis_in_fog/maxDis , 0, 1);
		}
		else if(fogAtten == 1)
			fogBlend = clamp(exp(-density * dis_in_fog ), 0, 1);
		else{
			float ind = pow(density * dis_in_fog, 2);
			fogBlend = clamp(exp(-ind ), 0, 1);
		}

		/*if( fogHeight > EPSON){
			//float H = dot(worldP - vec3(0), gVertical);
			float factor = 1.0 - min( max( H - fogHeight, 0) / (fogHeight*5), 1.0);
			fogBlend = fogBlend*factor + 1.0*(1 - factor);
		}*/

		//2025-3-12, wxg, 雾是来自于地面的雾，当相机高于雾的高度时，天空上的雾应该消失
		if(H0  > fogHeight){
			float factor = max(1.0 - (H0 - fogHeight) / (fogHeight), 0.0);
			fogBlend = fogBlend*factor + 1.0*(1 - factor);
		}

		
   	 }

	return fogBlend;
}

void main() {
	if (bit_and(flag, 0x800000) == true) earthPos = vec3(0.0);//normalize(worldCamera - vec3(0.0)) * 10000;
	else earthPos.z += 1000;  //避免下部颜色太深

    vec3 worldP = (cameraToWorld * vec4(posToCamera, 1.0)).xyz;
    vec3 V = normalize(viewDir);
    //vec3 V = normalize(worldP - worldCamera);

    vec3 sunColor = vec3(step(cos(3.1415926 / 180.0), dot(V, worldSunDir))) * SUN_INTENSITY;
    vec3 extinction;
    //vec3 P_earth = (matLocalToSurface * vec4(worldCamera, 1)).xyz; + earthPos;
    //vec3 V_surf = normalize((matLocalToSurface * vec4(V, 0)).xyz);
    //vec3 worldSunDir_surf = normalize((matLocalToSurface * vec4(worldSunDir, 0)).xyz);

    //vec3 inscatter = skyRadiance(P_earth, V, worldSunDir, extinction);
    vec3 inscatter = skyRadiance(worldCamera +  earthPos, V, worldSunDir, extinction);
    vec3 finalColor = sunColor * extinction + inscatter;
    gl_FragColor.rgb = hdr(finalColor, 0.6);
    
   float fogBlend;
	//vec3 worldP = (cameraToWorld * horizonRotation * screenToCamera * vec4(screenPos, 1.0)).xyz;
	
	if (bit_and(flag, 0x800000) == true){
	 	fogBlend = CalcFogBlend(worldP);
	}
	else{
		fogBlend = CalcFogBlend(worldP);
	}

	if(fogBlend < 1 - 0.000001){
        
		gl_FragColor.rgb = gl_FragColor.rgb*fogBlend + fogColor*(1-fogBlend);
    }

	//gl_FragColor = vec4(worldP, fogBlend);
	//return;
    
   /* //体积雾
    vec2 uv = vec2(  gl_FragCoord.x / screenSize.x, gl_FragCoord.y / screenSize.y );
	vec4 back = texture2D(backTex, uv);
 	vec4 front = texture2D(frontTex, uv);
	if( back.a > 0.5  ){
		float fogBlend = clamp((back.r-front.r) * back.g, 0, 1);
		fogBlend *= fogBlend;
		gl_FragColor.rgb = gl_FragColor.rgb*(1-fogBlend) + cloudColor2*fogBlend;
	}*/
   
    ///2023-3-21, 确保天空与后向渲染的模型融合
    gl_FragColor.a = -1.0;

}

#endif
