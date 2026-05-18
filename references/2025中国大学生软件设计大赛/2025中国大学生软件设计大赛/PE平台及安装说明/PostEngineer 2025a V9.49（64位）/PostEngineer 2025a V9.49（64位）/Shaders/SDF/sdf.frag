#version 330

#define MAX_SUB_NUM  16
#define MAX_ARR_NUM  128

layout (location = 0) out vec4 gPosition;   ///位置+线性深度
layout (location = 1) out vec4 gMaterialShadow;     ///材质索引+阴影+AO

in vec2 vUv;

uniform sampler2D gPositionDepth;
uniform sampler2D gScene;
uniform sampler2D gMotionVector;
uniform sampler1D randSampler;

uniform mat4 gModelview;
uniform mat4 gModelviewInverse;
uniform mat4 gProjectionInverse;

uniform vec2 gNearFar;

uniform vec3 gMainLightPos;

uniform int flag;

uniform vec2 jitter;

uniform vec3 gCameraPos;

uniform float hdrExposure;


struct SDFBase
{
	int type; 
	vec4 param;   
	mat4 transformInverse;    
	float scale;
	    
	int materialIndex;	
};



struct SDFComplex
{
	SDFBase subShapes[MAX_SUB_NUM];
	int subNum;
	
	int relations[MAX_SUB_NUM*4];
	int relationNum;
};



uniform SDFComplex gShapes[MAX_ARR_NUM];
uniform int gShapeNum;


uniform float aspect;//近平面高:宽
uniform float nearHeight;//近平面高 


const float EPSILON = 1e-3;
const int maxMarchingNum = 200;


struct SceneInfo
{
	float distance;
	ivec2 shapeIndex;
	int materialIndex;
};


struct OpInfo
{
	int op;
	float distance;
	int subIndex;
};


OpInfo OpArray[MAX_SUB_NUM*4];
int OpCount = 0;

bool PushOperator(OpInfo opInfo)
{
	if(OpCount == MAX_ARR_NUM) return false;
	
	for(int i=OpCount; i>0; i--){
		OpArray[i] = OpArray[i-1];
	}
	
	OpArray[0] = opInfo;
	OpCount++;
	
	return true;
}

OpInfo GetTopOperator()
{
	return OpArray[0];
}

void PopOperator()
{
	for(int i=0; i<OpCount-1; i++){
		OpArray[i] = OpArray[i+1];
	}
	OpCount--;
}


bool bit_and(int val, int ref) {
  if(val == 0) return false;

  return (val/ref) % 2 != 0;
}



//裁剪空间转换为眼空间
vec3 uvToEye(vec2 texCoord,float depth)
{
	vec2 deltaUV=(2.0*texCoord-vec2(1.0))*vec2(aspect,1.0);    
	
	//计算近平面的平移向量    
	vec2 deltaView=nearHeight*deltaUV*depth/gNearFar.x;    
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
	vec3 origin = (gModelviewInverse * vec4(0.0f, 0.0f, 0.0f, 1.0f)).xyz;    
	vec3 direction = uvToEye(uv, gNearFar.x);    
	direction = (gModelviewInverse * vec4(direction, 0.0f)).xyz;    
	direction = normalize(direction);  
	  
	Ray ray;    
	ray.origin = origin;   
	ray.eye = origin;
	ray.direction = direction;    
	return ray;
}




float sdSphere( vec3 p, float s )
{
  return length(p)-s;
}

float sdEllipsoid( vec3 p, vec3 r )
{
  float k0 = length(p/r);
  float k1 = length(p/(r*r));
  return k0*(k0-1.0)/k1;
}


float sdBox( vec3 p, vec3 b )
{
  vec3 q = abs(p) - b;
  return length(max(q,0.0)) + min(max(q.x,max(q.y,q.z)),0.0);
}
float sdRoundedBox( vec3 p, vec3 b, float r )
{
  vec3 q = abs(p) - b;
  return length(max(q,0.0)) + min(max(q.x,max(q.y,q.z)),0.0) - r;
}


float sdCylinder( vec3 p, float h, float r )
{
  vec2 d = abs(vec2(length(p.xz),p.y)) - vec2(h,r);
  return min(max(d.x,d.y),0.0) + length(max(d,0.0));
}
float sdRoundedCylinder( vec3 p, float ra, float rb, float h )
{
  vec2 d = vec2( length(p.xz)-2.0*ra+rb, abs(p.y) - h );
  return min(max(d.x,d.y),0.0) + length(max(d,0.0)) - rb;
}


