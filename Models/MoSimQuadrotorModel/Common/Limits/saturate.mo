within MoSimQuadrotorModel.Common.Limits;
function saturate
  input Real u;
  input Real limit;
  output Real y;
algorithm
  y := if u > limit then limit else if u < -limit then -limit else u;
  annotation(__MWORKS(hide=true,version="26.3.0"));
end saturate;