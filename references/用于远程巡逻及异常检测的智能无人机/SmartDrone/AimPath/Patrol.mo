model Patrol "巡逻路径"

  parameter Real z_height = 100;
  parameter Real scale = 1.0;
  Modelica.Blocks.Sources.Ramp z_on[3](height={0,0,z_height},duration=10,offset={0,0,0}) 

    annotation (Placement(transformation(origin={-199,6}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Ramp z_off[3](height={0,0,-z_height},duration=10,offset={0,0,0},startTime=40) 

    annotation (Placement(transformation(origin={-199,-32}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.VectorAdd vectorAdd(n=3) 
    annotation (Placement(transformation(origin={-145,-12}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.VectorAdd vectorAdd1(n=3) 
    annotation (Placement(transformation(origin={49,6}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Ramp xy1[3](height={150,0,0},duration=3,offset={0,0,0},startTime=10) 

    annotation (Placement(transformation(origin={-110,60}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Ramp xy2[3](height={0,150,0},duration=3,offset={0,0,0},startTime=13) 

    annotation (Placement(transformation(origin={-110,84}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Ramp xy3[3](height={-450,0,0},duration=6,offset={0,0,0},startTime=16) 

    annotation (Placement(transformation(origin={-144,84}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Ramp xy4[3](height={-150,-300,0},duration=6,offset={0,0,0},startTime=22) 

    annotation (Placement(transformation(origin={-176,60}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Ramp xy5[3](height={600,-100,0},duration=6,offset={0,0,0},startTime=28) 

    annotation (Placement(transformation(origin={-144,36}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Ramp xy6[3](height={0,250,0},duration=3,offset={0,0,0},startTime=34) 

    annotation (Placement(transformation(origin={-110,36}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Sources.Ramp xy7[3](height={-150,0,0},duration=3,offset={0,0,0},startTime=37) 

    annotation (Placement(transformation(origin={-143,60}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.Gain gain[3](k=scale) 
    annotation (Placement(transformation(origin={19,66}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.Add3 add3_1[3] 
    annotation (Placement(transformation(origin={-52,84}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.Add3 add3_2[3] 
    annotation (Placement(transformation(origin={-52,58}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Math.Add3 add3_3[3] 
    annotation (Placement(transformation(origin={-16.5,66}, 
extent={{-10,-10},{10,10}})));
  Modelica.Blocks.Interfaces.RealOutput y[3] 
    annotation (Placement(transformation(origin={110,0}, 
extent={{-10,-10},{10,10}})));
  annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})),Icon(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2}),graphics = {Rectangle(origin={0,0}, 
fillColor={255,255,255}, 
fillPattern=FillPattern.Solid, 
extent={{-100,100},{100,-100}}), Bitmap(origin={0,-2}, 
extent={{-100,-100},{100,100}}, 
fileName="modelica://SmartDrone/../../../Downloads/icons8-%E9%87%8D%E5%90%AF-240.png", 
imageSource="iVBORw0KGgoAAAANSUhEUgAAAPAAAADwCAYAAAA+VemSAAAACXBIWXMAAAsTAAALEwEAmpwYAAAWCElEQVR4nO2dC9hWVZXH/x93xBufoJUgihlikiJmmjpGiTGUFyw0LSkr0VERtTFN0SHHEEvAS4klimbjpewiXgpRKycdTRpvoKggIBfFK4pyUeCdZ82sN9/eOXuffe7vPuf/e579PD4fnvPuy9rn7LP3Wv8FEEIIIYQQQgghhBBCCCGEEEIIIYQQQgghhBBCCCGEEEIIIYQQQgghhBBCCCGEEEIIIYQ08IahvAzgaQB/ATATwPUApgAYD+BbAD4DoC+ANvYmIcVRS1jW6US/Qyf4aAADAXTgoBLS+hPYVN4G8EcAPwJwFICPcDAJ8WcCB5WFAH4KYBSALTiYhPg1gRvLWgD3ADgdwPYcSEL8msCNZaNulo0DsB0HkhB35Nu0J4DuALbU/94BQH8AgwAMATAcwNcBnAPgcgC3AngAwIoMJvN7AO4C8FUAXTmQhGTL1gD206OlSwH8HsCrKU3mVwBM1OMqQkiO9NcjJXljz9FlcpIl9mwAh/LcmZBi6AXgawBuAfBmgsn8FICjec5MSHF0AjBUl9zPx5zIc/V8mQ4jhBTMEF1qx/l2nqdL9Y5FN4KQqiO7zl9W3+v3I07kxwD8U9ENIIT8Hx8GMAHA6xEnsvhk92MnEtIabA5gDID5ESbxuzr5uxVdeUKypguAS9QpYzmASfq3VqOj+lDPizCRZYNsWNEVJyRLJgUY/sUR77EzgBMAHJnD5O+om1YvOE7iTQB+AqBHxvUipBCWBxi9/M0VOZNd33RO2xvZIw+Kkw31N72N98+hXqQFv8EOAvBdAL8G8AjKRdAEWOZ4bTfDJtNk5MdmAC5SYYGwSbxBPxfoY11SOqoD/7cBXAPgSR30RiOQSVwmLg4wdPE/dmEXw0S5H/kzQN0tXd7GT2jdiedsr99t8lT+E4DVDoMvb+Iy0UUn8XJ9806M8B0rq5O3AvpoGorjaG1H2DiuUt9q4ulS2GWQg4qIuZEPGKMbRfX+WaLhiK7IaufP+taWzak0ELWPnzlucF1Id0w/l8JxygZ9EJB/ZLA+GE/SeGJXzgro49NS7NzDAKx0GNe7AbRzUP1aCscp8iAg6bHYoJuVJtupd1YtpMjv7pryb5MMl8JxirzNSXqsMgTxp00bgBMBrAkZ39cA7JvB71eWrJbCcYvUg6THDQF9PD3jqKclIWP8DoARGdah1OS1FI5b5GFC0qNdI4/q/fs7lejJkm3VtsJ0uUQDjERkQgtMUlORhwljTrOhZ86bSJ0BXOGwQ122I8NKT2LJMkBah+661B2ewLPqm/q2tY37uSnXuxK04iSWZT1pDQY0fcsuVBG9OHxBww9tY39GyvWvBGe3wKRtLCOL7hDyd+4OGJ87E/TPp3QH2raclsAJ4vGbmOk/WoegzU1RukzCJ0KE6kXa9hsp1b9StMIkdo3OIfnwlEETKyn9Q+KMN6ivNfFsEpctAsl3Dm3afFqf4tntTgCWWmxBwhYZV+zZJOZxQuuxlyYUn6K+2Glvkq202IP8244p/2YlKGpjS1w3SbUYFKKI+TSArYqupI/kPYkZgVRd9gHwtsU2/kDnntZfTjMCqdoMCxGZn1p0BX0lr0nMCKTysIOmQo2qUHlKiI1wZ7qFJzEjkPyngz6IG0MWJblaFKZZbGSV7l6TFpzEjEAqh+xPram8rP7UUQIg7rPYyUOadZG00CRmBFI5uNUwvrJJFYX2kHSoP8io/qVnZEYTmBFI5eAyg39z3xj32sOiQS3ulp/NoP6lprejcFmcwgikctBPfaUbx1ZUK+MyzmIzIs9LgbwI/DLD719RByHlmcSXAbhFNyZlYyuJxtZdFrvhyYUjR2U4eaUwAonYpHleMtiNLM8PNF5J/pctLeFf0oE3JZy8jEAiYRzSJGrfWOa1aJrWlmGqZfJdlcLuNCOQiAtXWWxovNMdKsggi5bRYk2tkdR3WrIGEOKyEjSlOF2nkU2kiQcsE0+WNc3EeRMzBxJx5WiLHc1yvktFsJ35yoG9iShvYkYgkajY0rd8PvLdSoq4s823eE31Cbne9U3MCKTqchiAZwCs1YyJrkvgnSzqlo8zA2J4VIi8YV1wmcQ8x6smeweEDi6K4ON8rsWmKp/pobvl3O2FiOLeYZOYEUjVZIrBHoZGsFGTnpboWHdDhTndMuGOjXE/2yRmBFI1mZzChubxFruSFWQl6WZx2vhbgu+LoEnMCKTqsqcqXDbaw7MRwwQ7GmRv629h2cepHGMjHhslmcSMQKo2/6wa028AuF19qKPyRYu9Sj6mStHRIrb9cEq/0XjENCmle5Jq86jBZhdULfB/lOVpJomp0qL+JmYEEsnaX0FsujI8ZOiE/9awLqQ8iRmBRNKgzfItLJ6ElWBfy1PsmKIrR0gIx1jsVzbMSs8NllC/Su7mEa/oZDkXno6Ss5XFNe2coitHiCPjDTa8puzSOydZGr5N0ZUjxJHtLCJ4J1dxG/4XRVeMkIjcmPExaMsx0PLx7+qXeoZ6voga4bUAts64zqT8tAOYoVkLXwRwpuN1B1nsuZQB/xMsh+AuR0ffDLh2Zg71JuXmzgC7OsHhujaLM1IpxeCfNjT2Asfr7wm4dlPZNw1IpvQy2KSkW3HhQsP1Eq5YKvawLDd2dbzHbE5gkjI9DQqU9zpe/1GLguXgKiyfxcHcleMCrhfJE0KScHuAXY2OcP0jBtsWmy8NfzU08nsxIpgWaepHcQjh8pmk8Ra+TjexFsSI7/2eRXKnNGdmG6u0W0cqxW6Wz8NS5Bf+hqFxsoNHSBmYb7BxcVzynpsNjbuy6IoRkhI/Mtj4r1ACTAr3I4quGCEpcYjBxl/1XXp2F0PDROZz86IrR0hKbGbxjZYjVG8J8p6S8l9FV4yQlPmTwdbF/ddbrjc06pKiK0ZIylwQIzVQy/NsDrpXhLQCnyvbacsWhvNfcT1jFBEpo1jFJsMkFp9r7zjA0BjxdnGhtyb8/guAqwHsmHF9CakjtjYNwINqg2KLSc6DRZfaO0zC7bc5XNs1QP1PdIio2kGyZhuNC260vbmOOZBMQf7n+Ths1xoaI3pCYRxuuPbUHOpNqs1Yg+25aIufYbhWJrZ3PJxgA8vkfnl+DvUm1eZ8g+2JTYYx3HDtHHjIawkcvEWI/b2Aza8hOdSbVJu9Ajaj1jsmB+hnsPnVGSQsyDxEK6gh6zUvkguyZHlFr3ur7Gp/pKUYozYntrcSwBGO14nb5DsG2+8Lj/ikoRGySxcF2czqD6BHRvUkxEQPtb0oSeah6YGCbF9E8LxPPyECYoSUmd+kmLC+MP7V0Igriq4YIRlzpcH2z4JHXGpoBNOnkLJzjsH2L4NH/NzQiMplMieV47gyBPfPSnAGTIjPDDPY/v3wiMcNjdi76IoRkjH7lMGZY6GhETsXXTFCMmZXg+0/D49YaWiESMwSUmY+bLB9cUryhtWGRkiMMCFl18eqBRTRzPKCNksgv4tCXxeV3FmhipaT9G+E5EmXmHbYyTCBZU54QVdDA9Y6Xj8p4NqLM64zIWnZYQeD/csLrBITeEXAtfI3QvJkRUw7bDPYf82XiKTOlkikuELwyzKuMyFp2qFJG8s1Eq9QOlrE3F24OODaiRnXmZA07XCjzxO4LeE3QBftvOX6xJNO4yYWyZsuMe2wm8H+RaDCG943NIITkVRBFK8WUN6ER7xhaARVJUnZ6WuwfXmTe8MiQyPoSknKzoAyuFI+YWjE4KIrRkjG7Gew/b/BIx4wNGJo0RUjJGOOMNj+7+ERvzU0QrSyCCkzJxpsfwY84sdl0AUiJAYTDLbvlS9DKXSBCInBNIPtn44S6AK5JDYjxGfuMdj+KHjE0JRkRSQwYncAm2dUT0JMiM19PIaw+8IynMCkkSPmSw2pVd5lahWSI6eozdXUBl0yE0I9DTcYbH9LeESHhg5oLn0cru9jSG4mKVsIyVqUblOAH7NLcrOPGWxeJKa84zFDYw52uJbpRYmP6UWPMFz7IDzkZkNjJIFyGIcZrmWCb5I1pxpszyVD4fcN117j47D9W4IDbREFeLLpuhcBtOdQb1Jt2gEsabK9J9Umw5hpsHkvU+MeamjMXMfrewGYDGC2nq3JxhghedBPbW625vkSW3ThRYPNi3+0d3zI0BhRK6C8LCkb2xrsfYPP+a2blyJeJjsmxIGRBlt/Bh5zm6FR5xZdMUJSZorB1q+Dx5xlaNS9RVeMkJSZk+D4qWXZ26IR3b3oyhGSotulSQeuPzymo0Uf67NFV46QjE9cvNLBihrc71V8JCEWrjbY+E0oAacZGjev6IoRkgISnLPUYOMSVus9uxgaV1Pnb0J8Zk/L+W9vlIS5hkZ+N+J9xgF4QcMSxde6Z0b1JdVynbwFwBr1pBoXMQnZeINtP4QScVEKjQxS+ZiVYZ1JNZgVYFfHp/ByOg8lwnSctCnCNvu9huuZ7YHEZRtDJsH7Ha8fZPk8lH8rDW0Wt8oLEk5gRiiRtCewq6PRxIQBO96na6ynnHD55hgdcK2EbxGShJkxd4/bdD+m9MvnOrtZlhufdrzHWBUNexXAtdzEIimwNYDpqn31fITYXZNw46Yy5wB7tAyq9YQAuNVgyw+XuXfGGRq9TuMpCfGB3mqzQbZ8EkpMLw1kCGq4ZHMgxOfMI6t9k4+NwwxD42WXulPRlSMkBNHGWmyw4Z+iAgyxbGYdVXTlCAnhqxb73QsV4UFDBzwe0Y2NkDxpUxsNst1HUCGOsTzFJLaSkFbk8xa79Sp5WVLkW3dBFbfhidf82eKMJOIVleIEy9NseIz77aQ6vrLL/WzVnojEypfVJtapm6TYSppv31IfHdkyuZmEsB/TBGlJ3ugbNIiCVJshARkDFzpmWmj89jWJ1r1cZX23sZanWhQ1A5Nb29QM6078YKrBNsRmECHVrclOz0SF6W55C8u5cDfH+3ACExOTDfb1GbjRWcXZg+6xNIKNlhZTKlEpZ0dYQj8fkNNVlk+k2gwOyDX9XASnoe9Y7FP2cSqPfOs+YXFN6+vYQzsCuENlbOUb+ouV71lSZ4TahNjG7RES5Ul+r7cMthnlIVB6hluecr8uunKkssyw2KV8F5MQbaJ6kScoIXlyoEGtQ8p9HIpg+VlTpNJCn1M0Ei83V58z2KKkUNm96Aq2Kudb3sI/LrpypDJcarHDy4quXKs7dzxt6DhZzgwruoKk9HwqwPGjXl6ijFOyb49l7ECSIT0sZ75SjmTvu3GtpRN/kcKx1RhV479cj5+In/TTJa3oU50Y0f026q6z/AaJoNe7LKMD9OlN93ozwrkgaR366dg1juU1GYW4igoqNdsiIvmDNxo6dK0mlYrKDob70WfaPy43jKWr408jIgO7yjKBqRSTshh8TV0nt4p4v30M95LlNPGLWwxj+cmI99kcwJMWO5PPORKTzipVYurcmRG/ezbT8K/m+3ybI1SKePKXIob2SZjgbRb7kg0t+h8kZGeLP2pNz+yiMLRhEstu989S2Pwg+dNBv3kbJ2+UEMEwv4N1MT/TSEQlwDhv0M10Od2Hve09fXUsowbVj7LssdQipFghjkyxdPZ7uulFiAsHWTIrJN3NJpYl0x2WTpdlNiV0SBgf17DCmiXpfNfQu5BYyK7zPEvnS4a5gexbYjk7Xmqxn2UaA0wy3tR6zTIISzNwzJD0pz/RgIp9U743+YD9tI+vArB/Bt/KL1js5m1V7yA5IHpG6y2DsUCdNtJgZNNmh4STHZbSvckHHK59W+/njSoHmwZ9LDrkNbUlBsrkzChL1EhNE1D1T+F3guR+nkrhvuQfCXKmkL8lZXtLbG/9KPFrHIziBPE2hXzTDEj4G6sMG2YkXd7MoJ93AbAo5AjyrJTqT2JySsgAvZTw2yZo51v+RtJlZkA/35XgfoMNXneN5YIU608ScHbIQK2Oma4FuiH2XJMPNkMQ06e5nxcm6OeDQoITpHw/5fqThEwIGTDZIPlWzHuLfOgBKjZAKdHsSKOfvx7ipCHlBynXm6TEmSHfxDWNcMozk9yHKhpL2g7gIzk7+vwwZOxr6v9MWpjRTccRQeUPamBZ0q6/0/jdnPVvtgI9m75nZ+XQ7i1DvPTqx1L0b/YESRK+JmRA5RtrjwzrcEPAb/4c5ef6DGSQbOwZckxUP+f9SoZ1IBlwoOFoorG8q/pYWfBKwO9JfcpOkJ/x6xn91hiLlni9yGbWIRn9PsmYgZrYOey76Deqw5UmzcnWanomWXYWGVY7afvE/4fDuMoY0Dfec2Sw73QYbHH6+FyKv3tywG+cFvFbUv7/iwqKspLMjv8O4NSIUr6nBbRb7pEWwywpaWsN5f4MHsqkIDroRAjboa4rdGyd0u8eq5s4syMmLJfzzxVN9cpzA+ZfmvpqecQAkeO0zbNUjCENemiQQ9gY1gBcqXJMpGR8SZ06wgxguTrXF8XVhmgZEWBzzXBxiT4EpC2T9G8ubKG/1fz78mArii+ERBLVGlwvqSBZcnYFMMfBGOqpTXcqoI73GerzUcfrJxnOv139h01L0rzpq/sTLmP1mNadVIDO6o1ji2aql7W6/O5RcHKtVyIoRSw3rCpc6GrYQZ+M/Oim7rHvOIzPJo0hlmtIxdjfcWlW3+Q6PidXyl5NYYzrNS4ZCSaw1N+VI5virSWsrzfy2auQCLMljmOyBMDBOdSLtDDyzXed4+aIlPnqFNAhh1XC4eq/LTGtSQXxJ0a8x/b62yMjfD8n/c61Caw3l+tiCPuTEjPUkto0qDyhihGtqCndRSfxcn3zTsxpEkalgz4gHo3Q7wsSRJaRktM5wrdXo0GdrFrTxI1Oerw0N0I/S4TRhTH0n0kF2SHC7mdjBjvZ7GKmQ3tk1vgQZcigIufJH8tx/ElJEM+shyMam0S93A3gCMYO/z3/kATY3xQiRBhUZGnNTSqSmMMjbrA0yvlcrnKpYshVYqAe1S2O0W/zdX+han1GMt5wOdYhdM1UFqmDxadzFhTIk08AOC+Co0xzWapZB6l6QjKjk2Zz/2tMI61/L98I4OiczlezPIIbAeAKB/XHsB390S26U05KzAHqbuni0WUqmzRdzDR9w7fyJti2OmEv0b2B9xO2WxRLKKhOCkcE5Kdq4HothfK6RvP8UCf1kJydFsSdcjc9oxUNqd86hvC5FAmUmA5gUI7tIcSJLmr0v4ux4+pSVgJ4UCVqJN3qdzR07xDNkbu7PkzaNYa3ufRRofshusMu0Vlj9fhrhr4RFyZcUZh25u/VujLjPfGCXhrI/kgEN82ylWd0U0uiigjxlm11k+aXhljbspQNugM9Qd/yhJSO7uq4f7Wed9Y8L+JvfbN+q1dBNpeQ/6dpfLC+tWY7yOEW/Yadp/K4YzTbPSGkKaBisJ41y+bSbRol9V7Ok3WxbmpN0cl6gD5sCCExJ/YA9SuWSJ4zVLnjRpXgmaOyMgt18r2hmshr9L+X67/N0//3PwH8Sp0wztNA+hEqdu+qvUUIIYQQQgghhBBCCCGEEEIIIYQQQgghhBBCCCGEEEIIIYQQQgghhBBCCCGEEEIIIYQQeMr/AKhzKQEngzvoAAAAAElFTkSuQmCC"
), Text(origin={0,-112}, 
lineColor={0,128,0}, 
extent={{-70,8},{70,-8}}, 
textString="%name", 
textStyle={TextStyle.None}, 
textColor={0,128,0}, 
horizontalAlignment=LinePattern.None)}));
equation
  connect(z_on.y, vectorAdd.u1) 
  annotation(Line(origin={-172,0}, 
points={{-16,6},{-3.5,6},{-3.5,-6},{15,-6}}, 
color={0,0,127}));
  connect(z_off.y, vectorAdd.u2) 
  annotation(Line(origin={-172,-25}, 
points={{-16,-7},{-3,-7},{-3,7},{15,7}}, 
color={0,0,127}));
  connect(vectorAdd.y, vectorAdd1.u2) 
  annotation(Line(origin={-48,-6}, 
points={{-86,-6},{85,-6},{85,6}}, 
color={0,0,127}));
  connect(gain.y, vectorAdd1.u1) 
  annotation(Line(origin={41,37}, 
points={{-11,29},{-4,29},{-4,-25}}, 
color={0,0,127}));
  connect(xy2.y, add3_1.u1) 
  annotation(Line(origin={-81,88}, 
  points={{-18,-4},{17,-4},{17,4}}, 
  color={0,0,127}));
  connect(xy3.y, add3_1.u2) 
  annotation(Line(origin={-98,84}, 
points={{-35,0},{34,0}}, 
color={0,0,127}));
  connect(xy4.y, add3_1.u3) 
  annotation(Line(origin={-114,68}, 
  points={{-51,-8},{50,-8},{50,8}}, 
  color={0,0,127}));
  connect(xy7.y, add3_2.u1) 
  annotation(Line(origin={-98,63}, 
points={{-34,-3},{34,-3},{34,3}}, 
color={0,0,127}));
  connect(xy1.y, add3_2.u2) 
  annotation(Line(origin={-81,59}, 
  points={{-18,1},{17,1},{17,-1}}, 
  color={0,0,127}));
  connect(xy5.y, add3_2.u3) 
  annotation(Line(origin={-98,43}, 
  points={{-35,-7},{34,-7},{34,7}}, 
  color={0,0,127}));
  connect(xy6.y, add3_3.u3) 
  annotation(Line(origin={-77,30}, 
points={{-22,6},{48.5,6},{48.5,28}}, 
color={0,0,127}));
  connect(add3_1.y, add3_3.u1) 
  annotation(Line(origin={-35,79}, 
  points={{-6,5},{6.5,5},{6.5,-5}}, 
  color={0,0,127}));
  connect(add3_2.y, add3_3.u2) 
  annotation(Line(origin={-35,62}, 
  points={{-6,-4},{6.5,-4},{6.5,4}}, 
  color={0,0,127}));
  connect(add3_3.y, gain.u) 
  annotation(Line(origin={1,62}, 
points={{-6.5,4},{6,4}}, 
color={0,0,127}));
  connect(vectorAdd1.y, y) 
  annotation(Line(origin={80,8}, 
points={{-20,-2},{18,-2}}, 
color={0,0,127}));
  end Patrol;