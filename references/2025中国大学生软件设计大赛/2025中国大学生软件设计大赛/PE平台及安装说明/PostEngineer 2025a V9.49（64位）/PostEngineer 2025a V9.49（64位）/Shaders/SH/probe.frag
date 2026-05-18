#version 330 core

//#extension GL_NV_shadow_samplers_cube : enable
#extension GL_NV_shader_buffer_load : enable

out vec4 FragColor;
in vec3 direction;

uniform vec3 SHFactors[9];

uniform mat3		gSceneRotation;

uniform int reflection;
uniform samplerCube reflectionMap;

const float PI = 3.1415926;

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




void main()
{		
    vec3 normal = normalize(direction);
    
    if(reflection == 1){
		//FragColor.rgb = textureCube(reflectionMap, normal).rgb;
		FragColor.rgb = texture(reflectionMap, normal).rgb;
		FragColor.a = 1.0;
		return;
	}
		
    float theta = acos(clamp(normal.y, -1, 1));
    float phi = 0;
    float l = sqrt(normal.x*normal.x + normal.z*normal.z);
    if(l > 1e-6){
		phi = acos( clamp(normal.x / l, -1, 1) );
		if(normal.z < 0){
			phi = 2*PI-phi;	
		}
	}
    
    float C[9];
    FragColor = vec4(0, 0, 0, 1.0);
    
    ///¿ÉÓÃ£¬ÔÝÊ±ÆÁ±Î
    //vec3 SHFactorsRot[9];
    //RotateSH(gSceneRotation, 3, SHFactors, SHFactorsRot);
     
    for(int k=0; k<9; k++){
		C[k] = SH(k, theta, phi);
		FragColor.rgb += SHFactors[k]*C[k];
    }
 
}