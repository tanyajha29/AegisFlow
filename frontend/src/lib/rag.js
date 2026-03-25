import api from './api';

const getField = (obj, keys, fallback = '') => {
  for (const k of keys) {
    if (obj?.[k] !== undefined && obj[k] !== null) return obj[k];
  }
  return fallback;
};

const buildPayload = (finding) => {
  const fallbackId =
    getField(finding, ['id', 'finding_id'], null) ||
    `${getField(finding, ['name', 'type'], 'finding')}-${getField(finding, ['file_name', 'file'], 'file')}-${getField(
      finding,
      ['line_number', 'line'],
      0,
    )}`;

  return {
    finding_id: String(fallbackId || 'unknown'),
    type: getField(finding, ['name', 'type'], 'Unknown'),
    severity: getField(finding, ['severity'], 'Medium'),
    file: getField(finding, ['file_name', 'file'], ''),
    line: Number(getField(finding, ['line_number', 'line'], 0) || 0),
    language: getField(finding, ['language'], ''),
    framework: getField(finding, ['framework'], ''),
    code_snippet: getField(finding, ['code_snippet', 'code'], ''),
    description: getField(finding, ['description'], ''),
  };
};

export async function explainVulnerability(finding) {
  const payload = {
    ...buildPayload(finding),
  };

  const { data } = await api.post('/rag/explain', payload);
  return data;
}

export async function suggestFix(finding) {
  const payload = buildPayload(finding);

  const { data } = await api.post('/rag/fix', payload);
  return data;
}

export default explainVulnerability;
