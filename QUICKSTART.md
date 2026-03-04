# Jira AI Agent - Quick Reference

## Installation (5 minutes)

```bash
cd c:\MyZone\Code\AI_Agent_Jira
pip install -r requirements.txt
```

## Run Basic Agent

```bash
python jira_agent.py
```

**Interactive Prompts:**
1. Jira URL: `https://your-jira.com`
2. Username/Email: Your email
3. API Token: [Get from https://id.atlassian.com/manage-profile/security/api-tokens]
4. Project Key: `TEST` (or leave blank)
5. Limit: `50`

**Output:** `jira_tickets_YYYYMMDD_HHMMSS.json`

## Run Advanced Agent (with CSV export)

```bash
python jira_agent_advanced.py
```

**Output:** 
- `jira_tickets_advanced_YYYYMMDD_HHMMSS.json`
- `jira_tickets_summary_YYYYMMDD_HHMMSS.csv`

## View Examples

```bash
python examples.py basic       # Basic extraction example
python examples.py advanced    # Advanced extraction example
python examples.py workflow    # Step-by-step workflow
python examples.py tips        # Tips and best practices
```

## What Gets Extracted

### From Ticket Sections:
- ✅ **Details** - Key information
- ✅ **Description** - Main description
- ✅ **Test Details** - Testing information

### Additional Data:
- ✅ Ticket key and summary
- ✅ Type, status, priority
- ✅ Created/Updated dates
- ✅ Assignee and reporter
- ✅ Labels and components

## Configuration (Optional)

Create `.env` file:
```env
JIRA_URL=https://your-jira.com
JIRA_USERNAME=your_email@example.com
JIRA_API_TOKEN=your_token
```

## Files Overview

| File | Purpose |
|------|---------|
| `jira_agent.py` | Basic ticket extraction agent |
| `jira_agent_advanced.py` | Advanced agent with smart extraction |
| `utils.py` | Helper functions and utilities |
| `examples.py` | Usage examples and guides |
| `requirements.txt` | Python dependencies |
| `README.md` | Full documentation |
| `SETUP.md` | Detailed setup guide |

## Troubleshooting

### "Invalid credentials"
→ Verify Jira username and API token

### "Connection timeout"
→ Check Jira URL and internet connection

### "No tickets found"
→ Try without specifying project (leave blank)

### Missing sections
→ Check if ticket description contains "Details:" or "Test Details:"

## Get API Token

1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Copy token
4. Use in agent when prompted

## Command Cheat Sheet

```bash
# Install
pip install -r requirements.txt

# Run basic agent
python jira_agent.py

# Run advanced agent
python jira_agent_advanced.py

# View examples
python examples.py

# Show help
python jira_agent.py --help
python jira_agent_advanced.py --help

# Delete old outputs
rm jira_tickets_*.json
rm jira_tickets_*.csv
```

## JSON Output Example

```json
[
  {
    "key": "TEST-1",
    "summary": "Implement authentication",
    "type": "Task",
    "status": "Open",
    "priority": "High",
    "created": "2024-01-15T10:30:00",
    "updated": "2024-03-04T14:20:00",
    "description": "Full ticket description...",
    "details": "Details section content...",
    "test_details": "Test details section...",
    "assignee": "John Doe",
    "labels": ["auth", "high-priority"]
  }
]
```

## Key Functions in utils.py

```python
from utils import (
    TextProcessor,           # Text extraction & processing
    JiraDataFormatter,       # Format data (JSON, CSV, Markdown)
    JiraFilter,             # Filter tickets
    CredentialsManager,     # Manage credentials
)

# Extract sections
TextProcessor.extract_markdown_section(text, "Details")

# Filter tickets
JiraFilter.filter_by_type(tickets, "Bug")
JiraFilter.filter_by_status(tickets, "Open")

# Format as markdown report
JiraDataFormatter.format_markdown_report(tickets)
```

## Common JQL Queries (in agent)

| Query | Projects |
|-------|---------|
| (leave blank) | All tickets |
| `TEST` | Only TEST project |
| `PROJ` | Only PROJ project |

## Security Tips

🔐 **Do:**
- Use API tokens (stronger than passwords)
- Store credentials in `.env` file only
- Rotate API tokens regularly

❌ **Don't:**
- Commit `.env` to version control
- Share API tokens
- Use default/weak passwords
- Store credentials in code

## Next Steps

1. ✅ Install dependencies
2. ✅ Generate Jira API token
3. ✅ Run basic agent: `python jira_agent.py`
4. ✅ Review extracted data in JSON file
5. ✅ Try advanced agent for more features
6. ✅ Use utils for custom analysis

## Need Help?

- See `README.md` for full documentation
- See `SETUP.md` for detailed setup
- Run `python examples.py` for examples
- Check Jira developer docs: https://developer.atlassian.com/

---

**Created:** March 4, 2026 | **Version:** 1.0
