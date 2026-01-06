from fastapi import APIRouter, Depends

from agents.orchestrator import AgentOrchestrator

router = APIRouter()


def get_orchestrator() -> AgentOrchestrator:
    return AgentOrchestrator()


@router.get("/feature-graph")
async def build_feature_graph(path: str | None = None, orch: AgentOrchestrator = Depends(get_orchestrator)):
    await orch.initialize()
    project_path = path or "."
    graph = await orch.build_feature_graph(project_path)
    return graph


@router.get("/gap-report")
async def gap_report(path: str | None = None, orch: AgentOrchestrator = Depends(get_orchestrator)):
    await orch.initialize()
    project_path = path or "."
    report = await orch.generate_gap_report(project_path)
    return report
