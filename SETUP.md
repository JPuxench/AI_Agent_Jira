# Jira AI Agent - Setup & Installation Guide

## Overview

This project provides AI agents for automatically reading and extracting data from Jira tickets. The agents can extract specific sections (Details, Description, Test Details) from Jira tickets and export the data in multiple formats.

## Project Structure

```
AI_Agent_Jira/
├── jira_agent.py              # Basic agent for ticket extraction
├── jira_agent_advanced.py     # Advanced agent with smart extraction
├── utils.py                   # Utility functions and helpers
├── examples.py                # Examples and usage guide
├── requirements.txt           # Python dependencies
├── .env.example               # Example environment variables
├── .gitignore                 # Git ignore rules
├── README.md                  # Main documentation
└── SETUP.md                   # This file
```

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Jira account with API token access

### Step 1: Clone and Navigate

```bash
cd c:\MyZone\Code\AI_Agent_Jira
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Generate Jira API Token

1. Log in to your Jira account
2. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
3. Click "Create API token"
4. Copy the generated token

### Step 4: Run the Agent

```bash
python jira_agent.py
```

Follow the interactive prompts:
- Jira URL: `https://your-jira-instance.com`
- Username/Email: Your Jira username
- API Token: Your generated token
- Project Key: Optional (leave blank for all projects)
- Limit: Number of tickets (default: 50)

### Step 5: Access Results

Results are saved as JSON files in the same directory:
```
jira_tickets_20260304_143000.json
```

## Agent Differences

### Basic Agent (`jira_agent.py`)

- Simple, lightweight extraction
- Outputs: JSON format
- Sections: Details, Description, Test Details
- Best for: Quick extraction of essential data

**Run:**
```bash
python jira_agent.py
```

### Advanced Agent (`jira_agent_advanced.py`)

- Comprehensive data extraction
- Smart regex-based section detection
- Outputs: JSON + CSV formats
- Extraction statistics
- XRay field detection support
- Best for: Detailed analysis and reporting

**Run:**
```bash
python jira_agent_advanced.py
```

## Configuration

### Environment Variables

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
JIRA_URL=https://your-jira.com
JIRA_USERNAME=your_email@example.com
JIRA_API_TOKEN=your_api_token
JIRA_PROJECT=TEST
JIRA_LIMIT=50
```

⚠️ **Important:** Never commit `.env` files to version control.

## Section Extraction

The agents automatically extract the following sections from ticket descriptions:

### Basic Agent Extracts:
- **Details** - Key information about the ticket
- **Test Details** - Testing information and requirements

### Advanced Agent Additionally Extracts:
- **Description** - Main ticket description
- **Steps** - Steps to reproduce (for bugs)
- **Expected** - Expected behavior/results
- **Actual** - Actual behavior/results
- **Environment** - Environment information
- **Acceptance Criteria** - Acceptance criteria (for features)

## Examples

### View Examples

```bash
python examples.py              # Show all examples
python examples.py basic        # Show basic extraction example
python examples.py advanced     # Show advanced extraction example
python examples.py workflow     # Show example workflow
python examples.py tips         # Show tips and best practices
```

### Using Utility Functions

```python
from utils import TextProcessor, JiraDataFormatter, JiraFilter

# Extract specific sections
details = TextProcessor.extract_markdown_section(text, "Details")

# Format data as markdown
report = JiraDataFormatter.format_markdown_report(tickets)

# Filter tickets
bugs = JiraFilter.filter_by_type(tickets, "Bug")
critical = JiraFilter.filter_by_status(tickets, "Critical")
```

## Output Formats

### JSON Output Structure

**Basic:**
```json
[
  {
    "key": "TEST-1",
    "summary": "Ticket title",
    "type": "Bug",
    "status": "Open",
    "description": "Full description",
    "details": "Extracted Details section",
    "test_details": "Extracted Test Details section"
  }
]
```

**Advanced:**
```json
[
  {
    "ticket_metadata": {
      "key": "TEST-1",
      "summary": "Ticket title",
      "type": "Bug",
      "status": "Open"
    },
    "extracted_sections": {
      "Details": "...",
      "Description": "...",
      "Test Details": "..."
    },
    "custom_metadata": {
      "labels": ["label1"],
      "assignee": "Name"
    }
  }
]
```

### CSV Output

The advanced agent also generates CSV files with:
- Key
- Summary
- Type
- Status
- Priority
- Details (first 100 chars)
- Test Details (first 100 chars)
- Created date
- Updated date

## Troubleshooting

### Connection Issues

**Error:** "Invalid credentials"
- **Solution:** Verify your username and API token are correct
- Generate a new token: https://id.atlassian.com/manage-profile/security/api-tokens

**Error:** "Connection timeout"
- **Solution:** Check your internet connection and Jira URL
- Ensure the Jira instance is accessible

### No Tickets Found

- Verify the project key is correct
- Check your Jira permissions
- Try without specifying a project (fetch all)

### Missing Sections

Some tickets may not have all sections. Check:
- Ticket description format
- Custom field configurations
- Project-specific templates

## Advanced Features

### Custom Filtering

```python
from utils import JiraFilter

# Filter by status
open_issues = JiraFilter.filter_by_status(tickets, "Open")

# Filter by type
bugs = JiraFilter.filter_by_type(tickets, "Bug")

# Search by keyword
results = JiraFilter.filter_by_contains(tickets, "authentication")

# Find incomplete tickets
incomplete = JiraFilter.get_tickets_with_missing_sections(tickets)
```

### Text Processing

```python
from utils import TextProcessor

# Clean and normalize text
cleaned = TextProcessor.normalize_whitespace(text)

# Extract code blocks
code = TextProcessor.extract_code_blocks(text)

# Find links
links = TextProcessor.extract_links(text)

# Remove HTML
plain = TextProcessor.remove_html_tags(html_text)
```

## Performance Tips

1. **Set reasonable limits** (50-100 tickets) to avoid timeouts
2. **Use project filtering** to reduce data volume
3. **Run during off-peak hours** for better performance
4. **Check batch size settings** in Jira if fetching large amounts

## Security Best Practices

1. ✅ Use API tokens instead of passwords
2. ✅ Store credentials in `.env` file (not in code)
3. ✅ Never commit credentials to version control
4. ✅ Rotate API tokens regularly
5. ✅ Use HTTPS URL for Jira
6. ✅ Restrict file permissions on credential files

## Support & Documentation

- [Jira Python Documentation](https://jira-python.readthedocs.io/)
- [Jira REST API Docs](https://developer.atlassian.com/cloud/jira/rest/v3/)
- [Jira API Token Guide](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)

## License & Attribution

This project is created for automated Jira ticket data extraction.

## FAQ

**Q: Can I use this with Jira Server/Data Center?**
A: Yes, update the URL to your Jira instance.

**Q: How do I handle 2FA/MFA?**
A: Use API tokens, which bypass 2FA requirements.

**Q: Can I extract custom fields?**
A: The advanced agent can detect custom fields. Extend `extract_xray_fields()` for specific fields.

**Q: How many tickets can I fetch at once?**
A: Depends on server limits. Start with 50-100 and adjust.

**Q: Can I schedule this to run automatically?**
A: Yes, use Windows Task Scheduler or cron (Linux/Mac).

---

**Last Updated:** March 4, 2026
