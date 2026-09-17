import { useCallback, useEffect, useMemo, useState } from "react";
import {
  applyNodeChanges,
  Background,
  Controls,
  ReactFlow,
  type Connection,
  type Edge,
  type Node,
  type NodeChange,
} from "@xyflow/react";

import { architect, generate, listBackends, validateSpec, type GenerateResult } from "./api";
import { layout } from "./layout";
import { emptySpec, type AgentSpec, type SystemSpec, type TaskSpec } from "./spec";

type Positions = Record<string, { x: number; y: number }>;

function specToEdges(spec: SystemSpec): Edge[] {
  const edges: Edge[] = [];
  for (const task of spec.tasks) {
    for (const dep of task.depends_on) {
      edges.push({ id: `${dep}->${task.id}`, source: dep, target: task.id, animated: true });
    }
  }
  return edges;
}

function specToNodes(spec: SystemSpec, positions: Positions, selected: string | null): Node[] {
  return spec.tasks.map((t) => ({
    id: t.id,
    position: positions[t.id] ?? { x: 0, y: 0 },
    data: { label: `${t.id} · ${t.agent}` },
    style: {
      border: t.id === selected ? "2px solid #2563eb" : "1px solid #cbd5e1",
      borderRadius: 8,
      padding: 8,
      background: "#fff",
      fontSize: 12,
    },
  }));
}

