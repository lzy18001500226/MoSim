#version 330


layout (location = 0) out vec4 gFragColor; 



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
uniform vec4 gEnviromentParam;


// ----------------------------------------------------------------------------
// PHYSICAL MODEL PARAMETERS
// ----------------------------------------------------------------------------

const float SCALE = 1000.0;

//const vec3 earthPos = vec3(0.0, 6360.0 * SCALE, 0);
const vec3 earthPos = vec3(0.0, 6378137, 0);

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

const float M_PI = 3.141592657;

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
    return texture(transmittanceSampler, uv).rgb;
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
    return texture(sampler, uv).rgb;
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
    
    result *= clamp((d-10)/100.f, 0, 1)*2;  ///剔除近距离噪点误差

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
    return texture(skySampler, (u * (0.5 / 1.1) + 0.5));
}

vec3 hdr(vec3 L, float expo) {
    L = L * expo;
    L.r = L.r < 1.413 ? pow(L.r * 0.38317, 1.0 / 2.2) : 1.0 - exp(-L.r);
    L.g = L.g < 1.413 ? pow(L.g * 0.38317, 1.0 / 2.2) : 1.0 - exp(-L.g);
    L.b = L.b < 1.413 ? pow(L.b * 0.38317, 1.0 / 2.2) : 1.0 - exp(-L.b);
    return L;
}






uniform sampler2D gPositionDepth;

uniform sampler3D gNoise;
uniform sampler3D gNoiseDetail;

uniform sampler2D gNoiseCurl;

uniform sampler2D gWeather;   //r:覆盖率， g:降水概率（高频覆盖率）, b:类型
uniform int gRepeat;

uniform sampler2D gBackTexture;

uniform vec2 gNearFar;
uniform vec2 gJitter;

uniform float gAspect;
uniform float gNearHeight;

uniform vec3 gBoundMin;
uniform vec3 gBoundMax;

uniform vec3 gVertical;

uniform mat4 gModelView;
uniform mat4 gModelViewInv;
uniform mat4 gProjectionInv;

//uniform mat4 objectToWorld;

uniform vec3 gCameraPos;

uniform mat4 cameraConvertMatrix;
uniform mat4 cameraConvertMatrixInverse;

uniform mat4 matLocalToRelative;
uniform mat4 matRelativeToWorld;

uniform vec3 worldSunDir;

uniform float gDensity;
uniform float gRain;

uniform int flag;


in vec2 vUv;


bool bit_and(int val, int ref) {
  if(val == 0) return false;
  return (val/ref) % 2 != 0;
}

//局部坐标到地心
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

//局部坐标到地心
vec3 VectorLocalToEarth(vec3 lVec)
{
	return (cameraConvertMatrix * vec4(lVec, 0.0)).xyz;
}


//局部坐标到相对坐标
vec3 PointLocalToRelative(vec3 lPt)
{
	return (matLocalToRelative * vec4(lPt, 1.0)).xyz;
}

//局部坐标到相对坐标
vec3 VectorLocalToRelative(vec3 lVec)
{
	return (matLocalToRelative * vec4(lVec, 0.0)).xyz;
}

//相对坐标到地心
vec3 PointRelativeToEarth(vec3 lPt)
{
	//地心坐标系
	if (bit_and(flag, 0x800000) == true){ 
		return (matRelativeToWorld * vec4(lPt, 1.0)).xyz;
	}
	//地表坐标系
	else{  
		return (matRelativeToWorld * vec4(lPt, 1.0)).xyz + earthPos;
	}
}

vec3 VectorRelativeToEarth(vec3 lVec)
{
	return (matRelativeToWorld * vec4(lVec, 0.0)).xyz;
}


//裁剪空间转换为眼空间
/*vec3 uvToEye(vec2 texCoord,float depth)
{
	vec2 deltaUV = (2.0*texCoord-vec2(1.0))*vec2(gAspect,1.0);    
	
	//计算近平面的平移向量    
	vec2 deltaView = gNearHeight*deltaUV * depth / gNearFar.x;    
	return vec3(vec2(deltaView),-depth);
}  */

