



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

const float SUN_INTENSITY = 100.0;

//uniform float atmosphere_density;

//uniform float sun_exposure;
uniform vec4 gEnviromentParam;

const float SCALE = 1000.0;

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
    return texture3D(table, vec3((uNu + uMuS) / float(RES_NU), uMu, uR)) * (1.0 - lerp) +
           texture3D(table, vec3((uNu + uMuS + 1.0) / float(RES_NU), uMu, uR)) * lerp;
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
    
    
    result *= clamp((d-10)/100.0, 0, 1);  ///剔除近距离噪点误差

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
	float angle;
	vec3 transmit;
};

uniform sampler2D gTransmittanceImage;


uniform vec3 gVertical;

uniform vec2 screenSize;

uniform mat4 modelToWorldFrag;

uniform Material material;
uniform Light lights[16];
uniform int lightCount;
uniform vec3 worldSunDir;

uniform vec3 globalAmbient;
uniform vec3 eyePositionLocal;
uniform vec3 gCameraPos;

uniform mat4 gModelToWorldInv;

uniform int flag;
uniform float hdrBrightness;
uniform float hdrGray;
uniform float hdrBlend;
uniform float materGray;
uniform float materBrightness;
uniform float reflectRatio;
uniform float alphaBooster;
uniform float sceneContrast;
uniform float sceneBrightness;
uniform float AOContrast;
uniform float AOBlend;
uniform float normalStrength;

uniform sampler2D diffuseMap;
uniform sampler2D diffuseMap1;
uniform sampler2D diffuseMap2;

//varying vec2 oTexcoordOrigin;
varying vec2 oTexcoord0;
//varying vec2 oTexcoord1;
//varying vec2 oTexcoord2;

uniform sampler2D specularMap;
uniform sampler2D normalMap;
uniform sampler2D AOMap;

varying vec2 oTexcoordSpec;
varying vec2 oTexcoordNorm;
//varying vec2 oTexcoordAO;

//uniform sampler2D templMap0;
uniform int mapCount;

uniform sampler2D reflectMap;
//uniform samplerCube enviromentMap;
//uniform sampler2D enviromentMap2;

//uniform samplerCube pbrIrradianceMap;
uniform samplerCube pbrSpecularMap;
uniform sampler2D pbrBRDFMap;


uniform float mirrorRatio;
uniform sampler2D mirrorMap;
uniform vec3 mirrorCenter;
uniform vec3 mirrorDirection;


uniform sampler2D projectorMap;	
uniform float projectorRepeat;
uniform float projectorBlend;
uniform int projectorBlendType;


uniform sampler2D gIrradiance;


uniform vec4 clipPlanes[3];
uniform int clipPlaneCount;


varying vec3 lightDir;
varying vec4 lightSpec;
varying vec4 lightAmbi;
varying vec3 halfAngle;
varying vec3 normalLocal;
varying vec3 normalWorld;

varying vec4 shadowTexCoord;
varying vec4 reflectTexCoord;
//varying vec4 projectorTexCoord;

varying vec3 I_World;
varying vec3 I_Local;

varying vec4 oColor;

uniform mat4 cameraConvertMatrix;
uniform mat4 gMatrixToProbe;

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


varying vec3 vPosition;
varying vec3 vNormal;
//varying vec3 vTangent;
varying vec3 worldP;
varying vec3 worldN;
varying vec3 worldP_no_offset;

uniform mat4 irrad_mat_red;
uniform mat4 irrad_mat_green;
uniform mat4 irrad_mat_blue;

uniform float roughFactor;
uniform float metaFactor;
uniform float occluFactor;
uniform float envFactor;
uniform float baseFactor;


uniform vec4 clipPlanesVol[3];
uniform int clipPlaneCountVol;

