
#extension GL_EXT_gpu_shader4 : enable

/**
 * Real-time Realistic Ocean Lighting using Seamless Transitions from Geometry to BRDF
 * Copyright (c) 2009 INRIA
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

uniform mat4 screenToCamera; // screen space to camera space
uniform mat4 cameraToWorld; // camera space to world space
uniform mat4 cameraToScreen; // screen space to camera space
uniform mat4 worldToCamera; // camera space to world space
//uniform mat4 worldToScreen; // world space to screen space
uniform vec3 worldCamera; // camera position in world space
uniform vec3 worldSunDir; // sun direction in world space
uniform mat4 horizonRotation;

uniform mat4 toSea;

uniform vec2 gridSize;
uniform float normals;
uniform float choppy;

uniform float waveAmp;

uniform sampler2DArray fftWavesSampler;
uniform vec4 GRID_SIZES;

uniform sampler3D slopeVarianceSampler;

uniform vec3 seaColor; // sea bottom color


uniform int bMirror;
uniform float mirrorRatio;
uniform sampler2D mirrorMap;
uniform vec3 mirrorCenter;
uniform vec3 mirrorDirection;
uniform float mirrorDepth;

uniform vec2 screenSize;

uniform vec3 fogColor;
uniform float fogDensity;
uniform float fogHeight;

uniform sampler2D frontTex;
uniform sampler2D backTex;
uniform vec3 cloudColor2;
uniform float cloudDensity;


uniform sampler2D clingColorMap;
uniform sampler2D clingAlphaMap;

uniform int materialID;


uniform sampler2DArray beachSampler;
uniform mat4 beachMVPs[8];
uniform int beachCount;
uniform sampler2D boamSampler;

struct TextureRect
{
	vec3 position;
	vec3 forward;
	vec2 size;
	sampler2DArray textures;
	float index;
	vec4 diffuse;
};

uniform TextureRect textureRects[16];
uniform int textureRectCount;


uniform vec4 clipPlanes[3];
uniform int clipPlaneCount;

uniform int flag;


varying vec2 u; // coordinates in world space used to compute P(u)
varying vec3 P; // wave point P(u) in world space

#ifdef _VERTEX_

vec2 oceanPos(vec4 vertex) {
    vec3 cameraDir = normalize((screenToCamera * vertex).xyz);
    vec3 worldDir = (cameraToWorld * vec4(cameraDir, 0.0)).xyz;
    float t = -worldCamera.z / worldDir.z;
    return worldCamera.xy + t * worldDir.xy;
}


void main() {
    gl_Position = gl_Vertex;

    u = oceanPos(gl_Vertex);
    vec2 ux = oceanPos(gl_Vertex + vec4(gridSize.x, 0.0, 0.0, 0.0));
    vec2 uy = oceanPos(gl_Vertex + vec4(0.0, gridSize.y, 0.0, 0.0));
    vec2 dux = abs(ux - u) * 2.0;
    vec2 duy = abs(uy - u) * 2.0;

    vec3 dP = vec3(0.0);
    dP.z += texture2DArrayGrad(fftWavesSampler, vec3(u / GRID_SIZES.x, 0.0), dux / GRID_SIZES.x, duy / GRID_SIZES.x).x;
    dP.z += texture2DArrayGrad(fftWavesSampler, vec3(u / GRID_SIZES.y, 0.0), dux / GRID_SIZES.y, duy / GRID_SIZES.y).y;
    dP.z += texture2DArrayGrad(fftWavesSampler, vec3(u / GRID_SIZES.z, 0.0), dux / GRID_SIZES.z, duy / GRID_SIZES.z).z;
    dP.z += texture2DArrayGrad(fftWavesSampler, vec3(u / GRID_SIZES.w, 0.0), dux / GRID_SIZES.w, duy / GRID_SIZES.w).w;

    if (choppy > 0.0) {
        dP.xy += texture2DArrayGrad(fftWavesSampler, vec3(u / GRID_SIZES.x, 3.0), dux / GRID_SIZES.x, duy / GRID_SIZES.x).xy;
        dP.xy += texture2DArrayGrad(fftWavesSampler, vec3(u / GRID_SIZES.y, 3.0), dux / GRID_SIZES.y, duy / GRID_SIZES.y).zw;
        dP.xy += texture2DArrayGrad(fftWavesSampler, vec3(u / GRID_SIZES.z, 4.0), dux / GRID_SIZES.z, duy / GRID_SIZES.z).xy;
        dP.xy += texture2DArrayGrad(fftWavesSampler, vec3(u / GRID_SIZES.w, 4.0), dux / GRID_SIZES.w, duy / GRID_SIZES.w).zw;
    }

    P = vec3(u + dP.xy, dP.z);

    gl_Position = cameraToScreen * horizonRotation * worldToCamera * vec4(P, 1.0);
}

#endif

#ifdef _FRAGMENT_

// ---------------------------------------------------------------------------
// REFLECTED SUN RADIANCE
// ---------------------------------------------------------------------------

// assumes x>0
float erfc(float x) {
	return 2.0 * exp(-x * x) / (2.319 * x + sqrt(4.0 + 1.52 * x * x));
}

float Lambda(float cosTheta, float sigmaSq) {
	float v = cosTheta / sqrt((1.0 - cosTheta * cosTheta) * (2.0 * sigmaSq));
    return max(0.0, (exp(-v * v) - v * sqrt(M_PI) * erfc(v)) / (2.0 * v * sqrt(M_PI)));
	//return (exp(-v * v)) / (2.0 * v * sqrt(M_PI)); // approximate, faster formula
}

// L, V, N, Tx, Ty in world space
float reflectedSunRadiance(vec3 L, vec3 V, vec3 N, vec3 Tx, vec3 Ty, vec2 sigmaSq) {
    vec3 H = normalize(L + V);
    float zetax = dot(H, Tx) / dot(H, N);
    float zetay = dot(H, Ty) / dot(H, N);

    float zL = dot(L, N); // cos of source zenith angle
    float zV = dot(V, N); // cos of receiver zenith angle
    float zH = dot(H, N); // cos of facet normal zenith angle
    float zH2 = zH * zH;

    float p = exp(-0.5 * (zetax * zetax / sigmaSq.x + zetay * zetay / sigmaSq.y)) / (2.0 * M_PI * sqrt(sigmaSq.x * sigmaSq.y));

    float tanV = atan(dot(V, Ty), dot(V, Tx));
    float cosV2 = 1.0 / (1.0 + tanV * tanV);
    float sigmaV2 = sigmaSq.x * cosV2 + sigmaSq.y * (1.0 - cosV2);

    float tanL = atan(dot(L, Ty), dot(L, Tx));
    float cosL2 = 1.0 / (1.0 + tanL * tanL);
    float sigmaL2 = sigmaSq.x * cosL2 + sigmaSq.y * (1.0 - cosL2);

    float fresnel = 0.02 + 0.98 * pow(1.0 - dot(V, H), 5.0);

    zL = max(zL, 0.01);
    zV = max(zV, 0.01);

    return fresnel * p / ((1.0 + Lambda(zL, sigmaL2) + Lambda(zV, sigmaV2)) * zV * zH2 * zH2 * 4.0);
}

// ---------------------------------------------------------------------------
// REFLECTED SKY RADIANCE
// ---------------------------------------------------------------------------

// manual anisotropic filter
vec4 myTexture2DGrad(sampler2D tex, vec2 u, vec2 s, vec2 t)
{
    const float TEX_SIZE = 512.0; // 'tex' size in pixels
    const int N = 1; // use (2*N+1)^2 samples
    vec4 r = vec4(0.0);
    float l = max(0.0, log2(max(length(s), length(t)) * TEX_SIZE) - 0.0);
    for (int i = -N; i <= N; ++i) {
        for (int j = -N; j <= N; ++j) {
            r += texture2DLod(tex, u + (s * float(i) + t * float(j)) / float(N), l);
        }
    }
    return r / pow(2.0 * float(N) + 1.0, 2.0);
}

// V, N, Tx, Ty in world space
vec2 U(vec2 zeta, vec3 V, vec3 N, vec3 Tx, vec3 Ty) {
    vec3 f = normalize(vec3(-zeta, 1.0)); // tangent space
    vec3 F = f.x * Tx + f.y * Ty + f.z * N; // world space
    vec3 R = 2.0 * dot(F, V) * F - V;
    return R.xy / (1.0 + R.z);
}

float meanFresnel(float cosThetaV, float sigmaV) {
	return pow(1.0 - cosThetaV, 5.0 * exp(-2.69 * sigmaV)) / (1.0 + 22.7 * pow(sigmaV, 1.5));
}

// V, N in world space
float meanFresnel(vec3 V, vec3 N, vec2 sigmaSq) {
    vec2 v = V.xy; // view direction in wind space
    vec2 t = v * v / (1.0 - V.z * V.z); // cos^2 and sin^2 of view direction
    float sigmaV2 = dot(t, sigmaSq); // slope variance in view direction
    return meanFresnel(dot(V, N), sqrt(sigmaV2));
}

// V, N, Tx, Ty in world space;
vec3 meanSkyRadiance(vec3 V, vec3 N, vec3 Tx, vec3 Ty, vec2 sigmaSq) {
    vec4 result = vec4(0.0);

    const float eps = 0.001;
    vec2 u0 = U(vec2(0.0), V, N, Tx, Ty);
    vec2 dux = 2.0 * (U(vec2(eps, 0.0), V, N, Tx, Ty) - u0) / eps * sqrt(sigmaSq.x);
    vec2 duy = 2.0 * (U(vec2(0.0, eps), V, N, Tx, Ty) - u0) / eps * sqrt(sigmaSq.y);

#ifdef HARDWARE_ANISTROPIC_FILTERING
    result = texture2DGrad(skySampler, u0 * (0.5 / 1.1) + 0.5, dux * (0.5 / 1.1), duy * (0.5 / 1.1));
#else
    result = myTexture2DGrad(skySampler, u0 * (0.5 / 1.1) + 0.5, dux * (0.5 / 1.1), duy * (0.5 / 1.1));
#endif
    //if texture2DLod and texture2DGrad are not defined, you can use this (no filtering):
    //result = texture2D(skySampler, u0 * (0.5 / 1.1) + 0.5);

    return result.rgb;
}


bool bit_and(int val, int ref) {
  if(val == 0) return false;

  return (val/ref) % 2 != 0;
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


// ----------------------------------------------------------------------------

void main() 
{
	if (bit_and(flag, 0x800000) == true) earthPos = vec3(0.0);

	if(bit_and(flag, 0x0200) == true ){
	
		for(int k=0; k<clipPlaneCount; k++){
			float d = dot(clipPlanes[k], P) + clipPlanes[k].w;
			if(d < 0){
				discard;
				return;
			}
		}
	}

	///采样沙滩高度
	///从上往下绘制沙滩，使用正则投影
	///把当前P变换到沙滩绘制视角，采样沙滩点，与海面高度对比差值
	///差值越小，颜色越绿，透明度越高，小于一定范围的加泡沫纹理
	float beachFactor = 1.0;
	int beachIndex = 0;
	if(bit_and(flag, 0x0400) == true && beachCount > 0){

		vec2 mapSize = textureSize(beachSampler, 0);

		for(int index=0; index<beachCount; index++){
			vec4 beachSpacePos = beachMVPs[index] * vec4(P, 1.0);
			beachSpacePos.xy = beachSpacePos.xy * 0.5 + vec2(0.5); // 变换到0.0 - 1.0的值域

			float h = 0;
			int c = 0;
			float maxHeight = 4.0;
			for(int i =-1; i<=1; i++)
			for(int j =-1; j<=1; j++)
			{
				vec4 bP = texture2DArray(beachSampler, vec3(beachSpacePos.xy + vec2(i/mapSize.x, j/mapSize.y), index));

				if(bP.w > 0.5){
					h += distance(P, (toSea * vec4(bP.xyz, 1.0)).xyz );
					c++;
				}
			}

			if(c > 0){
				h /= c;
				beachFactor = min(h / maxHeight, 1.0);
				beachIndex = index;
				break;
			}
		}
	}


    vec3 V = normalize(worldCamera - P);

    vec2 slopes = texture2DArray(fftWavesSampler, vec3(u / GRID_SIZES.x, 1.0)).xy;
    slopes += texture2DArray(fftWavesSampler, vec3(u / GRID_SIZES.y, 1.0)).zw;
    slopes += texture2DArray(fftWavesSampler, vec3(u / GRID_SIZES.z, 2.0)).xy;
    slopes += texture2DArray(fftWavesSampler, vec3(u / GRID_SIZES.w, 2.0)).zw;

    vec3 N = normalize(vec3(-slopes.x, -slopes.y, 1.0));
    if (dot(V, N) < 0.0) {
        N = reflect(N, V); // reflects backfacing normals
    }


    float Jxx = dFdx(u.x);
    float Jxy = dFdy(u.x);
    float Jyx = dFdx(u.y);
    float Jyy = dFdy(u.y);
    float A = Jxx * Jxx + Jyx * Jyx;
    float B = Jxx * Jxy + Jyx * Jyy;
    float C = Jxy * Jxy + Jyy * Jyy;
    const float SCALE = 10.0;
    float ua = pow(A / SCALE, 0.25);
    float ub = 0.5 + 0.5 * B / sqrt(A * C);
    float uc = pow(C / SCALE, 0.25);
    vec2 sigmaSq = texture3D(slopeVarianceSampler, vec3(ua, ub, uc)).xw;

    sigmaSq = max(sigmaSq, 2e-5);

    vec3 Ty = normalize(vec3(0.0, N.z, -N.y));
    vec3 Tx = cross(Ty, N);

#if defined(SEA_CONTRIB) || defined(SKY_CONTRIB)
    float fresnel = 0.02 + 0.98 * meanFresnel(V, N, sigmaSq);
#endif

    vec3 Lsun;
    vec3 Esky;
    vec3 extinction;
    sunRadianceAndSkyIrradiance(worldCamera + earthPos, worldSunDir, Lsun, Esky);

    gl_FragColor = vec4(0.0);

#ifdef SUN_CONTRIB
    gl_FragColor.rgb += reflectedSunRadiance(worldSunDir, V, N, Tx, Ty, sigmaSq) * Lsun * beachFactor;
#endif

#ifdef SKY_CONTRIB
    gl_FragColor.rgb += fresnel * meanSkyRadiance(V, N, Tx, Ty, sigmaSq) * beachFactor;
#endif

#ifdef SEA_CONTRIB
    vec3 Lsea = seaColor * Esky / M_PI;
    gl_FragColor.rgb += (1.0 - fresnel) * Lsea * beachFactor;
#endif

#if !defined(SEA_CONTRIB) && !defined(SKY_CONTRIB) && !defined(SUN_CONTRIB)
    gl_FragColor.rgb += 0.0001 * seaColor * (Lsun * max(dot(N, worldSunDir), 0.0) + Esky) / M_PI * beachFactor;
#endif

	gl_FragColor.rgb = hdr(gl_FragColor.rgb, 0.5);

	gl_FragColor.rgb = gl_FragColor.rgb * beachFactor + vec3(0.6, 1.0, 0.8) * ( 1.0 - max(beachFactor - 0.1, 0.0) );



	///添加倒影
	if (bMirror) {
		vec2 uv = vec2( 1 - gl_FragCoord.x / screenSize.x, gl_FragCoord.y / screenSize.y ) + vec2( -slopes.x, -slopes.y )*0.1;
		vec4 mirror = texture2D(mirrorMap, uv);
		vec3 viewDir = normalize(V);
		float dotv = min(max(dot(viewDir, vec3(0, 0, 1)), 0.0), 1.0);
		//dotv = pow(dotv, 2.0);

		
		//2021/11/19, wxg
		//float factor = mix(mirror.a, 1.0, dot);
		vec3 DP = P - mirrorCenter;
		//2024-4-7, wxg
		float screenMirrorDepth = mirror.a;  //min(dot(DP, mirrorDirection) / mirrorDepth, 1.0) + 0.1;
		float factor = mix(screenMirrorDepth, 1.0, dotv);

		//factor = mix(0.1, 1.0, factor);

		float b = clamp((1-dotv) * (1-factor) * 0.9, 0, 1) * 0.8;

		if(mirror.a < -1.5) b = 0.0;
		
		gl_FragColor.rgb = mix( clamp(mirror.rgb, 0, 1), gl_FragColor.rgb, clamp((1-b) * (1.0 + waveAmp/10), 0.0, 1.0) );

		//gl_FragColor.rgb += mirror.rgb * 0.5 * (1- factor);
   }


   
    
    float fogBlend = 1;	
    if(fogDensity > 0.0000001){
        float dis = distance(worldCamera, P);
      /*  if(P.z > fogHeight  && worldCamera.z < fogHeight){
           float f = (fogHeight - worldCamera.z) / (P.z - worldCamera.z);
           if( f < 0) f = 0;
           dis *= f;
        }*/
		fogBlend = exp(-fogDensity * dis );
    }
    
    gl_FragColor.rgb = gl_FragColor.rgb*fogBlend + fogColor*(1-fogBlend);
    
    //体积雾
    vec2 uv = vec2(  gl_FragCoord.x / screenSize.x, gl_FragCoord.y / screenSize.y );
	vec4 back = texture2D(backTex, uv);
 	vec4 front = texture2D(frontTex, uv);
	if( back.a > 0.5  ){
		float sceneDis = distance(worldCamera, P);
		if(sceneDis >  front.r){
			if(sceneDis < back.r ) back.r = sceneDis;
			float fogBlend = clamp((back.r-front.r) * back.g, 0, 1);
			fogBlend *= fogBlend;
			gl_FragColor.rgb = gl_FragColor.rgb*(1-fogBlend) + cloudColor2*fogBlend;
		}
	}

	
	vec3 up = vec3(0, 0, 1);
	for(int i=0; i<textureRectCount; i++){
		vec3 right = cross(textureRects[i].forward, up);
		float w = textureRects[i].size.x;
		float h = textureRects[i].size.y;

		vec3 DP = P - textureRects[i].position;
		float u = (dot(DP, textureRects[i].forward) + w/2) / w;
		float v = (dot(DP, right) + h/2) / h;

		if(u >=0 && u<=1 && v>=0 && v<=1){
			vec4 texColor = texture2DArray(textureRects[i].textures, vec3(1-u, v, textureRects[i].index));
			gl_FragColor.rgb += texColor.rgb * textureRects[i].diffuse.rgb * textureRects[i].diffuse.a;
		}
	}


	/*if(  -slopes.x > 0.1){
		float factor = clamp(( -slopes.x - 0.1) * 10, 0 , 1) ;
		//gl_FragColor.rgb += vec3(1, 1, 1) * factor;
		gl_FragColor.rgb = gl_FragColor.rgb*(1 - factor) +  vec3(1, 1, 1) * factor;
	} */

	//vec2 slopes2 = texture2DArray(fftWavesSampler, vec3(u / GRID_SIZES.y, 1.0)).xy;  //pf1/x,  pf2/y,   pf1/y, pf2/x
	//vec2 slopes3 = texture2DArray(fftWavesSampler, vec3(u.yx / GRID_SIZES.y, 2.0)).xy;


	/*const float eps = 0.01;
    vec2 u0 = U(u+vec2(0.0), V, N, Tx, Ty);
    vec2 dux = (U(u+vec2(eps, 0.0), V, N, Tx, Ty) - u0) / eps;
    vec2 duy = (U(u+vec2(0.0, eps), V, N, Tx, Ty) - u0) / eps;


	float detJ = dux.x * duy.y - dux.y * duy.x;

	if(  detJ < 0 ){
		gl_FragColor.rgb = vec3(1, 1, 1);
	}*/


	///海面到达一定高度后逐渐消隐
	gl_FragColor.a = 1.0 - clamp((worldCamera.z - 50000)/50000, 0.0, 1.0);

	gl_FragColor.a *= min(beachFactor + 0.1, 1.0);

