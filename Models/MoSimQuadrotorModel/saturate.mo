within MoSimQuadrotorModel;
function saturate
  input Real u;
  input Real limit;
  output Real y;
algorithm
  y := if u > limit then limit else if u < -limit then -limit else u;
  annotation(__MWORKS(hide=true));
end saturate;
