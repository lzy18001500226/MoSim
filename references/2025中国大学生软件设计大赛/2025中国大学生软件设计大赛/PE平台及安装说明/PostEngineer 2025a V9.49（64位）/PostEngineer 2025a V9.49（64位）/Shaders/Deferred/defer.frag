#version 330 core
//#extension GL_NV_shadow_samplers_cube : enable
#extension GL_NV_shader_buffer_load : enable

layout (location = 0) out vec4 gMainColor;
//layout (location = 1) out vec4 gShadow;
layout (location = 1) out vec4 gBloom;
//layout (location = 2) out vec4 gAtmosphere;
//layout (location = 3) out vec4 gVolumeLightColor;


/**
 * Precomputed Atmospheric Scattering
 * Copyright (c) 2008 INRIA
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. Neither the name of the copyright holders nor the names of its
 *    contributors may be used to endorse or promote products derived from
 *    this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
 * THE POSSIBILITY OF SUCH DAMAGE.
 */

/**
 * Author: Eric Bruneton
 */



//uniform float atmosphere_density;
uniform vec4 gEnviromentParam;

float SUN_INTENSITY = gEnviromentParam.x * 10;

const float SCALE = 1000.0;//*1.01;//导致大气出现断层

const vec3 earthPos = vec3(0.0, 6360.010*SCALE, 0);

// ----------------------------------------------------------------------------
// PHYSICAL MODEL PARAMETERS
// ----------------------------------------------------------------------------


const float Rg = 6360.0 * SCALE;
const float Rt = 6420.0 * SCALE;
const float RL = 6421.0 * SCALE;

const float AVERAGE_GROUND_REFLECTANCE = 0.1;

// Rayleigh
const float HR = 8.0 * SCALE;
const vec3 betaR = vec3(5.8e-3, 1.35e-2, 3.31e-2) / SCALE;

// Mie
// DEFAULT
const float HM = 1.2 * SCALE;
const vec3 betaMSca = vec3(4e-3) / SCALE;
const vec3 betaMEx = betaMSca / 0.9;
const float mieG = 0.8;
// CLEAR SKY
/*const float HM = 1.2 * SCALE;
const vec3 betaMSca = vec3(20e-3) / SCALE;
const vec3 betaMEx = betaMSca / 0.9;
const float mieG = 0.76;*/
// PARTLY CLOUDY
/*const float HM = 3.0 * SCALE;
const vec3 betaMSca = vec3(3e-3) / SCALE;
const vec3 betaMEx = betaMSca / 0.9;
const float mieG = 0.65;*/

const float g = 9.81;

const float M_PI = 3.1415926535897932384626433832795;
const float M_2PI = 2.0 * M_PI;
const float M_INV_PI = 0.31830988618379067153776752674503;
const float M_INV_LOG2 = 1.4426950408889634073599246810019;

// ----------------------------------------------------------------------------
// NUMERICAL INTEGRATION PARAMETERS
// ----------------------------------------------------------------------------

const int TRANSMITTANCE_INTEGRAL_SAMPLES = 500;
const int INSCATTER_INTEGRAL_SAMPLES = 50;
const int IRRADIANCE_INTEGRAL_SAMPLES = 32;
const int INSCATTER_SPHERICAL_INTEGRAL_SAMPLES = 16;

// ----------------------------------------------------------------------------
// PARAMETERIZATION OPTIONS
// ----------------------------------------------------------------------------

const int TRANSMITTANCE_W = 256;
const int TRANSMITTANCE_H = 64;

const int SKY_W = 64;
const int SKY_H = 16;

const int RES_R = 32;
const int RES_MU = 128;
const int RES_MU_S = 32;
const int RES_NU = 8;

#define TRANSMITTANCE_NON_LINEAR
#define INSCATTER_NON_LINEAR

// ----------------------------------------------------------------------------
// PARAMETERIZATION FUNCTIONS
// ----------------------------------------------------------------------------


uniform sampler2D transmittanceSampler;

uniform sampler2D skyIrradianceSampler;

uniform sampler3D inscatterSampler;

vec2 getTransmittanceUV(float r, float mu) {
    float uR, uMu;
#ifdef TRANSMITTANCE_NON_LINEAR
    uR = sqrt((r - Rg) / (Rt - Rg));
    uMu = atan((mu + 0.15) / (1.0 + 0.15) * tan(1.5)) / 1.5;
#else
    uR = (r - Rg) / (Rt - Rg);
    uMu = (mu + 0.15) / (1.0 + 0.15);
#endif
    return vec2(uMu, uR);
}

void getTransmittanceRMu(out float r, out float muS) {
    r = gl_FragCoord.y / float(TRANSMITTANCE_H);
    muS = gl_FragCoord.x / float(TRANSMITTANCE_W);
#ifdef TRANSMITTANCE_NON_LINEAR
    r = Rg + (r * r) * (Rt - Rg);
    muS = -0.15 + tan(1.5 * muS) / tan(1.5) * (1.0 + 0.15);
#else
    r = Rg + r * (Rt - Rg);
    muS = -0.15 + muS * (1.0 + 0.15);
#endif
}

vec2 getIrradianceUV(float r, float muS) {
    float uR = (r - Rg) / (Rt - Rg);
    float uMuS = (muS + 0.2) / (1.0 + 0.2);
    return vec2(uMuS, uR);
}

void getIrradianceRMuS(out float r, out float muS) {
    r = Rg + (gl_FragCoord.y - 0.5) / (float(SKY_H) - 1.0) * (Rt - Rg);
    muS = -0.2 + (gl_FragCoord.x - 0.5) / (float(SKY_W) - 1.0) * (1.0 + 0.2);
}

vec4 texture4D(sampler3D table, float r, float mu, float muS, float nu)
{
    float H = sqrt(Rt * Rt - Rg * Rg);
    float rho = sqrt(r * r - Rg * Rg);
#ifdef INSCATTER_NON_LINEAR
    float rmu = r * mu;
    float delta = rmu * rmu - r * r + Rg * Rg;
    vec4 cst = rmu < 0.0 && delta > 0.0 ? vec4(1.0, 0.0, 0.0, 0.5 - 0.5 / float(RES_MU)) : vec4(-1.0, H * H, H, 0.5 + 0.5 / float(RES_MU));
    float uR = 0.5 / float(RES_R) + rho / H * (1.0 - 1.0 / float(RES_R));
    float uMu = cst.w + (rmu * cst.x + sqrt(delta + cst.y)) / (rho + cst.z) * (0.5 - 1.0 / float(RES_MU));
    // paper formula
    //float uMuS = 0.5 / float(RES_MU_S) + max((1.0 - exp(-3.0 * muS - 0.6)) / (1.0 - exp(-3.6)), 0.0) * (1.0 - 1.0 / float(RES_MU_S));
    // better formula
    float uMuS = 0.5 / float(RES_MU_S) + (atan(max(muS, -0.1975) * tan(1.26 * 1.1)) / 1.1 + (1.0 - 0.26)) * 0.5 * (1.0 - 1.0 / float(RES_MU_S));
#else
    float uR = 0.5 / float(RES_R) + rho / H * (1.0 - 1.0 / float(RES_R));
    float uMu = 0.5 / float(RES_MU) + (mu + 1.0) / 2.0 * (1.0 - 1.0 / float(RES_MU));
    float uMuS = 0.5 / float(RES_MU_S) + max(muS + 0.2, 0.0) / 1.2 * (1.0 - 1.0 / float(RES_MU_S));
#endif
    float lerp = (nu + 1.0) / 2.0 * (float(RES_NU) - 1.0);
    float uNu = floor(lerp);
    lerp = lerp - uNu;
    return texture(table, vec3((uNu + uMuS) / float(RES_NU), uMu, uR)) * (1.0 - lerp) +
           texture(table, vec3((uNu + uMuS + 1.0) / float(RES_NU), uMu, uR)) * lerp;
}

void getMuMuSNu(float r, vec4 dhdH, out float mu, out float muS, out float nu) {
    float x = gl_FragCoord.x - 0.5;
    float y = gl_FragCoord.y - 0.5;
#ifdef INSCATTER_NON_LINEAR
    if (y < float(RES_MU) / 2.0) {
        float d = 1.0 - y / (float(RES_MU) / 2.0 - 1.0);
        d = min(max(dhdH.z, d * dhdH.w), dhdH.w * 0.999);
        mu = (Rg * Rg - r * r - d * d) / (2.0 * r * d);
        mu = min(mu, -sqrt(1.0 - (Rg / r) * (Rg / r)) - 0.001);
    } else {
        float d = (y - float(RES_MU) / 2.0) / (float(RES_MU) / 2.0 - 1.0);
        d = min(max(dhdH.x, d * dhdH.y), dhdH.y * 0.999);
        mu = (Rt * Rt - r * r - d * d) / (2.0 * r * d);
    }
    muS = mod(x, float(RES_MU_S)) / (float(RES_MU_S) - 1.0);
    // paper formula
    //muS = -(0.6 + log(1.0 - muS * (1.0 -  exp(-3.6)))) / 3.0;
    // better formula
    muS = tan((2.0 * muS - 1.0 + 0.26) * 1.1) / tan(1.26 * 1.1);
    nu = -1.0 + floor(x / float(RES_MU_S)) / (float(RES_NU) - 1.0) * 2.0;
#else
    mu = -1.0 + 2.0 * y / (float(RES_MU) - 1.0);
    muS = mod(x, float(RES_MU_S)) / (float(RES_MU_S) - 1.0);
    muS = -0.2 + muS * 1.2;
    nu = -1.0 + floor(x / float(RES_MU_S)) / (float(RES_NU) - 1.0) * 2.0;
#endif
}