/*vec3 ScreenToCameraLinear(vec2 uv, float depth)
{
	vec4 viewPos = gProjectionInv * vec4( 2.0*uv - vec2(1.0), -1.0, 1.0 );
	return vec3(viewPos.xy/viewPos.w, -depth);
} */


vec3 ScreenToCamera(vec2 uv, float depth)
{
	vec4 viewPos = gProjectionInv * vec4( 2.0*uv - vec2(1.0), depth * 2.0 - 1.0, 1.0 );
	return viewPos.xyz/viewPos.w;
} 




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



const float EPS = 1e-6f;


vec3 SolvingQuadratics(float a, float b, float c)
{
	float delta = b * b - 4 * a * c;
	if (delta < 0)
	{
		return vec3(0, 0, 0);
	}

	if (abs(delta) < EPS)
	{
		return vec3(1, -b / (2 * a), -b / (2 * a));
	}
	else if (abs(a) < EPS)
	{
		return vec3(0, 0, 0);
	}
	else
	{
		if( a > 0)
			return vec3(2, (- b - sqrt(delta)) / (2 * a), (- b + sqrt(delta)) / (2 * a));
		else
			return vec3(2, (- b + sqrt(delta)) / (2 * a), (- b - sqrt(delta)) / (2 * a));
	}
}

vec3 LineIntersectSphere(vec3 O, vec3 E, vec3 Center, float R)
{
	vec3 D = E - O;			//线段方向向量

	float a = (D.x * D.x) + (D.y * D.y) + (D.z * D.z);
	float b = (2 * D.x * (O.x - Center.x) + 2 * D.y * (O.y - Center.y) + 2 * D.z* (O.z - Center.z));
	float c = ((O.x - Center.x)*(O.x - Center.x) + (O.y - Center.y) * (O.y - Center.y) + (O.z - Center.z) * (O.z - Center.z)) - R * R;

	return SolvingQuadratics(a, b, c);
}


float LineIntersectPlane(vec3 O, vec3 E, vec3 B, vec3 N)
{
	vec3 D = (E - O);			//线段方向向量
	return  -dot(O - B, N) / dot(D, N);
}


float GetArcLen(float d, float R)
{
	return 2*R*asin(d/2/R);
}


