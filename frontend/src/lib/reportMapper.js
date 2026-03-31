/**
 * reportMapper.js
 *
 * Normalizes the backend FullStructuredReportSchema response into a stable
 * frontend shape. All field variations are handled here so the UI never
 * needs to guess field names.
 *
 * Backend shape (from /api/reports/:scanId):
 *   summary.total / critical / high / medium / low / overall_risk
 *   findings[].type, .severity, .line, .code, .description, .impact,
 *              .attack_example, .recommendation, .fix_code
 *   risk_score.score, .reason
 *   ai_insights.summary, .most_critical_issue, .fix_priority
 *   secure_version
 *   file_name (from scan, may be on root or nested)
 *   scan_date  (may be on root or nested)
 */

const str  = (v, fb = '')  => (v !== undefined && v !== null && String(v).trim() !== '' ? String(v).trim() : fb);
const num  = (v, fb = 0)   => (typeof v === 'number' && !isNaN(v) ? v : (parseFloat(v) || fb));
const arr  = (v)           => (Array.isArray(v) ? v : []);

/**
 * Normalize a single finding from any backend shape into the UI shape.
 */
export function normalizeFinding(raw) {
  if (!raw || typeof raw !== 'object') return null;
  return {
    // name: backend uses "type" in ReportFindingSchema
    name:           str(raw.name || raw.type, 'Unknown Finding'),
    type:           str(raw.type || raw.name, 'Unknown'),
    severity:       str(raw.severity, 'Low'),
    // file: may come from finding or parent scan
    file_name:      str(raw.file_name || raw.file, ''),
    // line: backend uses "line" (int), raw vulns use "line_number"
    line_number:    num(raw.line_number ?? raw.line, 0) || null,
    // code: backend uses "code", raw vulns use "code_snippet"
    code_snippet:   str(raw.code_snippet || raw.code, ''),
    description:    str(raw.description, ''),
    impact:         str(raw.impact, ''),
    attack_example: str(raw.attack_example, ''),
    // remediation: backend uses "recommendation", raw vulns use "remediation"
    remediation:    str(raw.remediation || raw.recommendation, ''),
    cwe_reference:  str(raw.cwe_reference, ''),
    category:       str(raw.category, ''),
  };
}

/**
 * Normalize the full report API response into a stable frontend shape.
 * Returns null if raw is falsy.
 */
export function normalizeReport(raw, scanId) {
  if (!raw || typeof raw !== 'object') return null;

  // ── summary ──────────────────────────────────────────────────────────────
  const s = raw.summary || {};
  // security_score may come from summary or be derived from risk_score
  const riskScore10 = num(raw.risk_score?.score, 0);
  const securityScore = num(
    s.security_score ?? raw.security_score ?? (riskScore10 > 0 ? Math.max(0, 100 - riskScore10 * 10) : null),
    0,
  );

  const summary = {
    total:          num(s.total, 0),
    critical:       num(s.critical, 0),
    high:           num(s.high, 0),
    medium:         num(s.medium, 0),
    low:            num(s.low, 0),
    overall_risk:   str(s.overall_risk || raw.risk_level, ''),
    security_score: securityScore,
  };

  // ── findings ─────────────────────────────────────────────────────────────
  // Backend may return findings, vulnerabilities, or scan.vulnerabilities
  const rawFindings =
    arr(raw.findings).length       ? arr(raw.findings)       :
    arr(raw.vulnerabilities).length ? arr(raw.vulnerabilities) :
    arr(raw.scan?.vulnerabilities);

  const findings = rawFindings.map(normalizeFinding).filter(Boolean);

  // ── ai insights ───────────────────────────────────────────────────────────
  const ai = raw.ai_insights || {};
  const ai_insights = {
    summary:              str(ai.summary, ''),
    most_critical_issue:  str(ai.most_critical_issue, ''),
    fix_priority:         str(ai.fix_priority, ''),
  };

  // ── risk score ────────────────────────────────────────────────────────────
  const rs = raw.risk_score || {};
  const risk_score = {
    score:  num(rs.score, 0),
    reason: str(rs.reason, ''),
  };

  // ── recommendations ───────────────────────────────────────────────────────
  // Backend may return an array of strings or objects
  const rawRecs = arr(raw.recommendations);
  const recommendations = rawRecs.map(r =>
    typeof r === 'string' ? r : str(r?.text || r?.recommendation, '')
  ).filter(Boolean);

  // ── file / date ───────────────────────────────────────────────────────────
  const file_name = str(
    raw.file_name || raw.display_file_name || raw.target || raw.scan?.file_name,
    `Scan #${scanId}`,
  );
  const scan_date = str(raw.scan_date || raw.created_at || raw.date, '');

  return {
    id:               str(scanId, ''),
    title:            'Security Analysis Report',
    file_name,
    scan_date,
    summary,
    risk_score,
    ai_insights,
    findings,
    recommendations,
    secure_version:   str(raw.secure_version, ''),
  };
}
