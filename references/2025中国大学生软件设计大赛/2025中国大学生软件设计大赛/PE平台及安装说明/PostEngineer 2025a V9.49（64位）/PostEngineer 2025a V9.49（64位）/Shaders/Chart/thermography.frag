#version 430

layout (location = 0) out vec4 gFragColor; 

layout(std430, binding = 1) buffer SSBOPointsData {
	vec4 gPointsData[];
};

uniform int gPointCount;

uniform vec4 gRange;
uniform float gRadius;

struct ColorSetting
{
	float value;
	vec4 color;
};

uniform ColorSetting gColorSettings[32];
uniform	int gColorSettingCount;

in vec2 vUv;


vec4 GetValueColor(float value)
{

	if(gColorSettingCount == 0) return vec4(0);

	vec4 VColor;

	int i;
	for(i=0; i<gColorSettingCount; i++){
		if( value < gColorSettings[i].value) break;
	}

	if( i==0 ) 
		VColor = gColorSettings[0].color;
	else if(i == gColorSettingCount) 
		VColor = gColorSettings[gColorSettingCount-1].color;
	else{
		float factor = (value - gColorSettings[i-1].value) / (gColorSettings[i].value - gColorSettings[i-1].value);

		VColor = gColorSettings[i-1].color*(1-factor) + gColorSettings[i].color*factor;
	}

	return VColor;
}

void main()
{
	vec2 position = vec2(gRange.x - gRadius + (gRange.y - gRange.x + 2*gRadius) * vUv.x,  gRange.z- gRadius + (gRange.w - gRange.z + 2*gRadius) * vUv.y);

	float sumValue = 0;
	for(int i=0; i<gPointCount; i++){
		float dis = distance(position, gPointsData[i].xy);
		float val = dis < gRadius? (1 - dis / gRadius) * gPointsData[i].z : 0;
		sumValue += val;
	}

	gFragColor = GetValueColor(sumValue);
	//gFragColor = vec4(sumValue, 0, 0, 0.5);
}

	
	
		