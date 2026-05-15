package SyslabFunctions "图像传输及识别"
  model channel
    "julia function"
    annotation (__MWorks(SyslabFunction(Type = "function",AllFuncNames="channel",Duplicated=true,BlockPort(in_pos(Scope=Input,Type=0,Dims={3},Value=1,Desc=""),out_image_number(Scope=Output,Type=1,Dims={-1},Value=1,Desc=""),out_pos(Scope=Output,Type=0,Dims={3},Value=1,Desc=""),out_SNR(Scope=Output,Type=0,Dims={-1},Value=1,Desc=""),out_transmissionTime_s(Scope=Output,Type=0,Dims={-1},Value=1,Desc="")))),
      Diagram(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
        grid = {2.0, 2.0})),
      Icon(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2}),graphics = {Bitmap(origin={0,0},
extent={{-100,-100},{100,100}},
fileName="Modelica://SyslabWorkspace/Resources/Images/NewFunctionAPI.svg"), Text(origin={0,130},
lineColor={0,0,255},
extent={{-150,20},{150,-20}},
textString="%name",
textColor={0,0,255})}));

    import Modelica;
    import SyslabWorkspace.Communication;

    extends SyslabWorkspace.Communication.SyslabSampleBase;


    Communication.SyslabFunctionBase base(funcName="channel", scriptText = "base64=ZnVuY3Rpb24gY2hhbm5lbChwb3MpCgogICAgeDA9MDsj5aGU5Y+w5Z2Q5qCHCiAgICB5MD0wOwogICAgejA9MDsKCiAgICBiYW5kd2lkdGg9MjBlNiAgICMg5L+h6YGT5bim5a6977yM5Y2V5L2N6LWr5YW5CiAgICBzaWduYWxQb3dlcj0wLjEgICAjIOS/oeWPt+WKn+eOh++8jOWNleS9jeeTpueJuQogICAgbm9pc2VQb3dlcj0xZS04ICAgIyDlmarlo7Dlip/njofvvIzljZXkvY3nk6bnibkKICAgIGxvc3M9MTsgICAgICAgICAgICAgIyDmjZ/ogJfns7vmlbAKICAgIE4gPSAxMDAwICAgICAgICAgICAjIOmHh+agt+eCueaVsAogICAgdCA9IHJhbmdlKDAsIDEvYmFuZHdpZHRoLCBOKSAgIyDml7bpl7TlkJHph48KCgogICAgIzEu5qih5ouf5Zu+54mH6YeH6ZuGCiAgICBpbWFnZV9udW1iZXIgPSByYW5kKDE6MTApCiAgICBnX2Fic3BhdGggPSAiQzpcXFVzZXJzXFxHbG93VHViZVxcRG9jdW1lbnRzXFxNV09SS1NcXFNtYXJ0RHJvbmUiCiAgICBmaWxlcGF0aCA9IGdfYWJzcGF0aCAqICIvZGF0YS9pbnB1dC8iICogc3RyaW5nKGltYWdlX251bWJlcikgKiIuanBnIgogICAgaW1hZ2VTaXplX2JpdHMgPSA4KmZpbGVzaXplKGZpbGVwYXRoKSAgI+ivu+WPluWbvueJh+Wkp+WwjwoKICAgICMyLuiuoeeul+S8oOi+k+i3neemu++8jOWNleS9jeexswogICAgZGlzdGFuY2VfbT1zcXJ0KChwb3NbMV0gLSB4MCleMiArIChwb3NbMl0gLSB5MCleMiArIChwb3NbM10gLSB6MCleMikKCiAgICAjMy7kv6Hlj7flv6voobDokL3mqKHmi58KICAgIHNpZ25hbCA9IHNxcnQoc2lnbmFsUG93ZXIpICogZXhwLigxaW0gKiAyICogcGkgKiBiYW5kd2lkdGggKiB0KSAj55Sf5oiQ5L+h5Y+3CiAgICBJID0gcmFuZG4oTikjIOeUn+aIkOS4pOS4queLrOeri+eahOmrmOaWr+maj+acuui/h+eoi++8jOWIhuWIq+WvueW6lEnlkoxR5YiG6YePCiAgICBRID0gcmFuZG4oTikKICAgIEggPSBzcXJ0KDAuNSkgKiAoSSArIDFpbSAqIFEpICMg6K6h566X55Ge5Yip6KGw6JC95L+h6YGT55qE5ZON5bqUCiAgICBmYWRlZF9zaWduYWwgPSBzaWduYWwgLiogSCAgICAjIOS/oeWPt+mAmui/h+eRnuWIqeihsOiQveS/oemBkwogICAgbm9pc2UgPSBzcXJ0KG5vaXNlUG93ZXIgLyAyKSAqIChyYW5kbihOKSArIDFpbSAqIHJhbmRuKE4pKSAjQVdHTgogICAgcmVjZWl2ZWRfc2lnbmFsID0gZmFkZWRfc2lnbmFsICsgbm9pc2UgI+a3u+WKoOWZquWjsAoKICAgICM0Luiuoeeul+S/oeWZquavlAogICAgc2lnbmFsUG93ZXJfZmFkZWQgPSBzdW0oYWJzMi4oZmFkZWRfc2lnbmFsKSkgLyBOICAj6KGw6JC95ZCO55qE5L+h5Y+35Yqf546HCiAgICBwYXRoTG9zc19kQiA9IDEwICogbG9zcyAqIGxvZzEwKGRpc3RhbmNlX20pICsgMzAgICMg6Lev5b6E5o2f6ICX6K6h566XCgogICAgU05SID0gMTAgKiBsb2cxMChzaWduYWxQb3dlcl9mYWRlZCAvIG5vaXNlUG93ZXIpLXBhdGhMb3NzX2RCCiAgIAoKICAgICM1LuS/oemBk+WuuemHj+iuoeeul++8iOmmmeWGnOWFrOW8j++8iQogICAgY2hhbm5lbENhcGFjaXR5X2JwcyA9IGJhbmR3aWR0aCAqIGxvZygxICsgMTBeKChTTlIgLyAxMCkpIC8gbG9nKDIpKQoKICAgICM2LuS8oOi+k+aXtumXtOiuoeeulwogICAgdHJhbnNtaXNzaW9uVGltZV9zID0gaW1hZ2VTaXplX2JpdHMgLyBjaGFubmVsQ2FwYWNpdHlfYnBzCgogICAgcmV0dXJuIGltYWdlX251bWJlciwgcG9zLCBTTlIsIHRyYW5zbWlzc2lvblRpbWVfcwogICAgCmVuZAo="
                                                                                                                                                                                                                                                                       , startTime = startTime, period = period,inputDims={{3}},inputTypes={0},outputDims={{-1}, {3}, {-1}, {-1}},outputTypes={1, 0, 0, 0},hasInput=true,hasOutput=true,outputNames={"out_image_number", "out_pos", "out_SNR", "out_transmissionTime_s"}) annotation(Placement(transformation(extent = {{-10.0, -10.0}, {10.0, 10.0}},origin={0.0, 0.0})));
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
    end channel;
  model imagehandle
    "julia function"
    annotation (__MWorks(SyslabFunction(Type = "function",AllFuncNames="imagehandle,addnoise,get_input_array,run_inference,process_output,yolobox,compute_iou,merge_overlapping_boxes",Duplicated=true,BlockPort(in_index(Scope=Input,Type=1,Dims={-1},Value=1,Desc=""),in_position(Scope=Input,Type=0,Dims={3},Value=1,Desc=""),in_SNR(Scope=Input,Type=0,Dims={-1},Value=1,Desc=""),in_delay(Scope=Input,Type=0,Dims={-1},Value=1,Desc=""),out_res(Scope=Output,Type=0,Dims={-1},Value=1,Desc="")))),
      Diagram(coordinateSystem(extent = {{-100.0, -100.0}, {100.0, 100.0}},
        grid = {2.0, 2.0})),
      Icon(coordinateSystem(extent={{-100,-100},{100,100}},
grid={2,2}),graphics = {Bitmap(origin={0,0},
extent={{-100,-100},{100,100}},
fileName="Modelica://SyslabWorkspace/Resources/Images/NewFunctionAPI.svg"), Text(origin={0,130},
lineColor={0,0,255},
extent={{-150,20},{150,-20}},
textString="%name",
textColor={0,0,255})}));

    import Modelica;
    import SyslabWorkspace.Communication;
    import Modelica.Utilities.Streams.print;
    import Modelica.Utilities.Streams.getWorkDirectory;

    parameter String absp =  Modelica.Utilities.System.getWorkDirectory();
    extends SyslabWorkspace.Communication.SyslabSampleBase;

    Communication.SyslabFunctionBase base(funcName="imagehandle", scriptText = "base64=dXNpbmcgT05OWFJ1blRpbWUKaW1wb3J0IE9OTlhSdW5UaW1lIGFzIE9OTlgKdXNpbmcgSW1hZ2VzLCBGaWxlSU8gI+WbvuWDj+mihOWkhOeQhgp1c2luZyBMdXhvcgp1c2luZyBDb2xvcnMgICMg55So5p2l566h55CG6aKc6ImyCnVzaW5nIFNwZWNpYWxGdW5jdGlvbnMKCgoj5Yqg6L295qih5Z6LCiNnbG9iYWwgZ19hYnNwYXRoDQpnX2Fic3BhdGggPSAiRTpcXOS4sOaAnemRq+aWh+S7tlxc5qih5Z6L5Lqn5ZOB56eR5paH5Lu2XFwyMDI1XFw25pyIXFwyMDI1MDYzMOS6p+WTgeino+WGs+aWueahiOaxh+aAu1xc5qGI5L6L5paH5Lu25rGH5oC7MjAyNTA3MDFcXDIuIOmrmOagoeahiOS+i1xcMi4g44CQ5py65qKw44CR55So5LqO6L+c56iL5beh6YC75Y+K5byC5bi45qOA5rWL55qE5pm66IO95peg5Lq65py6XFxTbWFydERyb25lIg0KY29uc3QgbW9kZWw6Ok9OTlhSdW5UaW1lLkluZmVyZW5jZVNlc3Npb24gPSBPTk5YLmxvYWRfaW5mZXJlbmNlKGdfYWJzcGF0aCoiL2RhdGEvZ2VsYW4tYy5vbm54IiwgZXhlY3V0aW9uX3Byb3ZpZGVyPTpjcHUpCg0KCmZ1bmN0aW9uIGltYWdlaGFuZGxlKGluZGV4LCBwb3NpdGlvbiwgU05SLCBkZWxheSkKICAgICMg5Zu+54mH5a2Y5YKo5L2N572uCiAgICBmaWxlID0gZ19hYnNwYXRoKiIvZGF0YS9pbnB1dC8iICogc3RyaW5nKGluZGV4KSoiLmpwZyIKICAgIGltZyA9IGxvYWQoZmlsZSkKICAgIGltZ19vcmlnaW4gPSBpbWcKICAgIG91dHB1dF9wYXRoID0gZ19hYnNwYXRoKiIvZGF0YS9vdXRwdXQvcHJlZC5wbmciCgogICAgIyDmt7vliqDpq5jmlq/lmarlo7AKICAgIGltZyA9IGFkZG5vaXNlKGltZywgU05SKQoKICAgICMg6L+Q6KGM5o6o55CG5ZKM5aSE55CG6L6T5Ye6CiAgICByZXMgPSBydW5faW5mZXJlbmNlKGltZykKICAgIGJveGVzLCBjbGFzc19pZHMgPSBwcm9jZXNzX291dHB1dChyZXMpCgogICAgIyDlsIbmo4DmtYvmoYbovazmjaLkuLrlnZDmoIfmoLzlvI8KICAgIGJveGVzX3h5eHkgPSBbeW9sb2JveChib3hbMV0sIGJveFsyXSwgYm94WzNdLCBib3hbNF0pIGZvciBib3ggaW4gZWFjaHJvdyhib3hlcyldCgogICAgIyDlkIjlubbph43lj6DnmoTkurrnianmlrnmoYYKICAgIG1lcmdlZF9ib3hlcywgbWVyZ2VkX2NsYXNzZXMgPSBtZXJnZV9vdmVybGFwcGluZ19ib3hlcyhib3hlc194eXh5LCBjbGFzc19pZHMpCgogICAgIyDpooTlpITnkIblm77lg4/lkozmlofku7bkv53lrZjot6/lvoQKICAgIGltZyA9IGltcmVzaXplKGltZywgNjQwLCA2NDApCiAgICBpbWdfb3JpZ2luID0gaW1yZXNpemUoaW1nX29yaWdpbiwgNjQwLCA2NDApCiAgICBpbWdfd2lkdGgsIGltZ19oZWlnaHQgPSBzaXplKGltZykKCiAgICAjIOaYoOWwhOaooeWei+WSjOe0ouW8lQogICAgbmFtZXMgPSBEaWN0KAogICAgICAgIDAgPT4gInBlcnNvbiIsCiAgICAgICAgMSA9PiAiYmljeWNsZSIsCiAgICAgICAgMiA9PiAiY2FyIiwKICAgICAgICAzID0+ICJtb3RvcmN5Y2xlIiwKICAgICAgICA0ID0+ICJhaXJwbGFuZSIsCiAgICAgICAgNSA9PiAiYnVzIiwKICAgICAgICA2ID0+ICJ0cmFpbiIsCiAgICAgICAgNyA9PiAidHJ1Y2siLAogICAgICAgIDggPT4gImJvYXQiLAogICAgICAgIDkgPT4gInRyYWZmaWMgbGlnaHQiLAogICAgICAgIDEwID0+ICJmaXJlIGh5ZHJhbnQiLAogICAgICAgIDExID0+ICJzdG9wIHNpZ24iLAogICAgICAgIDEyID0+ICJwYXJraW5nIG1ldGVyIiwKICAgICAgICAxMyA9PiAiYmVuY2giLAogICAgICAgIDE0ID0+ICJiaXJkIiwKICAgICAgICAxNSA9PiAiY2F0IiwKICAgICAgICAxNiA9PiAiZG9nIiwKICAgICAgICAxNyA9PiAiaG9yc2UiLAogICAgICAgIDE4ID0+ICJzaGVlcCIsCiAgICAgICAgMTkgPT4gImNvdyIsCiAgICAgICAgMjAgPT4gImVsZXBoYW50IiwKICAgICAgICAyMSA9PiAiYmVhciIsCiAgICAgICAgMjIgPT4gInplYnJhIiwKICAgICAgICAyMyA9PiAiZ2lyYWZmZSIsCiAgICAgICAgMjQgPT4gImJhY2twYWNrIiwKICAgICAgICAyNSA9PiAidW1icmVsbGEiLAogICAgICAgIDI2ID0+ICJoYW5kYmFnIiwKICAgICAgICAyNyA9PiAidGllIiwKICAgICAgICAyOCA9PiAic3VpdGNhc2UiLAogICAgICAgIDI5ID0+ICJmcmlzYmVlIiwKICAgICAgICAzMCA9PiAic2tpcyIsCiAgICAgICAgMzEgPT4gInNub3dib2FyZCIsCiAgICAgICAgMzIgPT4gInNwb3J0cyBiYWxsIiwKICAgICAgICAzMyA9PiAia2l0ZSIsCiAgICAgICAgMzQgPT4gImJhc2ViYWxsIGJhdCIsCiAgICAgICAgMzUgPT4gImJhc2ViYWxsIGdsb3ZlIiwKICAgICAgICAzNiA9PiAic2thdGVib2FyZCIsCiAgICAgICAgMzcgPT4gInN1cmZib2FyZCIsCiAgICAgICAgMzggPT4gInRlbm5pcyByYWNrZXQiLAogICAgICAgIDM5ID0+ICJib3R0bGUiLAogICAgICAgIDQwID0+ICJ3aW5lIGdsYXNzIiwKICAgICAgICA0MSA9PiAiY3VwIiwKICAgICAgICA0MiA9PiAiZm9yayIsCiAgICAgICAgNDMgPT4gImtuaWZlIiwKICAgICAgICA0NCA9PiAic3Bvb24iLAogICAgICAgIDQ1ID0+ICJib3dsIiwKICAgICAgICA0NiA9PiAiYmFuYW5hIiwKICAgICAgICA0NyA9PiAiYXBwbGUiLAogICAgICAgIDQ4ID0+ICJzYW5kd2ljaCIsCiAgICAgICAgNDkgPT4gIm9yYW5nZSIsCiAgICAgICAgNTAgPT4gImJyb2Njb2xpIiwKICAgICAgICA1MSA9PiAiY2Fycm90IiwKICAgICAgICA1MiA9PiAiaG90IGRvZyIsCiAgICAgICAgNTMgPT4gInBpenphIiwKICAgICAgICA1NCA9PiAiZG9udXQiLAogICAgICAgIDU1ID0+ICJjYWtlIiwKICAgICAgICA1NiA9PiAiY2hhaXIiLAogICAgICAgIDU3ID0+ICJjb3VjaCIsCiAgICAgICAgNTggPT4gInBvdHRlZCBwbGFudCIsCiAgICAgICAgNTkgPT4gImJlZCIsCiAgICAgICAgNjAgPT4gImRpbmluZyB0YWJsZSIsCiAgICAgICAgNjEgPT4gInRvaWxldCIsCiAgICAgICAgNjIgPT4gInR2IiwKICAgICAgICA2MyA9PiAibGFwdG9wIiwKICAgICAgICA2NCA9PiAibW91c2UiLAogICAgICAgIDY1ID0+ICJyZW1vdGUiLAogICAgICAgIDY2ID0+ICJrZXlib2FyZCIsCiAgICAgICAgNjcgPT4gImNlbGwgcGhvbmUiLAogICAgICAgIDY4ID0+ICJtaWNyb3dhdmUiLAogICAgICAgIDY5ID0+ICJvdmVuIiwKICAgICAgICA3MCA9PiAidG9hc3RlciIsCiAgICAgICAgNzEgPT4gInNpbmsiLAogICAgICAgIDcyID0+ICJyZWZyaWdlcmF0b3IiLAogICAgICAgIDczID0+ICJib29rIiwKICAgICAgICA3NCA9PiAiY2xvY2siLAogICAgICAgIDc1ID0+ICJ2YXNlIiwKICAgICAgICA3NiA9PiAic2Npc3NvcnMiLAogICAgICAgIDc3ID0+ICJ0ZWRkeSBiZWFyIiwKICAgICAgICA3OCA9PiAiaGFpciBkcmllciIsCiAgICAgICAgNzkgPT4gInRvb3RoYnJ1c2giCiAgICApCgogICAgIyDliJvlu7rkuIDkuKrmlrDnmoTnu5jlm77njq/looMKICAgIERyYXdpbmcoMTQwMCwgODAwLCBvdXRwdXRfcGF0aCkKCiAgICAjIOWwhuWKoOi9veeahOWbvuWDj+iuvue9ruS4uuiDjOaZrwogICAgYmFja2dyb3VuZCgid2hpdGUiKQogICAgcGxhY2VpbWFnZShpbWcsIEx1eG9yLlBvaW50KDcyMCwgMTAwKSkKICAgIHBsYWNlaW1hZ2UoaW1nX29yaWdpbiwgTHV4b3IuUG9pbnQoNTAsIDEwMCkpCgogICAgIyDorr7nva7lrZfkvZPlkozmlrnmoYbnspfnu4YKICAgIHNldGZvbnQoIkFyaWFsIiwgODgpICAjIOehruS/neS9v+eUqOato+ehrueahOWtl+S9k+WQjeensAogICAgZm9udHNpemUoMjApCiAgICBzZXRsaW5lKDIpCgogICAgIyDpgJDkuKrnu5jliLblkIjlubblkI7nmoTmlrnmoYblkozmoIfnrb4KICAgIGZvciAoaSwgYm94KSBpbiBlbnVtZXJhdGUobWVyZ2VkX2JveGVzKQogICAgICAgIGNsYXNzX2lkID0gbWVyZ2VkX2NsYXNzZXNbaV0KICAgICAgICAjIOWwhuexu+WIq+i9rOS4uuWtl+espuS4sgogICAgICAgIGxhYmVsX3RleHQgPSBzdHJpbmcoY2xhc3NfaWQpCiAgICAgICAgIyDmoLnmja7nsbvliKvorr7nva7popzoibIKICAgICAgICBzZXRodWUoY2xhc3NfaWQgPT0gMSA/ICJyZWQiIDogImJsdWUiKQogICAgICAgICMg57uY5Yi255+p5b2iCiAgICAgICAgcmVjdChib3hbMV0gKyA3MjAsIGJveFsyXSArIDEwMCwgYm94WzNdIC0gYm94WzFdLCBib3hbNF0gLSBib3hbMl0sIDpzdHJva2UpCiAgICAgICAgbGFiZWxfdGV4dCA9IG5hbWVzW2NsYXNzX2lkLTFdICAjIOWIm+W7uuagh+etvuaWh+acrAogICAgICAgICMg5Zyo55+p5b2i5LiK5pa557uY5Yi25paH5pysCiAgICAgICAgdGV4dChsYWJlbF90ZXh0LCAoYm94WzNdIC0gYm94WzFdIC0gbGVuZ3RoKGxhYmVsX3RleHQpICogMTApIC8gMiArIGJveFsxXSArIDcyMCwgYm94WzJdICsgMTAwKQogICAgZW5kCgogICAgIyDnu5jliLblu7bml7Ygcm91bmQocFsxXTsgZGlnaXRzPTMpCiAgICBmb250c2l6ZSgzMCkKICAgIHNldGh1ZSgiYmxhY2siKQogICAgZGVsYXlfdGV4dCA9ICJEZWxheTogIiAqIHN0cmluZyhyb3VuZChkZWxheSoxMDAwLCBkaWdpdHM9MykpICogIiBtcyIKICAgIGRlc3RpbmF0aW9uX3RleHQgPSAiRGVzdGluYXRpb246ICIgKiAieC0iICogc3RyaW5nKHJvdW5kKHBvc2l0aW9uWzFdOyBkaWdpdHM9MSkpKiIgeS0iKiBzdHJpbmcocm91bmQocG9zaXRpb25bMl07IGRpZ2l0cz0xKSkqICIgei0iKnN0cmluZyhyb3VuZChwb3NpdGlvblszXTsgZGlnaXRzPTEpKSAqIm0iCiAgICBTTlJfdGV4dCA9ICJTTlI6ICIgKiBzdHJpbmcocm91bmQoU05SOyBkaWdpdHM9MikgKSAqICIgZEIiCiAgICByZXNfdGV4dCA9ICJHcm91bmQgcmVjZXB0aW9uIGFuZCByZWNvZ25pdGlvbiByZXN1bHRzOiAiCiAgICB0ZXh0KGRlc3RpbmF0aW9uX3RleHQsIDUwLCA1MCkKICAgIHRleHQoU05SX3RleHQsIDUwLCA5MCkKICAgIHRleHQoZGVsYXlfdGV4dCwgNzIwLCA1MCkKICAgIHRleHQocmVzX3RleHQsIDcyMCwgOTApCgogICAgIyDkv53lrZjnu5Pmnpzlm77lg48KICAgIHJlcyA9IGZpbmlzaCgpCiAgICByZXR1cm4gcmVzCmVuZAoKZnVuY3Rpb24gYWRkbm9pc2UoaW1nLCBTTlIpCiAgICAjIOWZquWjsOW8uuW6pue6v+aAp+i9rOWMlgogICAgbm9pc2VfbGV2ZWwgPSAwLjUgKiBlcmZjKFNOUiAvIDI1KQoKICAgICMg5bCG5Zu+5YOP6L2s5o2i5Li65rWu54K55pWw57uECiAgICBpbWdfZmxvYXQgPSBGbG9hdDY0LihjaGFubmVsdmlldyhpbWcpKQoKICAgICMg5re75Yqg6auY5pav5Zmq5aOwCiAgICBub2lzeV9pbWdfZmxvYXQgPSBpbWdfZmxvYXQgKyBub2lzZV9sZXZlbCAuKiByYW5kbihzaXplKGltZ19mbG9hdCkpCgogICAgIyDoo4HliarlgLzliLBbMCwxXeiMg+WbtAogICAgbm9pc3lfaW1nX2Zsb2F0ID0gY2xhbXAuKG5vaXN5X2ltZ19mbG9hdCwgMCwgMSkKCiAgICAjIOi9rOWbnuWbvueJh+agvOW8jwogICAgbm9pc3lfaW1nID0gY29sb3J2aWV3KFJHQiwgbm9pc3lfaW1nX2Zsb2F0KQogICAgCiAgICByZXR1cm4gbm9pc3lfaW1nCmVuZAoKZnVuY3Rpb24gZ2V0X2lucHV0X2FycmF5KGltZykKICAgIHJlc2l6ZWQgPSBpbXJlc2l6ZShpbWcsICg2NDAsIDY0MCkpCiAgICBtYXQgPSBjaGFubmVsdmlldyhyZXNpemVkKQogICAgb3JpZ2luYWxfYXJyYXkgPSBGbG9hdDMyLihtYXQpCiAgICByZXR1cm4gcmVzaGFwZShvcmlnaW5hbF9hcnJheSwgKDEsIHNpemUob3JpZ2luYWxfYXJyYXkpLi4uKSkKZW5kCgojIOaOqOeQhuWHveaVsApmdW5jdGlvbiBydW5faW5mZXJlbmNlKGltZykKICAgIGlucHV0X2FycmF5ID0gZ2V0X2lucHV0X2FycmF5KGltZykKICAgIHJlcyA9IG1vZGVsKERpY3QoImltYWdlcyIgPT4gaW5wdXRfYXJyYXkpKVsib3V0cHV0MCJdICAjIOefqemYtei+k+WHuuS4uiAxeDg0eDg0MDAKICAgIHJldHVybiByZXMKZW5kCgojIOi+k+WHuuWkhOeQhuWHveaVsO+8jOi/lOWbnuajgOa1i+ahhuWSjOexu+WIqwpmdW5jdGlvbiBwcm9jZXNzX291dHB1dChyZXMpCiAgICBwcmVkaWN0aW9ucyA9IHRyYW5zcG9zZShyZXNbMSwgOiwgOl0pICAjIOefqemYtei+k+WHuuS4uiAoODQwMCwgODQpCiAgICBjb25mX3RocmVzaG9sZCA9IDAuNAogICAgc2NvcmVzID0gbWF4aW11bShwcmVkaWN0aW9uc1s6LCA1OmVuZF0sIGRpbXM9MikKCiAgICAjIOWfuuS6jue9ruS/oeW6pumYiOWAvOi/h+a7pAogICAgcHJlZGljdGlvbnMgPSBwcmVkaWN0aW9uc1t2ZWMoc2NvcmVzIC4+IGNvbmZfdGhyZXNob2xkKSwgOl0KCiAgICBjbGFzc19pZHMgPSBhcmdtYXgocHJlZGljdGlvbnNbOiwgNTplbmRdLCBkaW1zPTIpCiAgICBjbGFzc19pZHMgPSB2ZWMobWFwKGkgLT4gaVsyXSwgY2xhc3NfaWRzKSkgICMg6I635Y+W5q+P5Liq5pa55qGG55qE57G75Yir57Si5byVCiAgICAjIHBlcnNvbl9jbGFzc19pbmRleCA9IDEgICMg5pWw5o2u6ZuG5Lit77yMInBlcnNvbiIg57G75Yir57Si5byV5YC85Li6IDEKICAgICMgcGVyc29uX3ByZWRpY3Rpb25zID0gcHJlZGljdGlvbnNbY2xhc3NfaWRzIC49PSBwZXJzb25fY2xhc3NfaW5kZXgsIDpdCgogICAgYm94ZXMgPSBwcmVkaWN0aW9uc1s6LCBiZWdpbjo0XSAgIyDojrflj5bmlrnmoYYKICAgIHJldHVybiBib3hlcywgY2xhc3NfaWRzICAjIOi/lOWbnuaWueahhuWSjOexu+WIqwplbmQKCiMg5bCG55+p5b2i5qGG6L2s5o2i5Li65Zu+5YOP5Z2Q5qCHCmZ1bmN0aW9uIHlvbG9ib3goeCwgeSwgdywgaCkKICAgIHgxLCB5MSA9IHggLSB3IC8gMiwgeSAtIGggLyAyCiAgICB4MiwgeTIgPSB4ICsgdyAvIDIsIHkgKyBoIC8gMgogICAgcmV0dXJuIHRydW5jLihJbnQsIFt4MSwgeTEsIHgyLCB5Ml0pCmVuZAoKIyDorqHnrpfkuqTlubbmr5QgKElvVSkKZnVuY3Rpb24gY29tcHV0ZV9pb3UoYm94MSwgYm94MikKICAgIHgxX21pbiwgeTFfbWluLCB4MV9tYXgsIHkxX21heCA9IGJveDEKICAgIHgyX21pbiwgeTJfbWluLCB4Ml9tYXgsIHkyX21heCA9IGJveDIKCiAgICBpbnRlcl94X21pbiA9IG1heCh4MV9taW4sIHgyX21pbikKICAgIGludGVyX3lfbWluID0gbWF4KHkxX21pbiwgeTJfbWluKQogICAgaW50ZXJfeF9tYXggPSBtaW4oeDFfbWF4LCB4Ml9tYXgpCiAgICBpbnRlcl95X21heCA9IG1pbih5MV9tYXgsIHkyX21heCkKCiAgICBpbnRlcl9hcmVhID0gbWF4KDAsIGludGVyX3hfbWF4IC0gaW50ZXJfeF9taW4pICogbWF4KDAsIGludGVyX3lfbWF4IC0gaW50ZXJfeV9taW4pCgogICAgYm94MV9hcmVhID0gKHgxX21heCAtIHgxX21pbikgKiAoeTFfbWF4IC0geTFfbWluKQogICAgYm94Ml9hcmVhID0gKHgyX21heCAtIHgyX21pbikgKiAoeTJfbWF4IC0geTJfbWluKQoKICAgIHVuaW9uX2FyZWEgPSBib3gxX2FyZWEgKyBib3gyX2FyZWEgLSBpbnRlcl9hcmVhCgogICAgcmV0dXJuIGludGVyX2FyZWEgLyB1bmlvbl9hcmVhCmVuZAoKIyDlkIjlubbph43lj6DmlrnmoYYKZnVuY3Rpb24gbWVyZ2Vfb3ZlcmxhcHBpbmdfYm94ZXMoYm94ZXMsIGNsYXNzX2lkcywgaW91X3RocmVzaG9sZD0wLjUpCiAgICBtZXJnZWRfYm94ZXMgPSBbXQogICAgbWVyZ2VkX2NsYXNzZXMgPSBbXQoKICAgIGZvciBpIGluIGVhY2hpbmRleChib3hlcykKICAgICAgICBib3ggPSBib3hlc1tpXQogICAgICAgIGNsYXNzX2lkID0gY2xhc3NfaWRzW2ldCiAgICAgICAgb3ZlcmxhcHBlZCA9IGZhbHNlCgogICAgICAgIGZvciBqIGluIGVhY2hpbmRleChtZXJnZWRfYm94ZXMpCiAgICAgICAgICAgIGlmIGNvbXB1dGVfaW91KG1lcmdlZF9ib3hlc1tqXSwgYm94KSA+IGlvdV90aHJlc2hvbGQKICAgICAgICAgICAgICAgICMg5aaC5p6c6YeN5Y+g77yM5ZCI5bm25Lik5Liq5pa55qGGCiAgICAgICAgICAgICAgICBtZXJnZWRfYm94ZXNbal0gPSBbCiAgICAgICAgICAgICAgICAgICAgbWluKG1lcmdlZF9ib3hlc1tqXVsxXSwgYm94WzFdKSwgICMg5ZCI5bm2IHhfbWluCiAgICAgICAgICAgICAgICAgICAgbWluKG1lcmdlZF9ib3hlc1tqXVsyXSwgYm94WzJdKSwgICMg5ZCI5bm2IHlfbWluCiAgICAgICAgICAgICAgICAgICAgbWF4KG1lcmdlZF9ib3hlc1tqXVszXSwgYm94WzNdKSwgICMg5ZCI5bm2IHhfbWF4CiAgICAgICAgICAgICAgICAgICAgbWF4KG1lcmdlZF9ib3hlc1tqXVs0XSwgYm94WzRdKSAgICMg5ZCI5bm2IHlfbWF4CiAgICAgICAgICAgICAgICBdCiAgICAgICAgICAgICAgICAjIOS4jeaUueWPmOmHjeWPoOeahGNsYXNz77yM5LiN5YaN5qyh5o6o5YWl57G75pWw57uECiAgICAgICAgICAgICAgICBvdmVybGFwcGVkID0gdHJ1ZQogICAgICAgICAgICAgICAgYnJlYWsKICAgICAgICAgICAgZW5kCiAgICAgICAgZW5kCgogICAgICAgIGlmICFvdmVybGFwcGVkCiAgICAgICAgICAgIHB1c2ghKG1lcmdlZF9ib3hlcywgYm94KSAgIyDlj6rmnInkuI3ph43lj6DnmoTmg4XlhrXmiY3liqDlhaUKICAgICAgICAgICAgcHVzaCEobWVyZ2VkX2NsYXNzZXMsIGNsYXNzX2lkKQogICAgICAgIGVuZAogICAgZW5kCgogICAgcmV0dXJuIG1lcmdlZF9ib3hlcywgbWVyZ2VkX2NsYXNzZXMKZW5k"




                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      , startTime = startTime, period = period,inputDims={{-1}, {3}, {-1}, {-1}},inputTypes={1, 0, 0, 0},outputDims={{-1}},outputTypes={0},hasInput=true,hasOutput=true,outputNames={"out_res"}) 
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
    algorithm
    when initial() then
    Modelica.Utilities.Streams.print("输出图片路径为："+absp+"/SmartDrone/data/output");
    end when;

    end imagehandle;
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

  end ArrayConverter;

end SyslabFunctions;