uniform vec3 clipCylinderOri;
uniform vec3 clipCylinderDir;
uniform vec2 clipCylinderParam;
uniform bool clipCylinderOutside;

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
	//if( abs(uvw.x) > 1 || abs(uvw.y) > 1 || abs(uvw.z) > 1 ) return vec4(0);
	if( uvw.x > 1 || uvw.y > 1 || uvw.z > 1 || uvw.x < 0  || uvw.y < 0 || uvw.z < 0 ) return vec4(0);

	vec3 data;// = texture(vt.texture, uvw).xyz;

	if(vt.factor > -0.000001){
		data = texture(vt.textureOld, uvw).xyz *(1 - vt.factor) + texture(vt.texture, uvw).xyz * vt.factor;
	}
	else
		data = texture(vt.texture, uvw).xyz;

	//float data_val = length(data);
	float data_val = vt.dimension > 1? length(data) : data.x;

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



const float environment_rotation = 0.0;
const float environment_exposure = 2.0;
const float EPSILON_COEF = 1e-4;




struct LightProbe
{
	vec3 position;
	vec3 factors[9];
};

uniform LightProbe	gLightProbes[32];
uniform int			gLightProbeCount;
uniform float		gLightProbeGIFactor;


struct LPTetrahedral
{
	int ptIndex[4];
	mat3 matrix;
};

uniform LPTetrahedral gTetrahedrals[64];
uniform int gTetrahedralCount;


vec3 GetTetrahedralPoint(int i, int k)
{
	int ptIndex = gTetrahedrals[i].ptIndex[k];
	return gLightProbes[ptIndex].position;
	
/*	if(ptIndex < gLightProbeCount) return gLightProbes[ptIndex].position;
	
	ptIndex = gTetrahedrals[i].ptIndex[(k+1)%4];
	if(ptIndex < gLightProbeCount) return gLightProbes[ptIndex].position;
	
	ptIndex = gTetrahedrals[i].ptIndex[(k+2)%4];
	if(ptIndex < gLightProbeCount) return gLightProbes[ptIndex].position;
	
	ptIndex = gTetrahedrals[i].ptIndex[(k+3)%4];
	if(ptIndex < gLightProbeCount) return gLightProbes[ptIndex].position;
	
	return vec3(0.0);*/
}


vec3 GetTetrahedralCenter(int i)
{
	vec3 center = vec3(0.0);
	for(int k=0; k<4; k++){
		center += GetTetrahedralPoint(i, k);
	}
	
	center /= 4.0;
	
	return center;
}


vec4 CalcTetrahedralCoord(vec3 P, int i)
{
	vec4 coord;	
	coord.xyz = gTetrahedrals[i].matrix * (P - GetTetrahedralPoint(i, 3));
	coord.w = 1 - coord.x - coord.y - coord.z;
	
	return coord;
}


void CalcSHFactors(vec3 P, out vec3 SHFactors[9])
{

	if(gTetrahedralCount < 4){
		for(int m=0; m<9; m++) SHFactors[m] = gLightProbes[0].factors[m];
		return;
	}
	
	for(int m=0; m<9; m++) SHFactors[m] = vec3(0.0);
	
	///根据重心坐标查找四面体
	int min_index = -1;
	vec4 coord = vec4(0);
	for(int i=0; i<gTetrahedralCount; i++){
		coord = CalcTetrahedralCoord(P, i);
		
		if( coord.x < 0 || coord.x > 1 || coord.y < 0 || coord.y > 1 
		 || coord.z < 0 || coord.z > 1 || coord.w < 0 || coord.w > 1)
			continue;
			
		min_index = i;
		break;
	}
	
	
	if(min_index == -1){
		///根据重心距离找到最近的四面体
		float min_dis = distance(P, GetTetrahedralCenter(0));
		min_index = 0;
		
		for(int i=0; i<gTetrahedralCount; i++){
		
			vec3 center = GetTetrahedralCenter(i);
		
			float dis = distance(P, center);
			if(dis < min_dis){
				min_dis = dis;
				min_index = i;
			}
		}
		
		coord = CalcTetrahedralCoord(P, min_index);
	}
	
	for(int k=0; k<4; k++){
			
		vec3 factors[9];
		int ptIndex = gTetrahedrals[min_index].ptIndex[k];
		if(ptIndex >= gLightProbeCount){
			int try_index = gTetrahedrals[min_index].ptIndex[(k+1)%4];
			if(try_index >= gLightProbeCount){
				try_index = gTetrahedrals[min_index].ptIndex[(k+2)%4];
				if(try_index >= gLightProbeCount){
					try_index = gTetrahedrals[min_index].ptIndex[(k+3)%4];
				}
			}			
			for(int m=0; m<9; m++){
				factors[m] = gLightProbes[try_index].factors[m];
			}
		}
		else{
			for(int m=0; m<9; m++){
				factors[m] = gLightProbes[ptIndex].factors[m];
			}
		}
		
		for(int m=0; m<9; m++){
			SHFactors[m] += factors[m] * coord[k];
		}
	}

}



