model ShortRangeTarget "近距离目标"
  Drone.TransToForce transToForce 
    annotation (Placement(transformation(origin={-86,-62},
extent={{-21,-21},{21,21}})));
  Drone.DroneBody_Ground droneBody_Ground1(world(nominalLength=10)) 
    annotation (Placement(transformation(origin={-30,-63},
extent={{-21,-21},{21,21}})));
  Modelica.Mechanics.MultiBody.Sensors.AbsolutePosition absolutePosition 
    annotation (Placement(transformation(origin={-30,-20},
extent={{-10,-10},{10,10}})));
  AimPath.PathGenerator PathGenerator(ramp3(height=-1),ramp2(height=1),ramp4(height=1),ramp5(height=-1)) 
    annotation (Placement(transformation(origin={-151,-62},
extent={{-21,-21},{21,21}})));
  AimPath.Destination_const destnation(const(k={100,100,100})) 
    annotation (Placement(transformation(origin={-213,-62},
extent={{-21,-21},{21,21}})));
  SyslabWorkspace.FunctionAPI.SyslabGlobalConfig syslabGlobalConfig(scriptText="base64=dXNpbmcgT05OWFJ1blRpbWUKaW1wb3J0IE9OTlhSdW5UaW1lIGFzIE9OTlgKdXNpbmcgSW1hZ2VzLCBGaWxlSU8gI+WbvuWDj+mihOWkhOeQhgp1c2luZyBMdXhvcgp1c2luZyBDb2xvcnMgICMg55So5p2l566h55CG6aKc6ImyCnVzaW5nIFNwZWNpYWxGdW5jdGlvbnMKCgoj5Yqg6L295qih5Z6LCiNnbG9iYWwgZ19hYnNwYXRoCmdfYWJzcGF0aCA9ICJHOlxc5qGI5L6L5paH5Lu25rGH5oC7MjAyNTA3MDFcXDIwMjUwNjMw5Lqn5ZOB6Kej5Yaz5pa55qGI5rGH5oC777yIMDgyNuabtOaWsO+8iVxc5qGI5L6L5paH5Lu25rGH5oC7MjAyNTA3MDFcXDIuIOmrmOagoeahiOS+i1xcMi4g44CQ5py65qKw44CR55So5LqO6L+c56iL5beh6YC75Y+K5byC5bi45qOA5rWL55qE5pm66IO95peg5Lq65py6XFxTbWFydERyb25lIgpjb25zdCBtb2RlbDo6T05OWFJ1blRpbWUuSW5mZXJlbmNlU2Vzc2lvbiA9IE9OTlgubG9hZF9pbmZlcmVuY2UoZ19hYnNwYXRoKiIvZGF0YS9nZWxhbi1jLm9ubngiLCBleGVjdXRpb25fcHJvdmlkZXI9OmNwdSkK") 
    annotation (Placement(transformation(origin={-228,50},
extent={{-10,-10},{10,10}})));
  ImportedTypes.SyslabFunction1 channel(startTime=22,period=30) 
    annotation (Placement(transformation(origin={68,-63},
extent={{-21,-21},{21,21}})));
  ImportedTypes.SyslabFunction2 imagehandle(startTime=23,period=30) 
    annotation (Placement(transformation(origin={190,-63},
extent={{-21,-21},{21,21}})));
  annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2}),graphics = {Rectangle(origin={-182,-74},
fillColor={255,255,127},
fillPattern=FillPattern.Solid,
extent={{-56,86},{56,-86}}), Rectangle(origin={-58,-74},
fillColor={0,255,127},
fillPattern=FillPattern.Solid,
extent={{-56,86},{56,-86}}), Rectangle(origin={66,-74},
fillColor={255,170,127},
fillPattern=FillPattern.Solid,
extent={{-56,86},{56,-86}}), Text(origin={-182,-135},
lineColor={0,0,0},
extent={{-52,21},{52,-21}},
textString="目的坐标配置模块",
fontSize=36,
textStyle={TextStyle.Bold},
textColor={0,0,0}), Text(origin={-58,-135},
lineColor={0,0,0},
extent={{-56,25},{56,-25}},
textString="无人机飞行模块",
fontSize=36,
textStyle={TextStyle.Bold},
textColor={0,0,0}), Text(origin={68,-135},
lineColor={0,0,0},
extent={{-56,25},{56,-25}},
textString="图像采集传输模块",
fontSize=36,
textStyle={TextStyle.Bold},
textColor={0,0,0}), Rectangle(origin={190,-74},
lineColor={0,0,0},
fillColor={170,255,255},
fillPattern=FillPattern.Solid,
extent={{-56,86},{56,-86}}), Text(origin={190,-135},
lineColor={0,0,0},
extent={{-52,21},{52,-21}},
textString="智能图像识别模块",
fontSize=36,
textStyle={TextStyle.Bold},
textColor={0,0,0})}),experiment(Algorithm=Dassl,InlineIntegrator=false,InlineStepSize=false,Interval=0.01,StartTime=0,StopTime=50,Tolerance=0.0001),__MWORKS(ContinueSimConfig(SaveContinueFile="false",SaveBeforeStop="false",NumberBeforeStop=1,FixedContinueInterval="false",ContinueIntervalLength=50,ContinueTimeVector),ResultViewerManager(resultViewers={
ResultViewer(name="结果曲线", executeTrigger=executeTrigger.SimulationFinished, commands={
CreatePlot(id=1, x_display_unit="s", legend_layout=1, fix_time_range_value=0, zoom_x=(0, 50), zoom_y_l=(-20, 120)),
Plot(y=["PathGenerator.position_command[1]", "PathGenerator.position_command[2]", "PathGenerator.position_command[3]"], thicknesses=[2, 2, 2], colors=["4278190335", "4294901760", "4278222848"]),
CreatePlot(id=2, x_display_unit="s", legend_layout=1, curve_vernier=True, fix_time_range_value=0, zoom_x=(0, 50), zoom_y_l=(-0.05, 0.2)),
Plot(y=["channel.out_transmissionTime_s"], thicknesses=[2], colors=["4278190335"]),
CreatePlot(id=-1, x_display_unit="s", legend_layout=1, curve_vernier=True, fix_time_range_value=0, sub_plot=(2, 1), zoom_x=(0, 50), zoom_y_l=(-5, 25)),
Plot(y=["channel.out_SNR"], thicknesses=[2], colors=["4278190335"])})
})),Icon(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2}),graphics = {Rectangle(origin={0,0},
fillColor={255,255,255},
fillPattern=FillPattern.Solid,
extent={{-100,100},{100,-100}}), Ellipse(origin={0,0},
fillColor={255,255,255},
fillPattern=FillPattern.Solid,
extent={{-100,100},{100,-100}}), Polygon(origin={21,1},
fillColor={0,128,0},
fillPattern=FillPattern.Solid,
points={{-77,81},{79,-1},{-79,-81},{-77,81}})}),Documentation(info="<html><p>
运行步骤：
</p>
<p>
<br>
</p>
<p>
（1）需要在Syslab里安装依赖，具体方式为：
</p>
<p>
在命令行输入\"]\"进入pkg模式，之后依次输入
</p>
<p>
add ONNXRunTime
</p>
<p>
add Images
</p>
<p>
add Luxor
</p>
<p>
add Colors
</p>
<p>
（1）关闭Syslab，打开Sysplorer。
</p>
<p>
需要更改下方两个Syslab函数中的项目所在路径，具体方式
</p>
<p>
为右键菜单栏&gt;&gt;编辑Syslab函数脚本&gt;&gt;找到变量g_abspath =
</p>
<p>
 \"C:\\\\Users\\\\GlowTube\\\\Documents\\\\MWORKS\\\\SmartDrone\"，
</p>
<p>
然后将其改为目前的路径。
</p>
<p>
（3）仿真成功后，输出结果在文件夹SmartDrone\\data\\output中
</p>
</html>"));
  package ImportedTypes
    model SyslabFunction1
      "julia function"
      annotation (__MWorks(SyslabFunction(Type = "function",AllFuncNames="channel",Duplicated=true,BlockPort(in_pos(Scope=Input,Type=0,Dims={3},Value=1,Desc=""),out_image_number(Scope=Output,Type=1,Dims={-1},Value=1,Desc=""),out_pos(Scope=Output,Type=0,Dims={3},Value=1,Desc=""),out_SNR(Scope=Output,Type=0,Dims={-1},Value=1,Desc=""),out_transmissionTime_s(Scope=Output,Type=0,Dims={-1},Value=1,Desc="")))),
        Diagram(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
          grid = {2.0, 2.0})),
        Icon(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2}),graphics = {Text(origin={0,130},
lineColor={0,0,255},
extent={{-150,20},{150,-20}},
textString="%name",
textColor={0,0,255}), Bitmap(origin={0,0},
extent={{-100,-100},{100,100}},
fileName="modelica://SyslabWorkspace/Resources/Images/FunctionAPI.svg")}));

      import Modelica;
      import SyslabWorkspace.Communication;
      extends SyslabWorkspace.Communication.SyslabSampleBase;

      Communication.SyslabFunctionBase base(funcName="channel",scriptText="base64=ZnVuY3Rpb24gY2hhbm5lbChwb3MpCgogICAgeDA9MDsj5aGU5Y+w5Z2Q5qCHCiAgICB5MD0wOwogICAgejA9MDsKCiAgICBiYW5kd2lkdGg9MjBlNiAgICMg5L+h6YGT5bim5a6977yM5Y2V5L2N6LWr5YW5CiAgICBzaWduYWxQb3dlcj0wLjEgICAjIOS/oeWPt+WKn+eOh++8jOWNleS9jeeTpueJuQogICAgbm9pc2VQb3dlcj0xZS04ICAgIyDlmarlo7Dlip/njofvvIzljZXkvY3nk6bnibkKICAgIGxvc3M9MTsgICAgICAgICAgICAgIyDmjZ/ogJfns7vmlbAKICAgIE4gPSAxMDAwICAgICAgICAgICAjIOmHh+agt+eCueaVsAogICAgdCA9IHJhbmdlKDAsIDEvYmFuZHdpZHRoLCBOKSAgIyDml7bpl7TlkJHph48KCgogICAgIzEu5qih5ouf5Zu+54mH6YeH6ZuGCiAgICBpbWFnZV9udW1iZXIgPSByYW5kKDE6MTApCiAgICBnX2Fic3BhdGggPSAiQzpcXFVzZXJzXFxHbG93VHViZVxcRG9jdW1lbnRzXFxNV09SS1NcXFNtYXJ0RHJvbmUiCiAgICBmaWxlcGF0aCA9IGdfYWJzcGF0aCAqICIvZGF0YS9pbnB1dC8iICogc3RyaW5nKGltYWdlX251bWJlcikgKiIuanBnIgogICAgaW1hZ2VTaXplX2JpdHMgPSA4KmZpbGVzaXplKGZpbGVwYXRoKSAgI+ivu+WPluWbvueJh+Wkp+WwjwoKICAgICMyLuiuoeeul+S8oOi+k+i3neemu++8jOWNleS9jeexswogICAgZGlzdGFuY2VfbT1zcXJ0KChwb3NbMV0gLSB4MCleMiArIChwb3NbMl0gLSB5MCleMiArIChwb3NbM10gLSB6MCleMikKCiAgICAjMy7kv6Hlj7flv6voobDokL3mqKHmi58KICAgIHNpZ25hbCA9IHNxcnQoc2lnbmFsUG93ZXIpICogZXhwLigxaW0gKiAyICogcGkgKiBiYW5kd2lkdGggKiB0KSAj55Sf5oiQ5L+h5Y+3CiAgICBJID0gcmFuZG4oTikjIOeUn+aIkOS4pOS4queLrOeri+eahOmrmOaWr+maj+acuui/h+eoi++8jOWIhuWIq+WvueW6lEnlkoxR5YiG6YePCiAgICBRID0gcmFuZG4oTikKICAgIEggPSBzcXJ0KDAuNSkgKiAoSSArIDFpbSAqIFEpICMg6K6h566X55Ge5Yip6KGw6JC95L+h6YGT55qE5ZON5bqUCiAgICBmYWRlZF9zaWduYWwgPSBzaWduYWwgLiogSCAgICAjIOS/oeWPt+mAmui/h+eRnuWIqeihsOiQveS/oemBkwogICAgbm9pc2UgPSBzcXJ0KG5vaXNlUG93ZXIgLyAyKSAqIChyYW5kbihOKSArIDFpbSAqIHJhbmRuKE4pKSAjQVdHTgogICAgcmVjZWl2ZWRfc2lnbmFsID0gZmFkZWRfc2lnbmFsICsgbm9pc2UgI+a3u+WKoOWZquWjsAoKICAgICM0Luiuoeeul+S/oeWZquavlAogICAgc2lnbmFsUG93ZXJfZmFkZWQgPSBzdW0oYWJzMi4oZmFkZWRfc2lnbmFsKSkgLyBOICAj6KGw6JC95ZCO55qE5L+h5Y+35Yqf546HCiAgICBwYXRoTG9zc19kQiA9IDEwICogbG9zcyAqIGxvZzEwKGRpc3RhbmNlX20pICsgMzAgICMg6Lev5b6E5o2f6ICX6K6h566XCgogICAgU05SID0gMTAgKiBsb2cxMChzaWduYWxQb3dlcl9mYWRlZCAvIG5vaXNlUG93ZXIpLXBhdGhMb3NzX2RCCiAgIAoKICAgICM1LuS/oemBk+WuuemHj+iuoeeul++8iOmmmeWGnOWFrOW8j++8iQogICAgY2hhbm5lbENhcGFjaXR5X2JwcyA9IGJhbmR3aWR0aCAqIGxvZygxICsgMTBeKChTTlIgLyAxMCkpIC8gbG9nKDIpKQoKICAgICM2LuS8oOi+k+aXtumXtOiuoeeulwogICAgdHJhbnNtaXNzaW9uVGltZV9zID0gaW1hZ2VTaXplX2JpdHMgLyBjaGFubmVsQ2FwYWNpdHlfYnBzCgogICAgcmV0dXJuIGltYWdlX251bWJlciwgcG9zLCBTTlIsIHRyYW5zbWlzc2lvblRpbWVfcwogICAgCmVuZA=="
                                                                                                                                                                                                                                                                                                                                                      ,startTime=startTime,period=period,inputDims={{3}},inputTypes={0},outputDims={{-1}, {3}, {-1}, {-1}},outputTypes={1, 0, 0, 0},outputNames={"out_image_number", "out_pos", "out_SNR", "out_transmissionTime_s"},hasInput=true,hasOutput=true)  annotation ( Placement ( transformation ( extent = { { -10.0 , -10.0 } , { 10.0 , 10.0 } } , origin = { 0.0 , 0.0 } ) ) ) ;
      Modelica.Blocks.Interfaces.RealInput in_pos[3] 
      annotation(Placement(transformation(origin={-110,0},
      extent={{-10.0,-10.0},{10.0,10.0}})));
      ArrayConverter._A2V_1D_Real in_pos_converter(dims = {3}) 
      annotation(HideResult=true,Placement(transformation(origin={-80,0},
      extent={{-10.0,-10.0},{10.0,10.0}})));
      Modelica.Blocks.Interfaces.IntegerOutput out_image_number 
      annotation(Placement(transformation(origin={110,67},
      extent={{-10.0,-10.0},{10.0,10.0}})));
      ArrayConverter._V2A_1D_Integer out_image_number_converter(dims = {1}) 
      annotation(HideResult=true,Placement(transformation(origin={80,67},
      extent={{-10.0,-10.0},{10.0,10.0}})));
      Modelica.Blocks.Interfaces.RealOutput out_pos[3] 
      annotation(Placement(transformation(origin={110,22},
      extent={{-10.0,-10.0},{10.0,10.0}})));
      ArrayConverter._V2A_1D_Real out_pos_converter(dims = {3}) 
      annotation(HideResult=true,Placement(transformation(origin={80,22},
      extent={{-10.0,-10.0},{10.0,10.0}})));
      Modelica.Blocks.Interfaces.RealOutput out_SNR 
      annotation(Placement(transformation(origin={110,-22},
      extent={{-10.0,-10.0},{10.0,10.0}})));
      ArrayConverter._V2A_1D_Real out_SNR_converter(dims = {1}) 
      annotation(HideResult=true,Placement(transformation(origin={80,-22},
      extent={{-10.0,-10.0},{10.0,10.0}})));
      Modelica.Blocks.Interfaces.RealOutput out_transmissionTime_s 
      annotation(Placement(transformation(origin={110,-67},
      extent={{-10.0,-10.0},{10.0,10.0}})));
      ArrayConverter._V2A_1D_Real out_transmissionTime_s_converter(dims = {1}) 
      annotation(HideResult=true,Placement(transformation(origin={80,-67},
      extent={{-10.0,-10.0},{10.0,10.0}})));
      equation
      connect(in_pos, in_pos_converter.u) 
      annotation (Line(origin = {-95, 0},
              points = {{-15, 0}, {0, 0}, {0, 0}, {15, 0}},
              color = {255, 127, 0}));
      connect(in_pos_converter.y, base.inputs[1:3]) 
      annotation (Line(origin = {-44, 32},
              points = {{-36, -32}, {0, -32}, {0, 33}, {36, 33}},
              color = {255, 127, 0}));
      connect(out_image_number, out_image_number_converter.y[1]) 
      annotation (Line(origin = {95, 67},
              points = {{15, 0}, {0, 0}, {0, 0}, {-15, 0}},
              color = {255, 127, 0}));
      connect(out_image_number_converter.u[1], base.outputs[1]) 
      annotation (Line(origin = {36, 66},
              points = {{44, 1}, {0, 1}, {0, -1}, {-44, -1}},
              color = {255, 127, 0}));
      connect(out_pos, out_pos_converter.y) 
      annotation (Line(origin = {95, 22},
              points = {{15, 0}, {0, 0}, {0, 0}, {-15, 0}},
              color = {255, 127, 0}));
      connect(out_pos_converter.u, base.outputs[2:4]) 
      annotation (Line(origin = {36, 43},
              points = {{44, -21}, {0, -21}, {0, 22}, {-44, 22}},
              color = {255, 127, 0}));
      connect(out_SNR, out_SNR_converter.y[1]) 
      annotation (Line(origin = {95, -22},
              points = {{15, 0}, {0, 0}, {0, 0}, {-15, 0}},
              color = {255, 127, 0}));
      connect(out_SNR_converter.u[1], base.outputs[5]) 
      annotation (Line(origin = {36, 21},
              points = {{44, -43}, {0, -43}, {0, 44}, {-44, 44}},
              color = {255, 127, 0}));
      connect(out_transmissionTime_s, out_transmissionTime_s_converter.y[1]) 
      annotation (Line(origin = {95, -67},
              points = {{15, 0}, {0, 0}, {0, 0}, {-15, 0}},
              color = {255, 127, 0}));
      connect(out_transmissionTime_s_converter.u[1], base.outputs[6]) 
      annotation (Line(origin = {36, -1},
              points = {{44, -66}, {0, -66}, {0, 66}, {-44, 66}},
              color = {255, 127, 0}));
      end SyslabFunction1;
    model SyslabFunction2
      "julia function"
      annotation (__MWorks(SyslabFunction(Type = "function",AllFuncNames="imagehandle,addnoise,get_input_array,run_inference,process_output,yolobox,compute_iou,merge_overlapping_boxes",Duplicated=true,BlockPort(in_index(Scope=Input,Type=1,Dims={-1},Value=1,Desc=""),in_position(Scope=Input,Type=0,Dims={3},Value=1,Desc=""),in_SNR(Scope=Input,Type=0,Dims={-1},Value=1,Desc=""),in_delay(Scope=Input,Type=0,Dims={-1},Value=1,Desc=""),out_res(Scope=Output,Type=0,Dims={-1},Value=1,Desc="")))),
        Diagram(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
          grid = {2.0, 2.0})),
        Icon(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2}),graphics = {Text(origin={0,130},
lineColor={0,0,255},
extent={{-150,20},{150,-20}},
textString="%name",
textColor={0,0,255}), Bitmap(origin={0,0},
extent={{-100,-100},{100,100}},
fileName="modelica://SyslabWorkspace/Resources/Images/FunctionAPI.svg")}));

      import Modelica;
      import SyslabWorkspace.Communication;
      extends SyslabWorkspace.Communication.SyslabSampleBase;

      Communication.SyslabFunctionBase base(funcName="imagehandle",scriptText="base64=ZnVuY3Rpb24gaW1hZ2VoYW5kbGUoaW5kZXgsIHBvc2l0aW9uLCBTTlIsIGRlbGF5KQogICAgIyDlm77niYflrZjlgqjkvY3nva4KICAgIGZpbGUgPSBnX2Fic3BhdGgqIi9kYXRhL2lucHV0LyIgKiBzdHJpbmcoaW5kZXgpKiIuanBnIgogICAgaW1nID0gbG9hZChmaWxlKQogICAgaW1nX29yaWdpbiA9IGltZwogICAgb3V0cHV0X3BhdGggPSBnX2Fic3BhdGgqIi9kYXRhL291dHB1dC9wcmVkLnBuZyIKCiAgICAjIOa3u+WKoOmrmOaWr+WZquWjsAogICAgaW1nID0gYWRkbm9pc2UoaW1nLCBTTlIpCgogICAgIyDov5DooYzmjqjnkIblkozlpITnkIbovpPlh7oKICAgIHJlcyA9IHJ1bl9pbmZlcmVuY2UoaW1nKQogICAgYm94ZXMsIGNsYXNzX2lkcyA9IHByb2Nlc3Nfb3V0cHV0KHJlcykKCiAgICAjIOWwhuajgOa1i+ahhui9rOaNouS4uuWdkOagh+agvOW8jwogICAgYm94ZXNfeHl4eSA9IFt5b2xvYm94KGJveFsxXSwgYm94WzJdLCBib3hbM10sIGJveFs0XSkgZm9yIGJveCBpbiBlYWNocm93KGJveGVzKV0KCiAgICAjIOWQiOW5tumHjeWPoOeahOS6uueJqeaWueahhgogICAgbWVyZ2VkX2JveGVzLCBtZXJnZWRfY2xhc3NlcyA9IG1lcmdlX292ZXJsYXBwaW5nX2JveGVzKGJveGVzX3h5eHksIGNsYXNzX2lkcykKCiAgICAjIOmihOWkhOeQhuWbvuWDj+WSjOaWh+S7tuS/neWtmOi3r+W+hAogICAgaW1nID0gaW1yZXNpemUoaW1nLCA2NDAsIDY0MCkKICAgIGltZ19vcmlnaW4gPSBpbXJlc2l6ZShpbWdfb3JpZ2luLCA2NDAsIDY0MCkKICAgIGltZ193aWR0aCwgaW1nX2hlaWdodCA9IHNpemUoaW1nKQoKICAgICMg5pig5bCE5qih5Z6L5ZKM57Si5byVCiAgICBuYW1lcyA9IERpY3QoCiAgICAgICAgMCA9PiAicGVyc29uIiwKICAgICAgICAxID0+ICJiaWN5Y2xlIiwKICAgICAgICAyID0+ICJjYXIiLAogICAgICAgIDMgPT4gIm1vdG9yY3ljbGUiLAogICAgICAgIDQgPT4gImFpcnBsYW5lIiwKICAgICAgICA1ID0+ICJidXMiLAogICAgICAgIDYgPT4gInRyYWluIiwKICAgICAgICA3ID0+ICJ0cnVjayIsCiAgICAgICAgOCA9PiAiYm9hdCIsCiAgICAgICAgOSA9PiAidHJhZmZpYyBsaWdodCIsCiAgICAgICAgMTAgPT4gImZpcmUgaHlkcmFudCIsCiAgICAgICAgMTEgPT4gInN0b3Agc2lnbiIsCiAgICAgICAgMTIgPT4gInBhcmtpbmcgbWV0ZXIiLAogICAgICAgIDEzID0+ICJiZW5jaCIsCiAgICAgICAgMTQgPT4gImJpcmQiLAogICAgICAgIDE1ID0+ICJjYXQiLAogICAgICAgIDE2ID0+ICJkb2ciLAogICAgICAgIDE3ID0+ICJob3JzZSIsCiAgICAgICAgMTggPT4gInNoZWVwIiwKICAgICAgICAxOSA9PiAiY293IiwKICAgICAgICAyMCA9PiAiZWxlcGhhbnQiLAogICAgICAgIDIxID0+ICJiZWFyIiwKICAgICAgICAyMiA9PiAiemVicmEiLAogICAgICAgIDIzID0+ICJnaXJhZmZlIiwKICAgICAgICAyNCA9PiAiYmFja3BhY2siLAogICAgICAgIDI1ID0+ICJ1bWJyZWxsYSIsCiAgICAgICAgMjYgPT4gImhhbmRiYWciLAogICAgICAgIDI3ID0+ICJ0aWUiLAogICAgICAgIDI4ID0+ICJzdWl0Y2FzZSIsCiAgICAgICAgMjkgPT4gImZyaXNiZWUiLAogICAgICAgIDMwID0+ICJza2lzIiwKICAgICAgICAzMSA9PiAic25vd2JvYXJkIiwKICAgICAgICAzMiA9PiAic3BvcnRzIGJhbGwiLAogICAgICAgIDMzID0+ICJraXRlIiwKICAgICAgICAzNCA9PiAiYmFzZWJhbGwgYmF0IiwKICAgICAgICAzNSA9PiAiYmFzZWJhbGwgZ2xvdmUiLAogICAgICAgIDM2ID0+ICJza2F0ZWJvYXJkIiwKICAgICAgICAzNyA9PiAic3VyZmJvYXJkIiwKICAgICAgICAzOCA9PiAidGVubmlzIHJhY2tldCIsCiAgICAgICAgMzkgPT4gImJvdHRsZSIsCiAgICAgICAgNDAgPT4gIndpbmUgZ2xhc3MiLAogICAgICAgIDQxID0+ICJjdXAiLAogICAgICAgIDQyID0+ICJmb3JrIiwKICAgICAgICA0MyA9PiAia25pZmUiLAogICAgICAgIDQ0ID0+ICJzcG9vbiIsCiAgICAgICAgNDUgPT4gImJvd2wiLAogICAgICAgIDQ2ID0+ICJiYW5hbmEiLAogICAgICAgIDQ3ID0+ICJhcHBsZSIsCiAgICAgICAgNDggPT4gInNhbmR3aWNoIiwKICAgICAgICA0OSA9PiAib3JhbmdlIiwKICAgICAgICA1MCA9PiAiYnJvY2NvbGkiLAogICAgICAgIDUxID0+ICJjYXJyb3QiLAogICAgICAgIDUyID0+ICJob3QgZG9nIiwKICAgICAgICA1MyA9PiAicGl6emEiLAogICAgICAgIDU0ID0+ICJkb251dCIsCiAgICAgICAgNTUgPT4gImNha2UiLAogICAgICAgIDU2ID0+ICJjaGFpciIsCiAgICAgICAgNTcgPT4gImNvdWNoIiwKICAgICAgICA1OCA9PiAicG90dGVkIHBsYW50IiwKICAgICAgICA1OSA9PiAiYmVkIiwKICAgICAgICA2MCA9PiAiZGluaW5nIHRhYmxlIiwKICAgICAgICA2MSA9PiAidG9pbGV0IiwKICAgICAgICA2MiA9PiAidHYiLAogICAgICAgIDYzID0+ICJsYXB0b3AiLAogICAgICAgIDY0ID0+ICJtb3VzZSIsCiAgICAgICAgNjUgPT4gInJlbW90ZSIsCiAgICAgICAgNjYgPT4gImtleWJvYXJkIiwKICAgICAgICA2NyA9PiAiY2VsbCBwaG9uZSIsCiAgICAgICAgNjggPT4gIm1pY3Jvd2F2ZSIsCiAgICAgICAgNjkgPT4gIm92ZW4iLAogICAgICAgIDcwID0+ICJ0b2FzdGVyIiwKICAgICAgICA3MSA9PiAic2luayIsCiAgICAgICAgNzIgPT4gInJlZnJpZ2VyYXRvciIsCiAgICAgICAgNzMgPT4gImJvb2siLAogICAgICAgIDc0ID0+ICJjbG9jayIsCiAgICAgICAgNzUgPT4gInZhc2UiLAogICAgICAgIDc2ID0+ICJzY2lzc29ycyIsCiAgICAgICAgNzcgPT4gInRlZGR5IGJlYXIiLAogICAgICAgIDc4ID0+ICJoYWlyIGRyaWVyIiwKICAgICAgICA3OSA9PiAidG9vdGhicnVzaCIKICAgICkKCiAgICAjIOWIm+W7uuS4gOS4quaWsOeahOe7mOWbvueOr+WigwogICAgRHJhd2luZygxNDAwLCA4MDAsIG91dHB1dF9wYXRoKQoKICAgICMg5bCG5Yqg6L2955qE5Zu+5YOP6K6+572u5Li66IOM5pmvCiAgICBiYWNrZ3JvdW5kKCJ3aGl0ZSIpCiAgICBwbGFjZWltYWdlKGltZywgTHV4b3IuUG9pbnQoNzIwLCAxMDApKQogICAgcGxhY2VpbWFnZShpbWdfb3JpZ2luLCBMdXhvci5Qb2ludCg1MCwgMTAwKSkKCiAgICAjIOiuvue9ruWtl+S9k+WSjOaWueahhueyl+e7hgogICAgc2V0Zm9udCgiQXJpYWwiLCA4OCkgICMg56Gu5L+d5L2/55So5q2j56Gu55qE5a2X5L2T5ZCN56ewCiAgICBmb250c2l6ZSgyMCkKICAgIHNldGxpbmUoMikKCiAgICAjIOmAkOS4que7mOWItuWQiOW5tuWQjueahOaWueahhuWSjOagh+etvgogICAgZm9yIChpLCBib3gpIGluIGVudW1lcmF0ZShtZXJnZWRfYm94ZXMpCiAgICAgICAgY2xhc3NfaWQgPSBtZXJnZWRfY2xhc3Nlc1tpXQogICAgICAgICMg5bCG57G75Yir6L2s5Li65a2X56ym5LiyCiAgICAgICAgbGFiZWxfdGV4dCA9IHN0cmluZyhjbGFzc19pZCkKICAgICAgICAjIOagueaNruexu+WIq+iuvue9ruminOiJsgogICAgICAgIHNldGh1ZShjbGFzc19pZCA9PSAxID8gInJlZCIgOiAiYmx1ZSIpCiAgICAgICAgIyDnu5jliLbnn6nlvaIKICAgICAgICByZWN0KGJveFsxXSArIDcyMCwgYm94WzJdICsgMTAwLCBib3hbM10gLSBib3hbMV0sIGJveFs0XSAtIGJveFsyXSwgOnN0cm9rZSkKICAgICAgICBsYWJlbF90ZXh0ID0gbmFtZXNbY2xhc3NfaWQtMV0gICMg5Yib5bu65qCH562+5paH5pysCiAgICAgICAgIyDlnKjnn6nlvaLkuIrmlrnnu5jliLbmlofmnKwKICAgICAgICB0ZXh0KGxhYmVsX3RleHQsIChib3hbM10gLSBib3hbMV0gLSBsZW5ndGgobGFiZWxfdGV4dCkgKiAxMCkgLyAyICsgYm94WzFdICsgNzIwLCBib3hbMl0gKyAxMDApCiAgICBlbmQKCiAgICAjIOe7mOWItuW7tuaXtiByb3VuZChwWzFdOyBkaWdpdHM9MykKICAgIGZvbnRzaXplKDMwKQogICAgc2V0aHVlKCJibGFjayIpCiAgICBkZWxheV90ZXh0ID0gIkRlbGF5OiAiICogc3RyaW5nKHJvdW5kKGRlbGF5KjEwMDAsIGRpZ2l0cz0zKSkgKiAiIG1zIgogICAgZGVzdGluYXRpb25fdGV4dCA9ICJEZXN0aW5hdGlvbjogIiAqICJ4LSIgKiBzdHJpbmcocm91bmQocG9zaXRpb25bMV07IGRpZ2l0cz0xKSkqIiB5LSIqIHN0cmluZyhyb3VuZChwb3NpdGlvblsyXTsgZGlnaXRzPTEpKSogIiB6LSIqc3RyaW5nKHJvdW5kKHBvc2l0aW9uWzNdOyBkaWdpdHM9MSkpICoibSIKICAgIFNOUl90ZXh0ID0gIlNOUjogIiAqIHN0cmluZyhyb3VuZChTTlI7IGRpZ2l0cz0yKSApICogIiBkQiIKICAgIHJlc190ZXh0ID0gIkdyb3VuZCByZWNlcHRpb24gYW5kIHJlY29nbml0aW9uIHJlc3VsdHM6ICIKICAgIHRleHQoZGVzdGluYXRpb25fdGV4dCwgNTAsIDUwKQogICAgdGV4dChTTlJfdGV4dCwgNTAsIDkwKQogICAgdGV4dChkZWxheV90ZXh0LCA3MjAsIDUwKQogICAgdGV4dChyZXNfdGV4dCwgNzIwLCA5MCkKCiAgICAjIOS/neWtmOe7k+aenOWbvuWDjwogICAgcmVzID0gZmluaXNoKCkKICAgIHJldHVybiByZXMKZW5kCgpmdW5jdGlvbiBhZGRub2lzZShpbWcsIFNOUikKICAgICMg5Zmq5aOw5by65bqm57q/5oCn6L2s5YyWCiAgICBub2lzZV9sZXZlbCA9IDAuNSAqIGVyZmMoU05SIC8gMjUpCgogICAgIyDlsIblm77lg4/ovazmjaLkuLrmta7ngrnmlbDnu4QKICAgIGltZ19mbG9hdCA9IEZsb2F0NjQuKGNoYW5uZWx2aWV3KGltZykpCgogICAgIyDmt7vliqDpq5jmlq/lmarlo7AKICAgIG5vaXN5X2ltZ19mbG9hdCA9IGltZ19mbG9hdCArIG5vaXNlX2xldmVsIC4qIHJhbmRuKHNpemUoaW1nX2Zsb2F0KSkKCiAgICAjIOijgeWJquWAvOWIsFswLDFd6IyD5Zu0CiAgICBub2lzeV9pbWdfZmxvYXQgPSBjbGFtcC4obm9pc3lfaW1nX2Zsb2F0LCAwLCAxKQoKICAgICMg6L2s5Zue5Zu+54mH5qC85byPCiAgICBub2lzeV9pbWcgPSBjb2xvcnZpZXcoUkdCLCBub2lzeV9pbWdfZmxvYXQpCiAgICAKICAgIHJldHVybiBub2lzeV9pbWcKZW5kCgpmdW5jdGlvbiBnZXRfaW5wdXRfYXJyYXkoaW1nKQogICAgcmVzaXplZCA9IGltcmVzaXplKGltZywgKDY0MCwgNjQwKSkKICAgIG1hdCA9IGNoYW5uZWx2aWV3KHJlc2l6ZWQpCiAgICBvcmlnaW5hbF9hcnJheSA9IEZsb2F0MzIuKG1hdCkKICAgIHJldHVybiByZXNoYXBlKG9yaWdpbmFsX2FycmF5LCAoMSwgc2l6ZShvcmlnaW5hbF9hcnJheSkuLi4pKQplbmQKCiMg5o6o55CG5Ye95pWwCmZ1bmN0aW9uIHJ1bl9pbmZlcmVuY2UoaW1nKQogICAgaW5wdXRfYXJyYXkgPSBnZXRfaW5wdXRfYXJyYXkoaW1nKQogICAgcmVzID0gbW9kZWwoRGljdCgiaW1hZ2VzIiA9PiBpbnB1dF9hcnJheSkpWyJvdXRwdXQwIl0gICMg55+p6Zi16L6T5Ye65Li6IDF4ODR4ODQwMAogICAgcmV0dXJuIHJlcwplbmQKCiMg6L6T5Ye65aSE55CG5Ye95pWw77yM6L+U5Zue5qOA5rWL5qGG5ZKM57G75YirCmZ1bmN0aW9uIHByb2Nlc3Nfb3V0cHV0KHJlcykKICAgIHByZWRpY3Rpb25zID0gdHJhbnNwb3NlKHJlc1sxLCA6LCA6XSkgICMg55+p6Zi16L6T5Ye65Li6ICg4NDAwLCA4NCkKICAgIGNvbmZfdGhyZXNob2xkID0gMC40CiAgICBzY29yZXMgPSBtYXhpbXVtKHByZWRpY3Rpb25zWzosIDU6ZW5kXSwgZGltcz0yKQoKICAgICMg5Z+65LqO572u5L+h5bqm6ZiI5YC86L+H5rukCiAgICBwcmVkaWN0aW9ucyA9IHByZWRpY3Rpb25zW3ZlYyhzY29yZXMgLj4gY29uZl90aHJlc2hvbGQpLCA6XQoKICAgIGNsYXNzX2lkcyA9IGFyZ21heChwcmVkaWN0aW9uc1s6LCA1OmVuZF0sIGRpbXM9MikKICAgIGNsYXNzX2lkcyA9IHZlYyhtYXAoaSAtPiBpWzJdLCBjbGFzc19pZHMpKSAgIyDojrflj5bmr4/kuKrmlrnmoYbnmoTnsbvliKvntKLlvJUKICAgICMgcGVyc29uX2NsYXNzX2luZGV4ID0gMSAgIyDmlbDmja7pm4bkuK3vvIwicGVyc29uIiDnsbvliKvntKLlvJXlgLzkuLogMQogICAgIyBwZXJzb25fcHJlZGljdGlvbnMgPSBwcmVkaWN0aW9uc1tjbGFzc19pZHMgLj09IHBlcnNvbl9jbGFzc19pbmRleCwgOl0KCiAgICBib3hlcyA9IHByZWRpY3Rpb25zWzosIGJlZ2luOjRdICAjIOiOt+WPluaWueahhgogICAgcmV0dXJuIGJveGVzLCBjbGFzc19pZHMgICMg6L+U5Zue5pa55qGG5ZKM57G75YirCmVuZAoKIyDlsIbnn6nlvaLmoYbovazmjaLkuLrlm77lg4/lnZDmoIcKZnVuY3Rpb24geW9sb2JveCh4LCB5LCB3LCBoKQogICAgeDEsIHkxID0geCAtIHcgLyAyLCB5IC0gaCAvIDIKICAgIHgyLCB5MiA9IHggKyB3IC8gMiwgeSArIGggLyAyCiAgICByZXR1cm4gdHJ1bmMuKEludCwgW3gxLCB5MSwgeDIsIHkyXSkKZW5kCgojIOiuoeeul+S6pOW5tuavlCAoSW9VKQpmdW5jdGlvbiBjb21wdXRlX2lvdShib3gxLCBib3gyKQogICAgeDFfbWluLCB5MV9taW4sIHgxX21heCwgeTFfbWF4ID0gYm94MQogICAgeDJfbWluLCB5Ml9taW4sIHgyX21heCwgeTJfbWF4ID0gYm94MgoKICAgIGludGVyX3hfbWluID0gbWF4KHgxX21pbiwgeDJfbWluKQogICAgaW50ZXJfeV9taW4gPSBtYXgoeTFfbWluLCB5Ml9taW4pCiAgICBpbnRlcl94X21heCA9IG1pbih4MV9tYXgsIHgyX21heCkKICAgIGludGVyX3lfbWF4ID0gbWluKHkxX21heCwgeTJfbWF4KQoKICAgIGludGVyX2FyZWEgPSBtYXgoMCwgaW50ZXJfeF9tYXggLSBpbnRlcl94X21pbikgKiBtYXgoMCwgaW50ZXJfeV9tYXggLSBpbnRlcl95X21pbikKCiAgICBib3gxX2FyZWEgPSAoeDFfbWF4IC0geDFfbWluKSAqICh5MV9tYXggLSB5MV9taW4pCiAgICBib3gyX2FyZWEgPSAoeDJfbWF4IC0geDJfbWluKSAqICh5Ml9tYXggLSB5Ml9taW4pCgogICAgdW5pb25fYXJlYSA9IGJveDFfYXJlYSArIGJveDJfYXJlYSAtIGludGVyX2FyZWEKCiAgICByZXR1cm4gaW50ZXJfYXJlYSAvIHVuaW9uX2FyZWEKZW5kCgojIOWQiOW5tumHjeWPoOaWueahhgpmdW5jdGlvbiBtZXJnZV9vdmVybGFwcGluZ19ib3hlcyhib3hlcywgY2xhc3NfaWRzLCBpb3VfdGhyZXNob2xkPTAuNSkKICAgIG1lcmdlZF9ib3hlcyA9IFtdCiAgICBtZXJnZWRfY2xhc3NlcyA9IFtdCgogICAgZm9yIGkgaW4gZWFjaGluZGV4KGJveGVzKQogICAgICAgIGJveCA9IGJveGVzW2ldCiAgICAgICAgY2xhc3NfaWQgPSBjbGFzc19pZHNbaV0KICAgICAgICBvdmVybGFwcGVkID0gZmFsc2UKCiAgICAgICAgZm9yIGogaW4gZWFjaGluZGV4KG1lcmdlZF9ib3hlcykKICAgICAgICAgICAgaWYgY29tcHV0ZV9pb3UobWVyZ2VkX2JveGVzW2pdLCBib3gpID4gaW91X3RocmVzaG9sZAogICAgICAgICAgICAgICAgIyDlpoLmnpzph43lj6DvvIzlkIjlubbkuKTkuKrmlrnmoYYKICAgICAgICAgICAgICAgIG1lcmdlZF9ib3hlc1tqXSA9IFsKICAgICAgICAgICAgICAgICAgICBtaW4obWVyZ2VkX2JveGVzW2pdWzFdLCBib3hbMV0pLCAgIyDlkIjlubYgeF9taW4KICAgICAgICAgICAgICAgICAgICBtaW4obWVyZ2VkX2JveGVzW2pdWzJdLCBib3hbMl0pLCAgIyDlkIjlubYgeV9taW4KICAgICAgICAgICAgICAgICAgICBtYXgobWVyZ2VkX2JveGVzW2pdWzNdLCBib3hbM10pLCAgIyDlkIjlubYgeF9tYXgKICAgICAgICAgICAgICAgICAgICBtYXgobWVyZ2VkX2JveGVzW2pdWzRdLCBib3hbNF0pICAgIyDlkIjlubYgeV9tYXgKICAgICAgICAgICAgICAgIF0KICAgICAgICAgICAgICAgICMg5LiN5pS55Y+Y6YeN5Y+g55qEY2xhc3PvvIzkuI3lho3mrKHmjqjlhaXnsbvmlbDnu4QKICAgICAgICAgICAgICAgIG92ZXJsYXBwZWQgPSB0cnVlCiAgICAgICAgICAgICAgICBicmVhawogICAgICAgICAgICBlbmQKICAgICAgICBlbmQKCiAgICAgICAgaWYgIW92ZXJsYXBwZWQKICAgICAgICAgICAgcHVzaCEobWVyZ2VkX2JveGVzLCBib3gpICAjIOWPquacieS4jemHjeWPoOeahOaDheWGteaJjeWKoOWFpQogICAgICAgICAgICBwdXNoIShtZXJnZWRfY2xhc3NlcywgY2xhc3NfaWQpCiAgICAgICAgZW5kCiAgICBlbmQKCiAgICByZXR1cm4gbWVyZ2VkX2JveGVzLCBtZXJnZWRfY2xhc3NlcwplbmQ="




                                                                                                                                                                                                                                                                                                                                            ,startTime=startTime,period=period,inputDims={{-1}, {3}, {-1}, {-1}},inputTypes={1, 0, 0, 0},outputDims={{-1}},outputTypes={0},outputNames={"out_res"},hasInput=true,hasOutput=true) 
        annotation (Placement(transformation(extent = {{-10.0, -10.0}, {10.0, 10.0}},origin={0.0, 0.0})));
      Modelica.Blocks.Interfaces.IntegerInput in_index 
      annotation(Placement(transformation(origin={-110,67},
      extent={{-10.0,-10.0},{10.0,10.0}})));
      ArrayConverter._A2V_1D_Integer in_index_converter(dims = {1}) 
      annotation(HideResult=true,Placement(transformation(origin={-80,67},
      extent={{-10.0,-10.0},{10.0,10.0}})));
      Modelica.Blocks.Interfaces.RealInput in_position[3] 
      annotation(Placement(transformation(origin={-110,22},
      extent={{-10.0,-10.0},{10.0,10.0}})));
      ArrayConverter._A2V_1D_Real in_position_converter(dims = {3}) 
      annotation(HideResult=true,Placement(transformation(origin={-80,22},
      extent={{-10.0,-10.0},{10.0,10.0}})));
      Modelica.Blocks.Interfaces.RealInput in_SNR 
      annotation(Placement(transformation(origin={-110,-22},
      extent={{-10.0,-10.0},{10.0,10.0}})));
      ArrayConverter._A2V_1D_Real in_SNR_converter(dims = {1}) 
      annotation(HideResult=true,Placement(transformation(origin={-80,-22},
      extent={{-10.0,-10.0},{10.0,10.0}})));
      Modelica.Blocks.Interfaces.RealInput in_delay 
      annotation(Placement(transformation(origin={-110,-67},
      extent={{-10.0,-10.0},{10.0,10.0}})));
      ArrayConverter._A2V_1D_Real in_delay_converter(dims = {1}) 
      annotation(HideResult=true,Placement(transformation(origin={-80,-67},
      extent={{-10.0,-10.0},{10.0,10.0}})));
      Modelica.Blocks.Interfaces.RealOutput out_res 
      annotation(Placement(transformation(origin={110,0},
      extent={{-10.0,-10.0},{10.0,10.0}})));
      ArrayConverter._V2A_1D_Real out_res_converter(dims = {1}) 
      annotation(HideResult=true,Placement(transformation(origin={80,0},
      extent={{-10.0,-10.0},{10.0,10.0}})));
      equation
      connect(in_index, in_index_converter.u[1]) 
      annotation (Line(origin = {-95, 67},
              points = {{-15, 0}, {0, 0}, {0, 0}, {15, 0}},
              color = {255, 127, 0}));
      connect(in_index_converter.y[1], base.inputs[1]) 
      annotation (Line(origin = {-44, 66},
              points = {{-36, 1}, {0, 1}, {0, -1}, {36, -1}},
              color = {255, 127, 0}));
      connect(in_position, in_position_converter.u) 
      annotation (Line(origin = {-95, 22},
              points = {{-15, 0}, {0, 0}, {0, 0}, {15, 0}},
              color = {255, 127, 0}));
      connect(in_position_converter.y, base.inputs[2:4]) 
      annotation (Line(origin = {-44, 43},
              points = {{-36, -21}, {0, -21}, {0, 22}, {36, 22}},
              color = {255, 127, 0}));
      connect(in_SNR, in_SNR_converter.u[1]) 
      annotation (Line(origin = {-95, -22},
              points = {{-15, 0}, {0, 0}, {0, 0}, {15, 0}},
              color = {255, 127, 0}));
      connect(in_SNR_converter.y[1], base.inputs[5]) 
      annotation (Line(origin = {-44, 21},
              points = {{-36, -43}, {0, -43}, {0, 44}, {36, 44}},
              color = {255, 127, 0}));
      connect(in_delay, in_delay_converter.u[1]) 
      annotation (Line(origin = {-95, -67},
              points = {{-15, 0}, {0, 0}, {0, 0}, {15, 0}},
              color = {255, 127, 0}));
      connect(in_delay_converter.y[1], base.inputs[6]) 
      annotation (Line(origin = {-44, -1},
              points = {{-36, -66}, {0, -66}, {0, 66}, {36, 66}},
              color = {255, 127, 0}));
      connect(out_res, out_res_converter.y[1]) 
      annotation (Line(origin = {95, 0},
              points = {{15, 0}, {0, 0}, {0, 0}, {-15, 0}},
              color = {255, 127, 0}));
      connect(out_res_converter.u[1], base.outputs[1]) 
      annotation (Line(origin = {36, 32},
              points = {{44, -32}, {0, -32}, {0, 33}, {-44, 33}},
              color = {255, 127, 0}));
      end SyslabFunction2;
    package ArrayConverter
      model _A2V_1D_Real
      "1 dimension Real array to Real vector"
        annotation(Diagram(coordinateSystem(extent={{-100.0,-100.0},{100.0,100.0}},preserveAspectRatio=false,grid={2.0,2.0})),
                          Icon(coordinateSystem(preserveAspectRatio = false, extent = { {-100, -100}, {100, 100} }), graphics = {
                            Rectangle(
                            lineColor = {200, 200, 200},
                            fillColor = {248, 248, 248},
                            fillPattern = FillPattern.HorizontalCylinder,
                            extent = {{-100.0, -100.0}, {100.0, 100.0}},
                            radius = 25.0),
                            Rectangle(
                            lineColor = {128, 128, 128},
                            extent = {{-100.0, -100.0}, {100.0, 100.0}},
                            radius = 25.0), Polygon(origin = {20.0, 0.0},
                            lineColor = {64, 64, 64},
                            fillColor = {255, 255, 255},
                            fillPattern = FillPattern.Solid,
                            points = {{-10.0, 70.0}, {10.0, 70.0}, {40.0, 20.0}, {80.0, 20.0}, {80.0, -20.0}, {40.0, -20.0}, {10.0, -70.0}, {-10.0, -70.0}}),
                            Polygon(fillColor = {102, 102, 102},
                            pattern = LinePattern.None,
                            fillPattern = FillPattern.Solid,
                            points = {{-100.0, 20.0}, {-60.0, 20.0}, {-30.0, 70.0}, {-10.0, 70.0}, {-10.0, -70.0}, {-30.0, -70.0}, {-60.0, -20.0}, {-100.0, -20.0}}) }));
        import Modelica;
        parameter Integer dims[1] = {2};
        Modelica.Blocks.Interfaces.RealInput u[dims[1]] 
          annotation(Placement(transformation(origin ={-120.0,0.0},extent ={{-20.0,-20.0}, {20.0, 20.0}})));
        Modelica.Blocks.Interfaces.RealOutput y[product(dims)] 
          annotation(Placement(transformation(origin={110.0,0.0},extent={{-10.0,-10.0},{10.0,10.0}})));
      protected
        Integer pos;
      algorithm
        pos := 1;
        for i1 in 1:dims[1] loop
          y[pos] := u[i1];
          pos := pos + 1;
        end for;
      end _A2V_1D_Real;
      model _V2A_1D_Real
      "Real vector to 1 dimension Real array"
        annotation(Diagram(coordinateSystem(extent={{-100.0,-100.0},{100.0,100.0}},preserveAspectRatio=false,grid={2.0,2.0})),
                          Icon(coordinateSystem(preserveAspectRatio = false, extent = { {-100, -100}, {100, 100} }), graphics = {
                            Rectangle(
                            lineColor = {200, 200, 200},
                            fillColor = {248, 248, 248},
                            fillPattern = FillPattern.HorizontalCylinder,
                            extent = {{-100.0, -100.0}, {100.0, 100.0}},
                            radius = 25.0),
                            Rectangle(
                            lineColor = {128, 128, 128},
                            extent = {{-100.0, -100.0}, {100.0, 100.0}},
                            radius = 25.0), Polygon(origin = {20.0, 0.0},
                            lineColor = {64, 64, 64},
                            fillColor = {255, 255, 255},
                            fillPattern = FillPattern.Solid,
                            points = {{-10.0, 70.0}, {10.0, 70.0}, {40.0, 20.0}, {80.0, 20.0}, {80.0, -20.0}, {40.0, -20.0}, {10.0, -70.0}, {-10.0, -70.0}}),
                            Polygon(fillColor = {102, 102, 102},
                            pattern = LinePattern.None,
                            fillPattern = FillPattern.Solid,
                            points = {{-100.0, 20.0}, {-60.0, 20.0}, {-30.0, 70.0}, {-10.0, 70.0}, {-10.0, -70.0}, {-30.0, -70.0}, {-60.0, -20.0}, {-100.0, -20.0}}) }));
        import Modelica;
        parameter Integer dims[1] = {2};
        Modelica.Blocks.Interfaces.RealInput u[product(dims)] 
        annotation(Placement(transformation(origin ={-120.0,0.0},extent ={{-20.0,-20.0}, {20.0, 20.0}})));
        Modelica.Blocks.Interfaces.RealOutput y[dims[1]] 
        annotation(Placement(transformation(origin={110.0,0.0},extent={{-10.0,-10.0},{10.0,10.0}})));
      protected
        Integer pos;
      algorithm
        pos := 1;
        for i1 in 1:dims[1] loop
          y[i1] := u[pos];
          pos := pos + 1;
        end for;
      end _V2A_1D_Real;
      model _V2A_1D_Integer
      "Real vector to 1 dimension Integer array"
        annotation(Diagram(coordinateSystem(extent={{-100.0,-100.0},{100.0,100.0}},preserveAspectRatio=false,grid={2.0,2.0})),
                          Icon(coordinateSystem(preserveAspectRatio = false, extent = { {-100, -100}, {100, 100} }), graphics = {
                            Rectangle(
                            lineColor = {200, 200, 200},
                            fillColor = {248, 248, 248},
                            fillPattern = FillPattern.HorizontalCylinder,
                            extent = {{-100.0, -100.0}, {100.0, 100.0}},
                            radius = 25.0),
                            Rectangle(
                            lineColor = {128, 128, 128},
                            extent = {{-100.0, -100.0}, {100.0, 100.0}},
                            radius = 25.0), Polygon(origin = {20.0, 0.0},
                            lineColor = {64, 64, 64},
                            fillColor = {255, 255, 255},
                            fillPattern = FillPattern.Solid,
                            points = {{-10.0, 70.0}, {10.0, 70.0}, {40.0, 20.0}, {80.0, 20.0}, {80.0, -20.0}, {40.0, -20.0}, {10.0, -70.0}, {-10.0, -70.0}}),
                            Polygon(fillColor = {102, 102, 102},
                            pattern = LinePattern.None,
                            fillPattern = FillPattern.Solid,
                            points = {{-100.0, 20.0}, {-60.0, 20.0}, {-30.0, 70.0}, {-10.0, 70.0}, {-10.0, -70.0}, {-30.0, -70.0}, {-60.0, -20.0}, {-100.0, -20.0}}) }));
        import Modelica;
        parameter Integer dims[1] = {2};
        Modelica.Blocks.Interfaces.RealInput u[product(dims)] 
        annotation(Placement(transformation(origin ={-120.0,0.0},extent ={{-20.0,-20.0}, {20.0, 20.0}})));
        Modelica.Blocks.Interfaces.IntegerOutput y[dims[1]] 
        annotation(Placement(transformation(origin={110.0,0.0},extent={{-10.0,-10.0},{10.0,10.0}})));
      protected
        Integer pos;
      algorithm
        pos := 1;
        for i1 in 1:dims[1] loop
          y[i1] := noEvent(integer(u[pos] + 0.5));
          pos := pos + 1;
        end for;
      end _V2A_1D_Integer;
      model _A2V_1D_Integer
      "1 dimension Integer array to Real vector"
        annotation(Diagram(coordinateSystem(extent={{-100.0,-100.0},{100.0,100.0}},preserveAspectRatio=false,grid={2.0,2.0})),
                          Icon(coordinateSystem(preserveAspectRatio = false, extent = { {-100, -100}, {100, 100} }), graphics = {
                            Rectangle(
                            lineColor = {200, 200, 200},
                            fillColor = {248, 248, 248},
                            fillPattern = FillPattern.HorizontalCylinder,
                            extent = {{-100.0, -100.0}, {100.0, 100.0}},
                            radius = 25.0),
                            Rectangle(
                            lineColor = {128, 128, 128},
                            extent = {{-100.0, -100.0}, {100.0, 100.0}},
                            radius = 25.0), Polygon(origin = {20.0, 0.0},
                            lineColor = {64, 64, 64},
                            fillColor = {255, 255, 255},
                            fillPattern = FillPattern.Solid,
                            points = {{-10.0, 70.0}, {10.0, 70.0}, {40.0, 20.0}, {80.0, 20.0}, {80.0, -20.0}, {40.0, -20.0}, {10.0, -70.0}, {-10.0, -70.0}}),
                            Polygon(fillColor = {102, 102, 102},
                            pattern = LinePattern.None,
                            fillPattern = FillPattern.Solid,
                            points = {{-100.0, 20.0}, {-60.0, 20.0}, {-30.0, 70.0}, {-10.0, 70.0}, {-10.0, -70.0}, {-30.0, -70.0}, {-60.0, -20.0}, {-100.0, -20.0}}) }));
        import Modelica;
        parameter Integer dims[1] = {2};
        Modelica.Blocks.Interfaces.IntegerInput u[dims[1]] 
          annotation(Placement(transformation(origin ={-120.0,0.0},extent ={{-20.0,-20.0}, {20.0, 20.0}})));
        Modelica.Blocks.Interfaces.RealOutput y[product(dims)] 
          annotation(Placement(transformation(origin={110.0,0.0},extent={{-10.0,-10.0},{10.0,10.0}})));
      protected
        Integer pos;
      algorithm
        pos := 1;
        for i1 in 1:dims[1] loop
          y[pos] := u[i1];
          pos := pos + 1;
        end for;
      end _A2V_1D_Integer;

    end ArrayConverter;
  end ImportedTypes;
  equation
  connect(transToForce.Fxyz, droneBody_Ground1.forcein) 
  annotation(Line(origin={-67,-77},
points={{4.52,2.82},{11.8,2.82},{11.8,5.18}},
color={0,0,127}));
  connect(droneBody_Ground1.frame_a, transToForce.frame_a) 
  annotation(Line(origin={-65,-70},
points={{10.64,18.34},{1.26,18.34},{1.26,18.5}},
color={95,95,95},
thickness=0.5));
  connect(absolutePosition.frame_a, droneBody_Ground1.frame_a) 
  annotation(Line(origin={-22,-70},
points={{-18,50},{-38,50},{-38,18.34},{-32.36,18.34}},
color={95,95,95},
thickness=0.5));
  connect(PathGenerator.position_command, transToForce.xyz) 
  annotation(Line(origin={-125,-74},
points={{-2.9,11.58},{13.8,11.58},{13.8,10.74}},
color={0,0,127}));
  connect(destnation.DestOut, PathGenerator.AimPos) 
  annotation(Line(origin={-174,-76},
points={{-15.9,14},{4.1,14},{4.1,13.58}},
color={0,0,127}));
  connect(absolutePosition.r, channel.in_pos) 
  annotation(Line(origin={13,-41},
  points={{-32,21},{7,21},{7,-22},{31.9,-22}},
  color={0,0,127}));
  connect(channel.out_image_number, imagehandle.in_index) 
  annotation(Line(origin={129,-49},
  points={{-37.9,0.07},{37.9,0.07}},
  color={255,127,0}));
  connect(channel.out_pos, imagehandle.in_position) 
  annotation(Line(origin={129,-58},
  points={{-37.9,-0.38},{37.9,-0.38}},
  color={0,0,127}));
  connect(channel.out_SNR, imagehandle.in_SNR) 
  annotation(Line(origin={129,-68},
  points={{-37.9,0.38},{37.9,0.38}},
  color={0,0,127}));
  connect(channel.out_transmissionTime_s, imagehandle.in_delay) 
  annotation(Line(origin={129,-77},
  points={{-37.9,-0.07},{37.9,-0.07}},
  color={0,0,127}));
  end ShortRangeTarget;