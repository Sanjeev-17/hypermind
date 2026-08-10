---
# Obsidian Connection

**Vault (HyperMind second brain):** `C:\Obsidian vaults\Hypermind vault`  
**Start:** `90 System/Home.md` · docs in `90 System/Documentation/`  
**Repo stub:** `obsidian/` in GitHub is documentation only — permanent notes live in the vault above.

---

## Current status

| Check | Status |
|-------|--------|
| Obsidian app | Running |
| Vault open | `C:\Obsidian vaults\Hypermind vault` |
| Local REST API plugin | **Not installed** — MCP cannot connect yet |
| Folder scaffold | Apply via OBSIDIAN_STRUCTURE / vault setup |

---

## Connect Cursor ↔ Obsidian (MCP)

### 1. In Obsidian (Portfolio vault)

1. Settings → Community plugins → Turn on community plugins  
2. Browse → install **Local REST API** (coddingtonbear)  
3. Enable the plugin  
4. Settings → Local REST API → copy **API Key**  
5. Optional but easier for Cursor: enable **Non-encrypted (HTTP) server** (port `27123`)

Keep Obsidian open while using the agent.

### 2. Add MCP to Cursor

Create or edit `C:\Users\Sanje\.cursor\mcp.json` (global) — **do not commit the API key to GitHub**.

**Preferred if HTTP enabled:**

```json
{
  "mcpServers": {
    "obsidian": {
      "url": "http://127.0.0.1:27123/mcp/",
      "headers": {
        "Authorization": "Bearer PASTE_API_KEY_HERE"
      }
    }
  }
}
```

**HTTPS default (needs trusting self-signed cert):**

```json
{
  "mcpServers": {
    "obsidian": {
      "url": "https://127.0.0.1:27124/mcp/",
      "headers": {
        "Authorization": "Bearer PASTE_API_KEY_HERE"
      }
    }
  }
}
```

Restart Cursor (or reload MCP). Confirm the `obsidian` server shows as ready.

### 3. Verify

Ask the agent to list vault files or read `00-System/Second Brain/Home.md`.

---

## Without MCP (fallback)

Agent can still read/write markdown under `C:\Obsidian vaults\Hypermind vault` via filesystem when permissions allow. MCP is preferred for search/open-in-app.

---

## Related

- `OBSIDIAN_STRUCTURE.md`
- `KNOWLEDGE_PIPELINE.md`
- `KNOWLEDGE_STANDARDS.md`
