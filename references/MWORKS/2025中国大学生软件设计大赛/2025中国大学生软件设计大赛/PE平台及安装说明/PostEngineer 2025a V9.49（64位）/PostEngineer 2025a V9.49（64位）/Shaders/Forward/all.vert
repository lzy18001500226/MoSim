

uniform mat4 modelToWorld;

uniform vec3 globalAmbient;
uniform vec3 eyePositionLocal;
uniform vec3 eyePositionW;

uniform mat4 texMatrix;
uniform mat4 texMatrix1;
uniform mat4 texMatrix2;


uniform mat4 texMatrixSpec;
uniform mat4 texMatrixNorm;
uniform mat4 texMatrixAO;

uniform int multiTexCount;

uniform int shadowMapEnable;
uniform mat4 shadowProjMatrix;
varying vec4 lightSpacePos;

uniform int reflectMapEnable;
uniform mat4 reflectProjMatrix;
varying vec4 reflectTexCoord;


uniform int projectorEnable;
uniform mat4 projectorProjMatrix;
varying vec4 projectorTexCoord;

uniform vec3 gCameraPos;
uniform vec3 gVertical;

varying vec2 oTexcoordOrigin;
varying vec2 oTexcoord0;
varying vec2 oTexcoord1;
varying vec2 oTexcoord2;


uniform int texCoordIndexSpec;
uniform int texCoordIndexNorm;
uniform int texCoordIndexAO;

varying vec2 oTexcoordSpec;
varying vec2 oTexcoordNorm;
varying vec2 oTexcoordAO;

varying vec3 halfAngle;
varying vec3 normalLocal;
varying vec3 normalWorld;

varying vec3 I_World;
varying vec3 I_Local;
/*varying vec3 tangent;
varying vec3 binormal;*/

varying vec4 oColor;

varying vec3 worldP;
varying vec3 worldN;


uniform mat4 cameraConvertMatrix;

//uniform float fogDensity;
//uniform float fogHeight;
uniform vec3 fogParam;
uniform vec3 fogColor;

float CalcFogBlend(vec3 worldP)
{
	float fogBlend = 1.0;
	const float EPSON = 0.0000001;

	float fogDensity = fogParam.x;
	float fogHeight = fogParam.y;
	int fogAtten = int(fogParam.z + 0.001);

	if(fogDensity > EPSON){

		//全部转换到世界坐标系下
		vec3 worldP0 = (cameraConvertMatrix * vec4(worldP, 1.0)).xyz;
		vec3 gCameraPos0 = (cameraConvertMatrix * vec4(gCameraPos, 1.0)).xyz;
 
		vec3 view_vec = worldP0 - gCameraPos0;
		vec3 viewDir = normalize(view_vec);
		vec3 gVertical0 = vec3(0, 1, 0);

		float dis_in_fog = length(view_vec);

		if( fogHeight > EPSON){
			float H0 = dot(gCameraPos0, gVertical0);
			float H1 = dot(worldP0, gVertical0);

			float h0 = H0 - fogHeight;
			float h1 = H1 - fogHeight;

			if(h0 <= 0 && h1 >= 0) dis_in_fog *= -h0/(-h0+h1);
			else if(h0 >= 0 && h1 <= 0) dis_in_fog *= -h1/(h0-h1);
			else if(h0 >= 0 && h1 >= 0) dis_in_fog = 0.0;
		}

		float density = fogDensity;

		vec3 up = gVertical0;
		density *= max(1.0 - dot(up, viewDir), 0);
        
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
   	 }

	return fogBlend;
}

uniform float heightFactor;
uniform sampler2D heightMap1;
uniform sampler2D heightMap2;
uniform sampler2D normalMap1;
uniform sampler2D normalMap2;

varying vec3 vPosition;
varying vec3 vNormal;

void main() {
  oTexcoord0 = (texMatrix * vec4(gl_MultiTexCoord0.xy, 0, 1)).xy;

  if(texCoordIndexNorm == 0) oTexcoordNorm = (texMatrixNorm * vec4(gl_MultiTexCoord0.xy, 0, 1)).xy;
  if(texCoordIndexNorm == 1) oTexcoordNorm = (texMatrixNorm * vec4(gl_MultiTexCoord1.xy, 0, 1)).xy;
  if(texCoordIndexNorm == 2) oTexcoordNorm = (texMatrixNorm * vec4(gl_MultiTexCoord2.xy, 0, 1)).xy;

  if(texCoordIndexSpec == 0) oTexcoordSpec = (texMatrixSpec * vec4(gl_MultiTexCoord0.xy, 0, 1)).xy;
  if(texCoordIndexSpec == 1) oTexcoordSpec = (texMatrixSpec * vec4(gl_MultiTexCoord1.xy, 0, 1)).xy;
  if(texCoordIndexSpec == 2) oTexcoordSpec = (texMatrixSpec * vec4(gl_MultiTexCoord2.xy, 0, 1)).xy;

  if(texCoordIndexAO == 0) oTexcoordAO = (texMatrixAO * vec4(gl_MultiTexCoord0.xy, 0, 1)).xy;
  if(texCoordIndexAO == 1) oTexcoordAO = (texMatrixAO * vec4(gl_MultiTexCoord1.xy, 0, 1)).xy;
  if(texCoordIndexAO == 2) oTexcoordAO = (texMatrixAO * vec4(gl_MultiTexCoord2.xy, 0, 1)).xy;

  gl_Position = ftransform();

  if(shadowMapEnable==1){
    lightSpacePos = shadowProjMatrix * modelToWorld*gl_Vertex;
  }
  vPosition = gl_Vertex.xyz;
  vNormal = gl_Normal;
  worldP = (modelToWorld * gl_Vertex).xyz;
  worldN = normalize((modelToWorld * vec4(gl_Normal, 0)).xyz);
}
