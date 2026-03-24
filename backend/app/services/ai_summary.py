import logging
from typing import Optional

from ..schemas.report_schema import Report

logger = logging.getLogger("dristi-scan")


def generate_ai_insight(report: Report) -> Optional[str]:
    """
    AI-generated insights are currently disabled. Returns None.
    """
    logger.info("AI insights are disabled; returning None.")
    return None