bool IntersectWithEarth(vec3 sp, vec3 sq,  vec3 amin, vec3 amax, out float tmin, out float tmax)
{	
	float h = amax.y-amin.y;
	
	float R = length(PointRelativeToEarth((amin+amax)/2)) - h/2;

	vec3 earth_sp = PointLocalToEarth(sp);
	vec3 earth_sq = PointLocalToEarth(sq);

	vec3 tS = LineIntersectSphere(earth_sp, earth_sq, vec3(0), R);
	vec3 tB = LineIntersectSphere(earth_sp, earth_sq, vec3(0), R+h);


	tmin = 0;
	tmax = 0;

	const float EPSON = 0.000001;

	if(tB.x < EPSON) return false;

	tmin = tB.y;
	if(tmin < EPSON && tS.x > EPSON){
		if(tS.y > EPSON) tmin = 0;
		else tmin = tS.z;
	}
	//if(tmin < EPSON && tS.x > EPSON) tmin = tS.z;
	if(tmin < EPSON) tmin = 0;

	tmax = tB.z;
	if(tmax < EPSON) tmax = 0;

	if(tS.x > EPSON && tS.y > EPSON && tS.y > tmin)
		tmax = tS.y;

	if(tmax - tmin < EPSON) return false;


	///计算直线与两个边界平面的交点
	/*vec3 Bmin = amin + earthPos;
	vec3 Bmax = amax + earthPos;


	vec3 D = normalize(sq - sp);	
	if( abs( dot(D, vec3(1, 0, 0))) > 0.3)
	{
		vec3 Nmin = normalize( vec3(Bmin.x, -Bmin.x*Bmin.x/Bmin.y, 0) );
		vec3 Nmax = normalize( vec3(Bmax.x, Bmax.x*Bmax.x/Bmax.y, 0) );

		float bmin = LineIntersectPlane(sp + earthPos, sq + earthPos, Bmin, Nmin);
		float bmax = LineIntersectPlane(sp + earthPos, sq + earthPos, Bmax, Nmax);

		if(bmin > bmax){
			float v = bmin;
			bmin = bmax;
			bmax = v;
		}

		
		if(tmin < bmin) tmin = bmin;
		if(tmax > bmax) tmax = bmax;

	}

	if( abs( dot(D, vec3(0, 0, 1))) > 0.3  )
	{
		vec3 Nmin = normalize( vec3(0, -Bmin.z*Bmin.z/Bmin.y, Bmin.z) );
		vec3 Nmax = normalize( vec3(0, Bmax.z*Bmax.z/Bmax.y, Bmax.z) );

		float bmin = LineIntersectPlane(sp + earthPos, sq + earthPos, Bmin, Nmin);
		float bmax = LineIntersectPlane(sp + earthPos, sq + earthPos, Bmax, Nmax);

		if(bmin > bmax){
			float v = bmin;
			bmin = bmax;
			bmax = v;
		}

		
		if(tmin < bmin) tmin = bmin;
		if(tmax > bmax) tmax = bmax;

	}*/

	/*if( abs( dot(D, vec3(0, 1, 0))) > 0.1  )
	{
		vec3 Nmin = normalize( vec3(-Bmin.y*Bmin.y/Bmin.x, Bmin.y, 0) );
		vec3 Nmax = normalize( vec3(Bmax.y*Bmax.y/Bmax.x, Bmin.y, 0) );

		float bmin = LineIntersectPlane(sp + earthPos, sq + earthPos, Bmin, Nmin);
		float bmax = LineIntersectPlane(sp + earthPos, sq + earthPos, Bmax, Nmax);

		if(bmin > bmax){
			float v = bmin;
			bmin = bmax;
			bmax = v;
		}

		
		if(tmin < bmin) tmin = bmin;
		if(tmax > bmax) tmax = bmax;

	}*/

	if(tmax - tmin < EPSON) return false;
		
	return true;
}



bool IntersectWithAABB(vec3 sp, vec3 sq,  vec3 amin, vec3 amax, out float tmin, out float tmax)
{	
	// 光线方向	
	float d[3];	
	d[0] = sq[0] - sp[0];	
	d[1] = sq[1] - sp[1];	
	d[2] = sq[2] - sp[2];	
	
	// 因为是线段 所以参数t取值在0和1之间	
	tmin = 0.0;	tmax = 1.0f;		
	for (int i = 0; i < 3; i++)	{		
	
		// 如果光线某一个轴分量为 0，且在包围盒这个轴分量之外，那么直接判定不相交 		
		if (abs(d[i]) < EPS)		
		{			
			if (sp[i] < amin[i] || sp[i] > amax[i])				
				return false;		
		}		
		else		
		{			
			float ood = 1.0f / d[i];			
			
			// 计算参数t 并令 t1为较小值 t2为较大值			
			float t1 = (amin[i] - sp[i]) * ood;			
			float t2 = (amax[i] - sp[i]) * ood;			
			if (t1 > t2) { float tmp = t1; t1 = t2; t2 = tmp; }						
			if (t1 > tmin) tmin = t1;			
			if (t2 < tmax) tmax = t2; 			
			
			// 判定不相交			
			if (tmin > tmax) 
				return false;		
		}	
	}		
		
	return true;
}






struct Ray
{
	vec3 origin;
	vec3 eye;
	vec3 direction;
};


Ray CreateCameraRay(vec2 uv)
{
	vec3 origin = (  gModelViewInv * vec4(0.0f, 0.0f, 0.0f, 1.0f)).xyz;    
	//vec3 direction = ScreenToCameraLinear(uv, gNearFar.x); 
	vec3 direction = ScreenToCamera(uv, 0.0);    
	direction = normalize(direction);  
	direction = (  gModelViewInv * vec4(direction, 0.0f)).xyz;    
	//direction = normalize(direction);  
	  
	Ray ray;    
	ray.origin = origin;   
	ray.eye = origin;
	ray.direction = direction;    
	return ray;
}