float P(int l, int m, float x)
{	
	// evaluate an Associated Legendre Polynomial P(l,m,x) at x	
	float pmm = 1.0;	
	if (m>0) {		
		float somx2 = sqrt((1.0 - x)*(1.0 + x));		
		float fact = 1.0;		
		for (int i = 1; i <= m; i++) {			
			pmm *= (-fact) * somx2;			
			fact += 2.0;		
		}	
	}	
	
	if (l == m) return pmm;	

	float pmmp1 = x * (2.0*m + 1.0) * pmm;	
	if (l == m + 1) return pmmp1;	

	float pll = 0.0;	
	for (int ll = m + 2; ll <= l; ++ll) {
		pll = ((2.0*ll - 1.0)*x*pmmp1 - (ll + m - 1.0)*pmm) / (ll - m);
		pmm = pmmp1;		
		pmmp1 = pll;	
	}	
	
	return pll;
}


int factorial(int n)
{
	int res = 1;
	for(int i=2; i<=n; i++) res *= i;

	return res;
}


float K(int l, int m)
{

	float temp = ((2.0*l + 1.0)*factorial(l - m)) / (4.0*M_PI*factorial(l + m));

	return sqrt(temp);

}

float SH(int l, int m, float theta, float phi)
{

	const float sqrt2 = sqrt(2.0);

	if (m == 0) return K(l, 0)*P(l, m, cos(theta));

	else if (m>0) return sqrt2*K(l, m)*cos(m*phi)*P(l, m, cos(theta));

	else return sqrt2*K(l, -m)*sin(-m*phi)*P(l, -m, cos(theta));

}

float SH(int SHIndex, float theta, float phi)
{

	if( SHIndex == 0 ) return SH(0, 0, theta, phi);

	else if( SHIndex == 1 ) return SH(1, -1, theta, phi);
	else if( SHIndex == 2 ) return SH(1, 0, theta, phi);
	else if( SHIndex == 3 ) return SH(1, 1, theta, phi);

	else if( SHIndex == 4 ) return SH(2, -2, theta, phi);
	else if( SHIndex == 5 ) return SH(2, -1, theta, phi);
	else if( SHIndex == 6 ) return SH(2, 0, theta, phi);
	else if( SHIndex == 7 ) return SH(2, 1, theta, phi);
	else if( SHIndex == 8 ) return SH(2, 2, theta, phi);

	return 0.f;

}


vec3 CalcProbeDiffuse(vec3 P, vec3 N)
{
	vec3 SHFactors0[9], SHFactors[9];
	CalcSHFactors(P, SHFactors);
	
	///可用，暂时屏蔽
	//RotateSH(gSceneRotation, 3, SHFactors0, SHFactors);

    float theta = acos(clamp(N.y, -1.0, 1.0));
    float phi = 0;
    float l = sqrt(N.x*N.x + N.z*N.z);
    if(l > 1e-6){
		phi = acos( clamp(N.x / l, -1.0, 1.0) );  ///注意三角函数要clamp
		if(N.z < 0) phi = 2*M_PI-phi;
	}
	
    
    float C[9];
    vec3 color = vec3(0.0);
    
    for(int k=0; k<9; k++){
		C[k] = SH(k, theta, phi);
		color += SHFactors[k]*C[k];
    }
    
    
    return color;
}



