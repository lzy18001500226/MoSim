#version 330
//#extension GL_NV_shadow_samplers_cube : enable

layout (location = 0) out vec4 gMainColor; 
layout (location = 1) out vec4 gClipColor; 


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
//uniform float sun_exposure;
uniform vec4 gEnviromentParam;

float SUN_INTENSITY = gEnviromentParam.x * 10;

const float SCALE = 1000.0;

/*const*/ vec3 earthPos = vec3(0.0, 6360.010*SCALE, 0);

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

bool bit_and(int val, int ref) {
  if(val == 0) return false;

  return (val/ref) % 2 != 0;
}


struct Material
{
	vec3 Ke, Ka, Kd, Ks;
	float shininess;
  	float alpha;
};

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
};

struct TextureLight
{
	vec3 position;
	vec3 size;
	float strength;
	sampler2D texture;
};

uniform vec3 tl_n;
uniform vec3 tl_u;
uniform vec3 tl_v;


uniform Material material;

uniform Light lights[16];
uniform int lightCount;
uniform vec3 worldSunDir;

uniform vec3 globalAmbient;
uniform vec3 eyePositionLocal;
uniform vec3 gCameraPos;

uniform mat4 modelToWorld;

uniform mat4 gModelToWorldInv;

uniform int flag;
uniform float hdrBlend;
uniform float reflectRatio;
uniform float AOContrast;
uniform float AOBlend;

uniform sampler2D diffuseMap;
uniform sampler2D diffuseMap1;
uniform sampler2D diffuseMap2;

uniform int diffuseMapCount;

uniform vec3 gVertical;

uniform sampler2D specularMap;
uniform sampler2D normalMap;
uniform sampler2D AOMap;

uniform sampler2D templMap0;
uniform int mapCount;

uniform samplerCube enviromentMap;

uniform vec4 clipPlanesVol[3];
uniform int clipPlaneCountVol;

uniform vec3 clipCylinderOri;
uniform vec3 clipCylinderDir;
uniform vec2 clipCylinderParam;
uniform bool clipCylinderOutside;


struct ColorSetting
{
	float value;
	vec4 color;
};


uniform ColorSetting colorSettings[32];
uniform	int colorSettingCount;

struct VolumeTexture
{
	vec3 boundMin;
	vec3 boundMax;
	float factor;
	mat4 transform;
	mat4 transformToObject;
	sampler3D texture;
	sampler3D textureOld;
	int dimension;
};

uniform VolumeTexture volumeTex;

float PointToLineDistance(vec3 P, vec3 B, vec3 D)
{
	vec3 dir = normalize(P - B);
	float dtv = dot(dir, D);
	if( abs(dtv) > 1-0.000001 ){
		return 0;
	}

	vec3 axis = cross(dir, D);
	vec3 orth = normalize(cross(axis, D));

	return abs(dot(P - B, orth));
}

bool IsPointInCylinder(vec3 P, vec3 C, vec3 D, float r, float l)
{
	vec3 PC = P - C;
	float dv = dot(PC, D);
	if( abs(dv) > l/2 ) return false;

	float d = PointToLineDistance(P, C, D);
	if(d > r) return false;

	return true;
}

