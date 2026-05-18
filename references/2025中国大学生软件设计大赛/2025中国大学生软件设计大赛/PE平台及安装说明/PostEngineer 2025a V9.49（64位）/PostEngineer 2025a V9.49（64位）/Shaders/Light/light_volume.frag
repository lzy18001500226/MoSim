#version 330 core
//#extension GL_NV_shadow_samplers_cube : enable
#extension GL_NV_shader_buffer_load : enable


layout (location = 0) out vec4 gVolumeLightColor;


const float M_PI = 3.1415926535897932384626433832795;

vec3 hdr(vec3 L, float expo) {
    L = L * expo;
    L.r = L.r < 1.413 ? pow(L.r * 0.38317, 1.0 / 2.2) : 1.0 - exp(-L.r);
    L.g = L.g < 1.413 ? pow(L.g * 0.38317, 1.0 / 2.2) : 1.0 - exp(-L.g);
    L.b = L.b < 1.413 ? pow(L.b * 0.38317, 1.0 / 2.2) : 1.0 - exp(-L.b);
    return L;
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

uniform float shadow_min_value;
uniform float shadow_distance_scale[3];
uniform int shadow_c_count;

uniform int shadow_level_count;
uniform sampler2DArray VSMMaps;
uniform mat4 shadowWVP[3];
uniform vec3 lightPosForShadow[3];
uniform float shadowRange[3];
uniform vec3 lightShadowDirection;



uniform sampler2D gTransmittanceImage;


uniform sampler2D gPositionDepth;

uniform sampler2D gLightDepth;
uniform mat4 gLightMVP;


uniform sampler2D gNoise;
uniform sampler3D gNoise3D;


uniform mat4 gProjection;
uniform mat4 gModelView;

uniform mat4 gProjectionInv;
uniform mat4 gModelViewInv;

uniform vec2 jitter;

//uniform float sun_exposure;
uniform vec4 gEnviromentParam;

uniform Light lights[16];
uniform int lightCount;
uniform vec3 worldSunDir;

uniform float gParticleDensity;


uniform vec3 gCameraPos;

uniform int flag;

varying vec2 vUv;



uniform float gAttenuationDistance;

uniform float gAspect;
uniform vec2 gNearFar;
uniform float gNearHeight;


bool bit_and(int val, int ref) {
  if(val == 0) return false;

  return (val/ref) % 2 != 0;
}

vec3 expand(vec3 v) {
  return (v - 0.5) * 2;
}


//裁剪空间转换为眼空间
vec3 UVToEye(vec2 uv, float depth)
{    
	vec2 deltaUV = (2.0*uv-vec2(1.0))*vec2(gAspect,1.0);    
	//计算近平面的平移向量    
	vec2 deltaView = gNearHeight*deltaUV*depth/gNearFar.x;    
	
	return vec3(vec2(deltaView),-depth);
} 

struct Ray
{
	vec3 origin;
	vec3 eye;
	vec3 direction;
};

Ray CreateCameraRay(vec2 uv)
{    
	//vec3 origin = (gModelViewInv * vec4(0.0f, 0.0f, 0.0f, 1.0f)).xyz;    
	vec3 direction = UVToEye(uv, gNearFar.x);    
	direction = (gModelViewInv * vec4(direction, 0.0f)).xyz;    
	direction = normalize(direction);  
	  
	Ray ray;    
	ray.origin = gCameraPos;   
	ray.eye = gCameraPos;
	ray.direction = direction;    
	return ray;
}



int CalcShadowLevel(vec3 viewPos)
{
	int k;
	for(k=0; k<3; k++){
		if(-viewPos.z < shadowRange[k]) break;
	}
	
	return k;
}


float CalcShadow(vec3 P)
{
	if(shadow_level_count == 0)
		return 1.0;

	float shadow = 1;
	vec3 viewPos = (gModelView * vec4(P,1)).xyz;
	int shadow_level = CalcShadowLevel(viewPos);
	
/*	if(shadow_level == 0) gMainColor.rgb *= vec3(1, 0, 0);
	else if(shadow_level == 1) gMainColor.rgb *= vec3(0, 1, 0);
	else if(shadow_level == 2) gMainColor.rgb *= vec3(0, 0, 1);
*/

	
	if(shadow_level < 3){

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



int IsVectorsParallel(vec3 v1, vec3 v2)
{

	float dtv = dot(v1, v2);

	if(abs(dtv) > 1 - 1e-6) return 1;
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
			if(t1 < 0) I1 = P1 - t1*D;
			else I1 = P1;

			if(t2 < l) I2 = P2;
			else I2 = P2 - (t2-l)*D;
		}
		else{
			if(t2 < 0) I2 = P2 - t2*D;
			else I2 = P2;

			if(t1 < l) I1 = P1;
			else I1 = P1 - (t1 - l)*D;
		}
		
		return 1;
	}

	vec3 inter1, inter2, L;
	int ret = CalcCommanVerticalLineOfTwoLine(P1, lineDir, B, D, inter1, inter2, L);

	float d = distance(inter1, inter2);

	///distance(inter2, B) > l会造成两个孔
	if(d > r/* || distance(inter2, B) > l*/) return 0;

	float s = sqrt(r*r - d*d);

	float angle = acos(dot(lineDir, D));
	float g = s / sin(angle);

	I1 = inter1 - g*lineDir;
	I2 = inter1 + g*lineDir;

	return 1;
}


int LineIntersectWithSphere(vec3 P1, vec3 P2,  vec3 O, float r, out vec3 I1, out vec3 I2)
{
	vec3 V = normalize(P2 - P1);
	vec3 proj;
	CalcPointProjectionOnLine(O, P1, V, proj);
	float dis = distance(O, proj);
	if(dis > r) return 0;

	float len = sqrt( r*r - dis*dis );

	I1 = proj - V*len;
	I2 = proj + V*len;

	return 1;
}



float PointInCone(vec3 P, vec3 O, vec3 D, float cos_angle, float range) 
{
	float dtv = dot(P-O, D);
	if(dtv < 0 || dtv > range) return -1;

	float Pangle = dtv / length(P - O);
	if(Pangle < cos_angle ) return -1;

	return (Pangle - cos_angle) / (1 - cos_angle) * max((1 - pow(dtv / range * 1.25, 0.2)), 0);

}


int LineToConePoint(vec3 origin, vec3 normal, float height, float radius, vec3 p1, vec3 p2, out vec3 rp1, out vec3 rp2)
{
    //首先判断直线是不是和圆锥法线平行
    rp1 = vec3(0);
    rp2 = vec3(0);
    vec3 v = normalize(p2 - p1);
    if (abs(dot(normal, v)) > 1 - 0.0000001)
    {
        //平行，判断线段的距离
        float dis = PointToLineDistance(p1, origin, origin + normal);
        if (dis > radius)
        {
            //无交点
            return 0;
        }
        else
        {
            float h1 = height * dis / radius;
            vec3 e = origin + (height - h1) * normal;
            vec3 ds = normalize( cross(cross(p1 - origin, normal),normal) );
            rp1 = e + dis * ds;
            return 1;
        }
    }
 
    vec3 g = p1 - origin;
    float vn = dot(v, normal);
    float gn = dot(g, normal);
    float gg = dot(g, g);
    float vg = dot(v, g);
    float rr = radius * radius;
    float hh = height * height;
 
    float A = 1 - vn * vn - rr * vn * vn / hh;
    float B = 2 * vg - 2 * gn * vn + 2 * rr * vn / height - 2 * rr * gn * vn / hh;
    float C = gg - gn * gn - rr + 2 * rr * gn/height - rr * gn * gn / hh;
 
    float fourac = B * B - 4 * A * C;
    if (fourac < 0)
    {
        //无交点
        return 0;
    }
 
    float k1 = abs(-B + (float)sqrt(fourac)) / (2 * A);
    float k2 = abs(-B - (float)sqrt(fourac)) / (2 * A);
 
    vec3 pa = p1 + k1 * v;
    vec3 pb = p1 + k2 * v;
    int t = 0;
    if (abs(PointToLineDistance(pa, origin, origin + normal)) > radius)
    {
        //在圆锥外排除
    }
    else
    {
        rp1 = pa;
        t++;
    }
            
    if (abs(PointToLineDistance(pb, origin, origin + normal)) > radius)
    {
        //在圆锥外排除
    }
    else
    {
        if (t == 0)
        {
            rp1 = pb;
        }
        else
        {
            rp2 = pb;
        }
 
        t++;
    }
 
    return t;
}





float random(vec4 seed)
{
	float dot_product = dot(seed, vec4(12.9898, 78.233, 45.164, 94.673));
	return fract( sin(dot_product) * 43758.5453 );
}

float GetFogNoise(vec3 P)
{
	float dis = 3000;
	vec3 gBoundMin = vec3( -dis, -dis, -dis );
	vec3 gBoundMax = vec3( dis, dis, dis );

	vec3 uvw = (P - gBoundMin) / (gBoundMax - gBoundMin);

	return texture(gNoise3D, uvw).r;
}


float CalcSeaTransmit(vec3 P, vec3 dir)
{
	float dis = 3;
	vec3 gBoundMin = vec3( -dis, -dis, -dis );
	vec3 gBoundMax = vec3( dis, dis, dis );

	vec3 uvw = (P - gBoundMin) / (gBoundMax - gBoundMin);

	return texture(gTransmittanceImage, uvw.xz).r;
}



float CalcSpotTransmittance(vec3 P, vec3 lightPos, vec3 lightDir, float transmit_near, float transmit_far, float transmit_width)
{
	vec3 dir = lightDir;
	vec3 u = vec3(1, 0, 0);
	vec3 v = vec3(0, 0, 1);

	vec3 D = P - lightPos;
	float h = dot(D, dir);
	vec3 Proj = D - h*dir;

	if(h < transmit_near) return 0;

	vec2 uv = vec2(dot(Proj, u), dot(Proj, v)) / transmit_width * transmit_near / h;

	float factor = h / transmit_far;
	if( factor > 1 ) return 0;

	return texture(gTransmittanceImage, uv).r * ( 1 - pow(factor, 2));
}

void main() 
{
	vec2 uv = vUv;

	Ray ray = CreateCameraRay(vUv);
	
	vec4 posDepth = texture(gPositionDepth, uv);

	float camera_dis = gNearFar.y - gNearFar.x;
	if(posDepth.w > 0.00001){
		camera_dis = posDepth.w;  //distance(gCameraPos, posDepth.xyz);
	}

	//vec3 V = normalize(gCameraPos - worldP);

	////////  计算体积光
	gVolumeLightColor = vec4(0);

	if (bit_and(flag, 0x0100) == true) {
	
		float len = camera_dis;// * (1 + texture(gNoise, uv*20).x);
		//float L = InScatter(gCameraPos, ray.direction, lightPos, lightDir, len, 0 ) * gParticleDensity;
		float factor = ( 2 + dot(worldSunDir, -ray.direction) );
		float L = gParticleDensity * pow(factor, 2) * 0.1;

		float coeff = abs(dot(worldSunDir, vec3(0, 1, 0)));
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
			const int step_count = 20;
			float line_shadow = 0;
			for(int k=0; k<step_count-1; k++){
				//vec3 P = worldP + camera_dis/step_count*(k+1)*V;
				vec3 P = ray.origin + camera_dis/step_count*(k+1) * ray.direction;
				///计算透射率
				//float transm = CalcSeaTransmit(P, worldSunDir);
				line_shadow += CalcShadow(P);// * transm;
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

				//float viewCoeff = max(dot(ray.direction, lightDirection), 0) * 0.5;

				vec3 transmit = lights[lightIndex].transmit;

				///使用最大圆柱范围，先计算到圆柱最近的交点
				float radius = range * tan(lights[lightIndex].angle);  
				vec3 I1, I2;
				float max_dis = distance(ray.origin, lightPosition) + range*10;
				max_dis = max_dis > camera_dis? camera_dis : max_dis;

				int num = LineIntersectWithCylinder(ray.origin, ray.origin + max_dis*ray.direction,  lightPosition, lightDirection, range, radius, I1, I2);
				
				///步进计算视线方向上的亮度
				if(num > 0)
				{

					///for test
				/*float dd1 = distance(I1, ray.origin);
				float dt1 = dot(I1 - (ray.origin), ray.direction);
				float dd2 = distance(I2, ray.origin);
				float dt2 = dot(I2 - (ray.origin), ray.direction);
				gVolumeLightColor = vec4(dd1, dt1, dd2, dt2);
				return;*/

					///从视线方向，I1比视点更近
					if(dot(I1 - (ray.origin), ray.direction) < 0) I1 = ray.origin;
					if(dot(I2 - (ray.origin), ray.direction) < 0) I2 = ray.origin;

					float dis1 = distance(I1, ray.origin);
					float dis2 = distance(I2, ray.origin);

					float dis = dis2 - dis1;

					if(camera_dis > 1e-6){
						if(dis1 > camera_dis) dis = 0;  ///超过可见范围
						else if(dis2 > camera_dis) dis = camera_dis - dis1;
					}


					if(dis > 1e-6){
						const int step_count = 1000;
						float samll_step = dis/step_count;
						float cur_step = samll_step;
						float cone_bright = 0;

						float cur_dis = 0;
						float old_b = -1;
						int count = 0;
						while(cur_dis < dis){
							vec3 P = I1 + cur_dis * ray.direction;

							float b = PointInCone(P, lightPosition, lightDirection, cos_angle, range);
							if(b < 0){
								if(old_b < 0){
									if(cur_step < samll_step * 16){
										cur_step *= 2;
									}
								}
								else break;

								old_b = b;
								cur_dis += cur_step;
								continue;
							}
							else if(b > 0){
								if( old_b < 0 && cur_step > samll_step * 1.5){  ///回溯去找第一个点
									cur_dis -= cur_step;
									cur_step /= 2;
									cur_dis += cur_step;
									continue;
								}
							}

							///P是否被遮挡
							vec4 lightSpacePos = gLightMVP * vec4(P, 1.0);
							lightSpacePos.xy /= lightSpacePos.w; // 透视划分
							lightSpacePos.xy = lightSpacePos.xy * 0.5 + vec2(0.5); // 变换到0.0 - 1.0的值域
	
							float Ldis = texture(gLightDepth, lightSpacePos.xy).x;
							if( Ldis < 0.00001 || distance(lightPosition, P) < Ldis + 0.00001 ){
								///计算透射率
								if(transmit.x > 0.000001){
									float transm = CalcSpotTransmittance(P, lightPosition, lightDirection, transmit.x, transmit.y, transmit.z); 
									if(b > 0)cone_bright += transm * b;
								}
								else{
									if(b > 0)cone_bright += b;
								}
							}


							count++;
							if(count > 1000) break;

							old_b = b;
							cur_dis += cur_step;
						}
	
												/*	for(int k=0; k<step_count-1; k++){
														vec3 P = I1 + dis/step_count*(k+1)*(ray.direction);
														float b = PointInCone(P, lightPosition, lightDirection, cos_angle, range);
	
														///计算透射率
														float transm = CalcSpotTransmittance(P, lightPosition, lightDirection, gTransmittanceParam.x, gTransmittanceParam.y, gTransmittanceParam.z);

														//cone_bright = cone_bright<b? b: cone_bright;
														cone_bright += transm * b;
													}
													spot_light_color += cone_bright /step_count  * lights[lightIndex].diffuse_color * gParticleDensity * 5;*/

						
						if(count > 0){
							float dotv = (dot(-lightDirection, ray.direction) + 1) + 0.1;
							spot_light_color += cone_bright /count  * lights[lightIndex].diffuse_color * gParticleDensity * 5 * dotv;
							max_brightness += cone_bright /count;
						}

					}
				}
			}  
		}

		if(spot_light_count > 0)gVolumeLightColor.rgb +=  spot_light_color / spot_light_count;
		float alpha = min(max_brightness, 1);
		//gVolumeLightColor.a = alpha > gVolumeLightColor.a ? alpha : gVolumeLightColor.a;
		gVolumeLightColor.a = max(alpha , gVolumeLightColor.a);

	}

	if(true){
		///计算点光源的体积光
		int point_light_count = 0;
		float max_brightness = 0;
		vec3 point_light_color = vec3(0);
		for (int lightIndex = 0; lightIndex < lightCount; lightIndex++) {
			  
			if (bit_and(flag, 0x0100) == true && lightIndex == 0) continue;
			  
			if(lights[lightIndex].type == 0 && lights[lightIndex].range > 0.000001 && lights[lightIndex].position[3] > 0.000001)
			{
				
				point_light_count++;

				vec3 lightPosition = lights[lightIndex].position.xyz;
				float radius = lights[lightIndex].range;

				vec3 I1, I2;
				float max_dis = distance(ray.origin, lightPosition) + radius;
				//max_dis = max_dis > camera_dis? camera_dis : max_dis;

				int num = LineIntersectWithSphere(ray.origin, ray.origin + max_dis*ray.direction,  lightPosition, radius, I1, I2);

				if(dot(I1 - (ray.origin), ray.direction) < 0) I1 = ray.origin;
				if(dot(I2 - (ray.origin), ray.direction) < 0) I2 = ray.origin;

				float dis1 = distance(I1, ray.origin);
				float dis2 = distance(I2, ray.origin);
				float dis = dis2 - dis1;

				if(camera_dis > 1e-6){
					if(dis1 > camera_dis) dis = 0;
					else if(dis2 > camera_dis) dis = camera_dis - dis1;
				}
				
				///计算视线方向上的亮度
				if(num > 0)
				{
					float width = PointToLineDistance(lightPosition, I1, ray.direction);

					point_light_color += (1 - width / radius)  * lights[lightIndex].diffuse_color * gParticleDensity * 2 * dis / radius / 2;
					float bri = dis / radius / 2 / 2;
					max_brightness = max_brightness < bri ?  bri : max_brightness;
				}
			}  
		}

		if(point_light_count > 0)gVolumeLightColor.rgb +=  point_light_color / point_light_count;
		float alpha = min(max_brightness, 1);
		//gVolumeLightColor.a = alpha > gVolumeLightColor.a ? alpha : gVolumeLightColor.a;
		gVolumeLightColor.a = max(alpha , gVolumeLightColor.a);

	}
}