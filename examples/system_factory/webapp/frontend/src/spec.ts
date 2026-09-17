// TypeScript mirror of the backend's SystemSpec (examples/system_factory/spec.py).

export interface AgentSpec {
  name: string;
  role: string;
  goal: string;
  backstory: string;
  tools: string[];
}

export interface TaskSpec {
  id: string;
  description: string;
  agent: string;
  expected_output: string;
  depends_on: string[];
}

export interface MCPServerSpec {
  name: string;
  command: string;
  args: string[];
  url: string;
}

export interface SystemSpec {
  name: string;
  description: string;
  provider_env: string;
  model_env: string;
  required_env: string[];
  agents: AgentSpec[];
  tasks: TaskSpec[];
  mcp_servers: MCPServerSpec[];
}

export function emptySpec(): SystemSpec {
  return {
    name: "my_system",
    description: "A multi-agent system.",
    provider_env: "AGENTS_DEFAULT_PROVIDER",
    model_env: "AGENTS_DEFAULT_MODEL",
    required_env: [],
    agents: [
      { name: "researcher", role: "Research Analyst", goal: "Gather facts", backstory: "", tools: [] },
      { name: "writer", role: "Writer", goal: "Write the result", backstory: "", tools: [] },
    ],
    tasks: [
      { id: "t1", description: "Research the topic.", agent: "researcher", expected_output: "", depends_on: [] },
      { id: "t2", description: "Write the output.", agent: "writer", expected_output: "", depends_on: ["t1"] },
    ],
    mcp_servers: [],
  };
}