float GetSubShapeDistance(SDFBase shape, vec3 eye) 
{
	vec3 local_eye = (shape.transformInverse * vec4(eye, 1)).xyz; 

	if (shape.type == 1) {  
		if(shape.param.w > EPSILON)
			return sdRoundedBox(local_eye, shape.param.xyz, shape.param.w);      
		else
			return sdBox(local_eye, shape.param.xyz);
	}    
	else if (shape.type == 2) {  
		return sdSphere(local_eye, shape.param.x);  
	} 
	else if (shape.type == 3) {  
		return sdEllipsoid(local_eye, shape.param.xyz);  
	}  
	else if (shape.type == 4) {
		if(shape.param.z > EPSILON)   
			return sdRoundedCylinder(local_eye, shape.param.x, shape.param.z, shape.param.y);        
		else
			return sdCylinder(local_eye, shape.param.y, shape.param.x);    
	}    
	
	return gNearFar.y;
}



void Operate(int op, int currentBestIndex, float currentBestDst, int localIndex, float localDst, out int bestIndex, out float bestDst)
{

	if(currentBestIndex < 0){
		bestIndex = localIndex;
		bestDst = localDst;
		return;
	}

	bestIndex = currentBestIndex;
	bestDst = currentBestDst;
	
	if( op == -1 ){
		if( localDst < currentBestDst ){
			bestIndex = localIndex;
			bestDst = localDst;
		}
	}
	else if( op == -2 ){
		if( localDst > currentBestDst ){
			bestIndex = localIndex;
			bestDst = localDst;
		}
	}
	else if( op == -3 ){
		if( -localDst > currentBestDst ){
			bestIndex = localIndex;
			bestDst = -localDst;
		}
	}
}

SceneInfo GetShapeDistance(int index, vec3 eye)
{
	SDFComplex shape = gShapes[index];
	
	if(shape.subNum == 1){
	
		SDFBase subShape = shape.subShapes[0];
	
		SceneInfo inf;
		inf.shapeIndex = ivec2(index, 0);
		inf.distance = GetSubShapeDistance(subShape, eye);  
		inf.materialIndex = subShape.materialIndex;
		
		return inf;	
	}

	float fatherBestDst = 0;    
	int fatherBestIndex = -1; 
	
	float currentBestDst = 0;    
	int currentBestIndex = -1; 
	
	int i = 0;
	int cur_op = shape.relations[i++];
	while (i < shape.relationNum)    
	{	
		int val = shape.relations[i];
		
		///如果遇到新的操作，则将当前操作压栈
		if(val == -1 || val == -2 || val == -3){
			OpInfo opi;
			
			opi.op = cur_op;
			opi.distance = currentBestDst;
			opi.subIndex = currentBestIndex;
			
			PushOperator(opi);

			cur_op = val;
			currentBestDst = 0;
			currentBestIndex = -1;
			i++;
			i++;  ///跳过'('
			continue;
		}
		
		///当前操作执行完毕
		if(val == -7){
			
			if(OpCount == 0){  ///结束
				break;
			}
			
			OpInfo opi = GetTopOperator();
			PopOperator();
			
			fatherBestDst = opi.distance;
			fatherBestIndex = opi.subIndex;
			
			Operate(opi.op, fatherBestIndex, fatherBestDst, currentBestIndex, currentBestDst, currentBestIndex, currentBestDst);
			
			cur_op = opi.op;
			i++;
			continue;
		}  
		
		if(val == -6) i++;  
		int subIndex = shape.relations[i];
		   
		float localDst = GetSubShapeDistance(shape.subShapes[subIndex], eye);	
		Operate(cur_op, currentBestIndex, currentBestDst, subIndex, localDst, currentBestIndex, currentBestDst);  
		i++;      
	}
	
	
	SceneInfo inf;
	inf.shapeIndex = ivec2(index, currentBestIndex);
	inf.distance = currentBestDst;  
	inf.materialIndex = shape.subShapes[currentBestIndex].materialIndex;
	
	return inf;
}


SceneInfo GetSceneInfo(vec3 eye)
{    

	SceneInfo globalInfo;
	globalInfo.distance = gNearFar.y;
	
	for(int i=0; i<gShapeNum; i++){

		SceneInfo localInfo = GetShapeDistance(i, eye); 
		
		if(localInfo.distance < globalInfo.distance){
			globalInfo = localInfo;
		}
	}

	return globalInfo;
}


