#!/usr/bin/env python3
"""
Utility functions for Jira ticket extraction agents.
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path


class TextProcessor:
    """Utilities for processing and cleaning text from Jira."""
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """
        Normalize whitespace in text.
        
        Args:
            text: Input text
            
        Returns:
            Text with normalized whitespace
        """
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        # Remove multiple newlines
        text = re.sub(r'\n\n+', '\n\n', text)
        return text.strip()
    
    @staticmethod
    def extract_markdown_section(text: str, section_name: str) -> str:
        """
        Extract a markdown section from text.
        
        Args:
            text: Full text
            section_name: Section name (e.g., "Details", "Test Details")
            
        Returns:
            Extracted section content
        """
        if not text:
            return ""
        
        # Create flexible regex pattern for markdown headers
        pattern = (
            rf'(?:^|\n)(?:#{1,6}\s+)?{re.escape(section_name)}\s*:?\s*(?:\n|$)'
            r'(.*?)(?=(?:\n(?:#{1,6}\s+)|$))'
        )
        
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        return match.group(1).strip() if match else ""
    
    @staticmethod
    def remove_html_tags(text: str) -> str:
        """Remove HTML tags from text."""
        return re.sub(r'<[^>]+>', '', text)
    
    @staticmethod
    def extract_links(text: str) -> List[str]:
        """Extract URLs from text."""
        url_pattern = r'https?://[^\s\)]+'
        return re.findall(url_pattern, text)
    
    @staticmethod
    def extract_code_blocks(text: str) -> List[str]:
        """Extract code blocks from text."""
        # Match triple backtick code blocks
        pattern = r'```(?:\w+)?\n(.*?)\n```'
        matches = re.findall(pattern, text, re.DOTALL)
        return matches


class JiraDataFormatter:
    """Utilities for formatting Jira data."""
    
    @staticmethod
    def flatten_ticket_data(ticket_data: Dict) -> Dict[str, Any]:
        """
        Flatten nested ticket data for export.
        
        Args:
            ticket_data: Nested ticket dictionary
            
        Returns:
            Flattened dictionary
        """
        flat = {}
        
        # Flatten top-level metadata
        if 'ticket_metadata' in ticket_data:
            meta = ticket_data['ticket_metadata']
            for key, value in meta.items():
                flat[f'metadata_{key}'] = value
        
        # Flatten sections
        if 'extracted_sections' in ticket_data:
            sections = ticket_data['extracted_sections']
            for section_name, content in sections.items():
                flat[f'section_{section_name.lower().replace(" ", "_")}'] = content
        
        return flat
    
    @staticmethod
    def format_markdown_report(tickets_data: List[Dict]) -> str:
        """
        Format tickets data as markdown report.
        
        Args:
            tickets_data: List of ticket dictionaries
            
        Returns:
            Markdown formatted report
        """
        lines = [
            "# Jira Tickets Report\n",
            f"Generated: {Path.cwd()}\n",
            f"Total tickets: {len(tickets_data)}\n\n",
            "---\n"
        ]
        
        for i, ticket in enumerate(tickets_data, 1):
            if 'ticket_metadata' in ticket:
                meta = ticket['ticket_metadata']
                lines.append(f"## {i}. {meta['key']}: {meta['summary']}\n")
                lines.append(f"- **Type**: {meta['type']}\n")
                lines.append(f"- **Status**: {meta['status']}\n")
                lines.append(f"- **Priority**: {meta['priority']}\n")
                lines.append(f"- **Created**: {meta['created']}\n\n")
                
                if 'extracted_sections' in ticket:
                    sections = ticket['extracted_sections']
                    for section_name, content in sections.items():
                        lines.append(f"### {section_name}\n")
                        lines.append(f"{content}\n\n")
                
                lines.append("---\n")
        
        return ''.join(lines)


class CredentialsManager:
    """Manage Jira credentials securely."""
    
    @staticmethod
    def load_credentials_from_file(filepath: str) -> Optional[Dict[str, str]]:
        """
        Load credentials from JSON file.
        
        Args:
            filepath: Path to credentials file
            
        Returns:
            Credentials dictionary or None
        """
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            return None
    
    @staticmethod
    def save_credentials_to_file(credentials: Dict[str, str], filepath: str) -> bool:
        """
        Save credentials to JSON file.
        WARNING: Do not commit credentials files to version control.
        
        Args:
            credentials: Credentials dictionary
            filepath: Path to save credentials
            
        Returns:
            True if successful
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(credentials, f, indent=2)
            # Set restrictive permissions on Windows
            Path(filepath).chmod(0o600)
            return True
        except Exception as e:
            print(f"Error saving credentials: {e}")
            return False


class JiraFilter:
    """Filter and query Jira data."""
    
    @staticmethod
    def filter_by_status(tickets: List[Dict], status: str) -> List[Dict]:
        """Filter tickets by status."""
        return [
            t for t in tickets
            if t.get('ticket_metadata', {}).get('status') == status
        ]
    
    @staticmethod
    def filter_by_type(tickets: List[Dict], issue_type: str) -> List[Dict]:
        """Filter tickets by type."""
        return [
            t for t in tickets
            if t.get('ticket_metadata', {}).get('type') == issue_type
        ]
    
    @staticmethod
    def filter_by_contains(tickets: List[Dict], keyword: str) -> List[Dict]:
        """Filter tickets containing keyword in summary or description."""
        results = []
        keyword_lower = keyword.lower()
        
        for ticket in tickets:
            meta = ticket.get('ticket_metadata', {})
            desc = ticket.get('full_description', '')
            
            if (keyword_lower in meta.get('summary', '').lower() or
                keyword_lower in desc.lower()):
                results.append(ticket)
        
        return results
    
    @staticmethod
    def get_tickets_with_missing_sections(tickets: List[Dict]) -> List[Dict]:
        """Get tickets missing Details or Test Details sections."""
        results = []
        
        for ticket in tickets:
            sections = ticket.get('extracted_sections', {})
            if 'Details' not in sections or 'Test Details' not in sections:
                results.append(ticket)
        
        return results


def validate_jira_url(url: str) -> bool:
    """Validate Jira URL format."""
    pattern = r'^https?://[a-zA-Z0-9\-._~:/?#\[\]@!$&\'()*+,;=]+'
    return bool(re.match(pattern, url))


def estimate_tokens_for_prompt(text: str) -> int:
    """
    Rough estimate of tokens in text (OpenAI GPT-style).
    
    Args:
        text: Input text
        
    Returns:
        Estimated token count
    """
    # Rough approximation: 1 token ≈ 4 characters
    return len(text) // 4