vec2 GetJitterUV(vec2 uv)
{
	return uv + gJitter / 2;
}


float R(float original_value, float original_min, float original_max, 
            float new_min, float new_max)
{
	//if(original_value <= original_min) return 0;
	
    return new_min + ((( original_value - original_min) / (original_max - original_min))
            * (new_max - new_min));
}


float SAT(float v)
{
	return clamp(v, 0.0, 1.0);
}


float Li(float v0,float v1,float ival){
    return (1.0-ival)*v0+ival*v1;
}


vec2 computeCurl2D(vec2 p, sampler2D noise)
{
  float eps = 0.0001;

  //Find rate of change in X direction
  float n1 = texture(noise, p + vec2(eps, 0)).r;
  //var n2 = noise.simplex2(x - eps, y); 
  float n2 = texture(noise, p + vec2(-eps, 0)).r;

  //Average to find approximate derivative
  float a = (n1 - n2)/(2 * eps);

  //Find rate of change in Y direction
  n1 = texture(noise, p + vec2(0, eps)).r;
  n2 = texture(noise, p + vec2(0, -eps)).r;

  //Average to find approximate derivative
  //var b = (n1 - n2)/(2 * eps);
  float b = (n1 - n2)/(2 * eps);

  //Curl
  return normalize( vec2(b, -a) );
}


vec3 computeCurl(vec3 p, sampler3D perlin)
{
    vec3 curl;
    float h = 0.0001f;
    float n, n1, a, b;
    

    n = texture(perlin, p).r;

   // n1 = N(x, y - h, z);
    n1 = texture(perlin, p-vec3(0, h, 0)).r;
    a = (n - n1) / h;

    //n1 = N(x, y, z - h);
    n1 = texture(perlin, p-vec3(0, 0, h)).r;
    b = (n - n1) / h;
    curl.x = a - b;

    //n1 = N(x, y, z - h);
    a = (n - n1) / h;

   // n1 = N(x - h, y, z);
    n1 = texture(perlin, p-vec3(h, 0, 0)).r;
    b = (n - n1) / h;
    curl.y = a - b;

    //n1 = N(x - h, y, z);
    a = (n - n1) / h;

    //n1 = N(x, y - h, z);
    n1 = texture(perlin, p-vec3(0, h, 0)).r;
    b = (n - n1) / h;
    curl.z = a - b;

    return curl;
}


/*
vec3 GetSphereSamplePos(vec3 P)
{
	vec3 earthP = PointLocalToEarth(P);
	float earthLocalH = length(PointLocalToEarth(vec3(0)));

	//float R = earthPos.y + gBoundMin.y;
	float R = earthLocalH + gBoundMin.y;

	vec3 D = P - gBoundMin;
	//D.y = length(P+earthPos) - length((gBoundMin+gBoundMax)/2 + earthPos) + (gBoundMin.y+gBoundMax.y)/2;
	D.y = length(earthP) - length(PointLocalToEarth((gBoundMin+gBoundMax)/2)) + (gBoundMin.y+gBoundMax.y)/2;

	vec3 p;
	p.x = GetArcLen(D.x, R) / (gBoundMax.x - gBoundMin.x);
	p.z = GetArcLen(D.z, R) / (gBoundMax.z - gBoundMin.z);
	p.y = D.y / (gBoundMax.y - gBoundMin.y);

	return p;;
}*/


vec3 GetSphereSamplePos(vec3 P)
{
	vec3 earthP = PointLocalToEarth(P);
	float earthRelativeH = length(PointRelativeToEarth(vec3(0)));

	float R = earthRelativeH + gBoundMin.y;

	vec3 D = PointLocalToRelative(P) - gBoundMin;
	D.y = length(earthP) - length(PointRelativeToEarth((gBoundMin+gBoundMax)/2)) + (gBoundMin.y+gBoundMax.y)/2;

	vec3 p;
	p.x = GetArcLen(D.x, R) / (gBoundMax.x - gBoundMin.x);
	p.z = GetArcLen(D.z, R) / (gBoundMax.z - gBoundMin.z);
	p.y = D.y / (gBoundMax.y - gBoundMin.y);

	return p;
}


