
uniform vec3 eyePositionLocal;
uniform sampler2D diffuseMap0;
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

vec3 CloudFromSpace(vec3 mapColor, float fNear, float fFar, vec3 v3Ray) {
	/* Calculate the ray's starting position, then calculate its scattering offset */
	vec3 v3Start = v3Pos;
	
	float fLength = fFar - fNear;
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
	
	vec3 v3Color = v3FrontColor * (v3InvWavelength * fKrESun + fKmESun);
	
	return v3Color + v3Attenuate * mapColor;
}

vec3 SkyFromSpace(float fNear, float fFar, vec3 v3Ray) {
	vec3 v3Start = v3Pos;

	float fLength = fFar - fNear;	
	float fStartAngle = dot(v3Ray, v3Start) / fOuterRadius;
	float fStartDepth = exp(-fInvScaleDepth);
	float fStartOffset = fStartDepth * scale(fStartAngle);
	float fSampleLength = fLength / fSamples;
	float fScaledLength = fSampleLength * fScale;
	
	vec3 v3SampleRay = v3Ray * fSampleLength;
	vec3 v3SamplePoint = v3Start + v3SampleRay * 0.5;
	vec3 v3FrontColor = vec3(0.0, 0.0, 0.0);
	
	for(int i=0; i<nSamples; i++) {

		float fHeight = length(v3SamplePoint);
		float fDepth = exp(fScaleOverScaleDepth * (fInnerRadius - fHeight));
		float fLightAngle = dot(v3LightDirection, v3SamplePoint) / fHeight;
		float fCameraAngle = dot(v3Ray, v3SamplePoint) / fHeight;
		float fScatter = (fStartOffset + fDepth * (scale(fLightAngle) - scale(fCameraAngle)));
		
		vec3 v3Attenuate = exp(-fScatter * (v3InvWavelength * fKr4PI + fKm4PI));

		v3FrontColor += v3Attenuate * (fDepth * fScaledLength);

		v3SamplePoint += v3SampleRay;

	}

	vec3 v3Color0 = v3FrontColor * (v3InvWavelength * fKrESun);
	vec3 v3Color1 = v3FrontColor * fKmESun;
	float fCos = dot(v3LightDirection, -v3Ray);
	float fCos2 = fCos * fCos;
	vec3 skyColor = getRayleighPhase(fCos2) * v3Color0 + getMiePhase(fCos, fCos2) * v3Color1;
	
	return skyColor;
}

void main()
{ 
	vec3 v3Ray = v3Pos - eyePositionLocal;
	
	float fNear = length(v3Ray);	
	
	v3Ray /= fNear;
	
	float B = 2.0 * dot(eyePositionLocal, v3Ray);
	float B2 = B * B;
	float C = fCameraHeight2 - fOuterRadius2;
	float det = max(0.0, B2 - 4.0 * C);		
	float fFar = 0.5 * (-B + sqrt(det));
	vec3 skyColor = SkyFromSpace(fNear, fFar, v3Ray);
	skyColor = clamp(skyColor, vec3(0), vec3(1));
		
	C = fCameraHeight2 - fInnerRadius2;
	det = B2 - 4.0 * C;
	
	if (det >= 0) 
	{
		float fFar = 0.5 * (-B - sqrt(det));
		
		vec3 brightColor = clamp(CloudFromSpace(vec3(1), fNear, fFar, v3Ray), vec3(0), vec3(1));
		float brightness = 0.3 * brightColor.r + 0.5 * brightColor.g + 0.2 * brightColor.b;
		float cloudIntensity = 0;		
		if (bit_and(flag, 0x0002))
		{
			cloudIntensity = texture2D(diffuseMap0, oTexcoord0.xy).b;
		}		
		float maxDepth = sqrt(fOuterRadius2 - fInnerRadius2);
		float minDepth = fOuterRadius - fInnerRadius;
		float fogIntensity = sin(((fFar - fNear) - minDepth) / (maxDepth - minDepth) * PI / 2);
		float alpha = max(fogIntensity, cloudIntensity);
		
		//2023-11-27， wxg, 去掉不正确光影
		float skyBlend = 0;//sin((0.1 * skyColor.r + 0.4 * skyColor.g + 0.5 * skyColor.b) * PI);
		vec3 fogColor = vec3(min((1.6 - fogIntensity), 1) * brightness, brightness, brightness);
		//vec3 fogColor = max(1.6 - fogIntensity, 0) * vec3(1.0, 1.5, 1.3);
		//fogColor = min(fogColor, vec3(1.5)) * brightColor;
		fogColor = min(fogColor, vec3(1.5)) * brightness;
		vec3 finalColor = skyColor * skyBlend + fogColor * (1 - skyBlend);
		
		gl_FragColor = vec4(finalColor, alpha);
	}
	else
	{
		float skyBlend = (0.3 * skyColor.r + 0.3 * skyColor.g + 0.4 * skyColor.b);
		gl_FragColor = vec4(skyColor, skyBlend);
	}
}