#version 330
#extension GL_EXT_gpu_shader4 : enable


layout (points) in;
layout (points) out;
layout (max_vertices = 64) out;


const float PI = 3.1415926;


struct AgeParamSetting
{
	float age;
	vec3 minVal;
	vec3 maxVal;
};

class AgeParamSettings
{
	AgeParamSetting m_paramSettings[16];
	int m_count;
};

vec3 GetParamSettinsValue(AgeParamSettings settings, float age, float randVal)
{
	if(settings.m_count == 0) return vec3(0);
	
	int k;
	for(k=1; k<settings.m_count; k++){
		if(age < settings.m_paramSettings[k].age) break;
	}
	
	if(k == settings.m_count){
		return settings.m_paramSettings[k-1].minVal*randVal + settings.m_paramSettings[k-1].maxVal*(1 - randVal);
	}
	else{
		float scale = (age - settings.m_paramSettings[k-1].age) / (settings.m_paramSettings[k].age - settings.m_paramSettings[k-1].age);
		vec3 minV = settings.m_paramSettings[k-1].minVal + scale * (settings.m_paramSettings[k].minVal - settings.m_paramSettings[k-1].minVal);
		vec3 maxV = settings.m_paramSettings[k-1].maxVal + scale * (settings.m_paramSettings[k].maxVal - settings.m_paramSettings[k-1].maxVal);
		
		return minV*randVal + maxV*(1 - randVal);
	}
}


struct VectorRange
{
	vec3  normal;
	vec3  binormal;
	//float angle;
	//float minLength;
	//float maxLength;
	vec3 angleLength;
};


struct PositionRange
{
	vec3  center;
	//float a;
	//float b;
	//float c;
	vec3 abc;
};




vec3 erot(vec3 p, vec3 ax, float ro) {

	return mix(dot(ax, p)*ax, p, cos(ro)) + cross(ax, p)*sin(ro);

}

vec3 PointRotateAroudAxis(vec3 point, vec3 pos, vec3 axis, float angle)
{
	vec3 p = point - pos;
	return erot(p, axis, angle) + pos;
}


vec3 GetVector(VectorRange setting, float u, float v, float w)
{
	float angle = setting.angleLength.x;
	float minLength = setting.angleLength.y;
	float maxLength = setting.angleLength.z;

	vec3 tangent = normalize(cross(setting.normal, setting.binormal));
	float r = minLength*w + maxLength*(1 - w);
	
	///将俯仰角从(0, PI)变换到(0, angle)
	float pitch = v * angle;
	float head = u*PI*2;
	
	vec3 dir = setting.normal;
	dir = erot(dir, setting.binormal, pitch);
	dir = erot(dir, setting.normal, head);
	
	return r * dir;
}


vec3 GetPosition(PositionRange setting, float u, float v, float w)
{
	return setting.center + vec3( cos(2*PI*(u-0.5))*cos(PI*(v-0.5))*setting.abc.x, sin(PI*(v-0.5))*setting.abc.y, sin(2*PI*(u-0.5))*cos(PI*(v-0.5))*setting.abc.z ) * w;
}



struct ForceScrew
{
	vec3 position;
	vec3 direction;
	//float length;
	//float radialLength;
	//float minField;
	//float maxField;
	vec4 lengthField;
};


class ForceScrews
{
	int m_count;
	ForceScrew m_screws[64];
};

ForceScrew GetForceScrew(ForceScrews screws, vec3 pos)
{
	float min_dis = -1;
	int index = -1;
	
	ForceScrew result;
	result.position = vec3(0);
	result.direction = vec3(0);
	//result.length = 0;
	//result.radialLength = 0;
	//result.minField = 0;
	//result.maxField = 0;
	result.lengthField = vec4(0.0);
	
	for(int k=0; k<screws.m_count; k++){
		float dis = distance(pos, screws.m_screws[k].position);
		if(min_dis < 0 || min_dis > dis){
			min_dis = dis;
			index = k;
		}
	}
	
	if(index != -1) result = screws.m_screws[index];
	
	return result;
}