vec4 GetWeatherData(vec3 P)
{
	vec3 p = GetSphereSamplePos(P);

	if(p.x < 0.0 || p.x > 1.0 || p.z < 0.0 || p.z > 1.0)
		return vec4(0.0);
	
	return texture(gWeather, p.xz * gRepeat);
}


float GetCloudHeightShape(float h, float type)
{
	if( type < 0.5 ){
		float b1 = SAT( R(h, 0.0,0.01, 0.0,1.0) );
		float t1 = SAT( R(h, 0.04,0.05, 1.0,0.0) );
		
		float b2 = SAT( R(h, 0.0,0.1, 0.0,1.0) );
		float t2 = SAT( R(h, 0.5,0.6, 1.0,0.0) );
		
		return SAT(b1*t1 * (0.5-type)*2 + b2*t2 * type*2);
	}
	else{
		float b2 = SAT( R(h, 0.0,0.1, 0.0,1.0) );
		float t2 = SAT( R(h, 0.5,0.6, 1.0,0.0) );
		
		float b3 = SAT( R(h, 0.0,0.05, 0.0,1.0) );
		float t3 = SAT( R(h, 0.7,1.0, 1.0,0.0) );
		
		type -= 0.5;
		return SAT(b2*t2 * (0.5-type)*2 + b3*t3 * type*2);
	}
}


