from cuopt.linear_programming.problem import Problem, INTEGER, MAXIMIZE
from cuopt.linear_programming.solver_settings import SolverSettings
from cuopt.linear_programming.solver.solver_parameters import CUOPT_TIME_LIMIT
from cuopt.linear_programming.internals import GetSolutionCallback, SetSolutionCallback

# Create a callback class to receive incumbent solutions
class IncumbentCallback(GetSolutionCallback):
    def __init__(self):
        super().__init__()
        self.solutions = []
        self.n_callbacks = 0

    def get_solution(self, solution, solution_cost):
        """
        Called whenever the solver finds a new incumbent solution.

        Parameters
        ----------
        solution : array-like
            The variable values of the incumbent solution
        solution_cost : array-like
            The objective value of the incumbent solution
        """
        self.n_callbacks += 1

        # Store the incumbent solution
        incumbent = {
            "solution": solution.copy_to_host(),
            "cost": solution_cost.copy_to_host()[0],
            "iteration": self.n_callbacks
        }
        self.solutions.append(incumbent)

        print(f"Incumbent {self.n_callbacks}: {incumbent['solution']}, cost: {incumbent['cost']:.2f}")

# Create a more complex MIP problem that will generate multiple incumbents
problem = Problem("Incumbent Example")

# Add integer variables
x = problem.addVariable(vtype=INTEGER)
y = problem.addVariable(vtype=INTEGER)

# Add constraints to create a problem that will generate multiple incumbents
problem.addConstraint(2 * x + 4 * y >= 230)
problem.addConstraint(3 * x + 2 * y <= 190)

# Set objective to maximize
problem.setObjective(5 * x + 3 * y, sense=MAXIMIZE)

# Configure solver settings with callback
settings = SolverSettings()
# Set the incumbent callback
incumbent_callback = IncumbentCallback()
settings.set_mip_callback(incumbent_callback)
settings.set_parameter(CUOPT_TIME_LIMIT, 30)  # Allow enough time to find multiple incumbents

# Solve the problem
problem.solve(settings)

# Display final results
print(f"\n=== Final Results ===")
print(f"Problem status: {problem.Status.name}")
print(f"Solve time: {problem.SolveTime:.2f} seconds")
print(f"Final solution: x={x.getValue()}, y={y.getValue()}")
print(f"Final objective value: {problem.ObjValue:.2f}")
