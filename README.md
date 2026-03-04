# Jira Ticket Data Extractor Agent

An AI agent that reads Jira tickets and extracts specific data sections including Details, Description, and Test Details.

## Features

- 🔗 Connect to any Jira instance
- 📥 Fetch tickets from specified project or all projects
- 🔍 Extract structured data from ticket sections
- 💾 Export data to JSON format
- 📊 Display summary of extracted information

## Requirements

- Python 3.8+
- pip or conda

## Installation

1. Clone this repository
   ```bash
   cd c:\MyZone\Code\AI_Agent_Jira
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the agent:
```bash
python jira_agent.py
```

### Interactive Prompts

The agent will ask for:

1. **Jira URL**: The URL of your Jira instance (e.g., `https://jira.example.com`)
2. **Username/Email**: Your Jira username or email address
3. **API Token**: Your Jira API token (or password)
   - To generate an API token: https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/
4. **Project Key** (optional): Filter by project (e.g., `TEST`, `PROJ`)
5. **Limit**: Maximum number of tickets to fetch (default: 50)

### Output

The agent will:
- Display a summary in the terminal showing processed tickets
- Extract and save data to a JSON file with timestamp: `jira_tickets_YYYYMMDD_HHMMSS.json`

### JSON Output Format

```json
[
  {
    "key": "TEST-1",
    "summary": "Ticket title",
    "type": "Bug",
    "status": "In Progress",
    "created": "2024-01-01T10:00:00+00:00",
    "updated": "2024-01-02T15:30:00+00:00",
    "description": "Full ticket description",
    "details": "Extracted Details section",
    "test_details": "Extracted Test Details section",
    "labels": ["label1", "label2"],
    "assignee": "John Doe",
    "reporter": "Jane Smith"
  }
]
```

## Section Extraction

The agent automatically extracts:

- **Details**: Content under "Details" section in description
- **Description**: Full ticket description
- **Test Details**: Content under "Test Details" section in description

## Configuration

You can also set environment variables (optional):

Create a `.env` file:
```
JIRA_URL=https://jira.example.com
JIRA_USERNAME=your_username
JIRA_API_TOKEN=your_token
```

## Troubleshooting

### Connection Issues
- Verify your Jira URL is correct (include http:// or https://)
- Check your username and API token
- Ensure you have network access to the Jira instance

### No Tickets Found
- Verify the project key is correct
- Check that you have permission to view tickets in that project
- Try fetching all projects by leaving project key empty

### API Token Issues
- Generate a new API token at https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/
- Ensure the token has read permissions

## Examples

### Fetch all tickets from all projects
```
Enter Jira URL: https://jira.example.com
Enter username/email: user@example.com
Enter API token: ****
Enter project key: <press Enter to skip>
Enter maximum number of tickets: 100
```

### Fetch only from TEST project
```
Enter Jira URL: https://jira.example.com
Enter username/email: user@example.com
Enter API token: ****
Enter project key: TEST
Enter maximum number of tickets: 50
```

## Notes

- API tokens are recommended over passwords for security
- The agent respects Jira instance permissions
- Maximum results depend on your Jira server configuration

## Support

For issues with Jira API, see:
- https://developer.atlassian.com/cloud/jira/rest/v3/
- https://jira-python.readthedocs.io/
