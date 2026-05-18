
Animation
{
	controller{
		life{0, 10}
		Program{
			string animName = moveEntityAutoPathAnim(名称, 起点, 终点, 总时间, 起始时间);
			addChildAnimation("", animName );
		}
	}
}