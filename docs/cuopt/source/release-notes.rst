=====================
Release Notes
=====================

====================
Release Notes 25.08
====================


New Features (25.08)
--------------------

- Added Python API for LP and MILP (`#223 <https://github.com/NVIDIA/cuopt/pull/223>`_) @Iroy30

Breaking Changes (25.08)
------------------------

- Fixed versioning for nightly and release package (`#175 <https://github.com/NVIDIA/cuopt/pull/175>`_) @rgsl888prabhu

Improvements (25.08)
--------------------

- New heuristic improvements (`#178 <https://github.com/NVIDIA/cuopt/pull/178>`_) @akifcorduk
- Add helm chart for cuOpt service (`#224 <https://github.com/NVIDIA/cuopt/pull/224>`_) @rgsl888prabhu
- Add nightly container support (`#180 <https://github.com/NVIDIA/cuopt/pull/180>`_) @rgsl888prabhu
- Adding deb package support as a beta feature (`#190 <https://github.com/NVIDIA/cuopt/pull/190>`_) @mostroot
- Use cusparsespmv_preprocess() now that Raft implements it (`#120 <https://github.com/NVIDIA/cuopt/pull/120>`_) @vitor1001
- Create a bash script to run MPS files in parallel (`#87 <https://github.com/NVIDIA/cuopt/pull/87>`_) @rg20
- Several fixes needed to compile cuOpt with LLVM (`#121 <https://github.com/NVIDIA/cuopt/pull/121>`_) @vitor1001
- Small fixes for corner cases (`#130 <https://github.com/NVIDIA/cuopt/pull/130>`_) @vitor1001
- Small improvements on how paths are handled in tests (`#129 <https://github.com/NVIDIA/cuopt/pull/129>`_) @vitor1001
- Update cxxopts to v3.3.1 (`#128 <https://github.com/NVIDIA/cuopt/pull/128>`_) @vitor1001
- Bump actions/checkout in nightly.yaml to v4 (`#230 <https://github.com/NVIDIA/cuopt/pull/230>`_) @ScottBrenner
- Remove CUDA 11 specific changes from repo (`#222 <https://github.com/NVIDIA/cuopt/pull/222>`_) @rgsl888prabhu
- Heuristic improvements with solution hash, MAB and simplex root solution (`#216 <https://github.com/NVIDIA/cuopt/pull/216>`_) @akifcorduk
- Various typos in comments and strings, note on result dir (`#200 <https://github.com/NVIDIA/cuopt/pull/200>`_) @MohdAatifSiddi
- Split very large tests into smaller individual test cases (`#152 <https://github.com/NVIDIA/cuopt/pull/152>`_) @vitor1001
- Fix compile error when using clang with C++20 (`#145 <https://github.com/NVIDIA/cuopt/pull/145>`_) @legrosbuffle
- refactor(rattler): remove cuda11 options and general cleanup (`#127 <https://github.com/NVIDIA/cuopt/pull/127>`_) @gforsyth
- Relax pinnings on several dependencies, remove nvidia channel (`#125 <https://github.com/NVIDIA/cuopt/pull/125>`_) @bdice
- Fix compile error when building with clang (`#119 <https://github.com/NVIDIA/cuopt/pull/119>`_) @legrosbuffle
- cuOpt service add healthcheck for / (`#114 <https://github.com/NVIDIA/cuopt/pull/114>`_) @tmckayus
- refactor(shellcheck): fix all remaining shellcheck errors/warnings (`#99 <https://github.com/NVIDIA/cuopt/pull/99>`_) @gforsyth
- Add CTK 12.9 fatbin flags to maintain existing binary sizes (`#58 <https://github.com/NVIDIA/cuopt/pull/58>`_) @robertmaynard

Bug Fixes (25.08)
-----------------

