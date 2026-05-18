#version 330 core

layout (location = 0) out vec4  FragColor;   
layout (location = 1) out vec3  gNormal;  

in vec3 vertex;
in vec3 normal;

in vec3 viewPos;

uniform float radius;

void main()
{		
    float r_2 = viewPos.x* viewPos.x + viewPos.y* viewPos.y;

    if( r_2 > radius*radius ) discard;

    FragColor = vec4(vertex, 1.0);
    gNormal = normalize(normal);
}