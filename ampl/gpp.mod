set V;
set E within {V,V};
param n := card(V);

var x {V} binary;
var y {E} binary;

minimize z: sum {(i,j) in E} y[i,j];

subject to
Equipart: sum {i in V} x[i] = n/2;
AcrossLR {(i,j) in E}: x[i] - x[j] <= y[i,j];
AcrossRL {(i,j) in E}: x[j] - x[i] <= y[i,j];