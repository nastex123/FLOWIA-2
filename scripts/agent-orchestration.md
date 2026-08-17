# Coordinación Multi-Agente — FlowMind AI

Tres agentes trabajan sobre el mismo repo, aislados por git worktrees para
evitar colisiones en el working tree. Hermes (este asistente) actúa como
orquestador: parte tareas, delega, integra y corre los tests.

## Topología

```
flowmind (main)              <- Hermes trabaja y hace merge final
  ├─ ../flowmind-agent-antigravity  (rama agent/antigravity)  <- Antigravity (CLI: agy)
  └─ ../flowmind-agent-opencode     (rama agent/opencode)     <- OpenCode + DeepSeek
```

## Agentes y cómo invocarlos

### 1. Hermes (orquestador)
- Edita `flowmind/` (main) directamente.
- Integra los PRs de los otros agentes y corre la suite de tests.

### 2. OpenCode + DeepSeek (gratis)
Modelo: `opencode/deepseek-v4-flash-free`
```bash
# Un solo comando (no interactivo):
opencode run '<tarea>' -m opencode/deepseek-v4-flash-free --dir ../flowmind-agent-opencode

# Iterativo en background (monitorear con process/poll):
opencode -m opencode/deepseek-v4-flash-free --dir ../flowmind-agent-opencode   # pty=true
```

### 3. Antigravity (CLI: agy)
Modo no interactivo (print):
```bash
agy --print '<tarea>' --dir ../flowmind-agent-antigravity
# o con modelo/agente explícito:
agy --print '<tarea>' --model <modelo> --agent <agente> --dir ../flowmind-agent-antigravity
```

## Flujo de trabajo (protocolo)

1. Hermes recibe una tarea y la parte en sub-tareas independientes.
2. Cada sub-tarea se asigna a un worktree/agente distinto.
3. El agente trabaja en su rama y hace commit (conventional commits).
4. Hermes integra: `git merge` desde cada rama hacia `main` (o crea PRs).
5. Hermes corre `pytest` y resuelve conflictos antes de push.

## Reglas de aislamiento (evitar conflictos)

- Nunca dos agentes tocan el MISMO archivo en la misma tarea.
- Si una tarea es grande, dividir por módulo (p.ej. backend vs frontend vs desktop).
- Commits pequeños y descriptivos (Conventional Commits, ver AGENTS.md §15).
- No hacer `push` directo a `origin/main` sin revisión de Hermes.

## Setup inicial (ejecutado)

```bash
git worktree add ../flowmind-agent-antigravity -b agent/antigravity
git worktree add ../flowmind-agent-opencode    -b agent/opencode
```

Para limpiar worktrees:
```bash
git worktree remove ../flowmind-agent-antigravity
git worktree remove ../flowmind-agent-opencode
```