// ----------------------------------------------------------------------------
// UTILITY FUNCTIONS
// ----------------------------------------------------------------------------

// nearest intersection of ray r,mu with ground or top atmosphere boundary
// mu=cos(ray zenith angle at ray origin)
float limit(float r, float mu) {
    float dout = -r * mu + sqrt(r * r * (mu * mu - 1.0) + RL * RL);
    float delta2 = r * r * (mu * mu - 1.0) + Rg * Rg;
    if (delta2 >= 0.0) {
        float din = -r * mu - sqrt(delta2);
        if (din >= 0.0) {
            dout = min(dout, din);
        }
    }
    return dout;
}

// optical depth for ray (r,mu) of length d, using analytic formula
// (mu=cos(view zenith angle)), intersections with ground ignored
// H=height scale of exponential density function
float opticalDepth(float H, float r, float mu, float d) {
    float a = sqrt((0.5/H)*r);
    vec2 a01 = a*vec2(mu, mu + d / r);
    vec2 a01s = sign(a01);
    vec2 a01sq = a01*a01;
    float x = a01s.y > a01s.x ? exp(a01sq.x) : 0.0;
    vec2 y = a01s / (2.3193*abs(a01) + sqrt(1.52*a01sq + 4.0)) * vec2(1.0, exp(-d/H*(d/(2.0*r)+mu)));
    return sqrt((6.2831*H)*r) * exp((Rg-r)/H) * (x + dot(y, vec2(1.0, -1.0)));
}

// transmittance(=transparency) of atmosphere for infinite ray (r,mu)
// (mu=cos(view zenith angle)), intersections with ground ignored
vec3 transmittance(float r, float mu) {
    vec2 uv = getTransmittanceUV(r, mu);
    return texture2D(transmittanceSampler, uv).rgb;
}

// transmittance(=transparency) of atmosphere for ray (r,mu) of length d
// (mu=cos(view zenith angle)), intersections with ground ignored
// uses analytic formula instead of transmittance texture
vec3 analyticTransmittance(float r, float mu, float d) {
    return exp(- betaR * opticalDepth(HR, r, mu, d) - betaMEx * opticalDepth(HM, r, mu, d));
}

// transmittance(=transparency) of atmosphere for infinite ray (r,mu)
// (mu=cos(view zenith angle)), or zero if ray intersects ground
vec3 transmittanceWithShadow(float r, float mu) {
    return mu < -sqrt(1.0 - (Rg / r) * (Rg / r)) ? vec3(0.0) : transmittance(r, mu);
}

// transmittance(=transparency) of atmosphere between x and x0
// assume segment x,x0 not intersecting ground
// r=||x||, mu=cos(zenith angle of [x,x0) ray at x), v=unit direction vector of [x,x0) ray
vec3 transmittance(float r, float mu, vec3 v, vec3 x0) {
    vec3 result;
    float r1 = length(x0);
    float mu1 = dot(x0, v) / r;
    if (mu > 0.0) {
        result = min(transmittance(r, mu) / transmittance(r1, mu1), 1.0);
    } else {
        result = min(transmittance(r1, -mu1) / transmittance(r, -mu), 1.0);
    }
    return result;
}

// transmittance(=transparency) of atmosphere between x and x0
// assume segment x,x0 not intersecting ground
// d = distance between x and x0, mu=cos(zenith angle of [x,x0) ray at x)
vec3 transmittance(float r, float mu, float d) {
    vec3 result;
    float r1 = sqrt(r * r + d * d + 2.0 * r * mu * d);
    float mu1 = (r * mu + d) / r1;
    if (mu > 0.0) {
        result = min(transmittance(r, mu) / transmittance(r1, mu1), 1.0);
    } else {
        result = min(transmittance(r1, -mu1) / transmittance(r, -mu), 1.0);
    }
    return result;
}

vec3 irradiance(sampler2D sampler, float r, float muS) {
    vec2 uv = getIrradianceUV(r, muS);
    return texture2D(sampler, uv).rgb;
}

// Rayleigh phase function
float phaseFunctionR(float mu) {
    return (3.0 / (16.0 * M_PI)) * (1.0 + mu * mu);
}

// Mie phase function
float phaseFunctionM(float mu) {
    return 1.5 * 1.0 / (4.0 * M_PI) * (1.0 - mieG*mieG) * pow(1.0 + (mieG*mieG) - 2.0*mieG*mu, -3.0/2.0) * (1.0 + mu * mu) / (2.0 + mieG*mieG);
}

// approximated single Mie scattering (cf. approximate Cm in paragraph "Angular precision")
vec3 getMie(vec4 rayMie) { // rayMie.rgb=C*, rayMie.w=Cm,r
    return rayMie.rgb * rayMie.w / max(rayMie.r, 1e-4) * (betaR.r / betaR);
}

// ----------------------------------------------------------------------------
// PUBLIC FUNCTIONS
// ----------------------------------------------------------------------------

// incident sun light at given position (radiance)
// r=length(x)
// muS=dot(x,s) / r
vec3 sunRadiance(float r, float muS) {
    return transmittanceWithShadow(r, muS) * SUN_INTENSITY;
}

// incident sky light at given position, integrated over the hemisphere (irradiance)
// r=length(x)
// muS=dot(x,s) / r
vec3 skyIrradiance(float r, float muS) {
    return irradiance(skyIrradianceSampler, r, muS) * SUN_INTENSITY;
}

// scattered sunlight between two points
// camera=observer
// viewdir=unit vector towards observed point
// sundir=unit vector towards the sun
// return scattered light and extinction coefficient
vec3 skyRadiance(vec3 camera, vec3 viewdir, vec3 sundir, out vec3 extinction)
{
    vec3 result;
    float r = length(camera);
    float rMu = dot(camera, viewdir);
    float mu = rMu / r;
    float r0 = r;
    float mu0 = mu;

    float deltaSq = sqrt(rMu * rMu - r * r + Rt*Rt);
    float din = max(-rMu - deltaSq, 0.0);
    if (din > 0.0) {
        camera += din * viewdir;
        rMu += din;
        mu = rMu / Rt;
        r = Rt;
    }

    if (r <= Rt) {
        float nu = dot(viewdir, sundir);
        float muS = dot(camera, sundir) / r;

        vec4 inScatter = texture4D(inscatterSampler, r, rMu / r, muS, nu) * gEnviromentParam.x;
        extinction = transmittance(r, mu);

        vec3 inScatterM = getMie(inScatter);
        float phase = phaseFunctionR(nu);
        float phaseM = phaseFunctionM(nu);
        result = inScatter.rgb * phase + inScatterM * phaseM;
    } else {
        result = vec3(0.0);
        extinction = vec3(1.0);
    }

    return result * SUN_INTENSITY;
}

// scattered sunlight between two points
// camera=observer
// point=point on the ground
// sundir=unit vector towards the sun
// return scattered light and extinction coefficient
vec3 inScattering(vec3 camera, vec3 point, vec3 sundir, out vec3 extinction) {
    vec3 result;
    vec3 viewdir = point - camera;
    float d = length(viewdir);
    viewdir = viewdir / d;
    float r = length(camera);
    float rMu = dot(camera, viewdir);
    float mu = rMu / r;
    float r0 = r;
    float mu0 = mu;

    float deltaSq = sqrt(rMu * rMu - r * r + Rt*Rt);
    float din = max(-rMu - deltaSq, 0.0);
    if (din > 0.0) {
        camera += din * viewdir;
        rMu += din;
        mu = rMu / Rt;
        r = Rt;
        d -= din;
    }

    if (r <= Rt) {
        float nu = dot(viewdir, sundir);
        float muS = dot(camera, sundir) / r;

        vec4 inScatter;

        if (r < Rg + 600.0) {
            // avoids imprecision problems in aerial perspective near ground
            float f = (Rg + 600.0) / r;
            r = r * f;
            rMu = rMu * f;
            point = point * f;
        }

        float r1 = length(point);
        float rMu1 = dot(point, viewdir);
        float mu1 = rMu1 / r1;
        float muS1 = dot(point, sundir) / r1;

        if (mu > 0.0) {
            extinction = min(transmittance(r, mu) / transmittance(r1, mu1), 1.0);
        } else {
            extinction = min(transmittance(r1, -mu1) / transmittance(r, -mu), 1.0);
        }

        vec4 inScatter0 = texture4D(inscatterSampler, r, mu, muS, nu) * gEnviromentParam.x;
        vec4 inScatter1 = texture4D(inscatterSampler, r1, mu1, muS1, nu) * gEnviromentParam.x;
        inScatter = max(inScatter0 - inScatter1 * extinction.rgbr, 0.0);

        // avoids imprecision problems in Mie scattering when sun is below horizon
        inScatter.w *= smoothstep(0.00, 0.02, muS);

        vec3 inScatterM = getMie(inScatter);
        float phase = phaseFunctionR(nu);
        float phaseM = phaseFunctionM(nu);
        result = inScatter.rgb * phase + inScatterM * phaseM;
    } else {
        result = vec3(0.0);
        extinction = vec3(1.0);
    }
    
    
    result *= clamp((d-100)/1000.f, 0, 1);  ///剔除近距离噪点误差


    return result * SUN_INTENSITY;
}