- Fixed a segfault on bnatt500 due to small mu leading to inf/nan (`#254 <https://github.com/NVIDIA/cuopt/pull/254>`_) @chris-maes
- Fixed a bug in basis repair. Recover from numerical issues in primal update (`#249 <https://github.com/NVIDIA/cuopt/pull/249>`_) @chris-maes
- Unset NDEBUG in cmake in assert mode (`#248 <https://github.com/NVIDIA/cuopt/pull/248>`_) @hlinsen
- Manual cuda graph creation in load balanced bounds presolve (`#242 <https://github.com/NVIDIA/cuopt/pull/242>`_) @kaatish
- Fixed bug on initial solution size in the check and cuda set device order (`#226 <https://github.com/NVIDIA/cuopt/pull/226>`_) @akifcorduk
- Disable cuda graph in batched PDLP (`#225 <https://github.com/NVIDIA/cuopt/pull/225>`_) @Kh4ster
- Fix logging levels format with timestamps (`#201 <https://github.com/NVIDIA/cuopt/pull/201>`_) @akifcorduk
- Fix bug in scaling of dual slacks and sign of dual variables for >= constraints (`#191 <https://github.com/NVIDIA/cuopt/pull/191>`_) @chris-maes
- Fix inversion crossover bug with PDP and prize collection (`#179 <https://github.com/NVIDIA/cuopt/pull/179>`_) @hlinsen
- Fix a bug in extract_best_per_route kernel (`#156 <https://github.com/NVIDIA/cuopt/pull/156>`_) @rg20
- Fix several bugs appeared in unit testing of JuMP interface (`#149 <https://github.com/NVIDIA/cuopt/pull/149>`_) @rg20
- Fix incorrect reported solving time (`#131 <https://github.com/NVIDIA/cuopt/pull/131>`_) @aliceb-nv
- Fix max offset (`#113 <https://github.com/NVIDIA/cuopt/pull/113>`_) @Kh4ster
- Fix batch graph capture issue caused by pinned memory allocator (`#110 <https://github.com/NVIDIA/cuopt/pull/110>`_) @Kh4ster
- Fix bug in optimization_problem_solution_t::copy_from (`#109 <https://github.com/NVIDIA/cuopt/pull/109>`_) @rg20
- Fix issue when problem has an empty problem in PDLP (`#107 <https://github.com/NVIDIA/cuopt/pull/107>`_) @Kh4ster
- Fix crash on models with variables but no constraints (`#105 <https://github.com/NVIDIA/cuopt/pull/105>`_) @aliceb-nv
- Fix inversion of constraint bounds in conditional bounds presolve (`#75 <https://github.com/NVIDIA/cuopt/pull/75>`_) @kaatish
- Fix data initialization in create depot node for max travel time feature (`#74 <https://github.com/NVIDIA/cuopt/pull/74>`_) @hlinsen

Documentation (25.08)
---------------------

- Added more pre-commit checks to ensure coding standards (`#213 <https://github.com/NVIDIA/cuopt/pull/213>`_) @rgsl888prabhu
- Mention GAMS and GAMSPy in third-party modeling languages page in documentation (`#206 <https://github.com/NVIDIA/cuopt/pull/206>`_) @0x17
- Enable doc build workflow and build script for PR and Nightly (`#203 <https://github.com/NVIDIA/cuopt/pull/203>`_) @rgsl888prabhu
- Fix the link to Python docs in README (`#118 <https://github.com/NVIDIA/cuopt/pull/118>`_) @Abinashbunty
- Add link checker for doc build and test (`#229 <https://github.com/NVIDIA/cuopt/pull/229>`_) @rgsl888prabh

====================
Release Notes 25.05
====================

New Features (25.05)
--------------------

- Added concurrent mode that runs PDLP and Dual Simplex together
- Added crossover from PDLP to Dual Simplex
- Added a C API for LP and MILP
- PDLP: Faster iterations and new more robust default PDLPSolverMode Stable2
- Added support for writing out mps file containing user problem. Useful for debugging

Breaking Changes (25.05)
------------------------

- NoTermination is now a NumericalError
- Split cuOpt as libcuopt and cuopt wheel

Improvements (25.05)
--------------------

- Hook up MILP Gap parameters and add info about number of nodes explored and simplex iterations
- FJ bug fixes, tests and improvements
- Allow no time limit in MILP
- Refactor routing
- Probing cache optimization
- Diversity improvements for routing
- Enable more compile warnings and faster compile by bypassing rapids fetch
- Constraint prop based on load balanced bounds update
- Logger file handling and bug fixes on MILP
- Add shellcheck to pre-commit and fix warnings

Bug Fixes (25.05)
-----------------

- In the solution, ``termination_status`` should be cast to correct enum.
- Fixed a bug using vehicle IDs in construct feasible solution algorithm.
- FP recombiner probing bug fix.
- Fix concurrent LP crashes.
- Fix print relative dual residual.
- Handle empty problems gracefully.
- Improve breaks to allow dimensions at arbitrary places in the route.
- Free var elimination with a substitute variable for each free variable.
- Fixed race condition when resetting vehicle IDs in heterogenous mode.
- cuOpt self-hosted client, some MILPs do not have all fields in ``lp_stats``.
- Fixed RAPIDS logger usage.
- Handle LP state more cleanly, per solution.
- Fixed routing solver intermittent failures.
- Gracefully exit when the problem is infeasible after presolve.
- Fixed bug on dual resizing.
- Fix occasional incorrect solution bound on maximization problems
- Fix inversion of constraint bounds in conditional bounds presolve
- Pdlp fix batch cuda graph
- Fix obj constant on max. Fix undefined memory access at root
- Allow long client version in service version check, this fixes the issue in case version is of the format 25.05.00.dev0

Documentation (25.05)
---------------------
- Restructure documementation to accomdate new APIs
