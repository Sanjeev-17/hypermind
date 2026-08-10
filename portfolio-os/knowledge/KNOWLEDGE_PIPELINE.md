---
# Knowledge Pipeline

**Status:** Permanent Portfolio OS capability  
**Owner:** portfolio-producer (process) · design-intelligence-lab (research distillation) · prompt-librarian (prompt IP sync)  
**Decision:** D-006  
**Vault workflow (authoritative detail):** `C:\Obsidian vaults\Hypermind vault\90 System\Documentation\KNOWLEDGE_WORKFLOW.md`  
**Vault freeze:** `HYPERMIND_VAULT_v1.0.md` · Decision **D-007**

---

## Tool roles

| Tool | Role | What lives here |
|------|------|-----------------|
| **Cursor** | Execution | Agents, skills, file ops |
| **Paper** | Temporary research sandbox | Exploration · drafts · experiments |
| **Obsidian** | Permanent knowledge / second brain + prompt authoring | Atomic notes · evergreen · patterns · Context Packs · Prompt Library |
| **GitHub** | Version control + Portfolio OS + production prompts | Skills · synced prompts · templates · governance |
| **Framer** | Final product | Shipped site · CMS |
| **Portfolio OS** | Workflow + governance | Gates · briefs · Decision Log |
| **HyperMind** | Automation + intelligence | Agents · MCP · compounding loops |

Nothing valuable may remain **only** in Paper.

---

## Pipeline

```
Research
    ↓
Paper              (explore, messy, temporary)
    ↓
Knowledge Distillation
    ↓
Obsidian           (permanent, linked, reusable)
    ↓
Knowledge Graph    (MOCs · wikilinks · backlinks)
    ↓
Reusable Principles
    ↓
Portfolio Decisions   (Decision Log + Product Brief / slate / craft)
```

| Stage | Where | Exit condition |
|-------|--------|----------------|
| Research | Sources, Framer CMS, web, interviews | Question clear |
| Paper | Exploration boards / drafts | Synthesis ready to distill |
| Knowledge Distillation | Producer or specialist | Permanent note(s) per vault KNOWLEDGE_STANDARDS |
| Obsidian | Vault note + links | YAML + evidence + insight + links |
| Knowledge Graph | Bidirectional `[[wikilinks]]` + MOCs | No orphan insights that matter |
| Portfolio Decisions | `governance/Decision_Log.md` + GitHub artefacts | Decision cites Obsidian paths when knowledge-backed |

---

## Research → application

```
Reference → Research → Knowledge → Framework → Application → Project
```

Never store screenshots without extracted principles.

## Prompt workflow

```
Draft → Testing → Review → Approved → GitHub Sync → Production
```

Author in Obsidian `03 Knowledge/Prompt Library/`; production in `portfolio-os/prompts/`.

## Research session exit ritual

1. Research Summary → Obsidian `04 Research`  
2. Design Principles → `03 Knowledge` / Evergreen (atomic)  
3. Actionable Insights in each note  
4. Link notes + update MOC / Context Pack if cluster changed  
5. Discard or archive Paper exploration  

---

## Token efficiency

- Prefer **one Context Pack** then 1–3 notes — never vault dumps  
- Link; do not copy  
- Deduplicate before create  

---

## Related

- Vault: `HYPERMIND_VAULT_v1.0` · `VAULT_ARCHITECTURE` · `KNOWLEDGE_STANDARDS` · `MCP_READINESS` · `PROMPT_WORKFLOW`  
- GitHub: `OBSIDIAN_STRUCTURE.md` · `OBSIDIAN_CONNECTION.md` · `WRITING_STANDARD.md` · Decision D-007  
