
Animation
{
	controller{
		life{0, 10}
		Program{
			string animName = moveEntityAutoPathWithSpeedAnim(名称, 起点, 终点, 速度, 起始时间);
			addChildAnimation("", animName );
		}
	}
}