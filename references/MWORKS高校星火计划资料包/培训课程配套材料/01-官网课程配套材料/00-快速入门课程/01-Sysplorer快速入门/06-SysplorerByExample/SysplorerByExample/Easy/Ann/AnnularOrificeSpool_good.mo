model AnnularOrificeSpool_good
"带有圆环节流孔的滑阀芯-参数框优化"
// 参数归类方式：
// 使用：annotation (Dialog(tab = “参数页名”,group = “参数组名”))
// tab=“”表示将此参数放在具体参数页
// group=“”表示将此参数放在具体参数组

  import SI=Modelica.SIunits;
  //参数
  parameter SI.Length ds(displayUnit = "mm") = 0.01 "筒径" 
    annotation (Dialog(group = "结构参数"));
  parameter SI.Length dr(displayUnit = "mm") = 0.005 "杆径" 
    annotation (Dialog(group = "结构参数"));
  parameter SI.Length len0(displayUnit = "mm") = 0 "初始压力腔长度" 
    annotation (Dialog(group = "结构参数"));
  parameter SI.Position underlap0(displayUnit = "mm") = 0 "零开口压力腔长" 
    annotation (Dialog(group = "结构参数"));
  parameter SI.Position xmin(displayUnit = "mm") = 0 "最小位移限制" 
    annotation (Dialog(group = "结构限制"));
  parameter SI.Position xmax(displayUnit = "mm") = 1e27 "最大位移限制" 
    annotation (Dialog(group = "结构限制"));
  parameter SI.Volume v0(displayUnit = "ml") = 0 "死区容积" 
    annotation (Dialog(group = "高级"));
  parameter Boolean UseJetForce = false "若为true，则考虑液动力，否则不考虑液动力" 
    annotation (Dialog(tab = "高级", group = "流体参数"));
  parameter Real Cqmax = 0.7 "最大流量系数" 
    annotation (Dialog(tab = "高级", group = "流体参数"));
  parameter Real lambda_crit = 100 "临界流量数" 
    annotation (Dialog(tab = "高级", group = "流体参数"));
end AnnularOrificeSpool_good;