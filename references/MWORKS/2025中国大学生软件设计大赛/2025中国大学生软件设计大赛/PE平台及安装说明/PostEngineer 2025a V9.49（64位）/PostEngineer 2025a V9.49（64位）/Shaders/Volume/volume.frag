#version 330 core

layout (location = 0) out vec4 gMainColor;
//layout (location = 1) out float gVolumeShadow;


uniform sampler2D gPositionDepth;
uniform sampler2D gForwardDepth;

uniform sampler2D gScene;

uniform sampler2D gNoise;
uniform sampler2D gBoxDepth;

uniform float gAttenuation;
uniform float gDirectionBrightness;
uniform float gMagnitudeBrightness;


uniform vec3 clipCylinderOri;
uniform vec3 clipCylinderDir;
uniform vec2 clipCylinderParam;
uniform bool  reversed;


uniform vec4 clipPlanes[3];
uniform int clipPlaneCount;

uniform int flag;

uniform vec3 gCameraPos;

uniform mat4 gModelView;
uniform mat4 gModelViewInv;
uniform mat4 gProjection;
uniform mat4 gModelToWorldInv;

uniform vec2 gNearFar;
uniform float gAspect;
uniform float gNearHeight;

uniform vec2 gJitter;

uniform float gRayDepth;

uniform vec3 lightDir;

//uniform float sun_exposure;
uniform vec4 gEnviromentParam;

uniform float calculusFactor;

varying vec2 vUv;

struct VolumeData
{
	vec3 boundMin;
	vec3 boundMax;
	vec3 step;
	int  dimension;
	float factor;
	
	sampler3D volumeTexture;
	sampler3D volumeTextureOld;
	sampler3D volumeTextureNormal;
};

uniform VolumeData gVolumeData;

struct ColorSetting
{
	float value;
	vec4 color;
};


uniform ColorSetting colorSettings[32];
uniform	int colorSettingCount;


bool bit_and(int val, int ref) 
{
  if(val == 0) return false;

  return (val/ref) % 2 != 0;
}


float LinearizeDepth(float depth)
{
    float z = depth * 2.0 - 1.0; // 回到NDC
    return (2.0 * gNearFar.x * gNearFar.y) / (gNearFar.y + gNearFar.x - z * (gNearFar.y - gNearFar.x));    
}



//裁剪空间转换为眼空间
vec3 UVToEyePos(vec2 uv, float linear_depth)
{    
	vec2 deltaUV = (2.0 * uv - vec2(1.0)) * vec2(gAspect, 1.0);    
	//计算近平面的平移向量    
	vec2 deltaView = gNearHeight * deltaUV * linear_depth/gNearFar.x;    
	
	return vec3(vec2(deltaView), -linear_depth);
} 

vec3 CalcWorldPosByDepth(vec2 uv, float linear_depth)
{
	vec3 posInEye = UVToEyePos(uv, linear_depth);

	vec4 worldPos = gModelViewInv * vec4(posInEye, 1);

	return worldPos.xyz / worldPos.w;
}




bool IntersectWithAABB(vec3 sp, vec3 sq,  vec3 amin, vec3 amax, out float tmin, out float tmax)
{	
	const float EPS = 1e-6f;		// 光线方向	
	float d[3];	
	d[0] = sq[0] - sp[0];	
	d[1] = sq[1] - sp[1];	
	d[2] = sq[2] - sp[2];	
	
	// 因为是线段 所以参数t取值在0和1之间	
	tmin = 0.0;	tmax = 1.0f;		
	for (int i = 0; i < 3; i++)	{		
	
		// 如果光线某一个轴分量为 0，且在包围盒这个轴分量之外，那么直接判定不相交 		
		if (abs(d[i]) <= EPS)		
		{			
			if (sp[i] <= amin[i] || sp[i] >= amax[i])				
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
			if (tmin >= tmax) 
				return false;		
		}	
	}		
		
	return true;
}

bool TestInVolume(VolumeData vd, vec3 cameraPos, vec3 P, out float t1, out float t2)
{
	bool bInter = IntersectWithAABB(cameraPos, P, vd.boundMin, vd.boundMax, t1, t2);
	
	if(bInter == false){
		return false;
	}
	
	return true;
}