void sunRadianceAndSkyIrradiance(vec3 worldP, vec3 worldS, out vec3 sunL, out vec3 skyE)
{
    vec3 worldV = normalize(worldP); // vertical vector
    float r = length(worldP);
    float muS = dot(worldV, worldS);
    sunL = sunRadiance(r, muS);
    skyE = skyIrradiance(r, muS);
}

// ----------------------------------------------------------------------------
// SKYMAP AND HDR
// ----------------------------------------------------------------------------

uniform sampler2D skySampler;

uniform float hdrExposure;

vec4 skyRadiance(vec2 u) {
    return texture2D(skySampler, (u * (0.5 / 1.1) + 0.5), 0.0);
}

vec3 hdr(vec3 L, float expo) {
    L = L * expo;
    L.r = L.r < 1.413 ? pow(L.r * 0.38317, 1.0 / 2.2) : 1.0 - exp(-L.r);
    L.g = L.g < 1.413 ? pow(L.g * 0.38317, 1.0 / 2.2) : 1.0 - exp(-L.g);
    L.b = L.b < 1.413 ? pow(L.b * 0.38317, 1.0 / 2.2) : 1.0 - exp(-L.b);
    return L;
}


vec3 get_ortho(vec3 n)
{
    vec3 v;
	float maxv = abs(n[0]);
	int mi=0;
	for(int i=1; i<3; i++)
	{
		if(abs(n[i]) > maxv)
		{
			maxv = abs(n[i]);
			mi = i;
		}
	}

	if(mi == 0)
	{
		v[0] = -n[1]/n[0] - n[2]/n[0];
    	v[1] = 1.0;
    	v[2] = 1.0;
	}
	else if(mi == 1)
	{
		v[1] = -n[0]/n[1] - n[2]/n[1];
    	v[0] = 1.0;
    	v[2] = 1.0;
	}
	else if(mi == 2)
	{
		v[2] = -n[0]/n[2] - n[1]/n[2];
    	v[0] = 1.0;
    	v[1] = 1.0;
	}
    return normalize(v);
}



struct Light
{
	int type;
	vec4 position;
	vec3 diffuse_color;
	vec3 specular_color;
	vec3 ambient_color;
	float range;
	vec3 direction;
	float cos_angle;
	float angle;
	vec3 transmit;
};

uniform sampler2D gTransmittanceImage;


uniform sampler2D gPositionDepth;
uniform sampler2D gNormal;
uniform sampler2D gDiffuse;
uniform sampler2D gSpecular;
uniform sampler2D gMaterial;
uniform sampler2D gIrradiance;

uniform sampler2D gBentNormal;

uniform sampler2D gBackground;

uniform vec3 gVertical;


uniform sampler2D gRand;

uniform sampler3D gNoise3D;


uniform float shadow_min_value;
uniform float shadow_distance_scale[3];
uniform int shadow_c_count;

uniform int shadow_level_count;
uniform sampler2DArray VSMMaps;
uniform mat4 shadowWVP[3];
uniform vec3 lightPosForShadow[3];
uniform float shadowRange[3];
uniform vec3 lightShadowDirection;


uniform float gSampleRad;
uniform mat4 gProj;
uniform mat4 gModelView;
uniform float AOFactor;
const int MAX_KERNEL_SIZE = 64;
uniform vec4 gKernel[MAX_KERNEL_SIZE];

uniform vec2 jitter;


uniform float bloomThreshold;


uniform Light lights[16];
uniform int lightCount;
uniform vec3 worldSunDir;

uniform float gParticleDensity;

uniform vec4 clipPlane;


uniform vec3 gCameraPos;

uniform int flag;

varying vec2 vUv;

//uniform sampler2D enviromentMap2;
//uniform samplerCube pbrIrradianceMap;
uniform samplerCube pbrSpecularMap;
uniform sampler2D pbrBRDFMap;

uniform mat4 cameraConvertMatrix;

uniform mat4 gMatrixToProbe;

uniform float mirrorRatio;
uniform sampler2D mirrorMap;
//uniform vec3 mirrorCenter;
uniform vec3 mirrorDirection;
//uniform float mirrorDepth;

uniform float gAttenuationDistance;

uniform vec2 screenSize;


bool bit_and(int val, int ref) {
  if(val == 0) return false;

  return (val/ref) % 2 != 0;
}

vec3 PointLocalToEarth(vec3 lPt)
{
	//地心坐标系
	if (bit_and(flag, 0x800000) == true){ 
		return (cameraConvertMatrix * vec4(lPt, 1.0)).xyz;
	}
	//地表坐标系
	else{  
		return (cameraConvertMatrix * vec4(lPt, 1.0)).xyz + earthPos;
	}
}

vec3 MakeAsEarthSphere(vec3 Pt)
{
	return normalize(Pt) * earthPos.y;
}

vec3 VectorLocalToEarth(vec3 lVec)
{
	//地心坐标系
	if (bit_and(flag, 0x800000) == true){ 
		return (cameraConvertMatrix * vec4(lVec, 0.0)).xyz;
	}
	//地表坐标系
	else{  
		return (cameraConvertMatrix * vec4(lVec, 0.0)).xyz;
	}
}


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
		//vec3 worldP0 = (cameraConvertMatrix * vec4(worldP, 1.0)).xyz;
		//vec3 gCameraPos0 = (cameraConvertMatrix * vec4(gCameraPos, 1.0)).xyz;
 
		vec3 view_vec = worldP - gCameraPos;
		vec3 viewDir = normalize(view_vec);

		float dis_in_fog = length(view_vec);

		//if( fogHeight > EPSON){
			float H0 = dot(gCameraPos, gVertical);
			float H1 = dot(worldP, gVertical);

			float h0 = H0 - fogHeight;
			float h1 = H1 - fogHeight;

			if(h0 <= 0 && h1 >= 0) dis_in_fog *= -h0/(-h0+h1);
			else if(h0 >= 0 && h1 <= 0) dis_in_fog *= -h1/(h0-h1);
			else if(h0 >= 0 && h1 >= 0) dis_in_fog = 0.0;
		//}

		float density = fogDensity;

		vec3 up = gVertical;
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
   	 }

	return fogBlend;
}


const float environment_rotation = 0.0;
const float environment_exposure = 2.0;
const float EPSILON_COEF = 1e-4;


uniform float		gLightProbeGIFactor;

uniform vec3		gReflectProbePos;
uniform int			gReflectProbeIndex;



vec3 expand(vec3 v) {
  return (v - 0.5) * 2;
}



/* CODE-BEGIN add by yub */
/*vec3 envIrradiance(vec3 dir)
{	
	float rot = environment_rotation * M_2PI;
	float crot = cos(rot);
	float srot = sin(rot);
	vec4 shDir = vec4(dir.xzy, 1.0);
	shDir = vec4(
		shDir.x * crot - shDir.y * srot,
		shDir.x * srot + shDir.y * crot,
		shDir.z,
		1.0);
	return max(vec3(0.0), vec3(
		dot(shDir, irrad_mat_red * shDir),
		dot(shDir, irrad_mat_green * shDir),
		dot(shDir, irrad_mat_blue * shDir)
	)) * environment_exposure;
}*/



/* CODE-END */

vec3 importanceSampleGGX(vec2 Xi, vec3 A, vec3 B, vec3 C, float roughness) {
  float a = roughness * roughness;
  float cosT = sqrt((1.0 - Xi.y)/(1.0 + (a * a - 1.0) * Xi.y));
  float sinT = sqrt(1.0 - cosT * cosT);
  float phi = 2.0 * 3.14159 * Xi.x;
  return (sinT * cos(phi)) * A + (sinT * sin(phi)) * B + cosT * C;
}