struct PlaneBoundary
{
	vec4 plane;
};



class PlaneBoundaries
{
	int m_count;
	PlaneBoundary m_boundaries[16];
};




in float type0[];
in vec3 position0[];
in vec3 velocity0[];
in float age0[];
in float randVal0[];
in float rotation0[];
in vec3 pipePosition0[];
in float monther_age0[];


out float type1;
out vec3 position1;
out vec3 velocity1;
out float age1;
out float randVal1;
out float rotation1;
out vec3 pipePosition1;
out float monther_age1;


//uniform float time;
//uniform float delta_time;
//uniform float life;
//uniform float life2;
uniform vec4 timeLifeSettings;

//uniform float launchInterval;
//uniform float launchInterval2;
//uniform float launchLife;
uniform vec3 launchLifeSettings;

uniform int   launchCount;
uniform int   allKilled;


uniform int motionType;

//uniform vec3 cameraDir;


uniform PositionRange iniPosSettings[8];
uniform int iniPosCount;

uniform VectorRange iniVeloSetting;

uniform AgeParamSettings rotationSettings;

uniform ForceScrews forceScrews;

uniform PlaneBoundaries boundaries;

uniform vec3 randForce;
uniform float mass;
uniform float resistFactor;
//uniform float gravityFactor;
uniform vec3 gravityAcc;

uniform sampler1D randSampler;

uniform sampler1D pipeForceSampler;
uniform sampler1D pipeSpaceSampler;
uniform sampler1D pipeInfoSampler;

uniform float totalDistance;