vec2 GetDensity(vec3 P)
{

	vec4 weather_data = GetWeatherData(P);

	float cloudCover = weather_data.r * gDensity;
    float cloudRain = weather_data.g;
    float cloudHeight = weather_data.b;
    
    if( cloudCover < 0.1) return vec2(0, cloudRain);
    
    
    float maxH = (gBoundMax.y - gBoundMin.y) * cloudHeight;	
    
    ///当前点的归一化高度
	//float p_h = SAT((P.y - gBoundMin.y) / maxH );
	///以下是球面
	//float p_h = SAT((length(P+earthPos) - length((gBoundMin+gBoundMax)/2 + earthPos) + (gBoundMax.y - gBoundMin.y)/2) / maxH );
	float p_h = SAT((length(PointLocalToEarth(P)) - length(PointRelativeToEarth((gBoundMin+gBoundMax)/2)) + (gBoundMax.y - gBoundMin.y)/2) / maxH );

	//vec3 SP = GetSphereSamplePos(P);
	//float p_h = SP.y / cloudHeight;
	

	
	//float height_shape = GetCloudHeightShape(p_h, 0.8);
	
	
	///云的归一化高度由覆盖系数和高度系数共同决定
	//cloudHeight = cloudHeight * SAT(pow(cloudCover*5, 1.0/2));
	
	if( cloudHeight < 0.05) return vec2(0, cloudRain);
	
	//float height_ratio = ( p_h - cloudHeight*0.1*(1 - cloudCover) ) / ( cloudHeight*cloudCover );
	
	///当前点在云空间中的归一化高度
	//float height_ratio = p_h / cloudHeight;
	float height_ratio = p_h;
	
	///使云的底部和顶部形成线性渐变
	float bottom = SAT(R(height_ratio, 0.0, 0.2,  0.0, 1.0 ));
	float top = SAT(R(height_ratio, 0.6, 1.0,  1.0, 0.0 ));
	
	float height_shape = bottom * top;
	
	///使降水量下沉在底部
	float rain_top = SAT(R(height_ratio, 0.2, 1.0,  1.0, 0.0 ));
	cloudRain = SAT(cloudRain * rain_top );
	 
   
    ///计算噪声采样空间坐标，高度方向要进行缩放，因为噪声是立方体纹理
    //vec3 samplePos = (P - gBoundMin)/(gBoundMax - gBoundMin);

	///以下是球面
	vec3 samplePos = GetSphereSamplePos(P);
    float h_scale = (gBoundMax.y - gBoundMin.y) / (gBoundMax.x - gBoundMin.x);
    samplePos.y *= h_scale * 5;
      
    vec4 low_frequency_noises = texture(gNoise, samplePos );
    
    float low_freq_FBM = (low_frequency_noises.g * 0.625) + (low_frequency_noises.b * 0.25)
        + (low_frequency_noises.a * 0.125);
   
    float base_cloud = SAT(R(low_frequency_noises.r,  -(1.0 - low_freq_FBM), 1.0,   0.0, 1.0));      

    base_cloud = SAT(base_cloud * height_shape);
    
    //if( base_cloud < 0.001) return vec2(0, cloudRain);
    
    // Cloud coverage is stored in weather_data's red channel.
	float cloud_coverage = cloudCover; 
	 
	// Use remap to apply the cloud coverage attribute
	///2023/10/9
	//float base_cloud_with_coverage = base_cloud * cloud_coverage;
	float base_cloud_with_coverage = SAT(R(base_cloud, cloud_coverage, 1.0,  0.0, 1.0));
	 
	// Multiply the result by the cloud coverage attribute so that
	// smaller clouds are lighter and more aesthetically pleasing
	base_cloud_with_coverage *= cloud_coverage;
	
	//base_cloud_with_coverage = base_cloud * cloud_coverage;
	
    //if( base_cloud_with_coverage < 0.001) return vec2(0, cloudRain);
    
    //细节噪声
    
    //vec3 curl_noise = computeCurl(samplePos, gNoise);
    vec2 curl_noise = computeCurl2D(samplePos.xz, gNoiseCurl);
    //samplePos.xz += curl_noise.xy * ( SAT(1.0 - height_ratio) ) / 10; 
   samplePos.xz += curl_noise.xy * height_ratio * 1.0; 
    
    vec3 high_frequency_noises = texture(gNoiseDetail, samplePos * 4 ).rgb;
    
    float high_freq_FBM = (high_frequency_noises.r * 0.625) + (high_frequency_noises.g * 0.25) + (high_frequency_noises.b * 0.125);

  
    float high_freq_noise_modifier = mix(high_freq_FBM,  1.0 - high_freq_FBM, SAT(height_ratio*10));
    
	float final_cloud = SAT(R(base_cloud_with_coverage, high_freq_noise_modifier * 0.2, 1.0, 0.0, 1.0));

	return vec2(final_cloud, cloudRain * gRain);

}



float HenyeyGreenstein(float cos_angle, float inG)
{
    return ((1.0 - inG * inG) / pow((1.0 + inG * inG - 2.0 * inG * cos_angle), 3.0/2.0))
        / 4.0 * 3.1415;
}


vec3 frac(vec3 p){
    return vec3(p.x-floor(p.x),p.y-floor(p.y),p.z-floor(p.z));
}
 
float frac(float p){
    return p-floor(p);
}
 
float hash(vec3 p){
    p = frac(p * 0.3183099 + 0.1);
    p *= 17.0;
    return frac(p.x * p.y * p.z * (p.x + p.y + p.z));
}
 
float Noise(vec3 x){
    vec3 p = vec3(floor(x.x),floor(x.y),floor(x.z));
    vec3 f = frac(x);
    f = f * f * (3.0 - 2.0 * f);
 
    return Li(Li(Li(hash(p + vec3(0, 0, 0)),
                        hash(p + vec3(1, 0, 0)), f.x),
                   Li(hash(p + vec3(0, 1, 0)),
                        hash(p + vec3(1, 1, 0)), f.x), f.y),
               Li(Li(hash(p + vec3(0, 0, 1)),
                        hash(p + vec3(1, 0, 1)), f.x),
                   Li(hash(p + vec3(0, 1, 1)),
                        hash(p + vec3(1, 1, 1)), f.x), f.y), f.z);
}
 