/*	if(beachFactor < 0.2){

		if(beachFactor > 0.05){
			vec4 boam = vec4(1.0, 1.0, 1.0, 1.0);
			gl_FragColor = gl_FragColor * ((beachFactor - 0.05)*1.0/0.15) + boam * (1.0 - (beachFactor - 0.05)*1.0/0.15);
		}
		else{
			vec4 boam = vec4(1.0, 1.0, 1.0, max(texture(boamSampler, u/2.0).r * 2 - 1.0, 0.0));
			gl_FragColor = vec4(1.0, 1.0, 1.0, 1.0) * (beachFactor*20) + boam * (1.0 - beachFactor*20);
		}
	}*/

	/*if(beachFactor < 0.1){
		float boam_alpha = clamp(texture(boamSampler, u).r * 2.0 - 1.0, 0.0, 1.0);
		boam_alpha = boam_alpha * (beachFactor*10) + boam_alpha * (1.0 - beachFactor*10);
		vec4 boam = vec4(1.0, 1.0, 1.0, boam_alpha);
		gl_FragColor = gl_FragColor * (beachFactor*10) + boam * (1.0 - beachFactor*10);
	}*/


	if(beachFactor < 0.1){
		float boam_alpha = clamp(texture(boamSampler, u).r * 2.0 - 0.3, 0.0, 1.0);
		boam_alpha = boam_alpha * (beachFactor*10) + boam_alpha * (1.0 - beachFactor*10);
		vec4 boam = vec4(1.0, 1.0, 1.0, boam_alpha);
		gl_FragColor = gl_FragColor * (beachFactor*10) + boam * (1.0 - beachFactor*10);
	}

	if(materialID > 0){
		vec4 SumColor = texture2D(clingColorMap, gl_FragCoord.xy / screenSize);
		vec4 SumAlpha = texture2D(clingAlphaMap, gl_FragCoord.xy / screenSize);
		int clingID = int(SumAlpha.g / SumAlpha.r + 0.1); ///消除积累
		
		vec4 clingColor = vec4( SumColor.rgb / clamp(SumAlpha.b, 0.000001, 5000000.0), SumColor.a);
		clingColor.a = 1 - clingColor.a;

		if(clingID == materialID){
			gl_FragColor.rgb = gl_FragColor.rgb*(1 - clingColor.a) + clingColor.rgb * clingColor.a;
		}
	}

}

#endif