vec3 GetRandomDir(float texCoord)
{
	vec3 dir = texture(randSampler, texCoord).xyz;
	dir -= vec3(0.5, 0.5, 0.5);
	return normalize(dir);
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

vec3 CalcPointProjectionOnLine(vec3 point, vec3 line_pt, vec3 line_dir)
{
	vec3 proj_pt;
	float k=0;
	int i;
	for(i=0;i<3;i++)
	{
		k+=(point[i]-line_pt[i])*line_dir[i];
	}
	for(i=0;i<3;i++)
	{
		proj_pt[i]=line_pt[i]+k*line_dir[i];
	}
	
	return proj_pt;
}


vec4 TextureForce(float axisPos)
{
	return texture(pipeForceSampler, abs(axisPos) / totalDistance );
}

float TextureRadialForceLength(float axisPos)
{
	return texture(pipeInfoSampler, abs(axisPos) / totalDistance ).x;
}


vec4 TextureSpace(float axisPos)
{
	return texture(pipeSpaceSampler, abs(axisPos) / totalDistance );
}


vec3 PipeToCartes(vec3 pipeCoord, vec3 binormal, float delta_angle, vec3 nextSegmentPoint, float nextSegmentPos, vec3 nextSegmentDirection)
{	
	vec4 pipeForce = TextureForce(pipeCoord.x);
	vec4 pipeCircle = TextureSpace(pipeCoord.x);
	
	vec3 direction = normalize(pipeForce.xyz);
	
	vec3 basePoint;
	if( pipeCoord.x < 0 ){  ///如果处于负空间则进行平移计算

		basePoint = nextSegmentPoint - (nextSegmentPos - abs(pipeCoord.x)) * nextSegmentDirection;
	}
	else basePoint = pipeCircle.xyz;
	
	vec3 P = basePoint + binormal * pipeCoord.y;
	return PointRotateAroudAxis(P, basePoint, direction, delta_angle);
}


vec3 CartesToPipe(vec3 pos, vec3 segmentPoint, float segmentPos, vec3 segmentDirection)
{
	vec3 proj_pt = CalcPointProjectionOnLine(pos, segmentPoint, segmentDirection);
	float dis = dot(pos - segmentPoint, segmentDirection);
	float r = distance(pos, proj_pt);
	
	vec3 pipeCoord;
	pipeCoord.x = segmentPos + dis;
	if(dis < 0) pipeCoord.x = -pipeCoord.x;   ///处于管道段的负空间
	
	pipeCoord.y = r;
	pipeCoord.z = 0;
	
	return pipeCoord;
}


vec4 GetPipeCircle(float pipePos, vec3 nextDirection)
{
	vec4 pipeForce = TextureForce(pipePos);
	vec4 pipeCircle = TextureSpace(pipePos);
		
	vec3 basePoint;
	if( pipePos < 0 ){
		float segmentPos = pipeForce.w;
		vec3 segmentPoint = TextureSpace(segmentPos).xyz;
		
		basePoint = segmentPoint - (segmentPos - abs(pipePos)) * nextDirection;
	}
	else basePoint = pipeCircle.xyz;
	
	return vec4(basePoint, pipeCircle.w);
}



vec4 GetPipeForce(float pipePos)
{
	vec4 pipeForce = TextureForce(pipePos);
	
	if( pipePos < 0 ){
		float segmentPos = pipeForce.w;	
		pipeForce = TextureForce(segmentPos + 1e-6 );
	}
	
	return pipeForce;
}



vec3 CalcPipeDisplayment(vec3 pipePos0, vec3 velocity0, float delta_time)
{
	vec3 pipePos1;
	
	pipePos1.x = abs(pipePos0.x) + velocity0.x * delta_time;
	pipePos1.yz = pipePos0.yz + velocity0.yz * delta_time;
	
	if(pipePos0.x < 0){
		float segmentPos = GetPipeForce(abs(pipePos0.x)).w;
		if( pipePos1.x < segmentPos ) pipePos1.x = -pipePos1.x; ///仍处于管道的负空间
	}
	
	return pipePos1;
}


float randomFunc(vec3 seed, float i)
{
	float dot_product = dot(vec4(seed, i), vec4(12.9898, 78.233, 45.164, 94.673));
	return fract( sin(dot_product) * 43758.5453 );
}



void main() 
{
	float time = timeLifeSettings.x;
	float delta_time = timeLifeSettings.y;
	float life = timeLifeSettings.z;
	float life2 = timeLifeSettings.w;

	float launchInterval = launchLifeSettings.x;
	float launchInterval2 = launchLifeSettings.y;
	float launchLife = launchLifeSettings.z;


	if(allKilled == 1){

		int par_type = int(type0[0]/10000+0.001);
		if(par_type == 0) par_type = 1;
	
		if(par_type == 1)
		{
			type1 = 10000.0;
			position1 = position0[0];
			velocity1 = velocity0[0];
			age1 = age0[0] + delta_time;
			randVal1 = randVal0[0]; 
			pipePosition1 = vec3(0);

			EmitVertex();
		}

		EndPrimitive();
		return;
	}

	vec3 randDir = GetRandomDir(time);
	
	///par_type = 1 是母粒子，只要母粒子没有消亡就持续发送子粒子
	
	int par_type = int(type0[0]/10000+0.001);
	if(par_type == 0) par_type = 1;
	
    if(par_type == 1 && age0[0] < launchLife)
    {
		///发射粒子
		float launchTime = type0[0] - 10000.0;
		if( launchTime >= launchInterval ){
		
			type1 = 10000.0;
			position1 = position0[0];
			velocity1 = velocity0[0];
			age1 = age0[0] + delta_time;
			randVal1 = randVal0[0]; 
			pipePosition1 = vec3(0);

			EmitVertex();
		
			vec3 pipeForce = normalize(GetPipeForce(0).xyz);
			vec3 binormal = MakeOrtho(pipeForce);
			
			float step = 0.5/(launchCount*iniPosCount);
			for(int k=0; k<launchCount; k++){
				for(int m=0; m<iniPosCount; m++){
					vec3 randCoord = texture(randSampler,  fract(time) + (k*iniPosCount+m)*step).xyz;
					//float rd = randomFunc(vec3(m, delta_time, k), fract(time));
					//vec3 randCoord = texture(randSampler, rd + (k*iniPosCount+m)*step).xyz;

					type1 = 20000.0;
					position1 = GetPosition(iniPosSettings[m], randCoord.x, randCoord.y, randCoord.z);
					velocity1 = GetVector(iniVeloSetting, randCoord.x, randCoord.y, randCoord.z);
					age1 = 0.0;
					randVal1 = randCoord.x;
					rotation1 = randVal1 * PI;
				
					vec3 dir = position1 - iniPosSettings[m].center;
					pipePosition1.x = 0.0;
					pipePosition1.y = length(dir);
					if(pipePosition1.y < 1e-6){
						pipePosition1.y = 1e-6;
						dir = binormal;
					}
					float dotv = dot(normalize(dir), binormal);
					pipePosition1.z = acos(dotv);
					dotv = dot(cross(dir, binormal), pipeForce);
					if( dotv < 0 ) pipePosition1.z = PI*2 - pipePosition1.z;

					if(motionType == 1){ ///管道空间的速度定义不一样
						vec3 velo;
						velo.x = dot(velocity1, normalize(pipeForce));
						velo.y = dot(velocity1, binormal);
						velo.z = dot(velocity1, cross(normalize(pipeForce), binormal));

						velocity1 = velo;
					}
					
					EmitVertex();
				}
			}
			
			EndPrimitive();
		}
		else if(age0[0] >= 0){
			
			type1 = type0[0] + delta_time;
			position1 = position0[0];
			velocity1 = velocity0[0];
			age1 = age0[0] + delta_time;
			randVal1 = randVal0[0];
			pipePosition1 = pipePosition0[0];

			EmitVertex();
			EndPrimitive();
		}
    }
    else if(par_type == 2 && age0[0] < life || par_type == 3 && age0[0] < life2){
    
		if(motionType == 0)
		{
			ForceScrew fs = GetForceScrew(forceScrews, position0[0]);

			float fs_length = fs.lengthField.x;
			float radialLength = fs.lengthField.y;
			float minField = fs.lengthField.z;
			float maxField = fs.lengthField.w;
			
			vec3 normal = normalize(fs.direction);
			vec3 dir = position0[0] - fs.position;
			float dotv = dot(dir, normal);
			vec3 binormal = -normalize(dir - dotv*normal);
			vec3 tangent = normalize(cross(binormal, normal));
			
			
			float r = length(dir - dotv*normal);
			
			float random = texture(randSampler, r).x;
			float field = minField*random + maxField*(1 - random);
			
			vec3 tangentForce = r>0? tangent * field * radialLength : vec3(0);
			
			vec3 radialForce = r>0? binormal * radialLength : vec3(0);
			
			vec3 resistForce = -resistFactor * velocity0[0] * length(velocity0[0]);
			
			vec3 randF = randForce;
			if(length(randForce) > 0){
				dotv = dot(normalize(randForce), fs.direction);
				if(dotv < 0) dotv = 1.0;
				else if(dotv > 1.0) dotv = 1.0;
				
				randF *= (1 - dotv);
			}
			
			randF = r>0? randF*random: randF;
			
			vec3 acc;
			if( par_type == 3 ){  ///二发射的粒子密度较低，降低外力
				acc = ( fs.direction*fs_length*0.1 + resistForce + tangentForce*0.1 + radialForce*0.1 + randF ) / mass + gravityAcc * 0.1;
			}
			else{	
				acc = ( fs.direction*fs_length + resistForce + tangentForce + radialForce + randF ) / mass + gravityAcc;
			}
				
			type1 = type0[0] + delta_time;;
			age1 = age0[0] + delta_time;
			randVal1 = randVal0[0];
			monther_age1 = monther_age0[0];
			
			position1 = position0[0] + velocity0[0] * delta_time;	
			velocity1 = velocity0[0] + acc * delta_time;
			
			pipePosition1.y = r;
		}
		// 管道空间
		else if(motionType == 1){
		
			///计算位移
			vec3 pipePos0 = pipePosition0[0];
			vec3 pipePos1 = CalcPipeDisplayment(pipePos0, velocity0[0], delta_time);
			
			vec3 pos0 = position0[0];			
	
			vec4 pipeF = GetPipeForce( abs(pipePos0.x) );
			vec3 pipeForce0 = pipeF.xyz;
			float nextSegmentPos = pipeF.w;
			
			vec4 pipeCircle0 = GetPipeCircle( abs(pipePos0.x), vec3(0) );
			float maxRange = pipeCircle0.w;

			float radialLength = TextureRadialForceLength(abs(pipePos0.x));
			
			vec3 nextSegmentPoint = GetPipeCircle(nextSegmentPos, vec3(0)).xyz;		
			vec3 pipeForceNext = GetPipeForce(nextSegmentPos + maxRange).xyz;
				
			vec3 cur_direction = normalize(pipeForce0.xyz);
			vec3 next_direction = normalize(pipeForceNext.xyz);
			
			
			///计算半径方向
			vec3 binormal = pos0 - pipeCircle0.xyz;
			if(pipePos0.y < 0) binormal = -binormal;  ///去掉符号的影响
			
			
			///处理接缝处的突变，即只有超出接缝的截面才等效中线的端点
			///假设两段管道的夹角不小于90度，则接缝界面与端面的夹角不大于45度
			///当管道位移落入这个区间时就开始进行判断
			
			///根据当前点所处的位置计算力，以及管道位移，位移的计算仅依靠上一次的速度

			if( nextSegmentPos - abs(pipePos0.x) < maxRange || pipePos0.x < 0){
				
				vec3 normal = normalize((cur_direction + next_direction) / 2);
				float judge = dot( pos0 - nextSegmentPoint, normal );
				pipeForce0 = judge < 0? pipeForce0 : pipeForceNext;
				
				///如果当前粒子位于接缝平面之上，则交给下一段管道
				if(judge >= 0){
				
					///转换到下一段的管道空间后再重新计算位移
					
					pipePos0 = CartesToPipe(pos0, nextSegmentPoint, nextSegmentPos, next_direction);	
					pipeCircle0 = GetPipeCircle( pipePos0.x, next_direction );
					pipePos1 = CalcPipeDisplayment(pipePos0, velocity0[0], delta_time);
					
					///计算半径方向
					binormal = pos0 - pipeCircle0.xyz;
				}
				///仍由当前段负责计算
				else if(pipePos1.x > nextSegmentPos || pipePos0.x < 0){
				
					///首先按照前一段空间的惯性计算pos1，再计算投射到下一个段空间的偏移
					
					vec3 pos1 = pos0 + cur_direction*(abs(pipePos1.x) - abs(pipePos0.x));
					
					///在下一段管道空间中表示管道坐标
										
					pipePos1 = CartesToPipe(pos1, nextSegmentPoint, nextSegmentPos, next_direction);
					pipePos1.z = pipePos0.z;
					
					pipeCircle0 = GetPipeCircle( pipePos1.x, next_direction );	
					binormal = pos1 - pipeCircle0.xyz;
					
				}
			}
			
			
			
			///随机力导致径向的移动和绕轴旋转，因此分为为径向力和圆周力，分别计算随机值
			
			vec2 random = texture(randSampler, time + pipePos0.y*randVal0[0]).xy;
			vec2 randF = (random-0.5)*2*length(randForce);
			
			vec3 resistForce = -resistFactor * velocity0[0] * abs(velocity0[0]);

			//考虑径向力
			vec2 radialForce = (length(velocity0[0].yz) > 0.0000001? normalize(velocity0[0].yz): vec2(0.0)) * radialLength;
			
			///计算加速度
			vec3 acc;
			acc.x = (length(pipeForce0.xyz) + resistForce.x) / mass;
			acc.y = (randF.x + resistForce.y + radialForce.x) / mass;
			acc.z = (randF.y + resistForce.z + radialForce.y) / mass;
			
			///保持属性
			type1 = type0[0] + delta_time;;
			age1 = age0[0] + delta_time;
			randVal1 = randVal0[0];
			monther_age1 = monther_age0[0];
		
			
			///归一化半径方向
			float len = length(binormal);
			if(len > 0){
				binormal /= len;
			}
			else{
				binormal = MakeOrtho( normalize(pipeForce0.xyz) );
			}
			
			
			pipePosition1 = pipePos1;
			if( pipePosition1.x > totalDistance ) return;
			
			///计算速度
			velocity1 = velocity0[0] + acc * delta_time;
	
			vec4 pipeCircle1 = GetPipeCircle(pipePosition1.x, next_direction);
						
			//与管壁发生碰撞，有衰减
			if(pipePosition1.y > pipeCircle1.w){
				pipePosition1.y = pipeCircle1.w - (pipePosition1.y - pipeCircle1.w)*0.9;
				if(pipePosition1.y < -pipeCircle1.w) pipePosition1.y = -pipeCircle1.w * 0.95;
				velocity1.y = -velocity1.y * 0.9;
			}
			else if(-pipePosition1.y > pipeCircle1.w){
				pipePosition1.y = -(pipeCircle1.w - (-pipePosition1.y - pipeCircle1.w)*0.9);
				if(pipePosition1.y > pipeCircle1.w) pipePosition1.y = pipeCircle1.w * 0.95;
				velocity1.y = -velocity1.y * 0.9;
			}
			

			///20235/23，杀死离开管道的粒子
			if( -pipePosition1.y > pipeCircle1.w || pipePosition1.y > pipeCircle1.w ) return;
			
			///将粒子坐标从管道空间转换到世界空间
			float delta_angle = 0;
			if( abs(pipePos0.y) > 0 ) delta_angle = (pipePosition1.z - pipePos0.z) / abs(pipePos0.y);
							
			position1 = PipeToCartes( pipePosition1, binormal, delta_angle, nextSegmentPoint, nextSegmentPos, next_direction); 	
			
		}
		
		//自转
		float rotationVelo = GetParamSettinsValue(rotationSettings, age0[0], randVal1).x;
		rotation1 = rotation0[0] + rotationVelo * delta_time;
		
		
		
		int killed = 0;
		for(int k=0; k<boundaries.m_count; k++){
			float d = dot(position1, boundaries.m_boundaries[k].plane.xyz) + boundaries.m_boundaries[k].plane.w;
			if(d < 0){
				killed = 1;
				break;
			}
		}
		
		if(killed == 0){
		
			float launchTime = type0[0] - 20000.0;
			if(par_type == 2){
				if(launchTime >= launchInterval2 && life2 > 1e-6){
					type1 = 20000.0;
				}
			}
			EmitVertex();
			
			
			///二次发射粒子，产生轨迹
			
			if(par_type == 2 && launchTime >= launchInterval2 && life2 > 1e-6){
				type1 = 30000.0;
				age1 = 0.0;
				//randVal1 = randVal0[0];
				randVal1 = texture(randSampler, time + randVal0[0]).x;
				
				position1 = position0[0];	
				velocity1 = velocity0[0] * 0.05;  /// 二发射的粒子能量损失
	
				pipePosition1 = pipePosition0[0];

				monther_age1 = age0[0];
				
				EmitVertex();
			}
			
			
			EndPrimitive();
		}
    }
}

