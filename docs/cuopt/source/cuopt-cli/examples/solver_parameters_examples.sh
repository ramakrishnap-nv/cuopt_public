#!/bin/bash
# Examples of using various solver parameters

# Set absolute primal tolerance and PDLP solver mode
cuopt_cli --absolute-primal-tolerance 0.0001 --pdlp-solver-mode 1 sample.mps

# Set time limit and use specific solver method
cuopt_cli --time-limit 5 --method pdlp sample.mps

# Turn off output to console and output the logs to a .log file and solution to a .sol file
cuopt_cli --log-to-console false --log-file mip_sample.log --solution-file mip_sample.sol mip_sample.mps

