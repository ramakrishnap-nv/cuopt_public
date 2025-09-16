#!/bin/bash
#
# Quick Start Example for NVIDIA cuOpt Python API
#
# This example demonstrates a basic routing optimization problem using cuOpt.
# It creates a simple cost matrix, defines task locations, and solves for optimal routes.

echo "NVIDIA cuOpt Quick Start Example"
echo "========================================"

python -c "
import cudf
from cuopt import routing

print('Cost Matrix:')
cost_matrix = cudf.DataFrame([[0,2,2,2],[2,0,2,2],[2,2,0,2],[2,2,2,0]], dtype='float32')
print(cost_matrix)
print()

print('Task locations: [1, 2, 3]')
print('Number of vehicles: 2')
print()

print('Solving routing problem...')
task_locations = cudf.Series([1,2,3])
n_vehicles = 2
dm = routing.DataModel(cost_matrix.shape[0], n_vehicles, len(task_locations))
dm.add_cost_matrix(cost_matrix)
dm.add_transit_time_matrix(cost_matrix.copy(deep=True))
ss = routing.SolverSettings()
sol = routing.Solve(dm, ss)

print()
print('Solution:')
print(sol.get_route())
print()
print('****************** Display Routes *************************')
sol.display_routes()
"