vec3 fresnel(float vdh, vec3 F0) {
  /* Schlick with Spherical Gaussian approximation
     cf http://blog.selfshadow.com/publications/s2013-shading-course/karis/s2013_pbs_epic_notes_v2.pdf p3
  */
  float sphg = pow(2.0, (-5.55473 * vdh - 6.98316) * vdh);
  return F0 + (vec3(1.0, 1.0, 1.0) - F0) * sphg;
}

float G1(float ndw, float k) {
  return 1.0 / (ndw * (1.0 - k) +  k);
}

float visibility(float ndl, float ndv, float Roughness) {
  /* Schlick with Smith-like choice of k
     cf http://blog.selfshadow.com/publications/s2013-shading-course/karis/s2013_pbs_epic_notes_v2.pdf p3
     visibility is a Cook-Torrance geometry function divided by (n.l)*(n.v)
  */
  float k = max(Roughness * Roughness * 0.5, 1e-5);
  return G1(ndl, k) * G1(ndv, k);
}

vec3 cook_torrance_contrib(float vdh, float ndh, float ndl, float ndv, vec3 Ks, float Roughness) {
  /* 
    This is the contribution when using importance sampling with the GGX based
    sample distribution. This means ct_contrib = ct_brdf / ggx_probability
  */
  return fresnel(vdh, Ks) * (visibility(ndl, ndv, Roughness) * vdh * ndl / ndh);
}

const vec3  DEFAULT_BASE_COLOR     = vec3(0.5);
const float DEFAULT_ROUGHNESS      = 0.3;
const float DEFAULT_METALLIC       = 0.0;
const float DEFAULT_OPACITY        = 1.0;
const float DEFAULT_AO             = 1.0;
const float DEFAULT_SPECULAR_LEVEL = 0.5;

vec3 getSpecularColor(sampler2D specular_tex, vec2 tex_coord)
{
  vec4 out_color = texture2D(specular_tex, tex_coord).rgba;
  vec3 specColor = out_color.rgb + DEFAULT_BASE_COLOR * (1.0 - out_color.a);
  vec3 defaultF0 = mix(vec3(0.04), specColor, DEFAULT_METALLIC);
  return mix(specColor, defaultF0, (1.0 - out_color.a));
}



float random(vec3 seed, float i)
{
	float dot_product = dot(vec4(seed, i), vec4(12.9898, 78.233, 45.164, 94.673));
	return fract( sin(dot_product) * 43758.5453 );
}

/*
float calcZFromDepth(float depth)
{
	float A = shadowProjection[2][2];
	float B = shadowProjection[3][2];

	float zn = 2*depth - 1;
	return B / ( A + zn );
}
*/

vec3 calc_fresnel_roughness(vec3 n, vec3 v, vec3 F0, float roughness) {

    float ndotv = max(dot(n, v), 0.0);

    return F0 + (max(vec3(1.0 - roughness), F0) - F0) * pow(1.0 - ndotv, 5.0);
}


int CalcShadowLevel(vec3 viewPos)
{
	int k;
	for(k=0; k<shadow_level_count; k++){
		if(-viewPos.z < shadowRange[k]) break;
	}
	
	return k;
}


void CalcShadowLevelGradual(vec3 viewPos, out int level, out float scale)
{
	const int max_level_count = 3;
	const float cross_band = 0.01;

	level = 0;
	scale = 1.0;
	int k;
	for(k=0; k<shadow_level_count; k++)
	{
		if(-viewPos.z < shadowRange[k]){
			level = k;

			if(k > 0){
				float scale_prev = -viewPos.z / shadowRange[k-1];
				if(scale_prev < 1.0 + cross_band){
					scale = -(0.5 + (scale_prev - 1.0) / (2*cross_band));
				}
			}
			
			if(k < max_level_count-1){
				float scale_cur = -viewPos.z / shadowRange[k];
				if(scale_cur > 1.0 - cross_band){
					scale = 1.0 - (scale - (1.0 - cross_band)) / (2*cross_band);
				}
			}

			break;
		}
	}
}


float CalcShadowByLevel(vec3 P, int shadow_level)
{
	float shadow = 1.0;

	if(shadow_level >= 0 && shadow_level < 3){
		vec4 lightSpacePos = shadowWVP[shadow_level] * vec4(P, 1);
		vec4 projCoord = lightSpacePos / lightSpacePos.w;
		projCoord = projCoord*0.5 + 0.5;
		bool outsideShadowMap = lightSpacePos.w <= 0.0f || (projCoord.x < 0 || projCoord.y < 0) || (projCoord.x >= 1 || projCoord.y >= 1);
		
		float D = 0, variance = 0;
		if(!outsideShadowMap){
			float depth; // = distance(worldP, lightPosForShadow[shadow_level].xyz) * shadow_distance_scale[shadow_level];
			vec3 LP = P - lightPosForShadow[shadow_level].xyz;
		//	if(length(lightShadowDirection) > 0.5){
		//		depth = dot(LP, lightShadowDirection);
		//	}
		//	else
				depth = length(LP);
				
			depth *= shadow_distance_scale[shadow_level];
			
			vec2 moments = texture(VSMMaps, vec3(projCoord.xy, float(shadow_level))).xy;

			/*vec2 moments = vec2(0);
			vec2 texSize = textureSize(gPositionDepth, 0);
			moments += texture(VSMMaps, vec3(projCoord.xy, float(shadow_level))).xy;
			moments += texture(VSMMaps, vec3(projCoord.xy+vec2(-1.0/texSize.x, 0), float(shadow_level))).xy;
			moments += texture(VSMMaps, vec3(projCoord.xy+vec2(1.0/texSize.x, 0), float(shadow_level))).xy;
			moments += texture(VSMMaps, vec3(projCoord.xy+vec2(0, -1.0/texSize.y), float(shadow_level))).xy;
			moments += texture(VSMMaps, vec3(projCoord.xy+vec2(0, 1.0/texSize.y), float(shadow_level))).xy;
			moments /= 5.0;*/
			
			D = exp(shadow_c_count*depth) - moments.x;
			if(D > 0 && moments.x > 1e-6){
				variance =  moments.y - moments.x*moments.x;
				
				shadow = variance / (variance + D*D);
				
				shadow = clamp((shadow - shadow_min_value)/(1.0 - shadow_min_value), 0.0, 1.0);
			}
			 
		}
	}

	return shadow;
}


float CalcShadow(vec3 P)
{
	if(shadow_level_count == 0)
		return 1.0;

	float shadow = 1;

	vec3 viewPos = (gModelView * vec4(P,1)).xyz;
	int shadow_level;
	float range_scale;
	CalcShadowLevelGradual(viewPos, shadow_level, range_scale);
	
	if(range_scale < 0.0){
		float s = -range_scale;
		shadow = CalcShadowByLevel(P, shadow_level-1) *(1 - s) + CalcShadowByLevel(P, shadow_level) * s;
	}
	else if(range_scale < 1.0)
	{
		float s = range_scale;
		shadow = CalcShadowByLevel(P, shadow_level) * s + CalcShadowByLevel(P, shadow_level+1) * (1 - s);
	}
	else{
		shadow = CalcShadowByLevel(P, shadow_level);
	}
	
	
	return shadow;
}



float InScatter(vec3 start, vec3 rd, vec3 lightPos, vec3 lightDir, float d, float g)
{
    vec3 q = start - lightPos;
    float b = dot(rd, q);
    float c = dot(q, q);
    float iv = 1.0f / sqrt(c - b*b);
    float L = iv * (atan( (d + b) * iv) - atan( b*iv ));
    
    ///散射
    float cosTheta = dot(lightDir,rd);
    float P = 1/(4*M_PI)* (1 - g*g)/ pow(1 + g*g -2*g* cosTheta, 1.5);
    
    ///透光率
    //float T = exp(-c*d);

    return L * P;
}


float CalcSpotTransmittance(vec3 P, vec3 lightPos, vec3 lightDir, float transmit_near, float transmit_far, float transmit_width)
{
	vec3 dir = lightDir;
	vec3 u = vec3(1, 0, 0);
	vec3 v = vec3(0, 0, 1);

	vec3 D = P - lightPos;
	float h = dot(D, dir);
	vec3 Proj = D - h*dir;

	if(h < transmit_near) return 0.f;

	vec2 uv = vec2(dot(Proj, u), dot(Proj, v)) / transmit_width * transmit_near / h;

	float factor = h / transmit_far;
	if( factor > 1 ) return 0.f;

	//return texture(gTransmittanceImage, uv).r * ( 1 - pow(factor, 2));
	return texture(gTransmittanceImage, uv).r * ( 1 - factor*factor);
}