vec4 GetVolumeColor(vec3 P, VolumeTexture vt)
{
	if(colorSettingCount == 0) return vec4(0);

	if(clipPlaneCountVol > 0){

		vec3 localP = (gModelToWorldInv * vec4(P.xyz, 1)).xyz;
		float d = dot(clipPlanesVol[0].xyz, localP) + clipPlanesVol[0].w;
		if(d < 0){
			return vec4(0);
		}
	}

	if(bit_and(flag, 0x200000) == true){
		float rad = clipCylinderParam.x;
		float len = clipCylinderParam.y;
		if(IsPointInCylinder(P, clipCylinderOri, clipCylinderDir, rad, len) == clipCylinderOutside){
			return vec4(0);
		}
	}


	vec3 localP = (vt.transform * vec4(P, 1)).xyz;

	vec3 len = vt.boundMax - vt.boundMin;
	vec3 uvw = (localP - vt.boundMin) / len;

	if( uvw.x > 1 || uvw.y > 1 || uvw.z > 1 || uvw.x < 0  || uvw.y < 0 || uvw.z < 0 ) return vec4(0);

	vec3 data;// = texture(vt.texture, uvw).xyz;

	if(vt.factor > -0.000001){
		data = texture(vt.textureOld, uvw).xyz *(1 - vt.factor) + texture(vt.texture, uvw).xyz * vt.factor;
	}
	else
		data = texture(vt.texture, uvw).xyz;

	//2024-12-23, wxg，导致始终显示红色
	//float data_val = length(data);
	float data_val = vt.dimension > 1 ? length(data.xyz) : data.x;

	int i;
	for(i=0; i<colorSettingCount; i++){
		if( data_val < colorSettings[i].value) break;
	}

	if( i==0 ) 
		return colorSettings[0].color;
	else if(i == colorSettingCount) 
		return colorSettings[colorSettingCount-1].color;
	else{
		float factor = (data_val - colorSettings[i-1].value) / (colorSettings[i].value - colorSettings[i-1].value);

		return colorSettings[i-1].color*(1-factor) + colorSettings[i].color*factor;
	}
}


uniform float mirrorRatio;
uniform sampler2D mirrorMap;
uniform vec3 mirrorCenter;
uniform vec3 mirrorDirection;
uniform float mirrorDepth;

uniform sampler2D projectorMap;	
uniform float projectorRepeat;
uniform float projectorBlend;
uniform int projectorBlendType;

uniform sampler2D SSAOMap;

uniform vec2 screenSize;

uniform vec4 clipPlanes[3];
uniform int clipPlaneCount;


uniform float materBrightness;

uniform float		gLightProbeGIFactor;

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


uniform int textureLightCount;
uniform TextureLight textureLights[8];
	
uniform sampler2D shadowMap;
//uniform sampler2D depthMap;



vec3 calcTextureLights(vec3 P, vec3 N, vec3 baseColor, vec3 ambColor)
{
	vec3 lightColor = vec3(0, 0, 0);

	int index;
	for(index = 0; index < textureLightCount; index++){
	
		float l = textureLights[index].size.x;
		float w = textureLights[index].size.y;
		float h = textureLights[index].size.z;
		float step = w>l?w/32:l/32;

		for(float wi = 0; wi <= w; wi+=step){
			for(float li=0; li<=l; li+=step){
				//vec3 lightPosition = textureLights[index].position + vec3(wi-w/2, 0, li-l/2);
				vec3 lightPosition = textureLights[index].position + tl_u*(wi-w/2) + tl_v*(li-l/2);
				vec3 lightDiffuse = texture2D(textureLights[index].texture, vec2(li/l, wi/w)).rgb;

				float coeff;
				vec3 Len = lightPosition - P;
	
				//float len2 = (Len.x*Len.x + Len.y*Len.y*step*step/h/h + Len.z*Len.z);
				float nf = 	abs(dot(Len, tl_n))/h;
				float uf = abs(dot(Len, tl_u))/step;
				float vf = 	abs(dot(Len, tl_v))/step;

				coeff = clamp(1 - (nf*nf + uf*uf + vf*vf), 0, 1);

				if(coeff > 0){
    					vec3 L = normalize(lightPosition - P);
    					float diffuseLight = max(dot(N, L), 0);
    					lightColor += (ambColor+baseColor) * lightDiffuse * diffuseLight * coeff * textureLights[index].strength;
				}
			}
		}
	}

	return lightColor;
}


in vec4 projectorTexCoord;

in vec2 oTexcoord0;
in vec2 oTexcoord1;
in vec2 oTexcoord2;

in vec2 oTexcoordSpec;
in vec2 oTexcoordNorm;
in vec2 oTexcoordAO;

in vec3 worldP;
in vec3 worldP_no_offset;

in vec3 vColor;
in vec3 vPosition;
in vec3 vNormal;



vec3 expand(vec3 v) {
  return (v - 0.5) * 2;
}

