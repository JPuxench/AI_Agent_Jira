#!/usr/bin/env python3
"""
Advanced Jira Ticket Extractor with XRay and Custom Field Support.
Extends the base agent with additional extraction capabilities.
"""

import json
import csv
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import sys
import os
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


@dataclass
class TicketSection:
    """Represents an extracted section from a ticket."""
    name: str
    content: str
    cleaned: str = ""
    
    def __post_init__(self):
        self.cleaned = self.content.strip()


class AdvancedJiraExtractor:
    """Advanced ticket extractor with XRay and custom field support."""
    
    def __init__(self, jira_url: str, username: str, api_token: str):
        """Initialize the advanced extractor."""
        self.jira_url = jira_url
        self.username = username
        self.api_token = api_token
        self.jira = None
        self.tickets_data = []
        self.extraction_stats = {
            'total_tickets': 0,
            'details_found': 0,
            'descriptions_found': 0,
            'test_details_found': 0,
            'custom_fields_found': 0
        }
    
    def connect(self) -> bool:
        """Connect to Jira instance."""
        try:
            print(f"🔗 Connecting to Jira: {self.jira_url}")
            self.jira = JIRA(
                server=self.jira_url,
                basic_auth=(self.username, self.api_token)
            )
            self.jira.myself()
            print("✅ Connected successfully!")
            return True
        except JIRAError as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def extract_smart_sections(self, text: str) -> Dict[str, str]:
        """
        Smartly extract multiple sections from text using regex and patterns.
        
        Args:
            text: Full ticket description
            
        Returns:
            Dictionary of extracted sections
        """
        sections = {}
        if not text:
            return sections
        
        # Define common section patterns
        patterns = {
            'Details': r'(?:##?\s*)?Details?\s*:?\n(.*?)(?=\n(?:##?\s*)?(?:Description|Test Details|Steps|Expected|Acceptance|Actual|Environment|Severity))',
            'Description': r'(?:##?\s*)?Description\s*:?\n(.*?)(?=\n(?:##?\s*)?(?:Details|Test Details|Steps|Expected))',
            'Test Details': r'(?:##?\s*)?Test Details?\s*:?\n(.*?)(?=\n(?:##?\s*)?(?:Details|Description|Steps|Expected))',
            'Steps': r'(?:##?\s*)?Steps?(?:\s+to\s+reproduce)?\s*:?\n(.*?)(?=\n(?:##?\s*)?(?:Expected|Actual|Details))',
            'Expected': r'(?:##?\s*)?Expected\s*(?:Result|Behavior)?\s*:?\n(.*?)(?=\n(?:##?\s*)?(?:Actual|Details|Steps))',
            'Actual': r'(?:##?\s*)?Actual\s*(?:Result|Behavior)?\s*:?\n(.*?)(?=\n(?:##?\s*)?(?:Expected|Environment|Details))',
            'Environment': r'(?:##?\s*)?Environment\s*:?\n(.*?)(?=\n(?:##?\s*)?|\Z)',
            'Acceptance Criteria': r'(?:##?\s*)?Acceptance\s+Criteria?\s*:?\n(.*?)(?=\n(?:##?\s*)?|\Z)',
        }
        
        for section_name, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                sections[section_name] = match.group(1).strip()
        
        return sections
    
    def extract_xray_fields(self, ticket) -> Dict[str, Any]:
        """
        Extract XRay test execution fields if present.
        
        Args:
            ticket: JIRA ticket object
            
        Returns:
            Dictionary of XRay-related fields
        """
        xray_data = {}
        
        # Common XRay custom field names
        xray_field_names = [
            'Test Type',
            'Test Status',
            'Test Execution',
            'Test Plan',
            'Environment',
            'Execution Details',
            'Test Evidence'
        ]
        
        # Look for custom fields
        for field_name in xray_field_names:
            for field_key, field_value in ticket.fields.__dict__.items():
                if isinstance(field_value, dict) and 'name' in field_value:
                    if field_name.lower() in field_value['name'].lower():
                        xray_data[field_name] = field_value
        
        return xray_data
    
    def extract_comprehensive_data(self, ticket) -> Dict[str, Any]:
        """
        Extract comprehensive data from a ticket including all sections.
        
        Args:
            ticket: JIRA ticket object
            
        Returns:
            Dictionary of all extracted data
        """
        full_description = ticket.fields.description or ""
        smart_sections = self.extract_smart_sections(full_description)
        xray_fields = self.extract_xray_fields(ticket)
        
        # Update stats
        self.extraction_stats['total_tickets'] += 1
        if 'Details' in smart_sections:
            self.extraction_stats['details_found'] += 1
        if full_description:
            self.extraction_stats['descriptions_found'] += 1
        if 'Test Details' in smart_sections:
            self.extraction_stats['test_details_found'] += 1
        if xray_fields:
            self.extraction_stats['custom_fields_found'] += 1
        
        data = {
            'ticket_metadata': {
                'key': ticket.key,
                'id': ticket.id,
                'summary': ticket.fields.summary,
                'type': ticket.fields.issuetype.name,
                'status': ticket.fields.status.name,
                'priority': ticket.fields.priority.name if ticket.fields.priority else None,
                'created': str(ticket.fields.created),
                'updated': str(ticket.fields.updated),
            },
            'full_description': full_description,
            'extracted_sections': smart_sections,
            'xray_fields': xray_fields,
            'custom_metadata': {}
        }
        
        # Add additional metadata
        if hasattr(ticket.fields, 'labels'):
            data['custom_metadata']['labels'] = ticket.fields.labels
        if hasattr(ticket.fields, 'assignee') and ticket.fields.assignee:
            data['custom_metadata']['assignee'] = ticket.fields.assignee.displayName
        if hasattr(ticket.fields, 'reporter') and ticket.fields.reporter:
            data['custom_metadata']['reporter'] = ticket.fields.reporter.displayName
        if hasattr(ticket.fields, 'components') and ticket.fields.components:
            data['custom_metadata']['components'] = [c.name for c in ticket.fields.components]
        
        return data
    
    def fetch_and_extract(self, project: Optional[str] = None, limit: int = 50, jql: str = None) -> bool:
        """Fetch and extract all ticket data."""
        try:
            if not self.jira:
                print("❌ Not connected to Jira.")
                return False
            
            # Build JQL query
            if jql:
                query = jql
            elif project:
                query = f'project = {project}'
            else:
                query = 'ORDER BY updated DESC'
            
            print(f"\n🔍 Fetching tickets (limit: {limit})...")
            print(f"   Query: {query}")
            issues = self.jira.search_issues(query, maxResults=limit)
            
            if not issues:
                print("⚠️  No tickets found.")
                return True
            
            print(f"✅ Found {len(issues)} tickets. Extracting comprehensive data...")
            
            for i, issue in enumerate(issues, 1):
                print(f"   [{i}/{len(issues)}] {issue.key}...", end='', flush=True)
                extracted = self.extract_comprehensive_data(issue)
                self.tickets_data.append(extracted)
                print(" ✓")
            
            return True
        except Exception as e:
            print(f"❌ Error fetching tickets: {e}")
            return False
    
    def save_json(self, filename: Optional[str] = None) -> str:
        """Save data to JSON."""
        if not self.tickets_data:
            return ""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"jira_tickets_advanced_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.tickets_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved to: {Path(filename).absolute()}")
            return filename
        except Exception as e:
            print(f"❌ Error saving JSON: {e}")
            return ""
    
    def save_csv(self, filename: Optional[str] = None) -> str:
        """Save ticket summary to CSV."""
        if not self.tickets_data:
            return ""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"jira_tickets_summary_{timestamp}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                fieldnames = [
                    'Key', 'Summary', 'Type', 'Status', 'Priority',
                    'Details', 'Test Details', 'Created', 'Updated'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for ticket in self.tickets_data:
                    sections = ticket['extracted_sections']
                    writer.writerow({
                        'Key': ticket['ticket_metadata']['key'],
                        'Summary': ticket['ticket_metadata']['summary'],
                        'Type': ticket['ticket_metadata']['type'],
                        'Status': ticket['ticket_metadata']['status'],
                        'Priority': ticket['ticket_metadata']['priority'],
                        'Details': sections.get('Details', '')[:100],
                        'Test Details': sections.get('Test Details', '')[:100],
                        'Created': ticket['ticket_metadata']['created'],
                        'Updated': ticket['ticket_metadata']['updated'],
                    })
            
            print(f"📊 Saved CSV to: {Path(filename).absolute()}")
            return filename
        except Exception as e:
            print(f"❌ Error saving CSV: {e}")
            return ""
    
    def print_report(self):
        """Print detailed extraction report."""
        print("\n" + "="*70)
        print("📊 ADVANCED EXTRACTION REPORT")
        print("="*70)
        
        print(f"\n📈 Statistics:")
        print(f"   Total tickets: {self.extraction_stats['total_tickets']}")
        print(f"   Details found: {self.extraction_stats['details_found']}")
        print(f"   Descriptions: {self.extraction_stats['descriptions_found']}")
        print(f"   Test Details found: {self.extraction_stats['test_details_found']}")
        print(f"   Custom fields: {self.extraction_stats['custom_fields_found']}")
        
        print(f"\n📋 Tickets processed:")
        for ticket in self.tickets_data:
            meta = ticket['ticket_metadata']
            sections = ticket['extracted_sections']
            print(f"\n   {meta['key']}: {meta['summary']}")
            print(f"      Status: {meta['status']} | Type: {meta['type']}")
            if sections:
                print(f"      Extracted sections: {', '.join(sections.keys())}")


