from cuopt_sh_client import (
    CuOptServiceSelfHostClient,
    ThinClientSolverSettings,
    PDLPSolverMode
)
import cuopt_mps_parser
import json
import time

# -- Parse the MPS file --

data = "sample.mps"

mps_data = """* optimize
    *  cost = -0.2 * VAR1 + 0.1 * VAR2
    * subject to
    *  3 * VAR1 + 4 * VAR2 <= 5.4
    *  2.7 * VAR1 + 10.1 * VAR2 <= 4.9
    NAME   good-1
    ROWS
     N  COST
     L  ROW1
     L  ROW2
    COLUMNS
        VAR1      COST      -0.2
        VAR1      ROW1      3              ROW2      2.7
        VAR2      COST      0.1
        VAR2      ROW1      4              ROW2      10.1
    RHS
        RHS1      ROW1      5.4            ROW2      4.9
    ENDATA
    """

with open(data, "w") as file:
    file.write(mps_data)

# Parse the MPS file and measure the time spent
parse_start = time.time()
data_model = cuopt_mps_parser.ParseMps(data)
parse_time = time.time() - parse_start

# -- Build the client object --

# If cuOpt is not running on localhost:5000, edit `ip` and `port` parameters
cuopt_service_client = CuOptServiceSelfHostClient(
    ip="localhost",
    port=5000,
    timeout_exception=False
)

# -- Set the solver settings --

ss = ThinClientSolverSettings()

# Set the solver mode to the same of the blogpost, Fast1.
# Stable1 could also be used.
ss.set_parameter("pdlp_solver_mode", PDLPSolverMode.Fast1)

# Set the general tolerance to 1e-4 which is already the default value.
# For more detail on optimality checkout `SolverSettings.set_optimality_tolerance()`
ss.set_optimality_tolerance(1e-4)

# Here you could set an iteration limit to 1000 and time limit to 10 seconds
# By default there is no iteration limit and the max time limit is 10 minutes
# Any problem taking more than 10 minutes to solve will stop and the current solution will be returned
# For this example, no limit is set
# settings.set_iteration_limit(1000)
# settings.set_time_limit(10)
ss.set_parameter("time_limit", 5)

# -- Call solve --

network_time = time.time()
solution = cuopt_service_client.get_LP_solve(data_model, ss)
network_time = time.time() - network_time

# -- Retrieve the solution object and print the details --

solution_status = solution["response"]["solver_response"]["status"]
solution_obj = solution["response"]["solver_response"]["solution"]

# Check Termination Reason
print("Termination Reason: ")
print(solution_status)

# Check found objective value
print("Objective Value:")
print(solution_obj.get_primal_objective())

# Check the MPS parse time
print(f"Mps Parse time: {parse_time:.3f} sec")

# Check network time (client call - solve time)
network_time = network_time - (solution_obj.get_solve_time())
print(f"Network time: {network_time:.3f} sec")

# Check solver time
solve_time = solution_obj.get_solve_time()
print(f"Engine Solve time: {solve_time:.3f} sec")

# Check the total end to end time (mps parsing + network + solve time)
end_to_end_time = parse_time + network_time + solve_time
print(f"Total end to end time: {end_to_end_time:.3f} sec")

# Print the found decision variables
print("Variables Values:")
print(solution_obj.get_vars())
