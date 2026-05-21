model AnnularOrificeSpool "带有圆环节流孔的滑阀芯-参数框默认"
  //参数
  import SI=Modelica.SIunits;
parameter SI.Length ds(displayUnit = "mm") = 0.01 "筒径";
parameter SI.Length dr(displayUnit = "mm") = 0.005 "杆径";
parameter SI.Length len0(displayUnit = "mm") = 0 "初始压力腔长度";
parameter SI.Position underlap0(displayUnit = "mm") = 0 "零开口压力腔长";
parameter SI.Position xmin(displayUnit = "mm") = 0 "最小位移限制";
parameter SI.Position xmax(displayUnit = "mm") = 1e27 "最大位移限制";
parameter SI.Volume v0(displayUnit = "ml") = 0 "死区容积";
parameter Boolean UseJetForce = false "若为true，则考虑液动力，否则不考虑液动力";
parameter Real Cqmax = 0.7 "最大流量系数";
parameter Real lambda_crit = 100 "临界流量数";
end AnnularOrificeSpool;