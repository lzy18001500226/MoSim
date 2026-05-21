
Animation
{
	controller{
		life{0, 10}
		Program{
			string animName = moveEntityOnRouteAnim(名称, 路线名, 总时间, 起始时间);
			addChildAnimation("", animName );
		}
	}
}