vec3 CalcLightsContribute(vec3 worldP, vec3 worldN, vec3 worldNBent, vec3 V, vec3 albedo, vec3 specColor, vec3 F0, vec2 dfg, float shininess, vec3 ambient, float amb_factor, vec3 diffuse, vec3 specular, float occlusion, float shadow)
{
	if(length(worldN) < 1e-6) return diffuse;

	for (int lightIndex = 0; lightIndex < lightCount; lightIndex++) {
			  
			if (bit_and(flag, 0x0100) == true && lightIndex == 0) continue;

			vec3 transmit = lights[lightIndex].transmit;
			  
			if(lights[lightIndex].type == 0){
				float coeff= 1.0;
				if(lights[lightIndex].position.w > 0.5 && lights[lightIndex].range > 1e-6){
					vec3 Len = worldP - lights[lightIndex].position.xyz;
					float len2 = (Len.x*Len.x + Len.y*Len.y + Len.z*Len.z);	
					coeff = clamp( 1.1-len2/(lights[lightIndex].range*lights[lightIndex].range), 0.0, 1.0);
				}
					
				ambient += albedo * amb_factor * lights[lightIndex].ambient_color * coeff;  // * min(0.02 + shadow, 1);  ///放开会导致自阴影

				vec3 lightPosition = lights[lightIndex].position.xyz;
				vec3 L = -(lights[lightIndex].position.w > 0.5 ? normalize(worldP - lightPosition) : normalize(lightPosition));

				float diffuseLight;
				diffuseLight = max(dot(worldNBent, L), 0); ///有太阳光时辅助灯不产生阴影
				if (bit_and(flag, 0x0100) != true) diffuseLight *= min(amb_factor*0.1 + shadow, 1);

				diffuse += albedo * lights[lightIndex].diffuse_color * diffuseLight * coeff * 1.5;
				    
				vec3 H = normalize(L + V);
				float specularLight = pow(max(dot(worldN, H), 0), shininess);
				if (bit_and(flag, 0x0100) != true) specularLight *= min(amb_factor*0.1 + shadow, 1);

				//if (diffuseLight <= 0) specularLight = 0;
				///2021-11-11,wxg,没有高光
				//specular += specColor * lights[lightIndex].specular_color * specularLight * coeff * (F0 * dfg.x + dfg.y);    
				specular += specColor * lights[lightIndex].specular_color * specularLight * coeff; 
			}
			else{
				float coeff= 1.0;
				if(lights[lightIndex].range > 1e-6){
					vec3 Len = worldP - lights[lightIndex].position.xyz;
					float len2 = (Len.x*Len.x + Len.y*Len.y + Len.z*Len.z);	
					coeff = clamp( 1.1-len2/(lights[lightIndex].range*lights[lightIndex].range), 0.0, 1.0);
				}
					
				vec3 lightPosition = lights[lightIndex].position.xyz;
				vec3 L = -(normalize(worldP - lightPosition));
					
				///在点光源的基础上根据角度计算聚光范围
				float dot1 = dot( -L, lights[lightIndex].direction );
				float d = 1.0 / ( 1.0 - lights[lightIndex].cos_angle );
				coeff *= clamp(1.0 - (1.0 - dot1) * d, 0.0, 1.0);
					
				ambient += albedo * amb_factor * lights[lightIndex].ambient_color * coeff;  /// * min(0.02 + shadow, 1); ///放开会导致自阴影

				float diffuseLight;
				diffuseLight = max(dot(worldNBent, L), 0);
				if (bit_and(flag, 0x0100) != true) diffuseLight *= min(amb_factor*0.1 + shadow, 1);

				///考虑水面焦散
				float transmFactor = 1.0;
				if(transmit.x > 0.000001){
					float dotv = (dot(-lights[lightIndex].direction, -L) + 1) / 2 + 1;
					transmFactor = CalcSpotTransmittance(worldP, lightPosition, lights[lightIndex].direction, transmit.x, transmit.y, transmit.z) * dotv; 
				}

				diffuse += albedo * lights[lightIndex].diffuse_color * diffuseLight * coeff * 1.5 * transmFactor;
				    
				vec3 H = normalize(L + V);
				float specularLight = pow(max(dot(worldN, H), 0), shininess);
				if (bit_and(flag, 0x0100) != true) specularLight *= min(amb_factor*0.1 + shadow, 1);

				//if (diffuseLight <= 0) specularLight = 0;
				///2021-11-11,wxg,没有高光
				//specular += specColor * lights[lightIndex].specular_color * specularLight * coeff * (F0 * dfg.x + dfg.y);   
				specular += specColor * lights[lightIndex].specular_color * specularLight * coeff;  
			}
		    
	  }
	  
	  if (bit_and(flag, 0x0100) == true) {
	  
			float coeff = abs(dot(worldSunDir, gVertical));
	
			coeff = pow(coeff, 0.5);
			//vec3 sunColor = mix(vec3(1, 0.8, 0.5), vec3(1.1, 1.05, 1.0), coeff)*gEnviromentParam.y*2;// * clamp(hdrExposure * 1.5, 0, 1);
			//vec3 sunColor = min(vec3(1, 0.9, 0.8)*gEnviromentParam.y*2, 5.0);
			//vec3 sunColor = min(vec3(1, 0.9, 0.8)*gEnviromentParam.y * 2.0, 2.0);
			vec3 sunColor = min(vec3(1.1, 1.05, 1.0)*gEnviromentParam.y * 2.0, 5.0);
	
		    
			//追加阳光的颜色
			vec3 worldL = -worldSunDir;
			float diffuseLight = max(dot(worldNBent, worldL), 0)  * min(amb_factor*0.1 + shadow, 1);
			diffuse += albedo * sunColor * diffuseLight;
			
			//ambient += albedo * amb_factor * (1 - diffuseLight) * coeff;
			ambient += amb_factor * sunColor * 0.1 * (coeff*coeff+0.01);// * min(0.02 + shadow, 1);  ///放开会导致自阴影

			 ambient *= gEnviromentParam.z;
		    
			vec3 worldV = normalize(gCameraPos - worldP);
			vec3 worldH = normalize(worldL + worldV);
			float specularLight = pow(max(dot(worldN, worldH), 0), shininess) * min(amb_factor*0.1 + shadow, 1);
			//if (diffuseLight <= 0) specularLight = 0;
			///2021-11-11,wxg,没有高光
			//specular += specColor * vec3(1, 1, 1) * specularLight * (F0 * dfg.x + dfg.y);
			specular += specColor * vec3(1, 1, 1) * specularLight *gEnviromentParam.y;

	  }
		
	  return (ambient*albedo + diffuse + specular) * occlusion;
}


float PointInCone(vec3 P, vec3 O, vec3 D, float cos_angle, float range) 
{
	float dtv = dot(P-O, D);
	if(dtv < 0 || dtv > range) return 0.f;

	float Pangle = dtv / length(P - O);
	if(Pangle < cos_angle ) return 0.f;

	return (Pangle - cos_angle) / (1 - cos_angle) * max((1 - pow(dtv / range * 1.25, 0.2)), 0);

}

float PointToLineDistance(vec3 P, vec3 B, vec3 D)
{
	vec3 dir = normalize(P - B);
	float dtv = dot(dir, D);
	if( abs(dtv) > 1.0 - 0.000001 ){
		return 0.f;
	}

	vec3 axis = cross(dir, D);
	vec3 orth = normalize(cross(axis, D));

	return abs(dot(P - B, orth));
}

int IsVectorsParallel(vec3 v1, vec3 v2)
{
	float dtv = dot(v1, v2);
	
	if(abs(dtv) > 1.0 - 1e-6) return 1;
	return 0;
}


void CalcPointProjection(vec3 P, vec3 B, vec3 N, out vec3 proj)
{
	float dtv = dot(P - B, N);
	proj = P - dtv*N;
}

void CalcPointProjectionOnLine(vec3 P, vec3 B, vec3 D, out vec3 proj)
{
	float dtv = dot(P - B, D);
	proj = B + dtv*D;
}


int CalcIntersectionOfLines(vec3 P1, vec3 D1, vec3 P2, vec3 D2, out vec3 I)
{
	int i, j;
	vec3 T;

	if(IsVectorsParallel(D1, D2) > 0) return 0;

	T = P2 - P1;
	if(length(T) < 1e-5){
		I = P1;
		return 1;
	}

	float val = 0;
	i = 0;
	int k;
	for(k=0; k<3; k++){
		if(abs(D1[k]) > val){
			val = abs(D1[k]);
			i = k;
		}
	}

	j = (i+1)%3;
	val = abs(D2[i]*D1[j] - D2[j]*D1[i]);
	for(k=0; k<3; k++){
		if(k==i)continue;
		float v = abs(D2[i]*D1[k] - D2[k]*D1[i]);
		if(v > val){
			val = v;
			j = k;
		}
	}

	float t2 = (T[j]*D1[i] - T[i]*D1[j]) / (D2[i]*D1[j] - D2[j]*D1[i] );
	I = P2 + t2 * D2;

	///验证解
	//float t1 = (T[i] + t2*D2[i]) / D1[i];
	//vec3 I1 = P1 + t1 * D1;
	//if(distance(I1, I) > 1e-5) return 0;

	return 1;
}


