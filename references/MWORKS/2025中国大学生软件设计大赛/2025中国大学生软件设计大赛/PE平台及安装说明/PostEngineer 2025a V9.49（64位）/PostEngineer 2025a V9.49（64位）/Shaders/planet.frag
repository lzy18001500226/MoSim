
uniform vec3 eyePositionLocal;
uniform sampler2D diffuseMap;
uniform sampler2D diffuseMap2;
uniform int flag;

uniform vec3 v3InvWavelength;
uniform float fInnerRadius;
uniform float fInnerRadius2;
uniform float fOuterRadius;
uniform float fOuterRadius2;
uniform float fKrESun;
uniform float fKmESun;
uniform float fKr4PI;
uniform float fKm4PI;
uniform float fScale;
uniform float fScaleDepth;
uniform float fInvScaleDepth;
uniform float fScaleOverScaleDepth;
uniform float fSamples;
uniform int nSamples;


varying float fCameraHeight;
varying float fCameraHeight2;
varying vec3 v3Pos;
varying vec3 v3Direction;
varying vec3 v3LightDirection;
varying vec2 oTexcoord0;
varying vec2 oTexcoord1;

const float g = -0.95;
const float g2 = g*g;
const float PI = 3.1415926535897932384626433832795;

bool bit_and(int val, int ref) {
  if(val == 0) return false;

  return (val/ref) % 2 != 0;
}

float scale(float fCos) {
    float x = 1.0 - fCos;
    return fScaleDepth * exp(-0.00287 + x*(0.459 + x*(3.83 + x*(-6.80 + x*5.25))));
}

/* Calculates the Mie phase function */
float getMiePhase(float fCos, float fCos2)
{
	return 1.5 * ((1.0 - g2) / (2.0 + g2)) * (1.0 + fCos2) / pow(abs(1.0 + g2 - 2.0*g*fCos), 1.5);
}

/* Calculates the Rayleigh phase function */
float getRayleighPhase(float fCos2)
{
	return 0.75 + 0.75*fCos2;
}

vec3 GroundFromSpace(vec3 dayColor, vec3 nightColor, float fNear, float fFar, vec3 v3Ray) {
	/* Calculate the ray's starting position, then calculate its scattering offset */
	float fLength = fFar - fNear;
	vec3 v3Start = v3Pos - fLength * v3Ray;
	float fDepth = exp((fInnerRadius - fOuterRadius) * fInvScaleDepth);
	float fCameraAngle = dot(-v3Ray, v3Direction);
	float fLightAngle = dot(v3LightDirection, v3Direction);
	float fCameraScale = scale(fCameraAngle);
	float fLightScale = scale(fLightAngle);
	float fCameraOffset = fDepth*fCameraScale;
	float fTemp = (fLightScale + fCameraScale);
	
	/* Initialize the scattering loop variables */
	float fSampleLength = fLength / fSamples;
	float fScaledLength = fSampleLength * fScale;
	vec3 v3SampleRay = v3Ray * fSampleLength;
	vec3 v3SamplePoint = v3Start + v3SampleRay * 0.5;
	
	/* Now loop through the sample rays */
	vec3 v3FrontColor = vec3(0.0, 0.0, 0.0);
	vec3 v3Attenuate = vec3(0.0, 0.0, 0.0);
	for(int i=0; i<nSamples; i++)
	{
	  float fHeight = length(v3SamplePoint);
	  float fDepth = exp(fScaleOverScaleDepth * (fInnerRadius - fHeight));
	  float fScatter = fDepth*fTemp - fCameraOffset;
	  v3Attenuate = exp(-fScatter * (v3InvWavelength * fKr4PI + fKm4PI));
	  v3FrontColor += v3Attenuate * (fDepth * fScaledLength);
	  v3SamplePoint += v3SampleRay;
	}
	
	//2023-11-27, wxg, ¼õÇá×ÏÉ«
	//vec3 v3Color = v3FrontColor * (v3InvWavelength * fKrESun + fKmESun);
	vec3 v3Color = v3FrontColor * (v3InvWavelength * fKrESun + fKmESun) * vec3(0.1, 1.5, 0.9);
	v3Color = clamp(v3Color, vec3(0), vec3(1));
	float darkness = v3Color.r + v3Color.g + v3Color.b;
	
	if (darkness < 0.01) {
		return nightColor * (1 - darkness*100);
	} else {
		return v3Color + v3Attenuate * dayColor;
	}
}

void main()
{ 
	vec3 v3Ray = v3Pos - eyePositionLocal;
	
	float fFar = length(v3Ray);
	
	v3Ray /= fFar;
	
	float B = 2.0 * dot(eyePositionLocal, v3Ray);    
	float C = fCameraHeight2 - fOuterRadius2;
	float det = max(0.0, B * B - 4.0 * C);
	float fNear = 0.5 * (-B - sqrt(det));
	
	vec3 dayColor = vec3(1, 1, 1);
	vec3 nightColor = vec3(0, 0, 0);
	if (bit_and(flag, 0x0002))
	{
		dayColor = texture2D(diffuseMap, oTexcoord0.xy).rgb;
		nightColor = texture2D(diffuseMap2, oTexcoord0.xy).rgb;
		nightColor = clamp(nightColor*2, 0, 2);
	}
	vec3 finalColor = GroundFromSpace(dayColor, nightColor, fNear, fFar, v3Ray);// * vec3(0.3, 0.43, 0.52) * 2;	
	
	gl_FragColor = vec4(finalColor, 1);
}