float sceneSDF(vec3 p)
{    
	return GetSceneInfo(p).distance;
}


vec3 estimateNormal(vec3 p) 
{    
	const float h = EPSILON; // replace by an appropriate value
    const vec2 k = vec2(1,-1);
    return normalize( k.xyy * sceneSDF( p + k.xyy*h ) + 
                      k.yyx * sceneSDF( p + k.yyx*h ) + 
                      k.yxy * sceneSDF( p + k.yxy*h ) + 
                      k.xxx * sceneSDF( p + k.xxx*h ) );
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


float CalcSDFAO(vec3 P, vec3 N, float r)
{
	vec3 T = get_ortho(N);
    vec3 B = normalize(cross(N, T));
        
    int total = 16;
    int num = 0;
	for (int i = 0 ; i < total ; i++) {
		vec3 rand = texture(randSampler, float(i)/total).xyz;
        vec3 D = (rand.x*2-1)*T + (rand.y*2-1)*B + rand.z*N;   //half sphere
        
        vec3 Q = P + D*r;
        float dst = GetSceneInfo(Q).distance;
        
        ///落进其他体内
        if(dst < EPSILON) num++;
    }
    
    return 1.0 - float(num) / total;
}



float CalcSDFShadow(Ray ray, float maxDst, float k)
{
	float rayDst = GetSceneInfo(ray.origin).distance;
	ray.eye = ray.origin + rayDst*ray.direction;
	int marchSteps = 0;  
	float prevDst = 1e10;

	float shadow = 1.0;
	
	while (rayDst < maxDst - EPSILON)
	{        
		marchSteps++;        
		SceneInfo sceneInfo = GetSceneInfo(ray.eye);        
		float dst = sceneInfo.distance; 	       
		
      
		if (dst < EPSILON) {   
			return 0.0;     
		}
		
		float y = dst*dst/2/prevDst;
		float d = sqrt(dst*dst - y*y);
		
		shadow = min(shadow, k*d/max(0.0, rayDst-y));          
		   
		ray.eye += ray.direction * dst;        
		rayDst += dst;   
		prevDst = dst; 
		
		if(marchSteps > maxMarchingNum){                         
			break;        
		}
	}
	
	return shadow;
}


vec2 GetJitterUV(vec2 uv)
{
	return uv + jitter / 2;
}


void main()
{
	vec2 jitterUv = GetJitterUV(vUv);
	
	//gMainColor = texture(gScene, jitterUv);
	
	Ray ray = CreateCameraRay(jitterUv);
	float maxDst = gNearFar.y;
	
	
	float depth = texture(gPositionDepth, jitterUv).w;
	if(depth < EPSILON){
		depth = gNearFar.y;
	}


	float rayDst = 0;
	int marchSteps = 0;  
	
	vec3 lightDir = normalize( gMainLightPos - ray.origin );
	  
	while (rayDst < maxDst) {        
		marchSteps++;        
		SceneInfo sceneInfo = GetSceneInfo(ray.eye);        
		float dst = sceneInfo.distance; 
		       
		//it means that rays already hit surface        
		if (dst <= EPSILON) {   
		
			vec3 surfacePoint = ray.eye + ray.direction * dst; 
			
			gPosition.xyz = surfacePoint;
			gPosition.w = rayDst + dst;
		
			vec3 normal = estimateNormal(surfacePoint);   
	
			gMaterialShadow.r = float(sceneInfo.materialIndex);
		    
		    vec3 offsetPoint = surfacePoint + normal * EPSILON;
			
			
			///计算阴影

			Ray shadowRay;
			shadowRay.origin = offsetPoint;
			vec3 delta_vec = gMainLightPos - offsetPoint;
			shadowRay.direction = normalize(delta_vec);
		
			float k = 10;
			float shadowSDF = CalcSDFShadow(shadowRay, length(delta_vec), k);
				
			gMaterialShadow.g = shadowSDF;
			
			float occlusion = CalcSDFAO(surfacePoint, normal, 0.1);  
			gMaterialShadow.b = min((occlusion + 0.5)*0.6, 1.0);	
			        
			break;        
		}        
		
		//if not hit,update origin and stepSize        
		ray.eye += ray.direction * dst;        
		rayDst += dst;    
		
		if(rayDst > depth || marchSteps > maxMarchingNum){                         
			break;        
		}
	}

}

	
	
		