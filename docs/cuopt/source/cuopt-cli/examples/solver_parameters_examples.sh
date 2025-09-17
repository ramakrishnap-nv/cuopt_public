#!/bin/bash
# Examples of using various solver parameters

# Create a sample MPS file for LP
echo "* optimize
*  cost = -0.2 * VAR1 + 0.1 * VAR2
* subject to
*  3 * VAR1 + 4 * VAR2 <= 5.4
*  2.7 * VAR1 + 10.1 * VAR2 <= 4.9
NAME          SAMPLE
ROWS
 N  COST
 L  ROW1
 L  ROW2
COLUMNS
 VAR1      COST                -0.2
 VAR1      ROW1                3.0
 VAR1      ROW2                2.7
 VAR2      COST                0.1
 VAR2      ROW1                4.0
 VAR2      ROW2               10.1
RHS
 RHS1      ROW1                5.4
 RHS1      ROW2                4.9
ENDATA" > sample.mps

# Create a sample MIP file for MIP
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


# Set absolute primal tolerance and PDLP solver mode
cuopt_cli --absolute-primal-tolerance 0.0001 --pdlp-solver-mode 1 sample.mps

# Set time limit and use specific solver method
cuopt_cli --time-limit 5 --method pdlp sample.mps

# Turn off output to console and output the logs to a .log file and solution to a .sol file
cuopt_cli --log-to-console false --log-file mip_sample.log --solution-file mip_sample.sol mip_sample.mps

