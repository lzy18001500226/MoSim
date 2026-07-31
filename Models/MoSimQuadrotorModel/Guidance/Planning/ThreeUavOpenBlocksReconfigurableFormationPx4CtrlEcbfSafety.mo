within MoSimQuadrotorModel.Guidance.Planning;
model ThreeUavOpenBlocksReconfigurableFormationPx4CtrlEcbfSafety
  "Three PX4CTRL loops with a pairwise ECBF reference-safety branch over the frozen OpenBlocks route"
  parameter Real planned_clearance_m[3] = {0.446636389524, 0.44832134251, 0.445867622045};
  parameter Real transit_start_s = 27;
  parameter Real arrival_phase_s = 295.840532932;

  PlannedQuinticPx4CtrlReference reference1(
    n_segments = 40,
    p_x = {
      -41, -41, -36.270083617, -32.3576787813, -29.9329913237, -28.6986328768,
      -27.0287217, -25.1472034564, -23.4, -17.5769016719, -16.2187204901, -14.2154541042,
      -12.1723866214, -7.16135537291, -4.33416809794, -3.7, 1.23539455558, 3.24091535806,
      8.25005056, 13.5683655975, 18.2208954639, 20.6776331257, 22.5480391867, 24.0899247908,
      25.0028120574, 26.0664069464, 26.7151848149, 28.2800462208, 30.6984106459, 32.1821388021,
      33.6519277123, 34.1582008164, 35.8197165584, 37.1752690239, 37.7571088917, 38.5577682719,
      39.4905565016, 40.1171208256, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41},
    p_y = {
      -26, -26, -25.1025251761, -24.4078120894, -22.339982579, -20.8395757566,
      -20.126964068, -19.339007232, -18.1002871845, -17.866120694, -18.1342396217, -17.4056203098,
      -16.231589448, -14.7436448406, -11.165428449, -6.7496, -1.30286033586, 2.75609190795,
      4.6, 9.89314171241, 14.3395373799, 15.6856038358, 16.9761823103, 16.729387666,
      16.0340602407, 16.1171793452, 16.9182710874, 17.1141529814, 17.2826144613, 16.4915010876,
      16.5465395027, 17.7089911979, 19.132073954, 20.4549732035, 21.6717350541, 22.3661889881,
      22.8463068907, 24.0977359464, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26},
    p_z = {
      1.5, 2.28, 1.57, 1.43, 1.51, 1.78,
      1.62, 1.46, 1.28, 1.72, 1.72, 2.09,
      1.99, 1.78, 2.01, 2.44, 2.42, 2.5,
      2.02, 2.33, 2.1, 2.33, 2.16, 2.1,
      1.98, 1.76, 1.75, 1.99, 1.7, 2.04,
      2, 1.97, 2.3, 2.25, 2.03, 2.1,
      1.9, 1.63, 1.46, 1.46, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68},
    segment_duration = {
      3, 9.90067874713, 8.08933646082, 6.485391251, 3.99082673749, 3.70817179377,
      4.1628317652, 4.37278891983, 11.8904442638, 2.81655469798, 4.40171317268, 4.79835937943,
      10.6434986512, 9.28981020008, 9.1182633344, 14.9540274272, 9.21242447674, 10.9034736592,
      15.2788393693, 13.1015451375, 5.71849973042, 4.63622251914, 3.17924807017, 2.34740236694,
      2.2161569978, 2.09737723339, 3.2455051357, 4.96726259576, 3.49017551677, 2.99349540334,
      2.58030000107, 4.5011325783, 3.85488268883, 2.78024425684, 2.16100629559, 2.17283544822,
      2.89983554525, 4.28068026343, 81.59929084, 3, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1})
    annotation(Placement(transformation(origin = {-82, 74}, extent = {{-18, -18}, {18, 18}})));
  PlannedQuinticPx4CtrlReference reference2(
    n_segments = 44,
    p_x = {
      -43, -43, -43, -37.0356816978, -32.3837818224, -30.1767088657,
      -28.5892368268, -27.9119795321, -25.4438531368, -23.4, -17.5422100286, -16.1172296833,
      -14.1375848899, -12.2309248586, -7.18816645189, -5.05562741104, -3.94786742907, -4.12236320724,
      -3.7, 3.58608509107, 7.68827958007, 8.93119242189, 9.2, 13.933630549,
      18.2368897596, 20.5408613227, 22.5480569164, 24.0899249656, 25.002812169, 26.0664069956,
      26.7151848353, 28.2800462257, 30.698410646, 32.1821388022, 33.6519277153, 34.1582008507,
      35.8310555146, 37.2159819265, 37.793620005, 37.9741947133, 38.8333200663, 40.4478580515,
      43, 43, 43, 43, 43, 43,
      43, 43, 43, 43, 43, 43,
      43, 43, 43, 43, 43, 43,
      43, 43, 43, 43, 43, 43,
      43, 43, 43, 43, 43, 43,
      43, 43, 43, 43, 43, 43,
      43, 43, 43, 43, 43, 43,
      43, 43, 43, 43, 43, 43,
      43},
    p_y = {
      -26, -26, -26, -25.0946505583, -24.4505164346, -22.5472773097,
      -20.7403325188, -20.7828714435, -19.5259559877, -18.0820358547, -17.866100949, -18.1219115002,
      -17.4004097087, -16.2402957413, -14.7866558094, -12.2012884807, -10.7275416185, -9.98227384805,
      -6.7076, 0.9, 1.63146374207, 3.2301825558, 5.36987572756, 10.1894617507,
      14.3564382526, 15.6512146483, 16.9761971211, 16.7293878117, 16.0340602351, 16.1171793705,
      16.9182711065, 17.1141529861, 17.2826144613, 16.4915010877, 16.5465395051, 17.7089912229,
      19.1433436742, 20.4897656985, 21.7922435261, 22.4378414287, 22.4472954786, 23.7781526257,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26},
    p_z = {
      1.5, 2.28, 2.28, 1.89, 1.43, 1.73,
      1.74, 1.55, 1.56, 1.28, 1.72, 2,
      2.2, 2.08, 1.78, 2.09, 2.08, 2.37,
      2.44, 2.5, 2.2, 2.18, 2.11, 2.41,
      2.1, 2.29, 2.16, 2.1, 1.98, 1.76,
      1.75, 1.99, 1.7, 2.04, 2, 1.97,
      2.3, 2.14, 2.01, 2.03, 1.81, 1.75,
      1.97, 1.97, 1.19, 1.19, 1.19, 1.19,
      1.19, 1.19, 1.19, 1.19, 1.19, 1.19,
      1.19, 1.19, 1.19, 1.19, 1.19, 1.19,
      1.19, 1.19, 1.19, 1.19, 1.19, 1.19,
      1.19, 1.19, 1.19, 1.19, 1.19, 1.19,
      1.19, 1.19, 1.19, 1.19, 1.19, 1.19,
      1.19, 1.19, 1.19, 1.19, 1.19, 1.19,
      1.19, 1.19, 1.19, 1.19, 1.19, 1.19,
      1.19},
    segment_duration = {
      3, 12, 15.3738242963, 12.0004232803, 7.45076347438, 6.11686145599,
      1.8310546875, 7.04387031777, 6.40376522063, 14.9491862002, 3.75006970105, 5.38252948682,
      5.68412188183, 13.3683793895, 8.55942168964, 4.68872487521, 2.08160064195, 8.39879701842,
      26.7894750078, 10.6243983684, 5.15016102851, 5.48718231747, 17.1968477577, 15.2540905397,
      6.73849755006, 6.12536477604, 3.97402192737, 2.93425306334, 2.7701960983, 2.62172148354,
      4.05688137624, 6.20907823173, 4.36271939608, 3.74186926179, 3.22537508568, 5.6665111512,
      4.92900183567, 3.63855757203, 1.8310546875, 2.25549493676, 5.32329952918, 8.62359143811,
      4.22749489384, 3, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1})
    annotation(Placement(transformation(origin = {-82, 4}, extent = {{-18, -18}, {18, 18}})));
  PlannedQuinticPx4CtrlReference reference3(
    n_segments = 35,
    p_x = {
      -41, -41, -41, -34.852176589, -30.0253057323, -26.6123427893,
      -23.695189143, -21.6823817835, -19.8587920515, -18, -11.3232837581, -7.14701535504,
      -6.63734108529, -4.93294026125, -4.13238887287, -3.7, 1.23863782085, 3.24091535806,
      8.25005056, 13.5683655975, 18.2208954639, 20.677633127, 22.5480391926, 24.0899249735,
      25.0793018179, 26.2159262274, 26.5579527521, 27.2287247892, 29.4022623207, 33.1703745116,
      34.1711251948, 35.3285657992, 35.5041113176, 36.4938184318, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41},
    p_y = {
      -28, -28, -28, -27.3070403698, -27.0481925793, -25.3040221331,
      -24.603368557, -23.1691494331, -22.2331680977, -21.0698756176, -15.3, -14.7007750977,
      -14.8003803015, -12.153834878, -9.93135310359, -6.7328, -1.29860331268, 2.75609931675,
      4.6, 9.89314171242, 14.33953738, 15.6856038372, 16.9761823167, 16.7293878763,
      16.0333596101, 16.2222810949, 17.1348314642, 17.1327298249, 17.6071922994, 18.3578564276,
      20.0006229443, 20.925340079, 21.9982254539, 24.2071056683, 28, 28,
      28, 28, 28, 28, 28, 28,
      28, 28, 28, 28, 28, 28,
      28, 28, 28, 28, 28, 28,
      28, 28, 28, 28, 28, 28,
      28, 28, 28, 28, 28, 28,
      28, 28, 28, 28, 28, 28,
      28, 28, 28, 28, 28, 28,
      28, 28, 28, 28, 28, 28,
      28, 28, 28, 28, 28, 28,
      28},
    p_z = {
      1.32, 2.1, 2.1, 1.75, 1.49, 1.91,
      1.93, 1.88, 1.42, 1.55, 2.1, 1.79,
      1.75, 2.19, 2.37, 2.44, 2.42, 2.5,
      2.02, 2.33, 2.1, 2.33, 2.16, 2.1,
      1.98, 2.16, 1.92, 1.9, 1.87, 1.89,
      2.18, 2.23, 2.14, 2.04, 1.69, 0.91,
      0.91, 0.91, 0.91, 0.91, 0.91, 0.91,
      0.91, 0.91, 0.91, 0.91, 0.91, 0.91,
      0.91, 0.91, 0.91, 0.91, 0.91, 0.91,
      0.91, 0.91, 0.91, 0.91, 0.91, 0.91,
      0.91, 0.91, 0.91, 0.91, 0.91, 0.91,
      0.91, 0.91, 0.91, 0.91, 0.91, 0.91,
      0.91, 0.91, 0.91, 0.91, 0.91, 0.91,
      0.91, 0.91, 0.91, 0.91, 0.91, 0.91,
      0.91, 0.91, 0.91, 0.91, 0.91, 0.91,
      0.91},
    segment_duration = {
      3, 24, 15.7588865412, 12.3107752042, 9.80569202903, 7.62986110947,
      6.28666942621, 5.34247747265, 5.58636176443, 22.4851522119, 10.7584948312, 1.8310546875,
      8.08331254067, 6.02497201727, 8.21025976391, 18.6744550634, 11.5021901578, 13.6293355914,
      19.0985492117, 16.376931422, 7.14812466736, 5.7952781658, 3.97406044947, 3.09147096524,
      2.96578245177, 2.5524354752, 1.8310546875, 5.65827046625, 9.77124149246, 4.94721364659,
      3.7697329417, 2.77422808532, 6.16082307138, 15.0053853199, 3, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1})
    annotation(Placement(transformation(origin = {-82, -66}, extent = {{-18, -18}, {18, 18}})));

  OpenBlocksMapTruthDisplay navigationDisplay(
    n_segments = 40,
    p_x = {
      -41, -41, -36.270083617, -32.3576787813, -29.9329913237, -28.6986328768,
      -27.0287217, -25.1472034564, -23.4, -17.5769016719, -16.2187204901, -14.2154541042,
      -12.1723866214, -7.16135537291, -4.33416809794, -3.7, 1.23539455558, 3.24091535806,
      8.25005056, 13.5683655975, 18.2208954639, 20.6776331257, 22.5480391867, 24.0899247908,
      25.0028120574, 26.0664069464, 26.7151848149, 28.2800462208, 30.6984106459, 32.1821388021,
      33.6519277123, 34.1582008164, 35.8197165584, 37.1752690239, 37.7571088917, 38.5577682719,
      39.4905565016, 40.1171208256, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41, 41, 41, 41, 41, 41,
      41},
    p_y = {
      -26, -26, -25.1025251761, -24.4078120894, -22.339982579, -20.8395757566,
      -20.126964068, -19.339007232, -18.1002871845, -17.866120694, -18.1342396217, -17.4056203098,
      -16.231589448, -14.7436448406, -11.165428449, -6.7496, -1.30286033586, 2.75609190795,
      4.6, 9.89314171241, 14.3395373799, 15.6856038358, 16.9761823103, 16.729387666,
      16.0340602407, 16.1171793452, 16.9182710874, 17.1141529814, 17.2826144613, 16.4915010876,
      16.5465395027, 17.7089911979, 19.132073954, 20.4549732035, 21.6717350541, 22.3661889881,
      22.8463068907, 24.0977359464, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26, 26, 26, 26, 26, 26,
      26},
    p_z = {
      1.5, 2.28, 1.57, 1.43, 1.51, 1.78,
      1.62, 1.46, 1.28, 1.72, 1.72, 2.09,
      1.99, 1.78, 2.01, 2.44, 2.42, 2.5,
      2.02, 2.33, 2.1, 2.33, 2.16, 2.1,
      1.98, 1.76, 1.75, 1.99, 1.7, 2.04,
      2, 1.97, 2.3, 2.25, 2.03, 2.1,
      1.9, 1.63, 1.46, 1.46, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68, 0.68, 0.68, 0.68, 0.68, 0.68,
      0.68},
    segment_duration = {
      3, 9.90067874713, 8.08933646082, 6.485391251, 3.99082673749, 3.70817179377,
      4.1628317652, 4.37278891983, 11.8904442638, 2.81655469798, 4.40171317268, 4.79835937943,
      10.6434986512, 9.28981020008, 9.1182633344, 14.9540274272, 9.21242447674, 10.9034736592,
      15.2788393693, 13.1015451375, 5.71849973042, 4.63622251914, 3.17924807017, 2.34740236694,
      2.2161569978, 2.09737723339, 3.2455051357, 4.96726259576, 3.49017551677, 2.99349540334,
      2.58030000107, 4.5011325783, 3.85488268883, 2.78024425684, 2.16100629559, 2.17283544822,
      2.89983554525, 4.28068026343, 81.59929084, 3, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1,
      1, 1, 1, 1, 1, 1})
    annotation(Placement(transformation(origin = {2, 116}, extent = {{-22, -22}, {22, 22}})));

  ThreeUavPairwiseEcbfReferenceSafetyFilter safetyFilter(
    pair_minimum_distance_m = 1.0,
    pair_activation_distance_m = 1.5,
    ecbf_lambda = 1.0,
    prediction_horizon_s = 0.8,
    reference_lookahead_s = 0.35,
    max_reference_offset_m = 0.5,
    max_safety_acceleration_correction_m_s2 = 1.5,
    projection_passes = 2)
    annotation(Placement(transformation(origin = {-2, 0}, extent = {{-20, -60}, {20, 60}})));
  ThreeUavPairwiseEcbfReferenceSmoother safetySmoother(
    correction_time_constant_s = 0.20,
    correction_damping_ratio = 1.0,
    maximum_correction_acceleration_m_s2 = 1.5)
    annotation(Placement(transformation(origin = {26, -102}, extent = {{-18, -18}, {18, 18}})));

  OpenBlocksPx4CtrlVehicle vehicle1(initial_position = {-41, -26, 1.5})
    annotation(Placement(transformation(origin = {70, 74}, extent = {{-22, -22}, {22, 22}})));
  OpenBlocksPx4CtrlVehicle vehicle2(initial_position = {-43, -26, 1.5})
    annotation(Placement(transformation(origin = {70, 4}, extent = {{-22, -22}, {22, 22}})));
  OpenBlocksPx4CtrlVehicle vehicle3(initial_position = {-41, -28, 1.32})
    annotation(Placement(transformation(origin = {70, -66}, extent = {{-22, -22}, {22, 22}})));

  Modelica.Blocks.Continuous.Derivative velocityEstimator1[3](
    each k = 1, each T = 0.05,
    each initType = Modelica.Blocks.Types.Init.InitialOutput, each y_start = 0)
    annotation(Placement(transformation(origin = {38, 48}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Continuous.Derivative velocityEstimator2[3](
    each k = 1, each T = 0.05,
    each initType = Modelica.Blocks.Types.Init.InitialOutput, each y_start = 0)
    annotation(Placement(transformation(origin = {38, -10}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Continuous.Derivative velocityEstimator3[3](
    each k = 1, each T = 0.05,
    each initType = Modelica.Blocks.Types.Init.InitialOutput, each y_start = 0)
    annotation(Placement(transformation(origin = {38, -68}, extent = {{-10, -10}, {10, 10}})));

  Real pair_distance_12_m;
  Real pair_distance_13_m;
  Real pair_distance_23_m;
  Real min_inter_uav_distance_m;
  Real reference_pair_distance_12_m;
  Real reference_pair_distance_13_m;
  Real reference_pair_distance_23_m;
  Real nominal_reference_pair_distance_12_m;
  Real nominal_reference_pair_distance_13_m;
  Real nominal_reference_pair_distance_23_m;
  Real formation_distance_error_m;
  Real nominal_formation_deviation_m;
  Real nominal_tracking_error_1_m;
  Real nominal_tracking_error_2_m;
  Real nominal_tracking_error_3_m;
  Real actual_clearance_lower_bound_m;
  Real safety_minimum_predicted_pair_distance_m;
  Integer safety_active_pair_count;
  Real safety_maximum_reference_offset_m;
  Real safety_requested_reference_offset_m;
  Real safety_maximum_ecbf_residual_m2_s2;
  Boolean safety_correction_saturated;
  Integer formation_mode "1 launch triangle, 2 corridor column, 3 arrival triangle";

equation
  connect(reference1.position_command, safetyFilter.nominal_position_1) annotation(Line(points = {{-64, 81.2}, {-42, 81.2}, {-42, 50.4}, {-26, 50.4}}, color = {0, 0, 127}));
  connect(reference1.velocity_command, safetyFilter.nominal_velocity_1) annotation(Line(points = {{-64, 74}, {-40, 74}, {-40, 38.4}, {-26, 38.4}}, color = {0, 0, 127}));
  connect(reference1.acceleration_command, safetyFilter.nominal_acceleration_1) annotation(Line(points = {{-64, 66.8}, {-38, 66.8}, {-38, 26.4}, {-26, 26.4}}, color = {0, 0, 127}));
  connect(reference2.position_command, safetyFilter.nominal_position_2) annotation(Line(points = {{-64, 11.2}, {-42, 11.2}, {-42, 7.2}, {-26, 7.2}}, color = {0, 0, 127}));
  connect(reference2.velocity_command, safetyFilter.nominal_velocity_2) annotation(Line(points = {{-64, 4}, {-40, 4}, {-40, -7.2}, {-26, -7.2}}, color = {0, 0, 127}));
  connect(reference2.acceleration_command, safetyFilter.nominal_acceleration_2) annotation(Line(points = {{-64, -3.2}, {-38, -3.2}, {-38, -21.6}, {-26, -21.6}}, color = {0, 0, 127}));
  connect(reference3.position_command, safetyFilter.nominal_position_3) annotation(Line(points = {{-64, -58.8}, {-42, -58.8}, {-42, -36}, {-26, -36}}, color = {0, 0, 127}));
  connect(reference3.velocity_command, safetyFilter.nominal_velocity_3) annotation(Line(points = {{-64, -66}, {-40, -66}, {-40, -50.4}, {-26, -50.4}}, color = {0, 0, 127}));
  connect(reference3.acceleration_command, safetyFilter.nominal_acceleration_3) annotation(Line(points = {{-64, -73.2}, {-38, -73.2}, {-38, -64.8}, {-26, -64.8}}, color = {0, 0, 127}));

  connect(reference1.position_command, safetySmoother.nominal_position_1);
  connect(reference1.velocity_command, safetySmoother.nominal_velocity_1);
  connect(reference1.acceleration_command, safetySmoother.nominal_acceleration_1);
  connect(reference2.position_command, safetySmoother.nominal_position_2);
  connect(reference2.velocity_command, safetySmoother.nominal_velocity_2);
  connect(reference2.acceleration_command, safetySmoother.nominal_acceleration_2);
  connect(reference3.position_command, safetySmoother.nominal_position_3);
  connect(reference3.velocity_command, safetySmoother.nominal_velocity_3);
  connect(reference3.acceleration_command, safetySmoother.nominal_acceleration_3);

  connect(vehicle1.position, safetyFilter.actual_position_1) annotation(Line(points = {{96.4, 87.2}, {106, 87.2}, {106, 100}, {-54, 100}, {-54, 50.4}, {-26, 50.4}}, color = {0, 0, 127}));
  connect(vehicle2.position, safetyFilter.actual_position_2) annotation(Line(points = {{96.4, 17.2}, {104, 17.2}, {104, 7.2}, {-26, 7.2}}, color = {0, 0, 127}));
  connect(vehicle3.position, safetyFilter.actual_position_3) annotation(Line(points = {{96.4, -52.8}, {104, -52.8}, {104, -36}, {-26, -36}}, color = {0, 0, 127}));
  connect(vehicle1.position, velocityEstimator1.u) annotation(Line(points = {{96.4, 87.2}, {104, 87.2}, {104, 48}, {50, 48}}, color = {0, 0, 127}));
  connect(vehicle2.position, velocityEstimator2.u) annotation(Line(points = {{96.4, 17.2}, {104, 17.2}, {104, -10}, {50, -10}}, color = {0, 0, 127}));
  connect(vehicle3.position, velocityEstimator3.u) annotation(Line(points = {{96.4, -52.8}, {104, -52.8}, {104, -68}, {50, -68}}, color = {0, 0, 127}));
  connect(velocityEstimator1.y, safetyFilter.actual_velocity_1) annotation(Line(points = {{49, 48}, {58, 48}, {58, 92}, {-50, 92}, {-50, 38.4}, {-26, 38.4}}, color = {0, 0, 127}));
  connect(velocityEstimator2.y, safetyFilter.actual_velocity_2) annotation(Line(points = {{49, -10}, {58, -10}, {58, -7.2}, {-26, -7.2}}, color = {0, 0, 127}));
  connect(velocityEstimator3.y, safetyFilter.actual_velocity_3) annotation(Line(points = {{49, -68}, {58, -68}, {58, -50.4}, {-26, -50.4}}, color = {0, 0, 127}));

  connect(safetyFilter.safe_position_1, safetySmoother.raw_safe_position_1);
  connect(safetyFilter.safe_position_2, safetySmoother.raw_safe_position_2);
  connect(safetyFilter.safe_position_3, safetySmoother.raw_safe_position_3);

  connect(safetySmoother.safe_position_1, vehicle1.position_reference);
  connect(safetySmoother.safe_velocity_1, vehicle1.velocity_reference);
  connect(safetySmoother.safe_acceleration_1, vehicle1.acceleration_reference);
  connect(safetySmoother.safe_position_2, vehicle2.position_reference);
  connect(safetySmoother.safe_velocity_2, vehicle2.velocity_reference);
  connect(safetySmoother.safe_acceleration_2, vehicle2.acceleration_reference);
  connect(safetySmoother.safe_position_3, vehicle3.position_reference);
  connect(safetySmoother.safe_velocity_3, vehicle3.velocity_reference);
  connect(safetySmoother.safe_acceleration_3, vehicle3.acceleration_reference);
  connect(vehicle1.position, navigationDisplay.actual_position) annotation(Line(points = {{96.4, 87.2}, {108, 87.2}, {108, 136}, {-34, 136}, {-34, 122.6}, {-24.4, 122.6}}, color = {0, 0, 127}));
  connect(safetySmoother.safe_position_1, navigationDisplay.reference_position);

  pair_distance_12_m = sqrt(sum((vehicle1.position[i] - vehicle2.position[i]) ^ 2 for i in 1:3));
  pair_distance_13_m = sqrt(sum((vehicle1.position[i] - vehicle3.position[i]) ^ 2 for i in 1:3));
  pair_distance_23_m = sqrt(sum((vehicle2.position[i] - vehicle3.position[i]) ^ 2 for i in 1:3));
  min_inter_uav_distance_m = min(pair_distance_12_m, min(pair_distance_13_m, pair_distance_23_m));
  reference_pair_distance_12_m = sqrt(sum((safetySmoother.safe_position_1[i] - safetySmoother.safe_position_2[i]) ^ 2 for i in 1:3));
  reference_pair_distance_13_m = sqrt(sum((safetySmoother.safe_position_1[i] - safetySmoother.safe_position_3[i]) ^ 2 for i in 1:3));
  reference_pair_distance_23_m = sqrt(sum((safetySmoother.safe_position_2[i] - safetySmoother.safe_position_3[i]) ^ 2 for i in 1:3));
  nominal_reference_pair_distance_12_m = sqrt(sum((reference1.position_command[i] - reference2.position_command[i]) ^ 2 for i in 1:3));
  nominal_reference_pair_distance_13_m = sqrt(sum((reference1.position_command[i] - reference3.position_command[i]) ^ 2 for i in 1:3));
  nominal_reference_pair_distance_23_m = sqrt(sum((reference2.position_command[i] - reference3.position_command[i]) ^ 2 for i in 1:3));
  formation_distance_error_m = (abs(pair_distance_12_m - reference_pair_distance_12_m) + abs(pair_distance_13_m - reference_pair_distance_13_m) + abs(pair_distance_23_m - reference_pair_distance_23_m)) / 3;
  nominal_formation_deviation_m = (abs(reference_pair_distance_12_m - nominal_reference_pair_distance_12_m) + abs(reference_pair_distance_13_m - nominal_reference_pair_distance_13_m) + abs(reference_pair_distance_23_m - nominal_reference_pair_distance_23_m)) / 3;
  nominal_tracking_error_1_m = sqrt(sum((vehicle1.position[i] - reference1.position_command[i]) ^ 2 for i in 1:3));
  nominal_tracking_error_2_m = sqrt(sum((vehicle2.position[i] - reference2.position_command[i]) ^ 2 for i in 1:3));
  nominal_tracking_error_3_m = sqrt(sum((vehicle3.position[i] - reference3.position_command[i]) ^ 2 for i in 1:3));
  actual_clearance_lower_bound_m = min(planned_clearance_m[1] - nominal_tracking_error_1_m, min(planned_clearance_m[2] - nominal_tracking_error_2_m, planned_clearance_m[3] - nominal_tracking_error_3_m));
  safety_minimum_predicted_pair_distance_m = safetyFilter.minimum_predicted_pair_distance_m;
  safety_active_pair_count = safetyFilter.active_pair_count;
  safety_maximum_reference_offset_m = safetySmoother.maximum_applied_reference_offset_m;
  safety_requested_reference_offset_m = safetyFilter.maximum_reference_offset_m;
  safety_maximum_ecbf_residual_m2_s2 = safetyFilter.maximum_ecbf_residual_m2_s2;
  safety_correction_saturated = safetyFilter.correction_saturated;
  formation_mode = if time < transit_start_s then 1 else if time < arrival_phase_s then 2 else 3;

  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 304.840532932, Tolerance = 0.0001, Interval = 0.05));
  annotation(__MWORKS(hide=false));
end ThreeUavOpenBlocksReconfigurableFormationPx4CtrlEcbfSafety;
