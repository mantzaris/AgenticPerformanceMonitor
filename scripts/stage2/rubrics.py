from trajectory_dashboards.stage2.backend import Engine
from trajectory_dashboards.stage2.evaluation import create_rubrics
create_rubrics(Engine())
print('Created evaluator-only independent facts and rubric for all 18 tasks.')
