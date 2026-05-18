#version 330 core
#extension GL_NV_shader_buffer_load : enable

layout (location = 0) out vec4 gMainColor;


varying vec2 vUv;

uniform sampler2D gPositionDepth;
uniform sampler2D gNormal;

uniform mat4 cameraConvertMatrix;

uniform mat4 gMatrixToProbe;

const float PI = 3.1415926535897932384626433832795;


struct LightProbe
{
	vec3 position;
	//vec3 normal;    ///节省缓存
	vec3 factors[9];
};

uniform LightProbe	gLightProbes[64];
uniform int			gLightProbeCount;


uniform vec3 gLightProbesCenter;


//uniform mat3		gSceneRotation;

uniform float gAttenuationDistance;

struct LPTetrahedral
{
	ivec2 index[4];
	//mat3 matrix;   ///节省缓存
};

uniform LPTetrahedral gTetrahedrals[90];
uniform int gTetrahedralCount;


vec3 GetTetrahedralPoint(int i, int k)
{
	int ptIndex = (gTetrahedrals[i].index[k]).x;
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



vec3 GetTetrahedralNormal(int i, int k)
{
	int ptIndex = (gTetrahedrals[i].index[k]).x;
	return normalize(gLightProbes[ptIndex].position - gLightProbesCenter);
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



float GetTetrahedralDistance(vec3 P, int i)
{
	float dis = 0;
	for(int k=0; k<4; k++){
		dis += distance(P, GetTetrahedralPoint(i, k));
	}
	
	return dis / 4;
}


vec4 CalcTetrahedralCoord(vec3 P, int i)
{
	vec4 coord;	
	
	vec3 P0 = GetTetrahedralPoint(i, 0);
	vec3 P1 = GetTetrahedralPoint(i, 1);
	vec3 P2 = GetTetrahedralPoint(i, 2);
	vec3 P3 = GetTetrahedralPoint(i, 3);
	
	mat3 matrix = inverse(mat3(P0-P3, P1-P3, P2 - P3));
	//coord.xyz = gTetrahedrals[i].matrix * (P - GetTetrahedralPoint(i, 3));
	coord.xyz = matrix * (P - GetTetrahedralPoint(i, 3));
	coord.w = 1 - coord.x - coord.y - coord.z;
	
	return coord;
}



vec3 CalcNormal(vec3 p1, vec3 p2, vec3 p3)
{	
	vec3 v1 = p2 - p1;
	vec3 v2 = p3 - p1;
	
	return normalize(vec3( v1.y*v2.z - v1.z*v2.y, v1.z*v2.x - v1.x*v2.z, v1.x*v2.y - v1.y*v2.x ));

}


vec3 CalcIntersection(vec3 P, int i, int k)
{
	vec3 P0 = GetTetrahedralPoint(i, k);
	vec3 P1 = GetTetrahedralPoint(i, (k+1)%4);
	vec3 P2 = GetTetrahedralPoint(i, (k+2)%4);
	vec3 P3 = GetTetrahedralPoint(i, (k+3)%4);
	
	vec3 normal = CalcNormal(P1, P2, P3);
	
	float t = dot(P1-P0, normal) / dot(P-P0, normal);
	return P0 + (P - P0)*t;
	
}


vec3 CalcIntersection(vec3 P, vec3 D, vec3 B, vec3 N)
{
	float dotv = dot(D, N);
	if( abs(dotv)<1e-6 ) return P;
	
	float t = dot(B-P, N) / dotv;
	return P + D*t;
}

float CalcArea(vec3 P1, vec3 P2, vec3 P3, vec3 N)
{
	vec3 V = cross( P1-P2, P3-P2 );
	float A = length(V) / 2;
	if( dot(V, N) < 0) A = -A;
	return A;
}

///过P点创建一个平行平面，与三个顶点的法线相交构成一个三角形，计算P在此三角形中的重心坐标
vec4 CalcTetrahedralCoordEdge(vec3 P, int i, int k)
{
	vec3 D1 = GetTetrahedralNormal(i, (k+1)%4);
	vec3 D2 = GetTetrahedralNormal(i, (k+2)%4);
	vec3 D3 = GetTetrahedralNormal(i, (k+3)%4);
	
	vec3 P1 = GetTetrahedralPoint(i, (k+1)%4);
	vec3 P2 = GetTetrahedralPoint(i, (k+2)%4);
	vec3 P3 = GetTetrahedralPoint(i, (k+3)%4);
	
	vec3 N = CalcNormal(P1, P2, P3);
	
	if( abs(dot(D1, N)) < 1e-6 || abs(dot(D2, N)) < 1e-6 || abs(dot(D3, N)) < 1e-6 ){
		return vec4(-1, 0, 0, 0);
	}
	
	vec3 iP1 = CalcIntersection(P1, D1, P, N);
	vec3 iP2 = CalcIntersection(P2, D2, P, N);
	vec3 iP3 = CalcIntersection(P3, D3, P, N);
	
	if( abs(dot(D1, iP1-P1)) < 0 || abs(dot(D2, iP2-P2)) < 0 || abs(dot(D3, iP3-P3)) < 0 ){
		return vec4(-1, 0, 0, 0);
	}
	
	float A1 = CalcArea(P, iP2, iP3, N);
	float A2 = CalcArea(P, iP3, iP1, N);
	float A3 = CalcArea(P, iP1, iP2, N);
	
	float A = A1+A2+A3;
	
	///衰减系数
	float f = 1.0;
	if(gAttenuationDistance > 1e-6){
		vec3 proj = P1*A1/A + P2*A2/A + P3*A3/A;
		float f = distance(P, proj)/gAttenuationDistance;
		f = clamp(1 - f*f, 0, 1);
	}
	
	if(k==0)		return vec4( 0, A1/A, A2/A, A3/A ) * f;
	else if(k==1)	return vec4( A3/A, 0, A1/A, A2/A) * f;
	else if(k==2)	return vec4( A2/A, A3/A, 0, A1/A) * f;
	else if(k==3)	return vec4( A1/A, A2/A, A3/A, 0) * f;
}


bool IsInTetrahedra(vec4 coord)
{
	return ( coord.x>=0 && coord.x <= 1 && coord.y>=0 && coord.y <= 1
	      && coord.z>=0 && coord.z <= 1 && coord.w>=0 && coord.w <= 1 );
}

bool IsInTetrahedraExtent(vec4 coord)
{
	return ( coord.x>-1e-6 && coord.y>-1e-6 && coord.z>-1e-6 && coord.w>-1e-6 );
}

int stack_index_arrry[64];
int stack_index_size;

void istack_reset()
{
	stack_index_size = 0;
}

bool istack_push(int index)
{
	if(stack_index_size == 63) return false;
	
	for(int i=0; i<stack_index_size; i++){
		if(stack_index_arrry[i] == index) return false;  ///避免重复
	}
	
	for(int i=stack_index_size; i>0; i--){
		stack_index_arrry[i] = stack_index_arrry[i-1];
	}
	
	stack_index_arrry[0] = index;
	stack_index_size++;
	
	return true;
}

int istack_pop()
{
	int ret_index = stack_index_arrry[0];
	
	for(int i=0; i<stack_index_size-1; i++){
		stack_index_arrry[i] = stack_index_arrry[i+1];
	}
	stack_index_size--;
	
	return ret_index;
}

bool istack_is_empty()
{
	return (stack_index_size > 0);
}


int SearchTetrahedra(vec3 P, out vec4 coord)
{
	istack_reset();
	istack_push(0);
	
	vec4 cur_coord = vec4(0);
	vec4 coord_edge = vec4(0);
	
	while( istack_is_empty() == false )
	{
		int cur_index = istack_pop();
		
		cur_coord = CalcTetrahedralCoord(P, cur_index);
		if( IsInTetrahedra(cur_coord) ){
			coord = cur_coord;
			return cur_index;
		}
		
		if(cur_coord.x < -1e-6){
			int next_index = gTetrahedrals[cur_index].index[0].y;
			
			if(next_index != -1)
			{
				istack_push(next_index);
			}
			else{
				coord_edge = CalcTetrahedralCoordEdge(P, cur_index, 0);
				if( IsInTetrahedraExtent(coord_edge) ){
					coord = coord_edge;
					return cur_index;
				}
			}
		}
		
		if(cur_coord.y < -1e-6){
			int next_index = gTetrahedrals[cur_index].index[1].y;
			
			if(next_index != -1)
			{
				istack_push(next_index);
			}
			else{
				coord_edge = CalcTetrahedralCoordEdge(P, cur_index, 1);
				if( IsInTetrahedraExtent(coord_edge)){
					coord = coord_edge;
					return cur_index;
				}
			}
		}
		
		if(cur_coord.z < -1e-6){
			int next_index = gTetrahedrals[cur_index].index[2].y;
			
			if(next_index != -1)
			{
				istack_push(next_index);
			}
			else{
				coord_edge = CalcTetrahedralCoordEdge(P, cur_index, 2);
				if( IsInTetrahedraExtent(coord_edge) ){
					coord = coord_edge;
					return cur_index;
				}
			}
		}
		
		if(cur_coord.w < -1e-6){
			int next_index = gTetrahedrals[cur_index].index[3].y;
			
			if(next_index != -1)
			{
				istack_push(next_index);
			}
			else{
				coord_edge = CalcTetrahedralCoordEdge(P, cur_index, 3);
				if( IsInTetrahedraExtent(coord_edge) ){
					coord = coord_edge;
					return cur_index;
				}
			}
		}
	}

	
	///快速查找不到则逐个遍历
	int min_index = -1;
	int edge_min_index = -1;
	coord = vec4(0);
	vec4 edge_min_coord = vec4(0);
	
	for(int i=0; i<gTetrahedralCount; i++){
		coord = CalcTetrahedralCoord(P, i);
		
		///注意连续if判断，前面语句对后面的影响
		if( coord.x < -1e-6 || coord.y < -1e-6 || coord.z < -1e-6 || coord.w < -1e-6 )
		{
			if(edge_min_index == -1){
				if(coord.x < -1e-6 && gTetrahedrals[i].index[0].y == -1){
					vec4 coord_edge = CalcTetrahedralCoordEdge(P, i, 0);
					if( IsInTetrahedraExtent(coord_edge)){
						edge_min_index = i;
						edge_min_coord = coord_edge;
					}
				}
				
				if(coord.y < -1e-6 && gTetrahedrals[i].index[1].y == -1){
					vec4 coord_edge = CalcTetrahedralCoordEdge(P, i, 1);
					if( IsInTetrahedraExtent(coord_edge) ){
						edge_min_index = i;
						edge_min_coord = coord_edge;
					}
				}
				
				if(coord.z < -1e-6 && gTetrahedrals[i].index[2].y == -1){
					vec4 coord_edge = CalcTetrahedralCoordEdge(P, i, 2);
					if( IsInTetrahedraExtent(coord_edge) ) {
						edge_min_index = i;
						edge_min_coord = coord_edge;
					}
				}
				
				if(coord.w < -1e-6 && gTetrahedrals[i].index[3].y == -1){
					vec4 coord_edge = CalcTetrahedralCoordEdge(P, i, 3);
					if( IsInTetrahedraExtent(coord_edge) ){
						edge_min_index = i;
						edge_min_coord = coord_edge;
					}
				}
			}
		
			continue;
		}		
			
		min_index = i;
		break;
	}
	
	if(min_index == -1){
		if(edge_min_index != -1){
			coord = edge_min_coord;
			min_index = edge_min_index;
		}
	}
	
	return min_index;
}


void CalcSHFactors(vec3 P, out vec3 SHFactors[9])
{	
			
	if(gLightProbeCount == 0){
		for(int m=0; m<9; m++) SHFactors[m] = vec3(0.0);
		return;
	}

	if(gLightProbeCount < 4){
		for(int m=0; m<9; m++) SHFactors[m] = gLightProbes[0].factors[m];
		return;
	}
	
	for(int m=0; m<9; m++) SHFactors[m] = vec3(0.0);
	
	
	vec4 coord;
	int min_index = SearchTetrahedra(P, coord);

	if(min_index != -1)
	{
		for(int k=0; k<4; k++){	
			vec3 factors[9];
			int ptIndex = (gTetrahedrals[min_index].index[k]).x;
			if(ptIndex >= gLightProbeCount){
				int try_index = (gTetrahedrals[min_index].index[(k+1)%4]).x;
				if(try_index >= gLightProbeCount){
					try_index = (gTetrahedrals[min_index].index[(k+2)%4]).x;
					if(try_index >= gLightProbeCount){
						try_index = (gTetrahedrals[min_index].index[(k+3)%4]).x;
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

	float temp = ((2.0*l + 1.0)*factorial(l - m)) / (4.0*PI*factorial(l + m));

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




const float kSqrt03_02    = sqrt( 3.0 /  2.0);

    const float kSqrt01_03    = sqrt( 1.0 /  3.0);

    const float kSqrt02_03    = sqrt( 2.0 /  3.0);

    const float kSqrt04_03    = sqrt( 4.0 /  3.0);

    const float kSqrt01_04    = sqrt( 1.0 /  4.0);

    const float kSqrt03_04    = sqrt( 3.0 /  4.0);
    
  const float kSqrt01_12    = sqrt( 1.0 / 12.0);


vec3 dp3(const vec3* a, const float* b)
    {

        return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];

    }


vec3 dp(int n, const vec3* a, const float* b)
 {
        vec3 result = (*a) * (*b);
        while (--n > 0)
        {

            a++;

            b++;

            result += (*a) * (*b);

        }

        return result;

    }

//#define VL_ROW_ORIENT

void RotateSH(mat3 orient, int n, const vec3 coeffsIn[9],  out vec3 coeffs[9])

    /// We could make faster "specialized" versions, as for the last band we don't

    /// need the full sh matrix, just a row.

    {
    
		int outIndex = 0;
		int inBaseIndex = 0;

        coeffs[outIndex++] = coeffsIn[0];

        if (n < 2)

            return;

            

        inBaseIndex += 1;

    #ifdef VL_ROW_ORIENT

        // for row vectors, v' = v M

     /*   float sh1[3*3] =

        {

            orient[1][1], orient[2][1], orient[0][1],

            orient[1][2], orient[2][2], orient[0][2],

            orient[1][0], orient[2][0], orient[0][0]

        };*/
        
        float sh1[3*3];
        sh1[0*3+0] = orient[1][1]; sh1[0*3+1] = orient[2][1]; sh1[0*3+2] = orient[0][1];
        sh1[1*3+0] = orient[1][2]; sh1[1*3+1] = orient[2][2]; sh1[1*3+2] = orient[0][2];
        sh1[2*3+0] = orient[1][0]; sh1[2*3+1] = orient[2][0]; sh1[2*3+2] = orient[0][0];

    #else

        // for column vectors, v' = M v

       /* float sh1[3*3] =

        {

            orient[1][1], orient[1][2], orient[1][0],

            orient[2][1], orient[2][2], orient[2][0],

            orient[0][1], orient[0][2], orient[0][0]

        };*/
        
        float sh1[3*3];
        sh1[0*3+0] = orient[1][1]; sh1[0*3+1] = orient[1][2]; sh1[0*3+2] = orient[1][0];
        sh1[1*3+0] = orient[2][1]; sh1[1*3+1] = orient[2][2]; sh1[1*3+2] = orient[2][0];
        sh1[2*3+0] = orient[0][1]; sh1[2*3+1] = orient[0][2]; sh1[2*3+2] = orient[0][0];

    #endif



        //(*coeffs++) = dp3(coeffsIn, sh1+0*3);
        coeffs[outIndex++] = coeffsIn[inBaseIndex+0] * sh1[0*3+0] + coeffsIn[inBaseIndex+1] * sh1[0*3+1] + coeffsIn[inBaseIndex+2] * sh1[0*3+2];

        //(*coeffs++) = dp3(coeffsIn, sh1+1*3);
        coeffs[outIndex++] = coeffsIn[inBaseIndex+0] * sh1[1*3+0] + coeffsIn[inBaseIndex+1] * sh1[1*3+1] + coeffsIn[inBaseIndex+2] * sh1[1*3+2];


        //(*coeffs++) = dp3(coeffsIn, sh1+2*3);
        coeffs[outIndex++] = coeffsIn[inBaseIndex+0] * sh1[2*3+0] + coeffsIn[inBaseIndex+1] * sh1[2*3+1] + coeffsIn[inBaseIndex+2] * sh1[2*3+2];


        
    // band 3:

        if (n < 3)

            return;

        //coeffsIn += 3;
        inBaseIndex+=3;

        float sh2[25];


        sh2[0*5+0] = kSqrt01_04 * ((sh1[2*3+2] * sh1[0*3+0] + sh1[2*3+0] * sh1[0*3+2]) + (sh1[0*3+2] * sh1[2*3+0] + sh1[0*3+0] * sh1[2*3+2]));

        sh2[0*5+1] = (sh1[2*3+1] * sh1[0*3+0] + sh1[0*3+1] * sh1[2*3+0]);

        sh2[0*5+2] = kSqrt03_04 * (sh1[2*3+1] * sh1[0*3+1] + sh1[0*3+1] * sh1[2*3+1]);

        sh2[0*5+3] = (sh1[2*3+1] * sh1[0*3+2] + sh1[0*3+1] * sh1[2*3+2]);

        sh2[0*5+4] = kSqrt01_04 * ((sh1[2*3+2] * sh1[0*3+2] - sh1[2*3+0] * sh1[0*3+0]) + (sh1[0*3+2] * sh1[2*3+2] - sh1[0*3+0] * sh1[2*3+0]));

		vec3 val = vec3(0);
		for(int k=0; k<5; k++) val += coeffsIn[inBaseIndex+k] * sh2[0*5+k];
        coeffs[outIndex++] = val;



        sh2[1*5+0] = kSqrt01_04 * ((sh1[1*3+2] * sh1[0*3+0] + sh1[1*3+0] * sh1[0*3+2]) + (sh1[0*3+2] * sh1[1*3+0] + sh1[0*3+0] * sh1[1*3+2]));

        sh2[1*5+1] = sh1[1*3+1] * sh1[0*3+0] + sh1[0*3+1] * sh1[1*3+0];

        sh2[1*5+2] = kSqrt03_04 * (sh1[1*3+1] * sh1[0*3+1] + sh1[0*3+1] * sh1[1*3+1]);

        sh2[1*5+3] = sh1[1*3+1] * sh1[0*3+2] + sh1[0*3+1] * sh1[1*3+2];

        sh2[1*5+4] = kSqrt01_04 * ((sh1[1*3+2] * sh1[0*3+2] - sh1[1*3+0] * sh1[0*3+0]) + (sh1[0*3+2] * sh1[1*3+2] - sh1[0*3+0] * sh1[1*3+0]));



        //(*coeffs++) = dp(5, coeffsIn, sh2+1*5);
        val = vec3(0);
		for(int k=0; k<5; k++) val += coeffsIn[inBaseIndex+k] * sh2[1*5+k];
        coeffs[outIndex++] = val;



        sh2[2*5+0] = kSqrt01_03 * (sh1[1*3+2] * sh1[1*3+0] + sh1[1*3+0] * sh1[1*3+2]) + -kSqrt01_12 * ((sh1[2*3+2] * sh1[2*3+0] + sh1[2*3+0] * sh1[2*3+2]) + (sh1[0*3+2] * sh1[0*3+0] + sh1[0*3+0] * sh1[0*3+2]));

        sh2[2*5+1] = kSqrt04_03 * sh1[1*3+1] * sh1[1*3+0] + -kSqrt01_03 * (sh1[2*3+1] * sh1[2*3+0] + sh1[0*3+1] * sh1[0*3+0]);

        sh2[2*5+2] = sh1[1*3+1] * sh1[1*3+1] + -kSqrt01_04 * (sh1[2*3+1] * sh1[2*3+1] + sh1[0*3+1] * sh1[0*3+1]);

        sh2[2*5+3] = kSqrt04_03 * sh1[1*3+1] * sh1[1*3+2] + -kSqrt01_03 * (sh1[2*3+1] * sh1[2*3+2] + sh1[0*3+1] * sh1[0*3+2]);

        sh2[2*5+4] = kSqrt01_03 * (sh1[1*3+2] * sh1[1*3+2] - sh1[1*3+0] * sh1[1*3+0]) + -kSqrt01_12 * ((sh1[2*3+2] * sh1[2*3+2] - sh1[2*3+0] * sh1[2*3+0]) + (sh1[0*3+2] * sh1[0*3+2] - sh1[0*3+0] * sh1[0*3+0]));



        //(*coeffs++) = dp(5, coeffsIn, sh2+2*5);
        val = vec3(0);
		for(int k=0; k<5; k++) val += coeffsIn[inBaseIndex+k] * sh2[2*5+k];
        coeffs[outIndex++] = val;



        sh2[3*5+0] = kSqrt01_04 * ((sh1[1*3+2] * sh1[2*3+0] + sh1[1*3+0] * sh1[2*3+2]) + (sh1[2*3+2] * sh1[1*3+0] + sh1[2*3+0] * sh1[1*3+2]));

        sh2[3*5+1] = sh1[1*3+1] * sh1[2*3+0] + sh1[2*3+1] * sh1[1*3+0];

        sh2[3*5+2] = kSqrt03_04 * (sh1[1*3+1] * sh1[2*3+1] + sh1[2*3+1] * sh1[1*3+1]);

        sh2[3*5+3] = sh1[1*3+1] * sh1[2*3+2] + sh1[2*3+1] * sh1[1*3+2];

        sh2[3*5+4] = kSqrt01_04 * ((sh1[1*3+2] * sh1[2*3+2] - sh1[1*3+0] * sh1[2*3+0]) + (sh1[2*3+2] * sh1[1*3+2] - sh1[2*3+0] * sh1[1*3+0]));



        //(*coeffs++) = dp(5, coeffsIn, sh2+3*5);
        val = vec3(0);
		for(int k=0; k<5; k++) val += coeffsIn[inBaseIndex+k] * sh2[3*5+k];
        coeffs[outIndex++] = val;



        sh2[4*5+0] = kSqrt01_04 * ((sh1[2*3+2] * sh1[2*3+0] + sh1[2*3+0] * sh1[2*3+2]) - (sh1[0*3+2] * sh1[0*3+0] + sh1[0*3+0] * sh1[0*3+2]));

        sh2[4*5+1] = (sh1[2*3+1] * sh1[2*3+0] - sh1[0*3+1] * sh1[0*3+0]);

        sh2[4*5+2] = kSqrt03_04 * (sh1[2*3+1] * sh1[2*3+1] - sh1[0*3+1] * sh1[0*3+1]);

        sh2[4*5+3] = (sh1[2*3+1] * sh1[2*3+2] - sh1[0*3+1] * sh1[0*3+2]);

        sh2[4*5+4] = kSqrt01_04 * ((sh1[2*3+2] * sh1[2*3+2] - sh1[2*3+0] * sh1[2*3+0]) - (sh1[0*3+2] * sh1[0*3+2] - sh1[0*3+0] * sh1[0*3+0]));



        //(*coeffs++) = dp(5, coeffsIn, sh2+4*5);
        val = vec3(0);
		for(int k=0; k<5; k++) val += coeffsIn[inBaseIndex+k] * sh2[4*5+k];
        coeffs[outIndex++] = val;

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
		if(N.z < 0) phi = 2*PI-phi;
	}
	
    
    float C[9];
    vec3 color = vec3(0.0);
    
 
     
    for(int k=0; k<9; k++){
		C[k] = SH(k, theta, phi);
		color += SHFactors[k]*C[k];
    }
    
    
    return color;
}



void main() 
{
		
	vec3 worldN = texture2D(gNormal, vUv).xyz;
	vec3 worldP = texture2D(gPositionDepth, vUv).xyz;

	//2025-3-18, wxg, 使用局部坐标降低误差
	vec3 localP = (gMatrixToProbe * vec4(worldP, 1)).xyz;
	vec3 localN = normalize((gMatrixToProbe * vec4(worldN, 0)).xyz);
	
	gMainColor.rgb = CalcProbeDiffuse(localP, localN);
	gMainColor.a = 1.0;
	
}