float R(float original_value, float original_min, float original_max, 
            float new_min, float new_max)
{
	//if(original_value <= original_min) return 0;
	
    return new_min + ((( original_value - original_min) / (original_max - original_min))
            * (new_max - new_min));
}

vec3 atmosphereColor(vec3 originColor, vec3 worldP, vec3 worldCamera, vec3 worldSunDir) {

    vec3 PP = worldP + earthPos;

    vec3 Lsun;
    vec3 Esky;
    vec3 extinction;
    sunRadianceAndSkyIrradiance(PP, worldSunDir, Lsun, Esky);

	vec3 cloudL = (Lsun * max(worldSunDir.z, 0.0) + Esky / 10.0) / M_PI;

    vec3 inscatter = inScattering(worldCamera + earthPos, PP, worldSunDir, extinction);
    cloudL = cloudL * extinction + inscatter;

    return cloudL * originColor;
}

float weight(float z, float a) 
{
	return clamp(pow(min(1.0, a * 10.0) + 0.01, 3.0) * 1e8 * pow(1.0 - z * 0.9, 3.0), 1e-2, 3e3);
}


void main() {

  vec4 FragColor = vec4(0, 0, 0, 1);
  
  if (bit_and(flag, 0x80000) == true) {
		float height = dot(worldP - mirrorCenter, mirrorDirection);
		if(height <= -mirrorDepth * 0.01){
			FragColor = vec4(0, 0, 0, 1.0);
			gMainColor = FragColor;
			return;
		}
   }

   
   
  if(bit_and(flag, 0x0200) == true ){
	
		for(int k=0; k<clipPlaneCount; k++){
			float d = dot(clipPlanes[k].xyz, worldP) + clipPlanes[k].w;
			if(d < 0){
				discard;
				return;
			}
		}
	}
 

  vec3 ambient = material.Ka * globalAmbient;
  vec3 diffuse = vec3(0, 0, 0);
  vec3 specular = vec3(0, 0, 0);
  vec3 Kd = material.Kd;
  vec3 Ks = material.Ks;
  vec3 Ka = material.Ka;
  vec3 Ke = material.Ke;
  float shininess = material.shininess;
  vec3 P = vPosition;
  vec3 N;
  if (bit_and(flag, 0x0001) == true) {
    vec3 mapN = texture2D(normalMap, oTexcoordNorm.xy).xyz * 2.0 - 1.0;
    
    /* Thanks to http://www.thetenthplanet.de/archives/1180 */
    /* get edge vectors of the pixel triangle */
		vec3 dp1 = dFdx(vPosition);
		vec3 dp2 = dFdy(vPosition);
		vec2 duv1 = dFdx(oTexcoordNorm.xy);
		vec2 duv2 = dFdy(oTexcoordNorm.xy);

		/* solve the linear system */
		vec3 dp2perp = cross(dp2, vNormal);
		vec3 dp1perp = cross(vNormal, dp1);
		vec3 tangent = dp2perp * duv1.x + dp1perp * duv2.x;
		vec3 binormal = dp2perp * duv1.y + dp1perp * duv2.y;

		/* construct a scale-invariant frame */
		float invmax = inversesqrt(max(dot(tangent, tangent), dot(binormal, binormal)));
		mat3 tsn = mat3(tangent * invmax, binormal * invmax, vNormal);

		N = normalize(tsn * mapN);
  } else {
    N = normalize(vNormal);
  }
  
  
  vec3 worldN = normalize(modelToWorld * vec4(N, 0)).xyz;

 
  
  
  vec3 baseColor = Kd;
  if (bit_and(flag, 0x0002) == true) {
    baseColor *= texture2D(diffuseMap, oTexcoord0.xy).rgb;
  } 
 
  if (bit_and(flag, 0x10000) == true) {
    baseColor = vColor;
	Ka = vColor * 0.3;
  } 

  gClipColor.rgb = baseColor;
  gClipColor.a = 1.0;
  

  

  ///直线
   if (bit_and(flag, 0x8000) == true) {
		gMainColor.rgb = baseColor;
		gMainColor.a = material.alpha;
		return;
  } 


  if (bit_and(flag, 0x0004) == true) {
    Ks *= texture2D(specularMap, oTexcoordSpec.xy).rgb;
  }
  vec3 V = normalize(eyePositionLocal - P);

  

  if (bit_and(flag, 0x0008) == true) {
    vec3 R = reflect(V, N);
    //vec3 reflectedColor = textureCube(enviromentMap, R).rgb;
	vec3 reflectedColor = texture(enviromentMap, R).rgb;
    float vdh = dot(V, N);
    float fresnel = hdrBlend + (1 - hdrBlend) * pow(2, (-5.55473 * vdh - 6.98316) * vdh);
    specular = Ks * reflectedColor * fresnel;
  }

  for (int lightIndex = 0; lightIndex < lightCount; lightIndex++) {
  
    if (bit_and(flag, 0x0100) == true && lightIndex == 0) continue;
  
	if(lights[lightIndex].type == 0){
		float coeff= 1.0;
		if(lights[lightIndex].position.w > 0.5 && lights[lightIndex].range > 1e-6){
			vec3 Len = lights[lightIndex].position.xyz - worldP;
			float len2 = (Len.x*Len.x + Len.y*Len.y + Len.z*Len.z);	
			coeff = clamp( 1.1-len2/(lights[lightIndex].range*lights[lightIndex].range), 0.0, 1.0);
		}
		
		ambient += Ka * lights[lightIndex].ambient_color * coeff;

		vec3 lightPosition = lights[lightIndex].position.xyz;
		vec3 L = -(lights[lightIndex].position.w > 0.5 ? normalize(worldP - lightPosition) : normalize(lightPosition));
		float diffuseLight = max(dot(worldN, L), 0);
		diffuse += baseColor * lights[lightIndex].diffuse_color * diffuseLight * coeff * 1.5;
	    
		vec3 H = normalize(L + V);
		float specularLight = pow(max(dot(worldN, H), 0), shininess);
		if (diffuseLight <= 0) specularLight = 0;
		specular += Ks * lights[lightIndex].specular_color * specularLight * coeff;
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
		
		ambient += Ka * lights[lightIndex].ambient_color * coeff;

		float diffuseLight = max(dot(worldN, L), 0);
		diffuse += baseColor * lights[lightIndex].diffuse_color * diffuseLight * coeff;
	    
		vec3 H = normalize(L + V);
		float specularLight = pow(max(dot(worldN, H), 0), shininess);
		if (diffuseLight <= 0) specularLight = 0;
		specular += Ks * lights[lightIndex].specular_color * specularLight * coeff;   
	}
  }


  
  if (bit_and(flag, 0x0100) == true) {
    float coeff = abs(dot(worldSunDir, vec3(0, 1, 0)));
   
    //vec3 sunColor = mix(vec3(1, 0.8, 0.5), vec3(0.9, 0.9, 0.8), coeff) * clamp(hdrExposure * 1.5, 0, 1);
    //vec3 sunColor = mix(vec3(1.0, 0.7, 0.4), vec3(1.3, 1.1, 1.0), verticle_angle) * clamp(hdrExposure, 0, 2);
    vec3 sunColor = mix(vec3(1, 0.8, 0.5), vec3(1.1, 1.05, 1.0), coeff) * gEnviromentParam.y * 2;// * clamp(hdrExposure * 1.5, 0, 1);
    
    //追加阳光的颜色
    vec3 worldL = -worldSunDir;
    float diffuseLight = max(dot(worldN, worldL), 0)  * min(Ka.r*0.1 + 1.0, 1);
    diffuse += baseColor * sunColor * diffuseLight;
    
    //ambient += Ka * sunColor * (coeff*coeff+0.1) *0.5;
    ambient += Ka * sunColor * 0.1 * (coeff*coeff+0.01);
    
    vec3 worldV = normalize(gCameraPos - worldP);
    vec3 worldH = normalize(worldL + worldV);
    //float specularLight = pow(max(dot(worldN, worldH), 0), shininess);
    float specularLight = pow(max(dot(worldN, worldH), 0), shininess) * min(Ka.r*0.1 + 1.0, 1);

    //if (diffuseLight <= 0) specularLight = 0;
    specular += Ks * vec3(1, 1, 1) * specularLight *gEnviromentParam.y;

  }
 
  if (bit_and(flag, 0x0010) == true) {
    
    float dotOfFace = 0;
    if (bit_and(flag, 0x0100) == true) {
		dotOfFace = dot(worldN, worldSunDir);
    }
    else{
		vec4 lightPosition = lights[0].position;
		if(lightPosition.w < 0.5){
			dotOfFace = dot(vNormal, lightPosition.xyz);
		}
		else{
			dotOfFace = dot(vNormal,  vPosition - lightPosition.xyz);
		}
	}


    if(dotOfFace < 0){
		float shadowFactor = texture(shadowMap, gl_FragCoord.xy / screenSize).r;
		diffuse *= shadowFactor;
	 	specular *= shadowFactor;
    }
  }

  vec3 finalColor = ambient*baseColor + diffuse + specular; 

  ///2024-1-17
  finalColor *= gLightProbeGIFactor;
  

  if (bit_and(flag, 0x400000) == true) {
    vec4 volumeColor = GetVolumeColor(worldP_no_offset, volumeTex);
	finalColor = finalColor*(1 - volumeColor.a) + volumeColor.rgb * volumeColor.a;
  } 
  
   
  if (bit_and(flag, 0x0040) == true) {
	vec3 occlusion = texture2D(AOMap, oTexcoordAO).rgb;
    finalColor *= occlusion;
  }  

  if(bit_and(flag, 0x0800)== true){
    finalColor *= texture(SSAOMap, gl_FragCoord.xy / screenSize).r;
  }

  float transparencySetting = material.alpha;
  

  finalColor += calcTextureLights( P, N, baseColor, material.Ka);
  
  if(Ke.r > 0.99 && Ke.g > 0.99 && Ke.b > 0.99)
	finalColor = Ke*baseColor;
  else
	finalColor += Ke;
  
  finalColor *= materBrightness;
  
  
   if( bit_and(flag, 0x20000)== true ){

		vec4 projectorTc = projectorTexCoord * projectorRepeat;
        projectorTc.w = 1;
		
		vec3 projectorColor = texture2DProj(projectorMap, projectorTc).rgb;
                
        if(projectorBlendType == 1){
   			float cs = ((finalColor.x+finalColor.y+finalColor.z)/3 - 0.1) * 2;
   			if(cs < 0) cs = 0;
   			finalColor += projectorColor*projectorBlend * cs;
		}
	    if(projectorBlendType == 2){
			finalColor = finalColor*(1-projectorBlend) + finalColor*projectorColor*projectorBlend;
	    }

   }

  
  if (bit_and(flag, 0x2000) == true) {

	if (bit_and(flag, 0x800000) == true) earthPos = vec3(0.0);

	vec3 worldP_abs = (cameraConvertMatrix * vec4(worldP, 1)).xyz;
	vec3 gCameraPos_abs = (cameraConvertMatrix * vec4(gCameraPos, 1)).xyz;
	vec3 worldSunDir_abs = normalize((cameraConvertMatrix * vec4(worldSunDir, 0)).xyz);
    
    	vec3 PP = worldP_abs + earthPos;
	vec3 viewDir = worldP_abs - gCameraPos_abs;
	vec3 v = normalize(viewDir);
	vec3 sunColor = vec3(step(cos(3.1415926 / 180.0), dot(v, worldSunDir_abs))) * SUN_INTENSITY;

	vec3 extinction;
	vec3 inscatter = inScattering(gCameraPos_abs + earthPos, PP, -worldSunDir_abs, extinction);
	float dotv = max(dot(v, normalize(PP)), 0);
	///导致地上也出现一个太阳
	vec3 scatterColor = /*sunColor * extinction +*/ inscatter * pow((1 - dotv), 3);
	scatterColor = hdr(scatterColor, 0.6);
	finalColor += scatterColor;
  }

  
   if (bit_and(flag, 0x40000) == true) {
		vec2 uv = vec2( 1 - gl_FragCoord.x / screenSize.x, gl_FragCoord.y / screenSize.y ) + (1 - dot(worldN, mirrorDirection));
		vec4 mirror = texture2D(mirrorMap, uv);
		vec3 viewDir = normalize(gCameraPos - worldP);
		float dot = min(max(dot(viewDir, mirrorDirection), 0), 1.0);
		dot = pow(dot, 0.5);

		float factor = mix(mirror.a, 1.0, dot);
		factor = mix(mirrorRatio, 1.0, factor);
		
		///2023/7/12, 把倒影变暗
		//finalColor = mix( mirror.rgb, finalColor, factor );
		mirror.rgb *= 0.3;

		factor = clamp((pow(mirrorRatio, 3) - 0.01), 0.0, 0.9);
		vec3 blendColor = finalColor * (1 - factor) + mirror.rgb * factor;
		finalColor = finalColor*finalColor + blendColor*( vec3(1) - finalColor );
   }
   
  

  FragColor.rgb = finalColor;
  FragColor.a = texture2D(diffuseMap, oTexcoord0.xy).a * transparencySetting;
  
  if(bit_and(flag, 0x0400) == true) {
	float alpha = (baseColor.r + baseColor.g + baseColor.b) / 3;
	if(alpha < 0.1) FragColor.a *= alpha*0.1;
	//else FragColor.a = 1;
  }
  
 
  ///绘制倒影
  if (bit_and(flag, 0x80000) == true) {
		//FragColor.a = min( dot(worldP - mirrorCenter, mirrorDirection) / mirrorDepth, 1.0);   ///记录倒影深度

		float height = max(dot(vPosition - mirrorCenter, mirrorDirection), 0);
		float screenMirrorDepth = max(1.0 - max((height - mirrorDepth ) / mirrorDepth, 0), 0);
		FragColor.a = screenMirrorDepth;
   }

  
  //FragColor.a = clamp(worldP.y / 5000, 0, 1);
  //FragColor.rgb = vec3(0)*( 1 -  FragColor.a) + vec3(0, 1, 1)*FragColor.a;


  //雾
  float fogBlend = CalcFogBlend(worldP);
  FragColor.rgb = FragColor.rgb*fogBlend + fogColor*(1-fogBlend);

					/*if(fogDensity > 0.0000001){
     					 float dis = distance(gCameraPos, worldP);
						 vec3 viewDir = normalize(worldP - gCameraPos);

						float density = fogDensity;// * 0.5 + fogDensity * 0.5 * GetFogNoise(worldP);  /// worldP no use

						//density = worldP.y < 0? density * max(1 + worldP.y / 30, 0) : density;

						vec3 up = gVertical;
						density *= (1 - dot(up, viewDir)) / 2;
        
						float fogBlend = clamp(exp(-density * dis ), 0, 1);
						//gAtmosphere.a = 1.0;  ///2023/4/15, 用雾来替代大气
		
						FragColor.rgb = FragColor.rgb*fogBlend + fogColor*(1-fogBlend);
					}*/
 

			 /* if( transparencySetting < 0.9-1e-6 )
			  {
					float transparency = FragColor.a;
					//获得要输出的颜色，把rgb乘上透明度，加到Color这张纹理上
					//gl_FragData[0] = vec4(FragColor.rgb * FragColor.a, FragColor.a);
					//在记录累加次数的纹理上加1
					//gl_FragData[1] = vec4(1.0);

					vec3 viewDir = worldP - gCameraPos;
					vec3 v = normalize(viewDir);
					float nv = abs(dot(v, N));

					FragColor.a += (1 - nv) * ( 1 - FragColor.a) * 0.8; 
					if(transparency < 0.25){
						FragColor.a = FragColor.a * (transparency * 4);
					}
	
					float w = weight(gl_FragCoord.z, FragColor.a);

					gl_FragData[0] = vec4(FragColor.rgb * FragColor.a * w, FragColor.a);  
					gl_FragData[1] = FragColor.a * w;
			  }
			  else{
				gl_FragData[0] = FragColor;
				gl_FragData[1] = 1.0;
			  }*/

	gMainColor = FragColor;

  //gl_FragCoord.z = R( FragColor.a, 1, 0, gl_FragCoord.z, 1);
}

