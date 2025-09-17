#!/bin/bash
# Create a sample MIP file for Mixed Integer Programming example and solve it with custom parameters using cuopt_cli

echo "* Optimal solution -28
NAME          MIP_SAMPLE
ROWS
 N  OBJ
 L  C1
 L  C2
 L  C3
COLUMNS
 MARK0001  'MARKER'                 'INTORG'
   X1        OBJ             -7
   X1        C1              -1
   X1        C2               5
   X1        C3              -2
   X2        OBJ             -2
   X2        C1               2
   X2        C2               1
   X2        C3              -2
 MARK0001  'MARKER'                 'INTEND'
RHS
   RHS       C1               4
   RHS       C2              20
   RHS       C3              -7
BOUNDS
 UP BOUND     X1               10
 UP BOUND     X2               10
ENDATA" > mip_sample.mps

cuopt_cli --mip-absolute-gap 0.01 --time-limit 10 mip_sample.mps
