from cuopt_sh_client import CuOptServiceSelfHostClient, ThinClientSolverSettings
import json

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

# If cuOpt is not running on localhost:5000, edit `ip` and `port` parameters
cuopt_service_client = CuOptServiceSelfHostClient(
    ip="localhost",
    port=5000,
    timeout_exception=False
)

ss = ThinClientSolverSettings()

ss.set_parameter("time_limit", 5)
ss.set_optimality_tolerance(0.00001)

solution = cuopt_service_client.get_LP_solve(data, solver_config=ss, response_type="dict")

print(json.dumps(solution, indent=4))
