#version 330 core

uniform int flag;
uniform int gID;
uniform sampler2D gBaseDepth;

uniform float gMaxDepth;

uniform vec2 gBasePos;
uniform vec2 gValidSize;

uniform vec2 screenSize;

varying vec3 ViewPos;



void main()
{
	////过滤超出有效范围的射线
	vec2 pixel_pos = gl_FragCoord.xy;
	vec2 grid_pos = pixel_pos - screenSize/2 + gBasePos;
	if(grid_pos.x > gValidSize.x || grid_pos.x < 0 || grid_pos.y > gValidSize.y || grid_pos.y < 0){
		discard;
		return;
	}
	
	float depth = -ViewPos.z;
	     //float depth = gl_FragCoord.z / gl_FragCoord.w;  //仅深度平面坐标，即垂直投影平面到相机的距离
	     //float depth = LinearizeDepth(gl_FragCoord.z);   //仅深度平面坐标，且靠近投影平面

	if(flag == 0){
		
		///剔除目标平面之外的相交
		if(depth > gMaxDepth + 0.0001){
			discard;
			return;
		}

		gl_FragColor = vec4( gID, ViewPos );
	}
	else if(flag == 1){  ///正面绘制，在基准向外，找离基准最近的点
		vec2 uv = vec2(gl_FragCoord.x / screenSize.x,  gl_FragCoord.y / screenSize.y);
		vec4 baseInfo = texture(gBaseDepth, uv);
		
		///	深度剥离，discard保证不会进行提前深度测试
		if(depth < -baseInfo.w + 0.0001 || depth > gMaxDepth + 0.0001){
			discard;
			return;
		}

		gl_FragColor = vec4( gID, ViewPos );
	}
	else if(flag == 2){  ///反面绘制，在基准向外，找离基准最近的点并与基准的ID相同
		vec2 uv = vec2(gl_FragCoord.x / screenSize.x,  gl_FragCoord.y / screenSize.y);
		vec4 baseInfo = texture(gBaseDepth, uv);
		
		if(depth < -baseInfo.w + 0.0001 /* || depth > gMaxDepth + 0.0001*/){
			discard;
			return;
		}

		gl_FragColor = vec4( gID, ViewPos );
	}

	
}

	
	
		