vec3 MakeOrtho(vec3 n)
{
	vec3 v;
	float maxv = abs(n[0]);
	int mi=0;
	for(int i=1; i<3; i++)
	{
		if(abs(n[i]) > maxv)
		{
			maxv = abs(n[i]);
			mi = i;
		}
	}

	if(mi == 0)
	{
		v[0] = -n[1]/n[0] - n[2]/n[0];
    	v[1] = 1.0;
    	v[2] = 1.0;
	}
	else if(mi == 1)
	{
		v[1] = -n[0]/n[1] - n[2]/n[1];
    	v[0] = 1.0;
    	v[2] = 1.0;
	}
	else if(mi == 2)
	{
		v[2] = -n[0]/n[2] - n[1]/n[2];
    	v[0] = 1.0;
    	v[1] = 1.0;
	}
	
	return normalize(v);
}


int CalcCommanVerticalLineOfTwoLine(vec3 P1, vec3 L1, vec3 P2, vec3 L2,
									 out vec3 I1, out vec3 I2,out vec3 L)
{
	/*算法:
	L = L1*L2;
	求P1到plane(P2,L)的投影PP1;
	求line(PP1, L1)与line(P2, L2)的交点I2;
	求line(I2, L)与line(P1, L1)的交点I1;*/

	if(IsVectorsParallel(L1, L2) > 0){
		I1 = P1;

		vec3 D;
		D = P2 -P1;
		if(IsVectorsParallel(D, L1) > 0){ 
			I2 = I1;
			L = MakeOrtho(L1);
			return 1;
		}

		CalcPointProjectionOnLine(P1 ,P2, L2, I2);
		L = I2 - I1;
		L = normalize(L);
		return 2;
	}

	L = cross(L1, L2);
	L = normalize(L);
	vec3 P1P2 = normalize(P1 - P2);
	if( abs(dot(P1P2, L)) < 0.00000001)
	{
		if(CalcIntersectionOfLines(P1, L1, P2, L2, I1) > 0){
			I2 = I1;
			return 3;
		}
		return 0;
	}

	vec3 PP1;
	CalcPointProjection(P1, P2, L, PP1);
	
	CalcIntersectionOfLines(PP1, L1, P2, L2, I2);
	CalcIntersectionOfLines(I2, L, P1, L1, I1);

	return 4;
}


int LineIntersectWithCylinder(vec3 P1, vec3 P2,  vec3 B, vec3 D, float l, float r, out vec3 I1, out vec3 I2)
{
	vec3 lineDir = normalize(P2 - P1);
	float dtv = dot(lineDir, D);
	if( abs(dtv) > 1-0.000001 ){
		if( PointToLineDistance(P1, B, D) > r ) return 0;

		float t1 = dot(P1-B, D);
		float t2 = dot(P2-B, D);

		if(t1 > l && t2 > 1 || t1 < 0 && t2 < 0){
			return 0;
		}

		if(dtv > 0){
			if(t1 < 0) I1 = B;
			else I1 = P1;

			if(t2 < l) I2 = P2;
			else I2 = B + l*D;
		}
		else{
			if(t2 < 0) I2 = B;
			else I2 = P2;

			if(t1 < l) I1 = P1;
			else I1 = B + l*D;
		}
		
		return 1;
	}

	vec3 inter1, inter2, L;
	int ret = CalcCommanVerticalLineOfTwoLine(P1, lineDir, B, D, inter1, inter2, L);

	float d = distance(inter1, inter2);
	if(d > r || distance(inter2, B) > l) return 0;

	float s = sqrt(r*r - d*d);
	I1 = inter1 - s*lineDir;
	I2 = inter1 + s*lineDir;

	return 1;
}

float random(vec4 seed)
{
	float dot_product = dot(seed, vec4(12.9898, 78.233, 45.164, 94.673));
	return fract( sin(dot_product) * 43758.5453 );
}

float GetFogNoise(vec3 P)
{
	float dis = 10;
	vec3 gBoundMin = vec3( -dis, -dis, -dis );
	vec3 gBoundMax = vec3( dis, dis, dis );

	vec3 uvw = (P - gBoundMin) / (gBoundMax - gBoundMin);

	return texture(gNoise3D, uvw).r;
}


