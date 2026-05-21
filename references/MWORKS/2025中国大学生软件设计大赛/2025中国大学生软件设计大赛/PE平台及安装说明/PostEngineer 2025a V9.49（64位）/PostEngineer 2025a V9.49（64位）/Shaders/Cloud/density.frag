
uniform float density;
uniform sampler2D frontTex;
uniform sampler2D backTex;
//uniform sampler2D normalMap;

varying vec2 uv;

float random(vec4 seed)
{
	float dot_product = dot(seed, vec4(12.9898, 78.233, 45.164, 94.673));
	return fract( sin(dot_product) * 43758.5453 );
}

void main() {
 
 float back = texture2D(backTex, uv).r;
 float front = texture2D(frontTex, uv).r;
 //float scene = texture2D(normalMap, uv).a;
 //if(scene < back && scene > front) back = scene;
 float dis = (back - front);
 
 gl_FragColor = vec4( dis*density, uv, 1.0 );

}
