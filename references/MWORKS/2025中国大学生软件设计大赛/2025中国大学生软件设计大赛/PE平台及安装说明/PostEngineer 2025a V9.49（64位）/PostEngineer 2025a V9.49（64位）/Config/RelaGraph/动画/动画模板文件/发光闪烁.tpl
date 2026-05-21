Animation{
	controller{
		life{0, 时间}
		Action{
			interval{50}
			Program{
				string path = 路径;
				if(stringInclude(path, "/scene") == false){
					path = "/scene/modules/" + getCurModulePath() + "/" + 路径;
				}

				float s = getEventProgress();
				if(s < 0.25){  setMaterialBrightness(path, 1+s*16); }
				else if(s < 0.5){  setMaterialBrightness(path, 5 - (s-0.25)*16); }
				else if(s < 0.75){  setMaterialBrightness(path, 1+(s-0.5)*16); }
				else {  setMaterialBrightness(path, 5 - (s-0.75)*16); }
				
			}
		}
	}
}
