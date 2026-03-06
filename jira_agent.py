#!/usr/bin/env python3
"""
AI Agent for extracting Jira tickets data.
Reads tickets from a Jira instance and extracts data from specific sections.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import getpass
import sys
from dotenv import load_dotenv

try:
    from jira import JIRA
    from jira.exceptions import JIRAError
except ImportError:
    print("ERROR: jira library not installed. Please run: pip install -r requirements.txt")
    sys.exit(1)

# Load environment variables from .env file
load_dotenv()


def masked_input(prompt: str) -> str:
    """Read input with asterisks displayed for each character."""
    sys.stdout.write(prompt)
    sys.stdout.flush()
    
    password = []
    while True:
        try:
            ch = sys.stdin.read(1)
            if ch == '\n':
                sys.stdout.write('\n')
                break
            elif ch == '\b':
                # Handle backspace
                if password:
                    password.pop()
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
            else:
                password.append(ch)
                sys.stdout.write('*')
                sys.stdout.flush()
        except (KeyboardInterrupt, EOFError):
            sys.stdout.write('\n')
            raise
    
    return ''.join(password)


class JiraTicketExtractor:
    """Agent for extracting data from Jira tickets."""

    def __init__(self, jira_url: str, pat: str = None, username: str = None, api_token: str = None):
        """
        Initialize the Jira extractor.

        Args:
            jira_url: URL of the Jira instance (e.g., https://jira.example.com)
            pat: Personal Access Token for Jira Server (preferred)
            username: Jira username or email (for basic auth fallback)
            api_token: Jira API token (for basic auth fallback)
        """
        self.jira_url = jira_url
        self.pat = pat
        self.username = username
        self.api_token = api_token
        self.jira = None
        self.tickets_data = []

    def connect(self) -> bool:
        """
        Connect to Jira instance.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            print(f"\n🔗 Connecting to Jira: {self.jira_url}")

            if self.pat:
                # Use Personal Access Token (Bearer token) for Jira Server
                self.jira = JIRA(
                    server=self.jira_url,
                    token_auth=self.pat
                )
            else:
                # Fallback to basic auth for Jira Cloud
                self.jira = JIRA(
                    server=self.jira_url,
                    basic_auth=(self.username, self.api_token)
                )

            # Test the connection
            self.jira.myself()
            print("✅ Successfully connected to Jira!")
            return True
        except JIRAError as e:
            print(f"❌ Connection error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def extract_section(self, text: str, section_name: str) -> str:
        """
        Extract a specific section from ticket description.
        
        Args:
            text: The full text to search in
            section_name: Name of the section to extract (e.g., "Details", "Description")
            
        Returns:
            str: The extracted section content
        """
        if not text:
            return ""
            
        lines = text.split('\n')
        section_content = []
        in_section = False
        
        for line in lines:
            # Check if this is the section header
            if line.strip().lower().startswith(section_name.lower()):
                in_section = True
                continue
                
            # If we were in a section and hit another section header, stop
            if in_section and line.strip() and line.strip()[0].isupper() and ':' in line:
                break
                
            # Collect section content
            if in_section:
                if line.strip():
                    section_content.append(line.strip())
        
        return '\n'.join(section_content).strip()
    
    def extract_ticket_data(self, ticket) -> Dict[str, Any]:
        """
        Extract relevant data from a single ticket.
        
        Args:
            ticket: JIRA ticket object
            
        Returns:
            Dict containing extracted data
        """
        data = {
            'key': ticket.key,
            'summary': ticket.fields.summary,
            'type': ticket.fields.issuetype.name,
            'status': ticket.fields.status.name,
            'created': str(ticket.fields.created),
            'updated': str(ticket.fields.updated),
            'description': ticket.fields.description or "",
            'details': {},
            'test_details': {}
        }
        
        # Extract sections from description
        full_description = ticket.fields.description or ""
        
        data['details'] = self.extract_section(full_description, 'Details')
        data['test_details'] = self.extract_section(full_description, 'Test Details')
        
        # Extract additional fields if they exist
        if hasattr(ticket.fields, 'labels'):
            data['labels'] = ticket.fields.labels
        if hasattr(ticket.fields, 'assignee') and ticket.fields.assignee:
            data['assignee'] = ticket.fields.assignee.displayName
        if hasattr(ticket.fields, 'reporter') and ticket.fields.reporter:
            data['reporter'] = ticket.fields.reporter.displayName
            
        return data
    
    def fetch_all_tickets(self, project: str = None, limit: int = 50, jql: str = None) -> bool:
        """
        Fetch all tickets from the Jira instance.
        
        Args:
            project: Optional project key to filter tickets (e.g., "TEST")
            limit: Maximum number of tickets to fetch
            jql: Optional custom JQL query to override project filtering
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.jira:
                print("❌ Not connected to Jira. Call connect() first.")
                return False
            
            # Build JQL query
            if jql:
                # Use custom JQL if provided
                query = jql
            elif project:
                query = f'project = {project}'
            else:
                query = 'ORDER BY updated DESC'
            
            print(f"\n🔍 Fetching tickets...")
            print(f"   Query: {query}")
            print(f"   Limit: {limit}")
            
            issues = self.jira.search_issues(query, maxResults=limit)
            
            if not issues:
                print("⚠️  No tickets found.")
                return True
            
            print(f"✅ Found {len(issues)} tickets. Extracting data...")
            
            for i, issue in enumerate(issues, 1):
                print(f"   [{i}/{len(issues)}] Processing {issue.key}...", end='', flush=True)
                extracted = self.extract_ticket_data(issue)
                self.tickets_data.append(extracted)
                print(" ✓")
            
            return True
        except JIRAError as e:
            print(f"❌ Error fetching tickets: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def save_results(self, output_file: str = None) -> str:
        """
        Save extracted data to a JSON file.
        
        Args:
            output_file: Optional output filename
            
        Returns:
            str: Path to the output file
        """
        if not self.tickets_data:
            print("⚠️  No data to save.")
            return ""
        
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"jira_tickets_{timestamp}.json"
        
        output_path = Path(output_file)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.tickets_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Data saved to: {output_path.absolute()}")
            return str(output_path.absolute())
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            return ""
    
    def display_summary(self):
        """Display a summary of extracted data."""
        print("\n" + "="*60)
        print("📊 EXTRACTION SUMMARY")
        print("="*60)
        print(f"Total tickets processed: {len(self.tickets_data)}")
        
        if self.tickets_data:
            print("\n📝 Tickets summary:")
            for ticket in self.tickets_data:
                print(f"\n  • {ticket['key']}: {ticket['summary']}")
                print(f"    Type: {ticket['type']}")
                print(f"    Status: {ticket['status']}")
                if isinstance(ticket['details'], str) and ticket['details']:
                    print(f"    Details: {ticket['details'][:100]}...")
                if isinstance(ticket['test_details'], str) and ticket['test_details']:
                    print(f"    Test Details: {ticket['test_details'][:100]}...")


def prompt_for_jira_url() -> str:
    """Prompt user for Jira URL."""
    # Check for env variable first
    env_url = os.getenv('JIRA_URL')
    if env_url and not env_url.endswith('jspa'):
        print(f"✅ Using Jira URL from .env: {env_url}")
        return env_url.rstrip('/')
    
    print("\n" + "="*60)
    print("🤖 JIRA TICKET EXTRACTOR AGENT")
    print("="*60)
    
    while True:
        url = input("\n📌 Enter Jira URL (e.g., https://jira.example.com): ").strip()
        if url.startswith('http://') or url.startswith('https://'):
            # Remove trailing slash if present
            return url.rstrip('/')
        else:
            print("❌ Please enter a valid URL starting with http:// or https://")


def prompt_for_credentials() -> tuple:
    """Prompt user for Jira credentials.

    Returns:
        tuple: (pat, username, api_token) - PAT is preferred for Jira Server
    """
    # Check for PAT first (Jira Server)
    env_pat = os.getenv('JIRA_PAT')
    if env_pat:
        print("\n🔐 Using Personal Access Token from .env file")
        return env_pat, None, None

    # Check for basic auth credentials (Jira Cloud)
    env_username = os.getenv('JIRA_USERNAME')
    env_token = os.getenv('JIRA_API_TOKEN')

    if env_username and env_token:
        print("\n🔐 Using credentials from .env file")
        return None, env_username, env_token

    # Prompt user for credentials
    print("\n🔐 Jira Authentication")
    print("   For Jira Server, use a Personal Access Token (PAT)")
    print("   For Jira Cloud, use username + API token")

    auth_type = input("Use PAT (p) or username/token (u)? [p]: ").strip().lower()

    if auth_type == 'u':
        username = input("Enter username/email: ").strip()
        api_token = masked_input("Enter API token (or password): ")
        return None, username, api_token
    else:
        pat = masked_input("Enter Personal Access Token: ")
        return pat, None, None


def prompt_for_project_and_limit() -> tuple:
    """Prompt user for project and limit."""
    # Check for env variables first
    env_project = os.getenv('JIRA_PROJECT')
    env_limit = os.getenv('JIRA_LIMIT')
    
    if env_project:
        project = env_project.upper()
        print(f"\n⚙️  Configuration (from .env)")
        print(f"   Project: {project}")
    else:
        print("\n⚙️  Configuration")
        project = input("Enter project key (press Enter to fetch all projects): ").strip().upper()
        project = project if project else None
    
    if env_limit:
        try:
            limit = int(env_limit)
            print(f"   Limit: {limit}")
        except ValueError:
            limit = 50
    else:
        try:
            limit = input("Enter maximum number of tickets to fetch (default: 50): ").strip()
            limit = int(limit) if limit else 50
        except ValueError:
            print("⚠️  Invalid number, using default limit of 50")
            limit = 50
    
    return project, limit


def prompt_for_xray_filter() -> str:
    """Prompt user for XRay-specific filtering (optional)."""
    print("\n🧪 XRay Configuration (Optional)")
    print("   For XRay test repositories, you can filter by custom criteria")
    
    use_xray = input("Do you want to filter by XRay path or custom criteria? (y/n): ").strip().lower()
    
    if use_xray == 'y':
        print("\n   Examples:")
        print("   - text ~ 'CrossAccounting'")
        print("   - labels = 'xray-test'")
        print("   - status = 'Open'")
        print("   - issuetype = 'Test'")
        jql_addition = input("\n   Enter additional JQL filter (or press Enter for none): ").strip()
        return jql_addition
    
    return None


def main():
    """Main entry point for the agent."""
    try:
        # Get user inputs
        jira_url = prompt_for_jira_url()
        pat, username, api_token = prompt_for_credentials()
        project, limit = prompt_for_project_and_limit()
        xray_filter = prompt_for_xray_filter()

        # Build JQL query
        jql_query = None
        if xray_filter:
            if project:
                jql_query = f'project = {project} AND {xray_filter}'
            else:
                jql_query = xray_filter

        # Create and run extractor
        extractor = JiraTicketExtractor(jira_url, pat=pat, username=username, api_token=api_token)
        
        if not extractor.connect():
            print("\n❌ Failed to connect to Jira. Exiting.")
            sys.exit(1)
        
        if not extractor.fetch_all_tickets(project, limit, jql_query):
            print("\n❌ Failed to fetch tickets. Exiting.")
            sys.exit(1)
        
        # Display summary and save results
        extractor.display_summary()
        extractor.save_results()
        
        print("\n✅ Agent completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Agent interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
