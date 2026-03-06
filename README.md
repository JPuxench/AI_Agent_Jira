# Jira Agent

A Python agent for interacting with Jira Server instances. It can read, extract, and create Jira tickets programmatically.

## Features

- **Read tickets**: Fetch and extract data from Jira tickets
- **Create tickets**: Replicate or create new tickets with all fields
- **XRay support**: Works with XRay Test Cases and Test Repository paths
- **Attachments**: Download and upload attachments between tickets
- **Export**: Save extracted data to JSON format

## Tech Stack

| Component | Version | Description |
|-----------|---------|-------------|
| Python | 3.8+ | Programming language |
| jira | 3.10.5 | Official Jira Python library |
| python-dotenv | 1.0.0 | Environment variable management |
| requests | 2.31.0 | HTTP library for API calls |

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/JPuxench/AI_Agent_Jira.git
cd AI_Agent_Jira
```

### 2. Create virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure credentials

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your credentials (see [Authentication](#authentication) below).

### 5. Run the agent

```bash
python jira_agent.py
```

## Authentication

This agent supports **two authentication methods**:

### Option 1: Personal Access Token (PAT) - Recommended for Jira Server

PAT is the recommended method for Jira Server/Data Center installations.

#### How to generate a PAT:

1. Log in to your Jira Server instance
2. Click on your **profile avatar** (top right corner)
3. Select **Profile**
4. In the left sidebar, click **Personal Access Tokens**
5. Click **Create token**
6. Give it a name (e.g., "Jira Agent") and click **Create**
7. **Copy the token immediately** - it won't be shown again!

#### Configure in `.env`:

```env
JIRA_URL=https://your-jira-server.com
JIRA_PAT=your_personal_access_token_here
JIRA_PROJECT=YOUR_PROJECT_KEY
JIRA_LIMIT=50
```

### Option 2: Basic Auth (Username + API Token) - For Jira Cloud

If you're using Jira Cloud (atlassian.net), use this method:

1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **Create API token**
3. Copy the token

#### Configure in `.env`:

```env
JIRA_URL=https://your-company.atlassian.net
JIRA_USERNAME=your_email@example.com
JIRA_API_TOKEN=your_api_token_here
JIRA_PROJECT=YOUR_PROJECT_KEY
JIRA_LIMIT=50
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `JIRA_URL` | Yes | Your Jira instance URL |
| `JIRA_PAT` | Yes* | Personal Access Token (for Jira Server) |
| `JIRA_USERNAME` | Yes* | Your email (for Jira Cloud) |
| `JIRA_API_TOKEN` | Yes* | API Token (for Jira Cloud) |
| `JIRA_PROJECT` | No | Default project key to filter tickets |
| `JIRA_LIMIT` | No | Maximum tickets to fetch (default: 50) |

\* Either `JIRA_PAT` or (`JIRA_USERNAME` + `JIRA_API_TOKEN`) is required.

## Usage Examples

### Read tickets from a project

```python
from jira import JIRA
import os
from dotenv import load_dotenv

load_dotenv()

# Connect using PAT
jira = JIRA(
    server=os.getenv('JIRA_URL'),
    token_auth=os.getenv('JIRA_PAT')
)

# Fetch tickets
issues = jira.search_issues('project = EBNC ORDER BY updated DESC', maxResults=10)
for issue in issues:
    print(f"{issue.key}: {issue.fields.summary}")
```

### Create a new ticket

```python
new_issue = jira.create_issue(fields={
    'project': {'key': 'EBNC'},
    'summary': 'New ticket created by agent',
    'description': 'This ticket was created programmatically',
    'issuetype': {'name': 'Task'},
})
print(f"Created: {new_issue.key}")
```

### Work with XRay Test Cases

```python
# Search for XRay Test Cases in a specific repository path
issues = jira.search_issues(
    'project = EBNC AND issuetype = "Xray Test Case"',
    maxResults=100
)

# Filter by XRay repository path
for issue in issues:
    path = getattr(issue.fields, 'customfield_21412', '')
    if 'CrossAccounting' in (path or ''):
        print(f"{issue.key}: {issue.fields.summary}")
```

### Upload attachments

```python
# Add attachment to a ticket
jira.add_attachment(issue='EBNC-12345', attachment='/path/to/file.png')
```

## Project Structure

```
AI_Agent_Jira/
├── jira_agent.py           # Main agent with PAT support
├── jira_agent_advanced.py  # Advanced extraction features
├── utils.py                # Utility functions
├── examples.py             # Usage examples
├── requirements.txt        # Python dependencies
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
├── README.md               # This file
├── SETUP.md                # Detailed setup guide
└── QUICKSTART.md           # Quick reference guide
```

## Troubleshooting

### "HTTP 500 Internal Server Error"

This usually means authentication failed:
- **Jira Server**: Make sure you're using PAT, not a Cloud API token
- **Jira Cloud**: Make sure you're using API token with username

### "Field does not exist"

Custom fields vary between Jira instances. Check available fields:

```python
for field in jira.fields():
    print(f"{field['id']}: {field['name']}")
```

### "Permission denied"

Ensure your account has the required permissions:
- Browse Projects
- Create Issues (if creating tickets)
- Attach Files (if uploading attachments)

## Security Best Practices

1. **Never commit `.env` files** - they contain credentials
2. **Use PAT over passwords** - PATs can be revoked independently
3. **Rotate tokens regularly** - regenerate PAT every few months
4. **Use minimal permissions** - only grant necessary access

## Support

- [Jira Python Library Docs](https://jira-python.readthedocs.io/)
- [Jira REST API Reference](https://developer.atlassian.com/cloud/jira/rest/v3/)
- [XRay Documentation](https://docs.getxray.app/)

---

**Last Updated**: 2026.Mar.06 - 16:30:00