export default function App() {
  const [spec, setSpec] = useState<SystemSpec>(emptySpec);
  const [positions, setPositions] = useState<Positions>({});
  const [selected, setSelected] = useState<string | null>(null);
  const [backend, setBackend] = useState("agents-python");
  const [backends, setBackends] = useState<string[]>(["agents-python", "crewai"]);
  const [result, setResult] = useState<GenerateResult | null>(null);
  const [openFile, setOpenFile] = useState<string | null>(null);
  const [status, setStatus] = useState<{ kind: "ok" | "err" | "info"; msg: string } | null>(null);
  const [busy, setBusy] = useState(false);
  const [task, setTask] = useState("");

  const edges = useMemo(() => specToEdges(spec), [spec]);
  const nodes = useMemo(() => specToNodes(spec, positions, selected), [spec, positions, selected]);

  const relayout = useCallback((s: SystemSpec) => {
    setPositions(() => {
      const laid = layout(specToNodes(s, {}, null), specToEdges(s));
      const next: Positions = {};
      laid.forEach((n) => (next[n.id] = n.position));
      return next;
    });
  }, []);

  useEffect(() => {
    relayout(spec);
    listBackends()
      .then((b) => setBackends(b.backends))
      .catch(() => undefined);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const onNodesChange = useCallback((changes: NodeChange[]) => {
    setPositions((prev) => {
      const applied = applyNodeChanges(changes, nodesRef(prev, spec, selected));
      const next: Positions = {};
      applied.forEach((n) => (next[n.id] = n.position));
      return next;
    });
  }, [spec, selected]);

  const onConnect = useCallback((conn: Connection) => {
    if (!conn.source || !conn.target || conn.source === conn.target) return;
    setSpec((s) => ({
      ...s,
      tasks: s.tasks.map((t) =>
        t.id === conn.target && !t.depends_on.includes(conn.source!)
          ? { ...t, depends_on: [...t.depends_on, conn.source!] }
          : t,
      ),
    }));
  }, []);

  const onEdgesDelete = useCallback((removed: Edge[]) => {
    setSpec((s) => ({
      ...s,
      tasks: s.tasks.map((t) => {
        const drop = removed.filter((e) => e.target === t.id).map((e) => e.source);
        return drop.length ? { ...t, depends_on: t.depends_on.filter((d) => !drop.includes(d)) } : t;
      }),
    }));
  }, []);

  const addAgent = () => {
    const name = `agent_${spec.agents.length + 1}`;
    setSpec((s) => ({ ...s, agents: [...s.agents, { name, role: "", goal: "", backstory: "", tools: [] }] }));
  };

  const addTask = () => {
    const id = `t${spec.tasks.length + 1}`;
    const agent = spec.agents[0]?.name ?? "";
    const next = { ...spec, tasks: [...spec.tasks, { id, description: "", agent, expected_output: "", depends_on: [] }] };
    setSpec(next);
    relayout(next);
    setSelected(id);
  };

  const updateAgent = (i: number, patch: Partial<AgentSpec>) =>
    setSpec((s) => ({ ...s, agents: s.agents.map((a, j) => (j === i ? { ...a, ...patch } : a)) }));

  const updateTask = (id: string, patch: Partial<TaskSpec>) =>
    setSpec((s) => ({ ...s, tasks: s.tasks.map((t) => (t.id === id ? { ...t, ...patch } : t)) }));

  const removeTask = (id: string) => {
    const next = {
      ...spec,
      tasks: spec.tasks
        .filter((t) => t.id !== id)
        .map((t) => ({ ...t, depends_on: t.depends_on.filter((d) => d !== id) })),
    };
    setSpec(next);
    relayout(next);
    if (selected === id) setSelected(null);
  };

  const doValidate = async () => {
    setBusy(true);
    try {
      const res = await validateSpec(spec);
      setStatus(res.ok ? { kind: "ok", msg: "Spec is valid." } : { kind: "err", msg: res.error ?? "Invalid." });
    } catch (e) {
      setStatus({ kind: "err", msg: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const doGenerate = async () => {
    setBusy(true);
    try {
      const res = await generate(spec, backend);
      setResult(res);
      setOpenFile(Object.keys(res.files)[0] ?? null);
      setStatus({ kind: "ok", msg: `Generated ${Object.keys(res.files).length} file(s).` });
    } catch (e) {
      setStatus({ kind: "err", msg: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const doArchitect = async () => {
    if (!task.trim()) return;
    setBusy(true);
    setStatus({ kind: "info", msg: "Asking the architect…" });
    try {
      const s = await architect(task, backend, "");
      setSpec(s);
      relayout(s);
      setStatus({ kind: "ok", msg: "Design generated." });
    } catch (e) {
      setStatus({ kind: "err", msg: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const selectedTask = spec.tasks.find((t) => t.id === selected) ?? null;

  return (
    <div className="app">
      <header className="topbar">
        <strong>System Factory Designer</strong>
        <input
          className="taskInput"
          placeholder="Describe a task, then Design →"
          value={task}
          onChange={(e) => setTask(e.target.value)}
        />
        <button disabled={busy} onClick={doArchitect}>Design (LLM)</button>
        <select value={backend} onChange={(e) => setBackend(e.target.value)}>
          {backends.map((b) => (
            <option key={b} value={b}>{b}</option>
          ))}
        </select>
        <button disabled={busy} onClick={doValidate}>Validate</button>
        <button disabled={busy} onClick={doGenerate}>Generate</button>
        <button disabled={busy} onClick={() => relayout(spec)}>Auto-layout</button>
        {status && <span className={`status ${status.kind}`}>{status.msg}</span>}
      </header>

      <div className="body">
        <aside className="panel left">
          <label>System name<input value={spec.name} onChange={(e) => setSpec((s) => ({ ...s, name: e.target.value }))} /></label>
          <label>Description<textarea value={spec.description} onChange={(e) => setSpec((s) => ({ ...s, description: e.target.value }))} /></label>
          <label>Required env (comma-separated names)
            <input
              value={spec.required_env.join(", ")}
              onChange={(e) => setSpec((s) => ({ ...s, required_env: e.target.value.split(",").map((x) => x.trim()).filter(Boolean) }))}
            />
          </label>

          <div className="section">Agents <button onClick={addAgent}>+ add</button></div>
          {spec.agents.map((a, i) => (
            <div key={i} className="card">
              <input placeholder="name" value={a.name} onChange={(e) => updateAgent(i, { name: e.target.value })} />
              <input placeholder="role" value={a.role} onChange={(e) => updateAgent(i, { role: e.target.value })} />
              <input placeholder="goal" value={a.goal} onChange={(e) => updateAgent(i, { goal: e.target.value })} />
            </div>
          ))}

          <div className="section">Tasks <button onClick={addTask}>+ add</button></div>
          {selectedTask ? (
            <div className="card">
              <input value={selectedTask.id} onChange={(e) => updateTask(selectedTask.id, { id: e.target.value })} />
              <textarea placeholder="description" value={selectedTask.description} onChange={(e) => updateTask(selectedTask.id, { description: e.target.value })} />
              <select value={selectedTask.agent} onChange={(e) => updateTask(selectedTask.id, { agent: e.target.value })}>
                {spec.agents.map((a) => <option key={a.name} value={a.name}>{a.name}</option>)}
              </select>
              <button onClick={() => removeTask(selectedTask.id)}>delete task</button>
            </div>
          ) : (
            <p className="hint">Click a task node to edit it. Drag between nodes to add a dependency.</p>
          )}
        </aside>

        <main className="canvas">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onConnect={onConnect}
            onEdgesDelete={onEdgesDelete}
            onNodeClick={(_, n) => setSelected(n.id)}
            fitView
          >
            <Background />
            <Controls />
          </ReactFlow>
        </main>

        <aside className="panel right">
          {result ? (
            <>
              <div className="section">Files ({backend})</div>
              <div className="files">
                <button className={openFile === "__presentation__" ? "active" : ""} onClick={() => setOpenFile("__presentation__")}>PRESENTATION.md</button>
                {Object.keys(result.files).map((f) => (
                  <button key={f} className={f === openFile ? "active" : ""} onClick={() => setOpenFile(f)}>{f}</button>
                ))}
              </div>
              <pre className="code">
                {openFile === "__presentation__"
                  ? result.presentation
                  : openFile
                    ? result.files[openFile]
                    : ""}
              </pre>
            </>
          ) : (
            <p className="hint">Generate to see the project files and presentation here.</p>
          )}
        </aside>
      </div>
    </div>
  );
}

// Helper: rebuild a Node[] from positions so applyNodeChanges can mutate positions immutably.
function nodesRef(positions: Positions, spec: SystemSpec, selected: string | null): Node[] {
  return specToNodes(spec, positions, selected);
}
