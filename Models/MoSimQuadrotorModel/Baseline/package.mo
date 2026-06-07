within MoSimQuadrotorModel;
package Baseline
  "官方基线适配（保留QuadrotorModel上游行为，用于回归对比）"

  extends Modelica.Icons.Package;

  model OfficialExample1
    "官方阶跃爬升基线（QuadrotorModel.Examples.Example1）"
    extends QuadrotorModel.Examples.Example1;
  end OfficialExample1;

  model OfficialExample2
    "官方螺旋爬升基线（QuadrotorModel.Examples.Example2）"
    extends QuadrotorModel.Examples.Example2;
  end OfficialExample2;

  model OfficialExample3
    "官方8字轨迹基线（QuadrotorModel.Examples.Example3）"
    extends QuadrotorModel.Examples.Example3;
  end OfficialExample3;

  model OfficialQuadChassis
    "官方机体基线（QuadrotorModel.Mechanics.QuadChassis，不在此处改写）"
    extends QuadrotorModel.Mechanics.QuadChassis;
  end OfficialQuadChassis;
end Baseline;