float map2(vec3 p){
    vec3 q = p;
    float f = 0.0f;
    f = 0.65000 * Noise(q);
    q = q * 2.02;
    f += 0.35000 * Noise(q);
    return clamp(f, 0.0, 1.0);
}
 
float Jitter(vec3 p){
    return R(map2(p * 100), 0, 1, 0.5, 1);
}


vec3 CalcAtmosphereColor(vec3 eye, vec3 P, vec3 viewDir, vec3 sunDir)
{	
	//vec3 PP = P + earthPos;
	vec3 PP = PointLocalToEarth(P);

	vec3 extinction;
	vec3 inscatter = inScattering(PointLocalToEarth(eye), PP, -sunDir, extinction);

	//vec3 scatterColor = /*sunColor * extinction +*/ inscatter;
   // scatterColor = hdr(scatterColor, hdrExposure);

   float dotv = abs(dot(viewDir, normalize(PP)));
	vec3 scatterColor =  inscatter * pow((1 - dotv), 3);

   
	scatterColor = hdr(scatterColor, 0.6);
	
	//finalColor = finalColor * (1 - (gEnviromentParam.x-1)*0.05) + scatterColor;
	return scatterColor;
}


float LinearizeDepth(float depth, float ClipNear, float ClipFar)
{
    float z = depth * 2.0 - 1.0; // 回到NDC
    return (2.0 * ClipNear * ClipFar) / (ClipFar + ClipNear - z * (ClipFar - ClipNear));    
}


const int maxMarchingNum = 1000;