void main() 
{
	vec2 uv = vUv;

	gMainColor.rgb = texture2D(gBackground, uv).rgb;
	gMainColor.a = -2;
	
	vec4 orm = texture2D(gMaterial, uv);
	
	float screenMirrorDepth = float(int(orm.a / 1000));
	float render_type = orm.a - screenMirrorDepth*1000;
	screenMirrorDepth /= 10.0;

	
	vec4 normalVal = texture2D(gNormal, uv);
	int option = int(normalVal.w / 100.0 + 0.00001);

	vec3 worldN = normalize(normalVal.xyz);
	vec3 worldNBent = bit_and(flag, 0x0400) == true? texture2D(gBentNormal, uv).xyz: worldN;

	vec3 albedo = texture2D(gDiffuse, uv).rgb ;
	float amb_factor = texture2D(gDiffuse, uv).a;

	if(length(worldN) < 1e-6){
		gMainColor.rgb = albedo;
		gMainColor.a = orm.a < 0.0001? -2: -1;
		return;
	}

	vec3 worldP = texture2D(gPositionDepth, uv).xyz;
	//float render_type = texture2D(gPositionDepth, uv).a;
	float emissive = normalVal.a - option * 100; 
	if(emissive < 0) emissive = 1.0;
	
	//gMainColor.rgb = vec3(0.0);
	
/*	if(bit_and(flag, 0x0200) == true ){
		float d = clipPlane.xyz*worldP + clipPlane.w;
		if(d < 0){
			gMainColor.a = 0;
			return;
		}
	}*/
	
	vec4 specularColor = texture2D(gSpecular, uv);
	float shininess = specularColor.w;

	//增强光照
	//specularColor.rgb *= gEnviromentParam.y * 2.0;
	//albedo *= gEnviromentParam.z;
  
    	float camera_dis = distance(gCameraPos, worldP);
	
	//gShadow = vec4(1.0, 1.0, 1.0, 1.0);
	
				///SSAO
					/*
	
					if(bit_and(flag, 0x0400) == true && AOFactor > 0.01 && camera_dis < gSampleRad*100){
		
						vec2 texSize = textureSize(gPositionDepth, 0);
						vec2 noiseScale = texSize / 2.0;
		
						vec3 fragPos = (gModelView * vec4(worldP,1)).xyz;
						vec3 normal = (gModelView * vec4(worldN,0)).xyz;
						vec3 randomVec = texture(gRand, uv * noiseScale).xyz;
		
						vec3 tangent = normalize(randomVec - normal * dot(randomVec, normal));
						vec3 bitangent = cross(normal, tangent);
						mat3 TBN = mat3(tangent, bitangent, normal);
		
						int kernelSize = 64;
						float radius = gSampleRad;
						vec3 bendNormal = worldN*64;
		
						float occlusion = 0.0;
						for(int i = 0; i < kernelSize; ++i)
						{
							// 获取样本位置
							vec3 sample = TBN * gKernel[i].xyz; // 切线->观察空间
			
							sample = fragPos + sample * radius; 
			
							vec4 offset = vec4(sample, 1.0);
							offset = gProj * offset; // 观察->裁剪空间
							offset.xyz /= offset.w; // 透视划分
							offset.xyz = offset.xyz * 0.5 + 0.5; // 变换到0.0 - 1.0的值域
		
			
							float sampleDepth = texture(gPositionDepth, offset.xy).w;
							vec3 sampleNormal = texture(gNormal, offset.xy).xyz;
			
							float rangeCheck = smoothstep(0.0, 1.0, radius / abs(-fragPos.z - sampleDepth));
							float fc = (sampleDepth > -sample.z + radius/1000 ? 0.0 : 1.0) * rangeCheck; 
							occlusion += fc;   
			
							//噪声无法忍受
							bendNormal += sampleNormal*(1-fc);
						}
		
						//噪声无法忍受
						worldN = normalize(bendNormal);
		
						occlusion = 1.0 - (max(occlusion / kernelSize - 0.1, 0));	
						gShadow.g = pow(occlusion, AOFactor);
					}
					else{
						gShadow.g = 1.0;
					}
					*/
	
	float csm_shadow = CalcShadow(worldP);
	
	if(normalVal.a < -0.5) csm_shadow = 1.0;  ///剪切断面去掉阴影
	
	vec3 V = normalize(gCameraPos - worldP);
	

	//vec4 orm = texture2D(gMaterial, uv);
  
	if(render_type >= 10 && render_type < 20)  ///pbr
	{ 
		//vec3 specColor = vec3(1.0);
		//vec3 emitColor = specularColor.rgb;
		vec3 specColor = specularColor.rgb;
		vec3 emitColor = vec3(0.0);
		
		float occlusion, roughness, metalic;
		occlusion = orm.r;
		roughness = orm.g;
		metalic  = orm.b;
		float envFactor = render_type - 10;


		vec3 worldN_probe = normalize((gMatrixToProbe * vec4(worldN, 0)).xyz);
		vec3 V_probe = normalize((gMatrixToProbe * vec4(V, 0)).xyz);

		vec3 F0 = mix(vec3(0.04, 0.04, 0.04), albedo, metalic);
		vec3 F = calc_fresnel_roughness(worldN_probe, V_probe, F0, roughness);
		
		float ndotv = max(0.0, dot(worldN_probe, V_probe));

		// Diffuse part
		vec3 T = vec3(1.0, 1.0, 1.0) - F;
		vec3 kD = T * (1.0 - metalic);
		
		//vec3 irradianceColor = texture(pbrIrradianceMap, worldN).rgb;
		//vec3 irradianceColor = CalcProbeDiffuse(worldP, worldN) * gLightProbeGIFactor;
		vec3 irradianceColor = texture(gIrradiance, uv).rgb * gLightProbeGIFactor;
		
		vec3 diffuse = kD * albedo * (irradianceColor*0.5 + 0.1);// * min(amb_factor*0.3 + csm_shadow, 1);

		// Specular part
		
		//vec3 r = 2.0 * ndotv * worldN - V;
		vec3 r = 2.0 * ndotv * worldN_probe - V_probe;
		
		vec3 ld =  textureLod(pbrSpecularMap, r, roughness*5).rgb * specColor;
		
		//衰减
		float attenuation = 1.0;
		if(gReflectProbeIndex >= 0){
			if(gAttenuationDistance > 1e-6){
				attenuation = distance(worldP, gReflectProbePos) / gAttenuationDistance;
				attenuation = clamp( 1 - attenuation*attenuation, 0, 1 );
			}
		}
		
		vec2 dfg = texture(pbrBRDFMap, vec2(ndotv, roughness)).xy;
		vec3 specular = ld * (F0 * dfg.x + dfg.y)  * gLightProbeGIFactor * min(attenuation * 10, 1);// * min(0.5 + csm_shadow, 1);		
		vec3 ambient = vec3(amb_factor * 0.1);
			
		gMainColor.rgb = CalcLightsContribute(worldP, worldN, worldNBent, V, albedo, specColor, F0, dfg, shininess, ambient, amb_factor, diffuse, specular, occlusion, csm_shadow);
			
		//gMainColor.rgb = (ambient + diffuse + specular) * occlusion;
		
		//gMainColor.rgb += emitColor;
	}
	
	else if(render_type >= 20 && render_type < 30)
	{
		//vec3 albedo = texture2D(gDiffuse, uv).rgb;
		vec3 specColor = specularColor.rgb;
		vec3 ambient = vec3(amb_factor * 0.1);
		vec3 specular = vec3(0.0);
		
		vec3 V = normalize(gCameraPos - worldP);
		float ndotv = max(0.0, dot(worldN, V));
			
		///2023-1-9, 非pbr不用环境的颜色，只用亮度
		vec3 irradianceColor = texture(gIrradiance, uv).rgb * gLightProbeGIFactor;
		float brightness = 0.3 * irradianceColor.r + 0.6 * irradianceColor.g + 0.1 * irradianceColor.b;
		vec3 diffuse = albedo * brightness * 0.4;//  * min(0.5 + csm_shadow, 1);
					  
		  
		gMainColor.rgb = CalcLightsContribute(worldP, worldN, worldNBent, V, albedo, specColor, vec3(0.0), vec2(0.0, 1.0), shininess, ambient, amb_factor, diffuse, specular, 1.0, csm_shadow);
		  
		//gMainColor.rgb = ambient*albedo + diffuse + specular; 
		float occlusion = render_type - 20;
		gMainColor.rgb *= occlusion;
		  
		  
		orm.b -= float(int(orm.b/100))*100;
		  
		///orm为emission
		if(orm.r>0.999 && orm.g>0.999 && orm.b>0.999) gMainColor.rgb = orm.rgb*albedo * gEnviromentParam.y;
		else gMainColor.rgb += orm.rgb;   //为什么叠加orm.rgb，加强点颜色值
	}
	
	else{  ///lines
		gMainColor.rgb = albedo*1.5;

		/*vec3 specColor = specularColor.rgb;
		vec3 ambient = vec3(amb_factor * 0.1);
		vec3 specular = vec3(0.0);
		
		vec3 V = normalize(gCameraPos - worldP);
		float ndotv = max(0.0, dot(worldN, V));
			
		///2023-1-9, 非pbr不用环境的颜色，只用亮度
		vec3 irradianceColor = texture(gIrradiance, uv).rgb * gLightProbeGIFactor;
		float brightness = 0.3 * irradianceColor.r + 0.6 * irradianceColor.g + 0.1 * irradianceColor.b;
		vec3 diffuse = albedo * brightness * 0.4;//  * min(0.5 + csm_shadow, 1);
					  
		  
		gMainColor.rgb = CalcLightsContribute(worldP, worldN, worldNBent, V, albedo, specColor, vec3(0.0), vec2(0.0, 1.0), shininess, ambient, amb_factor, diffuse, specular, 1.0, csm_shadow);
		*/
	}

	
	
	gMainColor.rgb *= emissive;   ///材质发光强度
	
	///添加倒影, screenMirrorDepth仅起标志作用，标志镜子材质
	if (bit_and(flag, 0x4000) == true && screenMirrorDepth  > 0.5 && orm.a > 0.00001) {
		vec3 T = get_ortho(mirrorDirection);
		vec3 B = cross(mirrorDirection, T);
		B = normalize(B);
		
		vec2 refl_uv = vec2( 1 - gl_FragCoord.x / screenSize.x, gl_FragCoord.y / screenSize.y ) + vec2( dot(worldN, T), dot(worldN, B) ) * 0.5;
		vec4 mirror = texture2D(mirrorMap, refl_uv);
		vec3 viewDir = normalize(gCameraPos - worldP);
													//float dot = min(max(dot(viewDir, mirrorDirection), 0), 1.0);
													//dot = pow(dot, 0.5);
		float dot = abs(dot(viewDir, mirrorDirection));

		float factor = mirrorRatio * (1 - dot) + 1*dot;
		
		///2023/7/12, 把倒影变暗
														//gMainColor.rgb = mix( mirror.rgb, gMainColor.rgb, factor );
		mirror.rgb *= 0.3;

														//factor = clamp((pow(mirrorRatio, 3) - 0.01), 0, 0.9);
		factor = mirrorRatio * 1.5;
															//vec3 blendColor = gMainColor.rgb * (1 - factor) + mirror.rgb * factor;
		vec3 blendColor = mirror.rgb * factor;
															//gMainColor.rgb = gMainColor.rgb*gMainColor.rgb + blendColor*( vec3(1) - gMainColor.rgb );
		gMainColor.rgb = gMainColor.rgb + blendColor*( vec3(1) - gMainColor.rgb ) * mirror.a;
   }
   
   
			   ///2021/4/14,无须记录深度
			   /*gMainColor.a = 1.0;
			   ///绘制倒影
			   if (bit_and(flag, 0x8000) == true) {
					gMainColor.a = mirrorDepth;   // min( dot(worldP - mirrorCenter, mirrorDirection) / gAttenuationDistance, 1.0);   ///记录倒影深度
			   }*/
   
   
   
  
     ////大气颜色
    //gAtmosphere = vec4(0.0, 0.0, 0.0, gEnviromentParam.x);
	vec4 atmo = vec4(0.0, 0.0, 0.0, gEnviromentParam.x);
	if (bit_and(flag, 0x2000) == true) {

		//vec3 worldP_abs = (cameraConvertMatrix * vec4(worldP, 1)).xyz;
		//vec3 gCameraPos_abs = (cameraConvertMatrix * vec4(gCameraPos, 1)).xyz;
		//vec3 worldSunDir_abs = normalize((cameraConvertMatrix * vec4(worldSunDir, 0)).xyz);

		vec3 worldP_earth = PointLocalToEarth(worldP);
		vec3 gCameraPos_earth = PointLocalToEarth(gCameraPos);
		vec3 worldSunDir_earth = VectorLocalToEarth(worldSunDir);

		//if (bit_and(flag, 0x800000) == true) earthPos = vec3(0.0);

		//vec3 PP = worldP_abs + earthPos;
		vec3 PP = worldP_earth;
		if(bit_and(option, 0x01)) PP = MakeAsEarthSphere(PP);

		vec3 viewDir = worldP_earth - gCameraPos_earth;
		vec3 v = normalize(viewDir);
		vec3 sunColor = vec3(step(cos(3.1415926 / 180.0), dot(v, worldSunDir_earth))) * SUN_INTENSITY;

		vec3 extinction;
		vec3 inscatter = inScattering(gCameraPos_earth, PP, -worldSunDir_earth, extinction);
		float dotv = max(dot(v, normalize(PP)), 0);
		///导致地上也出现一个太阳
		//gAtmosphere.rgb = /*sunColor * extinction +*/ inscatter * pow((1 - dotv), 3);
		//gAtmosphere.rgb = hdr(gAtmosphere.rgb, 0.6);

		//gMainColor.rgb = gMainColor.rgb * (1 - (gAtmosphere.a-1)*0.05) * (1 - gAtmosphere.b) + gAtmosphere.rgb;

		atmo.rgb = /*sunColor * extinction +*/ inscatter;// * pow((1 - dotv), 3);
		atmo.rgb = hdr(atmo.rgb, 0.6);

		gMainColor.rgb = gMainColor.rgb * (1 - (atmo.a-1)*0.05) * (1 - atmo.b) + atmo.rgb;
		//gMainColor.rgb = gMainColor.rgb* 0.2 + (gMainColor.rgb * (1 - (atmo.a-1)*0.05) * (1 - atmo.b) + atmo.rgb) * 0.8;
	}
	
	
	//雾
	float fogBlend = CalcFogBlend(worldP);
	if(fogBlend < 1 - 0.000001){
		//gAtmosphere.a = 1.0;  ///2023/4/15, 用雾来替代大气
		gMainColor.rgb = gMainColor.rgb*fogBlend + fogColor*(1-fogBlend);
	}

			/*if(fogDensity > 0.0000001){
     			 float dis = distance(gCameraPos, worldP);
				 vec3 viewDir = normalize(worldP - gCameraPos);

				float density = fogDensity;// * 0.5 + fogDensity * 0.5 * GetFogNoise(worldP);  /// worldP no use

				//density = worldP.y < 0? density * max(1 + worldP.y / 30, 0) : density;

				vec3 up = gVertical;
				density *= (1 - dot(up, viewDir)) / 2;
        
				float fogBlend = clamp(exp(-density * dis ), 0, 1);
				gAtmosphere.a = 1.0;  ///2023/4/15, 用雾来替代大气
		
				gMainColor.rgb = gMainColor.rgb*fogBlend + fogColor*(1-fogBlend);
			}*/
    
						//体积雾
					/*	vec4 back = texture2D(backTex, uv);
 						vec4 front = texture2D(frontTex, uv);
						float cloudBlend = 0.0;
						if( back.a > 0.5  ){
							float sceneDis = distance(gCameraPos, worldP);
							if(sceneDis >  front.r){
								if(sceneDis < back.r ) back.r = sceneDis;
								cloudBlend = clamp((back.r-front.r)*back.g, 0, 1);
								cloudBlend *= cloudBlend;
								gMainColor.rgb = gMainColor.rgb*(1-cloudBlend) + cloudColor*cloudBlend;
							}
						}
   
						 //gShadow.g += delta_factor * ( 1 - gShadow.g );
						float factor = clamp(cloudBlend*5, 0.0, 1.0);
						gShadow.rg = gShadow.rg*(1-factor) + vec2(1.0)*factor;*/


	///bloom

	if(bit_and(flag, 0x0800) == true){
		float brightness = dot(gMainColor.rgb, vec3(1.0));  ///超越白色的程度
		if(brightness > bloomThreshold*3 && brightness < 100.0)
			gBloom = gMainColor;
		else
			gBloom = vec4(0.0, 0.0, 0.0, 1.0);
	}
	else{
		gBloom = vec4(0.0, 0.0, 0.0, 1.0);
	}
	

	gBloom.a = normalVal.a;  ///记录剪切断面标志
	
	
	vec3 lightPos, lightDir, lightColor;

	if (bit_and(flag, 0x0100) == true) {
 
		lightColor = mix(vec3(1, 0.8, 0.5), vec3(0.9, 0.9, 0.8), 1.0) * clamp(hdrExposure * 1.5, 0, 1);
	   
		lightDir = -worldSunDir;
		lightPos = worldP - lightDir * 1.0;
		
	}
	else if(lightCount > 0){
		if(lights[0].type == 0){
			lightPos = lights[0].position.xyz;
			lightDir = -(lights[0].position.w > 0.5 ? normalize(worldP - lightPos) : normalize(lightPos));
			if(lights[0].position.w < 0.5)  lightPos = worldP - lightDir * 1.0;
		}
		else{
			lightPos = lights[0].position.xyz;
			lightDir = -(normalize(worldP - lightPos));
		}
		
		lightColor = lights[0].diffuse_color;
	}
	  	 

							////////  计算体积光
							/*gVolumeLightColor = vec4(0);
							if (bit_and(flag, 0x0100) == true) {
	
								float len = camera_dis;// * (1 + texture(gNoise, uv*20).x);
								//float L = InScatter(gCameraPos, -V, lightPos, lightDir, len, 0 ) * gParticleDensity;
								float factor = ( 2 + dot(worldSunDir, V) );
								float L = gParticleDensity * pow(factor, 2);

								float coeff = abs(dot(worldSunDir, gVertical));
								coeff = pow(coeff, 0.5);
								vec3 sunColor = mix(vec3(1, 0.8, 0.5), vec3(1.1, 1.05, 1.0), coeff)*gEnviromentParam.y;
								gVolumeLightColor.rgb = sunColor * 0.1 * L;
		
								float attenuation = 1.0;
								if(gAttenuationDistance > 1e-6){
									attenuation = camera_dis / gAttenuationDistance / 2;
									attenuation = clamp( 1-attenuation, 0, 1 );
								}
	
								///步进计算视线方向上的遮挡率
								if(true){
									//gVolumeLightColor.rgb = clamp(lightColor * L * attenuation, 0, 5);
									const int step_count = 200;
									float line_shadow = 0;
									for(int k=0; k<step_count-1; k++){
										vec3 P = worldP + camera_dis/step_count*(k+1)*V;
										line_shadow += CalcShadow(P);
									}
									gVolumeLightColor.a = min(line_shadow / (step_count-1), 1.0);
								}
							}

							if(true){
								///计算聚光灯的体积光
								int spot_light_count = 0;
								float max_brightness = 0;
								vec3 spot_light_color = vec3(0);
								for (int lightIndex = 0; lightIndex < lightCount; lightIndex++) {
			  
									if (bit_and(flag, 0x0100) == true && lightIndex == 0) continue;
			  
									if(lights[lightIndex].type != 0 && lights[lightIndex].range > 0.000001)
									{
										//spot_light_color += lights[lightIndex].diffuse_color * gParticleDensity * 0.5;
										spot_light_count++;

										vec3 lightPosition = lights[lightIndex].position.xyz;
										vec3 lightDirection = lights[lightIndex].direction;
										float cos_angle = lights[lightIndex].cos_angle;
										float range = lights[lightIndex].range;

										///使用最大圆柱范围，先计算到圆柱最近的交点
										float radius = range * tan(lights[lightIndex].angle);  
										vec3 I1, I2;
										int num = LineIntersectWithCylinder(gCameraPos, worldP,  lightPosition, lightDirection, range, radius, I1, I2);
				
										///步进计算视线方向上的亮度
										if(num > 0)
										{
											if(dot(I1 - gCameraPos, I2-I1) < 0) I1 = gCameraPos;

											float dis1 = distance(I1, gCameraPos);
											float dis2 = distance(I2, gCameraPos);

											float dis = dis2 - dis1;

											if(camera_dis > 1e-6){
												if(dis1 > camera_dis) dis = 0;
												else if(dis2 > camera_dis) dis = camera_dis - dis1;
											}

											if(dis > 1e-6){
												const int step_count = 100;
												float cone_bright = 0;
	
												for(int k=0; k<step_count-1; k++){
													vec3 P = I1 + dis/step_count*(k+1)*(-V);
													float b = PointInCone(P, lightPosition, lightDirection, cos_angle, range);
	
													cone_bright = cone_bright<b? b: cone_bright;
												}
												spot_light_color += cone_bright * lights[lightIndex].diffuse_color * gParticleDensity * 5;
												max_brightness += cone_bright;

											}
										}		
									}  
								}

								if(spot_light_count > 0)gVolumeLightColor.rgb +=  spot_light_color / spot_light_count;
								float alpha = min(max_brightness, 1);
								gVolumeLightColor.a = alpha > gVolumeLightColor.a ? alpha : gVolumeLightColor.a;
							}*/

	///2023-1-12, -2表示没有gbuffer绘制像素
	//gMainColor.a = orm.a < 0.0001? -2: -1;
	gMainColor.a = orm.a < 0.0001? -2: 1;

	if(gMainColor.a < -1.5) gMainColor.rgb = texture2D(gBackground, uv).rgb;


	/// for test
	/*vec3 viewPos = (gModelView * vec4(worldP,1)).xyz;
	int shadow_level = CalcShadowLevel(viewPos);

	if(shadow_level == 0) gMainColor.rgb *= vec3(1, 0, 0);
	else if(shadow_level == 1) gMainColor.rgb *= vec3(0, 1, 0);
	else if(shadow_level == 2) gMainColor.rgb *= vec3(0, 0, 1);*/
}