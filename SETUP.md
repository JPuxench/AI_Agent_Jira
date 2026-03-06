# Jira Agent - Setup & Installation Guide

## Overview

This project provides a Python agent for interacting with Jira Server instances. It can:

- **Read** tickets and extract all field data
- **Create** new tickets with custom fields
- **Replicate** existing tickets (including attachments)
- **Search** using JQL queries
- **Work with XRay** Test Cases and Test Repository

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Access to a Jira Server instance
- Personal Access Token (PAT) for authentication

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/JPuxench/AI_Agent_Jira.git
cd AI_Agent_Jira
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Generate Personal Access Token (PAT)

> **Important**: PAT is required for Jira Server. Do NOT use Atlassian Cloud API tokens - they won't work!

#### How to generate a PAT:

1. Open your Jira Server in a browser (e.g., `https://jira.yourcompany.com`)
2. Click on your **profile avatar** in the top-right corner
3. Select **Profile** from the dropdown menu
4. In the left sidebar, click **Personal Access Tokens**
5. Click the **Create token** button
6. Enter a name for your token (e.g., "Jira Agent")
7. Click **Create**
8. **Copy the token immediately!** It will only be shown once.

![PAT Location](https://confluence.atlassian.com/enterprise/files/1049769181/1049769180/1/1600186163407/PAT.png)

### Step 5: Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
JIRA_URL=https://jira.yourcompany.com
JIRA_PAT=your_personal_access_token_here
JIRA_PROJECT=EBNC
JIRA_LIMIT=50
```

### Step 6: Test the Connection

```bash
python -c "
from jira import JIRA
import os
from dotenv import load_dotenv

load_dotenv()
jira = JIRA(server=os.getenv('JIRA_URL'), token_auth=os.getenv('JIRA_PAT'))
me = jira.myself()
print(f'Connected as: {me[\"displayName\"]}')
"
```

If successful, you'll see: `Connected as: Your Name`

## Usage

### Interactive Mode

Run the main agent:

```bash
python jira_agent.py
```

Follow the prompts to:
1. Confirm Jira URL (from .env)
2. Confirm authentication (PAT from .env)
3. Select project and limit
4. Choose XRay filters (optional)

### Programmatic Usage

```python
from jira import JIRA
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to Jira
jira = JIRA(
    server=os.getenv('JIRA_URL'),
    token_auth=os.getenv('JIRA_PAT')
)

# Search for tickets
issues = jira.search_issues(
    'project = EBNC AND issuetype = "Xray Test Case"',
    maxResults=50
)

# Process tickets
for issue in issues:
    print(f"{issue.key}: {issue.fields.summary}")
    print(f"  Status: {issue.fields.status.name}")
    print(f"  Assignee: {issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned'}")
```

## Working with XRay Test Cases

### Find Tests by Repository Path

XRay Test Cases have a custom field for the repository path (`customfield_21412` in our instance):

```python
# Fetch all Xray Test Cases
issues = jira.search_issues(
    'project = EBNC AND issuetype = "Xray Test Case"',
    maxResults=500
)

# Filter by path
crossaccounting_tests = []
for issue in issues:
    path = getattr(issue.fields, 'customfield_21412', '') or ''
    if 'CrossAccounting' in path:
        crossaccounting_tests.append(issue)

print(f"Found {len(crossaccounting_tests)} tests in CrossAccounting")
```

### Extract Cucumber Scenarios

```python
issue = jira.issue('EBNC-50706')

# Get Cucumber scenario (customfield_21404)
cucumber = getattr(issue.fields, 'customfield_21404', '')
print(cucumber)
```

### Create a Test Case

```python
new_test = jira.create_issue(fields={
    'project': {'key': 'EBNC'},
    'summary': 'Test case created by agent',
    'description': 'Test description here',
    'issuetype': {'name': 'Xray Test Case'},
    'labels': ['automated'],
    'components': [{'name': 'Cross-Accounting'}],
    'customfield_21412': '/CrossAccounting',  # XRay path
    'customfield_21402': {'id': '25005'},     # Test Type: Cucumber
    'customfield_21403': {'id': '25007'},     # Scenario
})
print(f"Created: {new_test.key}")
```

## Custom Fields Reference

Common custom fields in our Jira instance:

| Field ID | Name | Description |
|----------|------|-------------|
| `customfield_21412` | XRay Test Repository Path | Path in test repository (e.g., `/CrossAccounting`) |
| `customfield_21402` | Test Type | Cucumber (id: 25005), Manual, Generic |
| `customfield_21403` | Test Type Sub | Scenario (id: 25007), etc. |
| `customfield_21404` | Cucumber Scenario | Gherkin test scenario |
| `customfield_12001` | Expected Result | Expected test result |
| `customfield_15518` | Automation Status | Pending Automation, Automated, etc. |

To list all custom fields:

```python
for field in jira.fields():
    if field['custom']:
        print(f"{field['id']}: {field['name']}")
```

## Troubleshooting

### Error: "HTTP 500 Internal Server Error"

**Cause**: Wrong authentication method.

**Solution**:
- Jira Server requires PAT (Personal Access Token)
- Jira Cloud requires Username + API Token
- Make sure you're using the correct method for your instance

### Error: "Could not find valid 'id' or 'value'"

**Cause**: Custom field requires specific format.

**Solution**: Use `{'id': 'xxx'}` format instead of string value:
```python
# Wrong
'customfield_21402': 'Cucumber'

# Correct
'customfield_21402': {'id': '25005'}
```

### Error: "Field 'xxx' does not exist"

**Cause**: Field ID varies between Jira instances.

**Solution**: List all fields and find the correct ID:
```python
for f in jira.fields():
    if 'test' in f['name'].lower():
        print(f"{f['id']}: {f['name']}")
```

### Error: "You do not have permission"

**Cause**: Your account lacks required permissions.

**Solution**: Contact your Jira administrator to grant:
- Browse Projects
- Create Issues
- Attach Files to Issues
- Edit Issues

## Security Best Practices

1. **Never commit `.env` files** to version control
2. **Never share your PAT** - treat it like a password
3. **Rotate PAT regularly** - regenerate every 3-6 months
4. **Revoke unused PATs** - delete tokens you no longer need
5. **Use minimal permissions** - only request necessary access

## Project Files

| File | Description |
|------|-------------|
| `jira_agent.py` | Main agent with PAT authentication support |
| `jira_agent_advanced.py` | Advanced extraction with additional features |
| `utils.py` | Utility functions for text processing |
| `examples.py` | Usage examples and code snippets |
| `requirements.txt` | Python dependencies |
| `.env.example` | Template for environment variables |

## Support

- **Jira Python Library**: https://jira-python.readthedocs.io/
- **Jira REST API**: https://developer.atlassian.com/cloud/jira/rest/v3/
- **XRay Documentation**: https://docs.getxray.app/

---

**Last Updated**: March 2026
