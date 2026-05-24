#version 130

uniform sampler2D srcImage;
uniform sampler2D dstImage;
uniform int mode;

varying vec2 vUv;



float gauss[] = float[]
(
    0.00000067, 0.00002292, 0.00019117, 0.00038771, 0.00019117, 0.00002292, 0.00000067,

    0.00002292, 0.00078633, 0.00655965, 0.01330373, 0.00655965, 0.00078633, 0.00002292,

    0.00019117, 0.00655965, 0.05472157, 0.11098164, 0.05472157, 0.00655965, 0.00019117,

    0.00038771, 0.01330373, 0.11098164, 0.22508352, 0.11098164, 0.01330373, 0.00038771,

    0.00019117, 0.00655965, 0.05472157, 0.11098164, 0.05472157, 0.00655965, 0.00019117,

    0.00002292, 0.00078633, 0.00655965, 0.01330373, 0.00655965, 0.00078633, 0.00002292,

    0.00000067, 0.00002292, 0.00019117, 0.00038771, 0.00019117, 0.00002292, 0.00000067

);


vec4 GaussBlur(sampler2D Color, vec2 uv)
{
    float step = 1.0;

    vec4 result = vec4(0);
    
    vec2 texSize = textureSize(Color, 0);

    int idx = 0;

    for(int i = -3;i <= 3;i++)
    {
        for(int j = -3; j <= 3;j++)
        {
            vec2 offset_uv = uv + vec2(step * i /texSize.x, step * j /texSize.y);

            vec4 s = texture2D(Color, offset_uv);

            float weight = gauss[idx++];

            result += weight * s;

        }

    }

    return result;
}




void main()
{
	//参考2023-12-28版本，使用了源图的brightness来降低光照强度，这里不再使用brightness，而是通过直接降低微粒浓度

	vec4 result = texture(srcImage, vUv);
	
	//vec4 lightVolume = texture(dstImage, vUv);
	//float alpha = GaussBlur(dstImage, vUv).a;
	vec4 lightVolume = GaussBlur(dstImage, vUv);

	vec3 color = lightVolume.rgb * lightVolume.a;
	//float brightness = 0.2126*result.r + 0.7152*result.g + 0.0722*result.b;
	//result.rgb += max(color, 0) * brightness;
	result.rgb += max(color, 0);
	
	gl_FragColor = result;
}

	
	
		