void main()
{
	const float EPS = 0.000001;

	vec2 jitterUv = GetJitterUV(vUv);

	gFragColor = texture(gBackTexture, vUv);

	Ray ray = CreateCameraRay(vUv);

	if(length(ray.direction) < EPS) return;

	float depthOfSence = texture(gPositionDepth, vUv).r;
	//float linearDepthOfScene = LinearizeDepth(depthOfSence, gNearFar.x, gNearFar.y);
	vec3 sight_point = ScreenToCamera(vUv, depthOfSence); 
	sight_point  = (  gModelViewInv * vec4(sight_point , 1.0f)).xyz;     
	float disOfSight = distance(sight_point, ray.eye); 
	
	float t1 = 0, t2 = 1;
	//float disOfSight = linearDepthOfScene;
	if(depthOfSence < EPS) disOfSight = gNearFar.y;

	bool bInter = IntersectWithEarth( ray.eye, ray.eye + ray.direction*disOfSight, gBoundMin, gBoundMax, t1, t2 );

	if(bInter == false){
		discard;	
		gFragColor = vec4(0, 1, 0, 1);
		return;
	}
	
	t1 *= disOfSight;
	t2 *= disOfSight;
	
	if( t1 > disOfSight * 1.5 && depthOfSence > EPS){
		discard;	

		//float h = gBoundMax.y-gBoundMin.y;
	
		//float R = length(PointRelativeToEarth((gBoundMin+gBoundMax)/2)) - h/2;

		//gFragColor = vec4(t1/disOfSight, disOfSight, 0, 5);
		return;
	}
	
	vec3 Len = gBoundMax - gBoundMin;
	
	ray.eye += ray.direction*t1;
	float maxDst = t2 - t1;
	
	float rayDst = 0;
	
	float D = max(Len.x, max(Len.y, Len.z));
	float marchStepSmall = D / maxMarchingNum; 
	float marchStepBig = marchStepSmall*4;
	
	float marchStep = marchStepSmall;
	
	vec4 colorSum = vec4(0);
	
	
	float verticle_angle = SAT(dot(worldSunDir, vec3(0, -1, 0))*2);
    	vec3 sunColor = mix(vec3(1.0, 0.7, 0.4), vec3(1.2, 1.18, 1.13), abs(verticle_angle)) * clamp(0.3 + verticle_angle, 0.0, 1.0);
    

	float l_of_Len = length(Len) * 5;
	
	float near_dis = -1;
	float prev_density = EPS+1;

	vec3 firstCloudPoint = vec3(0);

	int inum = 0;

	while (rayDst < maxDst) 
	{        

		if( rayDst > disOfSight && depthOfSence > EPS){
			break;
		}
		        
		vec2 density_rain = GetDensity(ray.eye);
		
		if(inum++ > maxMarchingNum) break;  ///2024-2-1, 确保退出, maxDst有可能是无效数字

		if(density_rain.x < EPS){
			ray.eye += ray.direction * marchStep; 
			rayDst += marchStep;  
			continue;
		}

		if(firstCloudPoint.x < EPS && firstCloudPoint.y < EPS && firstCloudPoint.z < EPS){
			firstCloudPoint = ray.eye;
		}

		prev_density = density_rain.x;

		if(near_dis < 0)
			near_dis = rayDst;
		
		
		///计算阳光反射的颜色
		const int sun_iter_num = 3;
		vec3 sun_pt = ray.eye - worldSunDir*marchStep*sun_iter_num;
		float density_samples_along_light_ray = 0.0;
		
		for(int k=0; k<sun_iter_num; k++)
		{
			sun_pt += worldSunDir*marchStep;
			density_samples_along_light_ray += GetDensity(sun_pt).x;

		}
		
		float depth = density_samples_along_light_ray/30;
		float powder_sugar_effect = 1.0 - exp(-depth * 5.0);
		float beers_law = exp(-depth );
		float light_energy = beers_law;
		
		float reflection = SAT(dot(worldSunDir, ray.direction)) * powder_sugar_effect * 0.5;
		light_energy = beers_law + reflection;
		light_energy *= ( 1.0 - density_rain.y);  ///被降雨系数吸收的光能
		
		float cos_angle = max(dot(worldSunDir, -ray.direction), 0);
		light_energy = mix(light_energy * 0.9, light_energy * HenyeyGreenstein(cos_angle, 0.15), cos_angle);
		
		///颜色与浓度不是一回事
		
		vec4 color = vec4(sunColor, 1.0) * light_energy;
		
		float dis = distance(ray.eye, ray.origin);
	
		color.a = 1.0;//min(l_of_Len / 2 / dis, 1.0);  
		
		density_rain.x = clamp(density_rain.x, 0.0, 1.0);


		////大气颜色
		//gAtmosphere = vec4(0.0, 0.0, 0.0, gEnviromentParam.x);
		vec4 atmo = vec4(0.0, 0.0, 0.0, gEnviromentParam.x);

		color *= density_rain.x;
		
        		colorSum = colorSum + color * (1.0 - colorSum.a) ;//* color.a * color.a * color.a;

		
        
        		if( colorSum.a > 1.0 - EPS ) break;
		
		ray.eye += ray.direction * marchStep;// * Jitter(ray.eye);       
		rayDst += marchStep;  
		
	}

	///为了性能而注释
		if(bit_and(flag, 0x2000) == true && length(firstCloudPoint) > EPS){
		
			vec3 atomsphereScatter = clamp( CalcAtmosphereColor(ray.origin, firstCloudPoint, ray.direction, worldSunDir), 0, 1);
			
	
			atomsphereScatter *= colorSum.a;

			float b = clamp( (atomsphereScatter.r + atomsphereScatter.g + atomsphereScatter.b) / 3 * 0.5 - 0.03, 0, 1);

			colorSum.rgb = mix(colorSum.rgb, atomsphereScatter, b);
		}

	
	//2025-3-28, wxg	
	gFragColor = clamp(colorSum + texture(gBackTexture, vUv), 0.0, 1.0);

	
	//雾颜色
	if(near_dis > 0){
		float fogBlend = CalcFogBlend(ray.origin + ray.direction*near_dis);
		if(fogBlend < 1 - 0.000001){
			//gFragColor.rgb = clamp(gFragColor.rgb*fogBlend + gFragColor.a * fogColor*(1-fogBlend), 0.0, 1.0);
			gFragColor.rgb = gFragColor.rgb*fogBlend + gFragColor.a * fogColor*(1-fogBlend);
		}
	}
		
}

	
	
		