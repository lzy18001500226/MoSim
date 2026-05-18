

uniform sampler2D textureMap;

uniform vec2 gNearFar;

varying vec2 vUv;



float LinearizeDepth(float depth)
{
    float z = depth * 2.0 - 1.0; // »Øµ½NDC
    return (2.0 * gNearFar.x * gNearFar.y) / (gNearFar.y + gNearFar.x - z * (gNearFar.y - gNearFar.x));    
}

void main() 
{

   float depth = texture(textureMap, vUv).x;
   gl_FragColor = vec4(depth, LinearizeDepth(depth), 0, 0);

}
