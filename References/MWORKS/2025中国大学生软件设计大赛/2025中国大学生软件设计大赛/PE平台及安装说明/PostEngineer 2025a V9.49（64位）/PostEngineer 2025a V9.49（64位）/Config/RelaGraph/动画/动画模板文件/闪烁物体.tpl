Animation{
	controller{
		life{0, 500}
		Action{
			program{
				hilightField(路径, 1);
			}
		}
	}
	controller{
		life{500, 1000}
		Action{
			program{
				hilightField(路径, 0);
			}
		}
	}
	controller{
		life{1000, 1500}
		Action{
			program{
				hilightField(路径, 1);
			}
		}
	}
	controller{
		life{1500, 2000}
		Action{
			program{
				hilightField(路径, 0);
			}
		}
	}
}