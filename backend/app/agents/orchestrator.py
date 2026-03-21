from __future__ import annotations

import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Optional

from app.config import get_settings
from app.agents.injection_agent import InjectionAgent
from app.agents.secrets_agent import SecretsAgent
from app.agents.auth_agent import AuthAgent
from app.agents.dependency_agent import DependencyAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.report_agent import ReportAgent
from app.agents.schemas import AgentResult, OrchestrationOutput
from app.schemas.report_schema import Report

logger = logging.getLogger(__name__)


# ------------------
# Individual hooks (preserve existing API)
# ------------------
def run_injection_agent_if_enabled(code_snippet: str, file_path: Optional[str] = None) -> Optional[AgentResult]:
    settings = get_settings()
    if not getattr(settings, "ai_injection_enabled", False):
        logger.debug("Injection Agent is disabled via configuration.")
        return None
    agent = InjectionAgent()
    return agent.analyze(code_snippet=code_snippet, file_path=file_path)


def run_secrets_agent_if_enabled(content: str, file_path: Optional[str] = None) -> Optional[AgentResult]:
    settings = get_settings()
    if not getattr(settings, "ai_secrets_enabled", False):
        logger.debug("Secrets Agent is disabled via configuration.")
        return None
    agent = SecretsAgent()
    return agent.analyze(content, file_path=file_path)


def run_auth_agent_if_enabled(content: str, file_path: Optional[str] = None) -> Optional[AgentResult]:
    settings = get_settings()
    if not getattr(settings, "ai_auth_enabled", False):
        logger.debug("Auth Agent is disabled via configuration.")
        return None
    agent = AuthAgent()
    return agent.analyze(content, file_path=file_path)


def run_dependency_agent_if_enabled(content: str, file_path: Optional[str] = None) -> Optional[AgentResult]:
    settings = get_settings()
    if not getattr(settings, "ai_dependency_enabled", False):
        logger.debug("Dependency Agent is disabled via configuration.")
        return None
    agent = DependencyAgent()
    return agent.analyze(content, file_path=file_path)


def run_planner_agent_if_enabled(content: str, file_path: Optional[str] = None) -> Optional[AgentResult]:
    settings = get_settings()
    if not getattr(settings, "ai_planner_enabled", False):
        logger.debug("Planner Agent is disabled via configuration.")
        return None
    agent = PlannerAgent()
    return agent.analyze(content, file_path=file_path)


def run_report_agent_if_enabled(report: Report) -> Optional[AgentResult]:
    settings = get_settings()
    if not getattr(settings, "ai_report_enabled", False):
        logger.debug("Report Agent is disabled via configuration.")
        return None
    agent = ReportAgent()
    return agent.analyze(report)


# ------------------
# Orchestrated execution
# ------------------
def _default_flags(file_path: Optional[str]) -> Dict[str, bool]:
    """Heuristic fallback when planner is disabled or fails."""
    path = (file_path or "").lower()
    ext = path.split(".")[-1] if "." in path else ""

    is_dep = ext in {"txt", "lock", "json"} and any(k in path for k in ["requirements", "package", "yarn", "poetry", "pipfile"])
    is_auth = "auth" in path or "login" in path

    return {
        "run_injection": ext in {"py", "js", "ts", "jsx", "tsx", "go", "rb", "php", "java", "c", "cpp"},
        "run_secrets": True,
        "run_auth": is_auth,
        "run_dependency": is_dep,
    }


def _planner_flags(content: str, file_path: Optional[str]) -> Dict[str, bool]:
    settings = get_settings()
    if not getattr(settings, "ai_planner_enabled", False):
        return _default_flags(file_path)

    planner_result = run_planner_agent_if_enabled(content, file_path)
    if not planner_result or not planner_result.findings:
        return _default_flags(file_path)

    desc = planner_result.findings[0].description
    try:
        flags = json.loads(desc)
        if not isinstance(flags, dict):
            raise ValueError("Planner flags not a dict")
    except Exception as exc:
        logger.warning("Planner output parse failed (%s); using defaults", exc)
        return _default_flags(file_path)

    merged = _default_flags(file_path)
    merged.update({k: bool(v) for k, v in flags.items() if k in merged})
    return merged


def run_ai_orchestration(content: str, file_path: Optional[str] = None) -> OrchestrationOutput:
    """
    Phase-7 orchestrator: decides (via planner or fallback) which agents to run,
    executes them (in parallel where safe), and returns unified output.
    """
    flags = _planner_flags(content, file_path)
    tasks = []

    if flags.get("run_injection"):
        tasks.append(("Injection Agent", run_injection_agent_if_enabled, content))
    if flags.get("run_secrets"):
        tasks.append(("Secrets Agent", run_secrets_agent_if_enabled, content))
    if flags.get("run_auth"):
        tasks.append(("Auth Agent", run_auth_agent_if_enabled, content))
    if flags.get("run_dependency"):
        tasks.append(("Dependency Agent", run_dependency_agent_if_enabled, content))

    results: list[AgentResult] = []

    with ThreadPoolExecutor(max_workers=min(4, len(tasks) or 1)) as executor:
        future_map = {
            executor.submit(func, content, file_path): name
            for name, func, content in tasks
        }
        for future in as_completed(future_map):
            name = future_map[future]
            try:
                res = future.result()
                if res:
                    results.append(res)
            except Exception as exc:
                logger.error("Agent %s failed during orchestration: %s", name, exc)
                results.append(
                    AgentResult(agent=name, findings=[], logs=[f"[{name}] Error: {exc}"])
                )

    findings = []
    logs = []
    agents_used = []
    for res in results:
        findings.extend(res.findings)
        logs.extend(res.logs)
        if res.agent:
            agents_used.append(res.agent)

    return OrchestrationOutput(
        agents_used=agents_used,
        findings=findings,
        agent_results=results,
        logs=logs,
    )
