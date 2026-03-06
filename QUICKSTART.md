# Jira Agent - Quick Start Guide

## 5-Minute Setup

### 1. Install

```bash
git clone https://github.com/JPuxench/AI_Agent_Jira.git
cd AI_Agent_Jira
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 2. Get Your PAT (Personal Access Token)

1. Go to **Jira** > **Profile** > **Personal Access Tokens**
2. Click **Create token**
3. Copy the token (only shown once!)

### 3. Configure

```bash
cp .env.example .env
```

Edit `.env`:
```env
JIRA_URL=https://jira.sage.com
JIRA_PAT=your_token_here
JIRA_PROJECT=EBNC
```

### 4. Run

```bash
python jira_agent.py
```

## Quick Commands

| Task | Command |
|------|---------|
| Run agent | `python jira_agent.py` |
| Run advanced | `python jira_agent_advanced.py` |
| View examples | `python examples.py` |

## Code Snippets

### Connect to Jira

```python
from jira import JIRA
import os
from dotenv import load_dotenv

load_dotenv()
jira = JIRA(server=os.getenv('JIRA_URL'), token_auth=os.getenv('JIRA_PAT'))
```

### Read Tickets

```python
issues = jira.search_issues('project = EBNC', maxResults=10)
for issue in issues:
    print(f"{issue.key}: {issue.fields.summary}")
```

### Create Ticket

```python
new = jira.create_issue(fields={
    'project': {'key': 'EBNC'},
    'summary': 'My ticket',
    'issuetype': {'name': 'Task'},
})
print(f"Created: {new.key}")
```

### Find XRay Tests

```python
tests = jira.search_issues('project = EBNC AND issuetype = "Xray Test Case"')
for t in tests:
    path = getattr(t.fields, 'customfield_21412', '')
    print(f"{t.key}: {path}")
```

## Common Issues

| Error | Solution |
|-------|----------|
| HTTP 500 | Use PAT, not Cloud API token |
| Permission denied | Ask admin for access |
| Field not found | Field IDs vary per Jira instance |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `JIRA_URL` | Yes | Jira server URL |
| `JIRA_PAT` | Yes | Personal Access Token |
| `JIRA_PROJECT` | No | Default project |
| `JIRA_LIMIT` | No | Max tickets (default: 50) |

## Output Files

- `jira_tickets_YYYYMMDD_HHMMSS.json` - Extracted data
- `jira_tickets_summary_*.csv` - Summary (advanced agent)

## Security

- **Never commit `.env`** to git
- **Rotate PAT** every 3-6 months
- **Revoke PAT** if compromised

## More Help

- Full docs: `README.md`
- Setup guide: `SETUP.md`
- Examples: `python examples.py`

---

**Version**: 2.0 | **Updated**: March 2026
