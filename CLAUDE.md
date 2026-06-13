# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the implementation folder for **Article #2 — "Optimizing LangChain AI Agents with Contextual Engineering"** (Fareed Khan / Level Up Coding), **Phase 1 — Agent Foundations** of the master roadmap (see `../roadmap.md`).

**Phase 1 theme:** Agent Foundations — solidify LangGraph multi-agent mechanics, context-engineering basics, and memory, the bedrock everything else assumes.

**What this article covers — the "basics of contextual engineering":**
- **Scratchpad** — giving an agent a working space to externalize intermediate reasoning/state.
- **Context isolation** — keeping each agent/sub-task's context scoped so it doesn't bleed or bloat.
- **Sub-agents** — delegating to scoped helpers to keep the main context lean.
- The cost/latency/quality trade-offs of how much context you feed an agent, and how to curate it.

**Why it matters in the roadmap:** this is the explicitly-flagged **prerequisite for #23 (Full-Stack Contextual Engineering)** and the head of the memory/context through-line **#2 → #3 → #4 → #23**. The grown-up version of every technique here returns in #23.

**Capstone link (Phase 1):** these techniques feed the *Client Portfolio Assistant (v0)* capstone (supervisor + sub-agents over a synthetic portfolio, with long-term memory + HITL) — built once #2–#4 are done.

> ⚠️ **Data & compliance:** use **only synthetic or public data**. No real client data, MNPI, or production systems. Trading-flavored examples are decision-support only.

Each top-level directory is a self-contained module covering one technique (e.g., `scratchpad/`, `context_isolation/`, `subagent_delegation/`). Each module contains a `.ipynb` notebook and a `learning.md` journal.

## Package Manager: uv

This project uses `uv`, not `pip` or `poetry`.

```bash
uv sync                  # install/update all dependencies from uv.lock
uv add <package>         # add a new dependency
uv remove <package>      # remove a dependency
uv run python <script>   # run a script in the project virtualenv
```

Never use `pip install` directly — it bypasses the lockfile.

## Linting and Type Checking

```bash
uv run ruff check .      # lint
uv run ruff format .     # format
uv run mypy .            # type check
```

**Ruff config** (from `pyproject.toml`):
- Google docstring convention (`D` rules, `pydocstyle.convention = "google"`)
- Line length is **not** enforced (E501 ignored)
- Modern type syntax enforced (`UP` rules) — use `list[str]` not `List[str]`, `str | None` not `Optional[str]`
- `UP006`, `UP007`, `UP035`, `D417` are ignored
- Test files are exempt from docstring requirements

## LangGraph Runtime Patterns

**Manual tool invocation loop:** `prompt | llm_with_tool` returns an `AIMessage` with tool call metadata — it does NOT invoke the tool. The loop (extract → invoke → `ToolMessage` → re-invoke) is always manual unless using `create_agent` (the `langchain` factory that superseded the deprecated `langgraph.prebuilt.create_react_agent`).

**State field initialization:** TypedDict state fields don't exist at runtime until explicitly populated. Always guard with `state.get("field", default)` or initialize in the input dict. Reading an uninitialized field will raise a KeyError.

**Parallel execution:** Use `Annotated[Type, reducer]` for merging parallel branch outputs. Use `Send()` API for explicit fan-out. `batch()` uses `ThreadPoolExecutor` internally for I/O-bound parallelism.

**Rate limiting:** Free-tier APIs need `max_concurrency=1` on `.batch()` calls to avoid 429 errors.

## LangSmith Tracing

`LANGSMITH_TRACING=true` is set in `.env` — every LangChain/LangGraph invocation is automatically traced to the cloud. Be aware of this when running notebooks; traces are sent to the cloud.

## Security Warning

**The `.env` file contains live API keys** (OpenAI, Anthropic, Tavily, HuggingFace, Mistral, Moonshot, Google, LangSmith). This file is currently NOT gitignored. Do not push this repository to any remote without first adding `.env` to `.gitignore` and rotating any exposed keys.

## Development Conventions

- **Notebook-first:** All source code lives in `.ipynb` files. There are no importable `.py` modules. Copy-paste across notebooks is the current pattern.
- **Learning journals:** Each module has a `learning.md` documenting design decisions, mistakes, and open questions. Update it after each session.
- **Template:** Use `concepts_learning_template.md` at the repo root as the starting point for new `learning.md` entries.
- **ADRs:** Before each build, write an Architecture Decision Record in `decisions/` using `adr_template.md` (≥2 candidate architectures + decision matrix + predicted failure modes).
- **Python version:** 3.12 (see `.python-version`). Range: `>=3.11, <3.14`.

## Learning Workflow — Skills & Agents

All learning-acceleration tools live in `.claude/skills/` and `.claude/agents/`.

### Skills (invoke with `/skill-name`)

| Skill | When to use |
|---|---|
| `/session-prep [module\|next]` | **Start of every session** — surfaces last insight, open questions, focus recommendation |
| `/concept-check [module\|all\|concept]` | After reading or building — force active retrieval, find gaps |
| `/quick-recap [module\|yesterday\|all]` | Next day / 3 days later — spaced repetition recap card |
| `/explain-deep <concept>` | When a concept feels slippery — 6-layer Feynman breakdown |
| `/pattern-map [all\|primitive\|module]` | For synthesis — shows cross-technique pattern connections |
| `/notebook-debug` | When a cell errors — matches against known LangGraph gotchas |
| `/update-learning <module>` | End of every session — appends structured journal entry + `_index.md` row |
| `/annotate-notebook <module>` | After building — adds Input/Output/Design/Observation cells |
| `/new-module <name>` | Starting a new technique — scaffolds directory, notebook, journal |
| `/adr [title\|reconcile N\|list]` | **Before a build** — record an architecture decision (constraint, ≥2 candidates, matrix, predicted failure modes) to `decisions/` and the master Design Decisions Log; `reconcile` closes the predicted-vs-actual loop after |
| `/explain-paper <pdf>` | Dropped a new paper PDF in `papers_pdf/` — generates the beginner-friendly explainer `.md` in `papers_and_articles/` in the house style (tables, callouts, analogies, Context-Engineering mapping) |
| `/paper-to-build <slug>` | After `/explain-paper` — scaffolds a short trading/wealth-management problem + a companion notebook (`builds/<slug>.ipynb`) whose sections cover **every** aspect of the paper, as a comprehension check |
| `/commit [push]` | End of session / "save everything" — stages all work (with a `.env`/secrets guard), then commits with a conventional-commit subject + short bullet summary of what changed; only pushes if you say `push` |

### Agents (invoked via Agent tool or directly)

| Agent | When to use |
|---|---|
| `learning-coach` | Big-picture guidance — what to work on, gap analysis, practice experiments |
| `pattern-detective` | Deep cross-technique analysis — primitive inventory, mistake taxonomy, dependency graph |

### Recommended Session Flow

```
Session start:  /session-prep
During build:   /notebook-debug  (if errors hit)
                /explain-deep    (if a concept is unclear)
Session end:    /update-learning
                /annotate-notebook
Next day:       /quick-recap
Weekly:         /concept-check all
                /pattern-map
```

After a session, run `/sync-master` from the workspace root to roll progress up into `../MASTER_INDEX.md`.
