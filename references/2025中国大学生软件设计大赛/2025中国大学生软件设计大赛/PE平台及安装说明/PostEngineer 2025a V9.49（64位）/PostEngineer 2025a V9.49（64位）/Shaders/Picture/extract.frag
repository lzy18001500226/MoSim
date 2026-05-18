#version 330

uniform sampler2D gImage;

uniform float  threshold;

in vec2 vUv;

void main()
{	
	vec3 color = vec3(0);

	vec2 tex_offset = 1.0 / textureSize(gImage, 0);

	for(int i = -1; i < 2; ++i)
    {
        color += texture(gImage, vUv + vec2(tex_offset.x * i, 0)).rgb;
		color += texture(gImage, vUv + vec2(0, tex_offset.y * i)).rgb;
    }

	color /= 6.0;

	float brightness = 0.2126*color.r + 0.7152*color.g + 0.0722*color.b;

	gl_FragColor.rgb = clamp(color * (brightness*brightness-threshold), 0.0, 0.8);
	gl_FragColor.a = 1.0;
}

	
	
		