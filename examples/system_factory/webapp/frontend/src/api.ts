import type { SystemSpec } from "./spec";

export interface GenerateResult {
  files: Record<string, string>;
  presentation: string;
  backend: string;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const resp = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    const detail = await resp.text();
    throw new Error(`${resp.status}: ${detail}`);
  }
  return resp.json() as Promise<T>;
}

export function listBackends(): Promise<{ backends: string[] }> {
  return fetch("/api/backends").then((r) => r.json());
}

export function validateSpec(spec: SystemSpec): Promise<{ ok: boolean; error: string | null }> {
  return post("/api/validate", spec);
}

export function generate(spec: SystemSpec, backend: string): Promise<GenerateResult> {
  return post("/api/generate", { spec, backend });
}

export function architect(task: string, backend: string, mcp_hint: string): Promise<SystemSpec> {
  return post("/api/architect", { task, backend, mcp_hint });
}