bool CalcByClipPlanes(vec3 N, float d, vec3 S, vec3 E, float t01, float t02, out float t1, out float t2)
{
	vec3 D = E - S;
	///计算直线与平面的交点
	///P = S + t*D;
	/// N*P+d = 0;  N(S + t*D) + d = 0; N*S + t*N*D = -d;  t*N*D = -(N*S + d);  t = -(N*S + d) / (N*D);

	float t = -( dot(N, S) + d ) / dot(N, D);

	float dtv = dot(N, D);

	if(dtv > 0)
	{
		if(t02 < t) return false;

		t1 = t01;
		t2 = t02;

		if(t1 < t) t1 = t;
	}
	else{
		if(t01 > t) return false;

		t1 = t01;
		t2 = t02;

		if(t2 > t) t2 = t;
	}

	return true;
}



float PointToLineDistance(vec3 P, vec3 B, vec3 D)
{
	vec3 dir = normalize(P - B);
	float dtv = dot(dir, D);
	if( abs(dtv) > 1-0.000001 ){
		return 0.f;
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



vec4 GetVolumeData(VolumeData vd, vec3 P)
{
	vec3 texSize = textureSize(vd.volumeTexture, 0);
	vec3 uvw = ( (P - vd.boundMin) / vd.step ) / texSize;

	if( uvw.x > 1.0 || uvw.y > 1.0 || uvw.z > 1.0 || uvw.x < 0.0  || uvw.y < 0.0 || uvw.z < 0.0 ) return vec4(0.0);

	if( vd.factor > -0.00001 ){
		return texture(vd.volumeTextureOld, uvw) * (1 - vd.factor) + texture(vd.volumeTexture, uvw) * vd.factor;
	}
	else
		return texture(vd.volumeTexture, uvw);
}


vec3 GetVolumeNormal(VolumeData vd, vec3 P)
{
	vec3 texSize = textureSize(vd.volumeTextureNormal, 0);
	vec3 uvw = ( (P - vd.boundMin) / vd.step ) / texSize;

	if( uvw.x > 1.0 || uvw.y > 1.0 || uvw.z > 1.0 || uvw.x < 0.0  || uvw.y < 0.0 || uvw.z < 0.0 ) return vec3(0.0);

	return texture(vd.volumeTextureNormal, uvw).xyz;
}


vec4 GetVolumeColor(VolumeData vd, vec3 P)
{

	// if(colorSettingCount == 0) return vec4(0);
	 if(colorSettingCount == 0) return GetVolumeData(vd, P);

	vec3 texSize = textureSize(vd.volumeTexture, 0);
	vec3 uvw = ( (P - vd.boundMin) / vd.step ) / texSize;

	if( uvw.x > 1.0 || uvw.y > 1.0 || uvw.z > 1.0 || uvw.x < 0.0  || uvw.y < 0.0 || uvw.z < .00 ) return vec4(0.0);

	vec4 data;  

	if( vd.factor > -0.00001  ){
		data = texture(vd.volumeTextureOld, uvw) * (1 - vd.factor) + texture(vd.volumeTexture, uvw) * vd.factor;
	}
	else
		data = texture(vd.volumeTexture, uvw);

	/*data += texture(vd.volumeTexture, clamp(uvw + vec3(-1, 0, 0)/texSize, 0, 1));
	data += texture(vd.volumeTexture, clamp(uvw + vec3(1, 0, 0)/texSize, 0, 1));
	data += texture(vd.volumeTexture, clamp(uvw + vec3(0, -1, 0)/texSize, 0, 1));
	data += texture(vd.volumeTexture, clamp(uvw + vec3(0, 1, 0)/texSize, 0, 1));
	data += texture(vd.volumeTexture, clamp(uvw + vec3(0, 0, -1)/texSize, 0, 1));
	data += texture(vd.volumeTexture, clamp(uvw + vec3(0, 0, 1)/texSize, 0, 1));
	data /= 7;*/

	float data_val = vd.dimension > 1 ? length(data.xyz) : data.x;
	

	vec4 VColor;

	int i;
	for(i=0; i<colorSettingCount; i++){
		if( data_val < colorSettings[i].value) break;
	}

	if( i==0 ) 
		VColor = colorSettings[0].color;
	else if(i == colorSettingCount) 
		VColor = colorSettings[colorSettingCount-1].color;
	else{
		float factor = (data_val - colorSettings[i-1].value) / (colorSettings[i].value - colorSettings[i-1].value);

		VColor = colorSettings[i-1].color*(1-factor) + colorSettings[i].color*factor;
	}

	VColor.a *= vd.dimension > 1 ? data.a : data.y;

	return VColor;
}



vec3 GetVolumeUVW(VolumeData vd, vec3 P)
{
	return ( (P - vd.boundMin) / vd.step ) / textureSize(vd.volumeTexture, 0);
}



vec2 GetJitterUV(vec2 uv)
{
	return uv + gJitter / 2;
}

float SAT(float v)
{
	return clamp(v, 0.0, 1.0);
}


vec2 NormalizedDeviceCoordToScreenCoord(vec2 ndc, vec2 screenSize)
{
	vec2 screenCoord;

	screenCoord.x = screenSize.x * (0.5 * ndc.x + 0.5);

	screenCoord.y = screenSize.y * (-0.5 * ndc.y + 0.5);

	return screenCoord;

}


float distanceSquared(vec2 a, vec2 b)
{
	a -= b;
	return dot(a, a);

}




float attenuation(float t)
{
	//return clamp(t, 0.1, 1.0) * 2;
	return clamp(t, 0.0, 1.0) * 2;
}

vec3 GetColor16(float coeff)
{
	int index = int(16*coeff);
	if(index == 16) index--;
	
	if(index == 0) return vec3(0.0);
	else if(index==1) return vec3(128/255.0, 0, 0);
	else if(index==2) return vec3(0, 128/255.0, 0);
	else if(index==3) return vec3(128/255.0, 128/255.0, 0);
	else if(index==4) return vec3(0, 0, 128/255.0);
	else if(index==5) return vec3(128/255.0, 0, 128/255.0);
	else if(index==6) return vec3(0, 128/255.0, 128/255.0);
	else if(index==7) return vec3(128/255.0, 128/255.0, 128/255.0);
	else if(index==8) return vec3(192/255.0, 192/255.0, 192/255.0);
	else if(index==9) return vec3(1.0, 0, 0);
	else if(index==10) return vec3(0, 1.0, 0);
	else if(index==11) return vec3(1.0, 1.0, 0);
	else if(index==12) return vec3(0, 0, 1.0);
	else if(index==13) return vec3(1.0, 0, 1.0);
	else if(index==14) return vec3(0, 1.0, 1.0);
	else if(index>=15) return vec3(1.0, 1.0, 1.0); 
}

float HenyeyGreenstein(float cos_angle, float inG)
{
    return ((1.0 - inG * inG) / pow((1.0 + inG * inG - 2.0 * inG * cos_angle), 3.0/2.0))
        / 4.0 * 3.1415;
}


void main() 
{

	///变换到抖动的屏幕空间
	vec2 jitUv = vUv;//GetJitterUV(vUv); //2024-8-123, wxg, 导致边缘闪烁
	
	gMainColor = texture(gScene, vUv);
	//gMainColor.a = 0;  //for test
	
	vec4 boxP = texture(gBoxDepth, jitUv); 
	//if(boxP.w > gNearFar.y - (gNearFar.y-gNearFar.x)/1000)  //2024-8-18, wxg, removed, 导致边角裁剪掉；但必须保留，是为了提高性能，修改CPU端的非有效值大小
	//	return;
	if(boxP.w < 1e-6)  //2024-8-18, wxg, removed, 导致边角裁剪掉；但必须保留，是为了提高性能，修改CPU端的非有效值大小
		return;

	vec4 worldP;// = texture(gPositionDepth, jitUv); 
	float depth = texture(gForwardDepth, jitUv).r;
	worldP.w = LinearizeDepth( depth );
	worldP.xyz = CalcWorldPosByDepth(jitUv, worldP.w);

	float range = distance(gVolumeData.boundMin, gVolumeData.boundMax);

	//if(worldP.w > boxP.w || worldP.w < gNearFar.x) worldP = boxP;  //2024-8-18, wxg, removed, 导致边缘闪烁
	if(worldP.w > boxP.w){
		worldP = boxP;  
	}

	vec3 localP = (gModelToWorldInv * vec4(worldP.xyz, 1)).xyz;
	vec3 localCameraPos = (gModelToWorldInv * vec4(gCameraPos, 1)).xyz;
	vec3 lv = vec3(worldP.w, 0, 0);
	vec3 lv2 = (gModelToWorldInv * vec4(lv, 0)).xyz;
	float localLen = length(lv2);

	vec3 localLightDir = (gModelToWorldInv * vec4(lightDir, 0)).xyz;

	///点到相机的距离超过了包围盒到相机的最远距离
	float maxDis = distance( (gVolumeData.boundMin+gVolumeData.boundMax)/2, localCameraPos ) + range;		
	//if(worldP.w > maxDis) return;
	//if(localLen > maxDis) return;  //2024-8-18, wxg, removed，导致进入场内部消失
	
	///当前射线是否穿过包围盒
	float t1, t2;
	bool bInter = TestInVolume(gVolumeData, localCameraPos, localP, t1, t2);
	if(bInter == false){
		return;
	}

	{
		///计算剖切
		if(clipPlaneCount > 0){
			bInter = CalcByClipPlanes(clipPlanes[0].xyz, clipPlanes[0].w, localCameraPos, localP, t1, t2, t1, t2);
			if(bInter == reversed){
				return;
			}
		}
	}

	
	
	///计算射线方向及长度
	vec3 rayDir = localP - localCameraPos;	
	float rayLen = length(rayDir);
	rayDir = normalize(rayDir);


	float sceneDepth = worldP.w / rayLen;
		
	float step = min(gVolumeData.step.x, min(gVolumeData.step.y, gVolumeData.step.z));

	float t = t1, dt = step/rayLen/2 / clamp(gMagnitudeBrightness, 0.02, 2); ///dt归一化
	float calculus_factor = step/range * 10 * calculusFactor;

	const float EPSON = 0.0000001;
	if(t1 > t2 - dt/4) return;


	//2024-8-18, removed
	//int calculus_num = 100;
	//if(calculus_num < rayLen/step) calculus_num = int(rayLen/step);
	//float calculus_factor = 1.0/calculus_num * 15.0;
	//if( dt < (t2-t1)/calculus_num ) dt = (t2-t1)/calculus_num;
	//if( dt > (t2-t1)/4 ) dt = (t2-t1)/4;
	
	vec3 I = vec3(0.0);
	float Tr = 1.0;  ///吸收系数累积
	float first_depth = 0;

	float remainAlpha = 1.0;

	float maxLen = distance(gVolumeData.boundMin, gVolumeData.boundMax);

	vec3 firstPoint = vec3(0);

	bool bFirstPoint = false;
	//gVolumeHeight = 0;
	//gVolumeShadow = 1.0;

	float shadow = 1.0;
	vec3 normal_test = vec3(1,0,0);
	
	while(t < t2){

		//if( t > sceneDepth && worldP.w > gNearFar.x ) break;
	
		{
			vec3 P = localCameraPos + t*rayLen*rayDir;

			///圆柱体剖切
			float rad = clipCylinderParam.x;
			float len = clipCylinderParam.y;
			if(bit_and(flag, 0x0002) == true && IsPointInCylinder(P, clipCylinderOri, clipCylinderDir, rad, len) == reversed){
				t += dt;
				continue;
			}
			
			///为什么访问3D纹理时x和z位置互换了？由于3D纹理存储顺序的原因
			vec4 G0 = GetVolumeColor(gVolumeData, P);   ///发光源

			if(G0.a < EPSON){
				t += dt;
				continue;
			}

			vec3 normal = vec3(0);
			if(bit_and(flag, 0x0004) == true){
				normal = normalize(GetVolumeNormal(gVolumeData, P));
				if( dot(normal, rayDir) > 0 ) normal = -normal;
			}

			if(abs(firstPoint.x) < EPSON && abs(firstPoint.y) < EPSON && abs(firstPoint.z) < EPSON
			  /*&& (bit_and(flag, 0x0004) == false || length(normal) > 0.0001)*/ ){
				firstPoint = P;
				bFirstPoint = true;
			}
						
			vec3 clr;
			if(bit_and(flag, 0x0001)){   ///矢量场
				clr = GetColor16(G0.x);
				vec3 M0 = G0.yzw;
				
				if(length(M0) > 1e-6){
				
					float r = 0;
					
					//反向积分
					float h = 0;
					vec3 Pi = P;
					vec3 Mi = vec3(0);
					vec3 noise = vec3(0);
					
					float hi =  step;
					for(int i=0; i<10; i++){
			
						Pi = Pi - Mi*hi;
						vec4 Gi = GetVolumeColor(gVolumeData, Pi);
						float ri = Gi.x;
						
						r += ri * hi;
						noise += texture(gNoise, GetVolumeUVW(gVolumeData, Pi).xy*20 ).rgb * hi;
						h += hi;
						
						Mi = Gi.yzw;
						hi = step;
						
						if( length(Mi) < 1e-6 ) break;
					}
					
					r /= h;
					noise /= h;
					//clr = GetColor16(r)*gMagnitudeBrightness + clamp((noise*4-vec3(2.0))*0.5, 0, 1)*gDirectionBrightness;
					clr = GetColor16(r) + clamp((noise*4-vec3(2.0))*0.5, 0, 1)*gDirectionBrightness;
				}
			}
			else{
				//clr = G0.rgb * gMagnitudeBrightness;
				clr = G0.rgb;
			}


			if(bit_and(flag, 0x0004) == true && bFirstPoint == true){
				bFirstPoint = false;
				///计算阴影
				/*const int light_iter_num = 10;
				vec3 pt_along_light_ray;
				float transmit = 1.0;
		
				for(int k=0; k<light_iter_num; k++)
				{
					pt_along_light_ray = P - lightDir * step * (k+1);
					float alpha = clamp(GetVolumeColor(gVolumeData, pt_along_light_ray).a, 0, 1);
					transmit *= ( 1.0 - alpha );

					if(transmit < EPSON) break;
				}*/
		
				/*
							float depth = density_samples_along_light_ray/light_iter_num;

							float powder_sugar_effect = 1.0 - exp(-depth * 5.0);
							float beers_law = exp(-depth );
							float light_energy = beers_law;
		
							float reflection = SAT(dot(lightDir, rayDir)) * powder_sugar_effect * 0.5;
							light_energy = beers_law + reflection;
		
							float cos_angle = max(dot(lightDir, -rayDir), 0);
							light_energy = mix(light_energy * 0.9, light_energy * HenyeyGreenstein(cos_angle, 0.15), cos_angle);
				*/

				//transmit = 0.3 + transmit*0.7;
				//clr *= transmit * gEnviromentParam.y * 3.0;
				//gVolumeShadow = clamp(1.0 - transmit * gEnviromentParam.y * G0.a, 0.0, 3.0);

				shadow = max(dot(-localLightDir, normal), 0) * 0.7 + 0.3;
				normal_test = normal;
			}

			I += remainAlpha * clr * Tr * G0.a * calculus_factor;
			remainAlpha *= 1 - G0.a * Tr * calculus_factor;
			if(remainAlpha < EPSON) break;
		
			if(first_depth < EPSON && remainAlpha < 1.0 - EPSON){
				first_depth = t;
			}

			if(first_depth > EPSON && gAttenuation > EPSON){	
				Tr *= min(exp( -attenuation((t-first_depth)/(t2-first_depth)) * dt * gAttenuation * 20 ) * remainAlpha * 10, 1);
				if(Tr < 1e-6) break;
			}

		}
	
		t += dt;
	}


	I *= shadow * gEnviromentParam.y * 2.5;

	gMainColor.rgb = gMainColor.rgb * remainAlpha + I * (1 - remainAlpha);
	gMainColor.a = max(gMainColor.a, 1 - remainAlpha);

	//gMainColor.rgb = vec3(normal_test.xy, shadow); // for test
	//gMainColor.rgb = normal_test; // for test

	/*
				float marchStep = dt * 1;
				///计算阳光反射的颜色
				const int sun_iter_num = 100;
				vec3 sun_pt;
				float density_samples_along_light_ray = 0.0;
	
				for(int k=0; k<sun_iter_num; k++)
				{
					sun_pt = firstPoint - k * lightDir*marchStep;
					float alpha = GetVolumeColor(gVolumeData, sun_pt).a;
					if(alpha < EPSON) break;
					density_samples_along_light_ray += alpha;
				}
		
				float density_depth = density_samples_along_light_ray/sun_iter_num;

				//float powder_sugar_effect = 1.0 - exp(-density_depth * 50.0);
				//float beers_law = exp(-density_depth );
				//float light_energy = beers_law;
		
				//float reflection = SAT(dot(lightDir, rayDir)) * powder_sugar_effect * 0.5;
				//light_energy = beers_law + reflection;
				//light_energy *= ( 1.0 - density_rain.y);  ///被降雨系数吸收的光能
		
				//float cos_angle = max(dot(lightDir, -rayDir), 0);
				//light_energy = mix(light_energy * 0.9, light_energy * HenyeyGreenstein(cos_angle, 0.15), cos_angle);

				gMainColor.rgb *= (1.0 - density_depth);*/
	

}