vec3 expand(vec3 v) {
  return (v - 0.5) * 2;
}


uniform int SSAOEnable;	
uniform sampler2D SSAOMap;


//uniform int shadowMapEnable;	
uniform sampler2D shadowMap;
//varying vec4 lightSpacePos;
//uniform float shadowColor;




/* CODE-BEGIN add by yub */
vec3 envIrradiance(vec3 dir)
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
}


vec3 computeWSNormal()
{
	vec3 N = vec3(0, 1, 0);
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
	  
	return N;
}

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


vec3 calc_fresnel_roughness(vec3 n, vec3 v, vec3 F0, float roughness) {

    float ndotv = max(dot(n, v), 0.0);

    return F0 + (max(vec3(1.0 - roughness), F0) - F0) * pow(1.0 - ndotv, 5.0);
}


float weight(float z, float a) 
{
	return clamp(pow(min(1.0, a * 10.0) + 0.01, 3.0) * 1e8 * pow(1.0 - z * 0.9, 3.0), 1e-2, 3e3);
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

	return texture(gTransmittanceImage, uv).r * ( 1 - pow(factor, 2));
}


vec3 CalcLightsContribute(vec3 worldP, vec3 worldN, vec3 worldNBent, vec3 V, vec3 albedo, vec3 specColor, vec3 F0, vec2 dfg, float shininess, vec3 ambient, float amb_factor, vec3 diffuse, vec3 specular, float occlusion, float shadow)
{
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
			//vec3 sunColor = mix(vec3(1.0, 0.7, 0.4), vec3(1.3, 1.1, 1.0), verticle_angle) * clamp(hdrExposure, 0, 2);
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



void main() 
{
	vec4 FragColor = vec4(0, 0, 0, 1);

	if(material.Ke.r > 0.1 || material.Ke.g > 0.1 || material.Ke.b > 0.1)
	{
		FragColor.rgb = material.Ke * materBrightness;
		FragColor.a = material.alpha;
		gl_FragData[0] = FragColor;

		///0.9以上
		if( FragColor.a < 0.9-1e-6 ){
			//获得要输出的颜色，把rgb乘上透明度，加到Color这张纹理上
			//gl_FragData[0] = vec4(FragColor.rgb * FragColor.a, FragColor.a);
			//在记录累加次数的纹理上加1
			//gl_FragData[1] = vec4(1.0);
		
			float w = weight(gl_FragCoord.z, FragColor.a);

			gl_FragData[0] = vec4(FragColor.rgb * FragColor.a * w, FragColor.a);  
			gl_FragData[1] = vec4(FragColor.a * w);
	    }

		return;
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
	

	vec3 Kd = material.Kd;
	vec3 Ks = material.Ks;
	vec3 Ka = material.Ka;
	float shininess = material.shininess;
	//vec3 P = vPosition;

	/* Thanks to http://www.thetenthplanet.de/archives/1180 */
	/* get edge vectors of the pixel triangle */
	vec3 dp1 = dFdx(worldP);
	vec3 dp2 = dFdy(worldP);
	vec2 duv1 = dFdx(oTexcoordNorm.xy);
	vec2 duv2 = dFdy(oTexcoordNorm.xy);

	/* solve the linear system */
	vec3 dp2perp = cross(dp2, worldN);
	vec3 dp1perp = cross(vNormal, dp1);
	vec3 tangent = dp2perp * duv1.x + dp1perp * duv2.x;
	vec3 binormal = dp2perp * duv1.y + dp1perp * duv2.y;

	/* construct a scale-invariant frame */
	float invmax = inversesqrt(max(dot(tangent, tangent), dot(binormal, binormal)));
	mat3 tsn = mat3(tangent * invmax, binormal * invmax, worldN);

	vec3 worldN2;
	if(bit_and(flag, 0x0001) == true){
		vec3 mapN = texture2D(normalMap, oTexcoordNorm.xy).xyz * 2.0 - 1.0;
		worldN2 = normalize(tsn * mapN); 
	}
	else{
		worldN2 = worldN;
	}

	vec3 V = normalize(gCameraPos - worldP);
	float ndv = dot(V, worldN2);
	if (ndv < 0) {
		V = reflect(V, worldN2);
		ndv = abs(ndv);
	}

	//取值范围[0, 2]，默认1
	//roughFactor = 1;  ///粗糙度
	//metaFactor = 1;   ///金属度
	//occluFactor = 1;  ///遮挡系数
	//envFactor = 1;    ///环境光强度
	//baseFactor = 1;   ///基础色强度


	float occlusion, roughness, metalic;
	if( bit_and(flag, 0x0040) == true){
		vec3 orm = texture2D(AOMap, oTexcoordSpec.xy).rgb;
		occlusion = clamp(1*(1-occluFactor) + orm.x * occluFactor, 0.0, 1.0);
		roughness = clamp(orm.y * roughFactor, 0.0, 10.0);
		metalic  = clamp(orm.z * metaFactor, 0.0, 10.0);
	}
	else{
		occlusion = clamp(occluFactor, 0.0, 1.0);
		roughness = clamp(roughFactor, 0.0, 1.0);
		metalic  = clamp(metaFactor, 0.0, 1.0);
	}

	if(SSAOEnable==1){
		occlusion *= texture2D(SSAOMap, gl_FragCoord.xy / screenSize).r;
	}

	vec3 worldN2_probe = normalize((gMatrixToProbe * vec4(worldN2, 0)).xyz);
	vec3 V_probe = normalize((gMatrixToProbe * vec4(V, 0)).xyz);

	vec3 baseColor = mapCount > 0 ? texture2D(diffuseMap, oTexcoord0.xy).rgb * Kd : Kd;
	vec3 albedo = baseColor;

	float amb_factor = max(material.Ka.r, max(material.Ka.g, material.Ka.b));
  
  ///2023-3-8, wxg
	vec3 specColor = Ks;
	//vec3 specColor = vec3(1.0);
  
  
    vec3 F0 = mix(vec3(0.04, 0.04, 0.04), albedo, metalic);
	vec3 F = calc_fresnel_roughness(worldN2_probe, V_probe, F0, roughness);

	// Diffuse part
	vec3 T = vec3(1.0, 1.0, 1.0) - F;
	vec3 kD = T * (1.0 - metalic);

	//vec3 irradiance = CalcProbeDiffuse(worldP, worldN2) * gLightProbeGIFactor;
	//vec3 diffuse = kD * albedo * irradiance;

	vec2 uv = gl_FragCoord.xy / screenSize;
	///有影子
	//vec3 irradiance = vec3(0);//texture2D(gIrradiance, uv).rgb * gLightProbeGIFactor;
	//vec3 diffuse = kD * albedo * gLightProbeGIFactor;// * irradiance;
	//vec3 diffuse = vec3(0);//kD * albedo;// * irradiance;
	vec3 diffuse = kD * albedo * gLightProbeGIFactor;



	// Specular part
	float ndotv = max(0.0, dot(worldN2_probe, V_probe));
	vec3 r = 2.0 * ndotv * worldN2_probe - V_probe;

	vec3 ld = textureLod(pbrSpecularMap, r, roughness*5).rgb * specColor;
	vec2 dfg = texture2D(pbrBRDFMap, vec2(ndotv, roughness)).xy;

	vec3 specular = ld * (F0 * dfg.x + dfg.y);// * gLightProbeGIFactor;// * 2.5; /// 2.5为修正系数
	//vec3 ambient = vec3(0);	
	//vec3 ambient = vec3(amb_factor * 0.1);
	vec3 ambient = vec3(amb_factor * 0.1)  * gLightProbeGIFactor;
	
	
	float shadow = 1.0;
	if (bit_and(flag, 0x0010) == true) {
	   vec4 lightPosition = lights[0].position;
	   float dotOfFace = 0;
	   if(lightPosition.w < 0.5){
			dotOfFace = dot(worldN2, lightPosition.xyz);
		}

		else{
			dotOfFace = dot(worldN2,  worldP - lightPosition.xyz);
		}

		if(dotOfFace < 0){
			shadow = texture2D(shadowMap, gl_FragCoord.xy / screenSize).r;
		}
	}
  
    
    FragColor.rgb = CalcLightsContribute(worldP, worldN2, worldN2, V, albedo, specColor, F0, dfg, shininess, ambient, amb_factor, diffuse, specular, occlusion, shadow);


	 //if (bit_and(flag, 0x40000) == true) {
	//	FragColor.rgb = FragColor.rgb*(1 - volumeTex.blend) + GetVolumeColor(worldP, volumeTex).rgb * volumeTex.blend;
	 //} 
	 if (bit_and(flag, 0x400000) == true) {
		vec4 volumeColor = GetVolumeColor(worldP_no_offset, volumeTex);
		FragColor.rgb = FragColor.rgb * (1 - volumeColor.a) + volumeColor.rgb * volumeColor.a;
	  } 
  
  
	if (bit_and(flag, 0x2000) == true) {
		vec3 PP = worldP + earthPos;
		vec3 viewDir = worldP - gCameraPos;
		vec3 v = normalize(viewDir);
		vec3 sunColor = vec3(step(cos(3.1415926 / 180.0), dot(v, worldSunDir))) * SUN_INTENSITY;

		vec3 extinction;
		vec3 inscatter = inScattering(gCameraPos + earthPos, PP, -worldSunDir, extinction);
		vec3 scatterColor = /*sunColor * extinction +*/ inscatter;
		// scatterColor = hdr(scatterColor, hdrExposure);
		scatterColor = hdr(scatterColor, 0.6);
		FragColor.rgb += scatterColor;
	}
  

	FragColor.a = material.alpha;

  
	///绘制倒影
	if (bit_and(flag, 0x80000) == true) {
		float mirrorDepth = 20.0;
		FragColor.a = min( dot(worldP - mirrorCenter, mirrorDirection) / mirrorDepth, 1.0);   ///记录倒影深度
	}

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

	
	gl_FragData[0] = clamp(FragColor, 0.0, 1.0); // 2025-3-20， wxg， 去掉白色噪点
	float transparency = FragColor.a;

	gl_FragData[0].a = material.alpha;

	//pbr不考虑透明融合
	///0.98以上
	if( FragColor.a < 0.98-1e-6 && bit_and(flag, 0x0020) == false ){
		//获得要输出的颜色，把rgb乘上透明度，加到Color这张纹理上
		//gl_FragData[0] = vec4(FragColor.rgb * FragColor.a, FragColor.a);
		//在记录累加次数的纹理上加1
		//gl_FragData[1] = vec4(1.0);

		float nv = abs(dot(V, worldN2));

		//float plus = (1 - nv) * ( 1 - FragColor.a) * 0.8;

		//if(plus > FragColor.a * 1.5) plus = FragColor.a * 1.5;

		//FragColor.a += plus; 

		FragColor.a += (1 - nv) * ( 1 - FragColor.a) * 0.8; 

		if(transparency < 0.25){
			FragColor.a = FragColor.a * (transparency * 4);
		}
		
		float w = weight(gl_FragCoord.z, FragColor.a);

		gl_FragData[0] = vec4(FragColor.rgb * FragColor.a * w, FragColor.a);  
		gl_FragData[1] = vec4(FragColor.a * w);
  	}
}