def main():
    """Main entry point."""
    try:
        print("\n" + "="*70)
        print("🤖 ADVANCED JIRA TICKET EXTRACTOR")
        print("="*70)
        
        # Check for env variables first
        env_url = os.getenv('JIRA_URL')
        if env_url and not env_url.endswith('jspa'):
            jira_url = env_url.rstrip('/')
            print(f"\n✅ Using Jira URL from .env: {jira_url}")
        else:
            # Get user inputs
            jira_url = input("\n📌 Enter Jira URL: ").strip().rstrip('/')
            if not jira_url.startswith('http'):
                jira_url = 'https://' + jira_url
        
        env_username = os.getenv('JIRA_USERNAME')
        env_token = os.getenv('JIRA_API_TOKEN')
        
        if env_username and env_token:
            username = env_username
            api_token = env_token
            print("✅ Using credentials from .env file")
        else:
            username = input("Enter username/email: ").strip()
            api_token = masked_input("Enter API token: ")
        
        env_project = os.getenv('JIRA_PROJECT')
        if env_project:
            project = env_project.strip().upper()
            print(f"\n⚙️  Configuration (from .env)")
            print(f"   Project: {project}")
        else:
            project = input("\nEnter project key (press Enter for all): ").strip().upper() or None
        
        print("\n🧪 XRay Configuration (Optional)")
        print("   Examples: text ~ 'CrossAccounting' | labels = 'xray-test' | status = 'Open'")
        xray_filter = input("Enter additional JQL filter (press Enter for none): ").strip() or None
        
        # Build JQL query
        jql_query = None
        if xray_filter:
            if project:
                jql_query = f'project = {project} AND {xray_filter}'
            else:
                jql_query = xray_filter
        
        env_limit = os.getenv('JIRA_LIMIT')
        if env_limit:
            try:
                limit = int(env_limit)
            except ValueError:
                limit = 50
        else:
            try:
                limit = int(input("\nEnter ticket limit (default: 50): ").strip() or 50)
            except ValueError:
                limit = 50
        
        # Run extractor
        extractor = AdvancedJiraExtractor(jira_url, username, api_token)
        
        if not extractor.connect():
            sys.exit(1)
        
        if not extractor.fetch_and_extract(project, limit, jql_query):
            sys.exit(1)
        
        # Save results
        extractor.save_json()
        extractor.save_csv()
        extractor.print_report()
        
        print("\n✅ Advanced extraction completed!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
