#!/bin/bash
# Solve MIP problem with custom parameters

cuopt_cli --mip-absolute-gap 0.01 --time-limit 10 mip_sample.mps
