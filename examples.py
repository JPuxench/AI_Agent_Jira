#!/usr/bin/env python3
"""
Example usage and test scenarios for Jira extraction agents.
"""

import json
from datetime import datetime
from typing import Dict, List, Any


def example_extracted_data() -> Dict[str, Any]:
    """
    Example of extracted Jira ticket data structure.
    
    Returns:
        Sample ticket data
    """
    return {
        "key": "TEST-1",
        "summary": "Implement user authentication",
        "type": "Task",
        "status": "In Progress",
        "priority": "High",
        "created": "2024-01-15T10:30:00+00:00",
        "updated": "2024-03-04T14:20:00+00:00",
        "description": """
        # User Authentication Feature
        
        ## Details
        We need to implement a secure authentication system for our application.
        This includes user registration, login, and password reset functionality.
        
        ## Description
        The authentication module should follow OAuth 2.0 standards and use JWT tokens
        for session management. The system should support email and social login options.
        
        ## Test Details
        - Unit tests for password hashing
        - Integration tests for login flow
        - E2E tests for user registration
        - Security tests for token validation
        """,
        "labels": ["authentication", "high-priority"],
        "assignee": "John Doe",
        "reporter": "Jane Smith",
        "details": "We need to implement a secure authentication system for our application.",
        "test_details": "Unit tests, integration tests, and E2E tests"
    }


def example_advanced_data() -> Dict[str, Any]:
    """
    Example of advanced extracted data with sections.
    
    Returns:
        Sample advanced ticket data
    """
    return {
        "ticket_metadata": {
            "key": "TEST-1",
            "id": "10000",
            "summary": "Bug in user login",
            "type": "Bug",
            "status": "Open",
            "priority": "Critical",
            "created": "2024-01-15T10:30:00+00:00",
            "updated": "2024-03-04T14:20:00+00:00",
        },
        "full_description": """
        Users are unable to log in with special characters in their passwords.
        
        ## Details
        The issue affects approximately 15% of our user base who have special
        characters in their passwords. This is blocking production access.
        
        ## Description
        When users attempt to log in with passwords containing symbols like
        @, #, $, %, the authentication fails with a generic "Invalid credentials" error.
        
        ## Steps to Reproduce
        1. Create account with password containing special characters
        2. Log out
        3. Attempt to log in
        
        ## Expected Result
        User should be able to log in successfully
        
        ## Actual Result
        Login fails with error message
        
        ## Environment
        Production. Affects all browsers. Multiple client versions.
        
        ## Test Details
        - Test with various special characters
        - Test with different password lengths
        - Verify token generation
        - Test session management
        """,
        "extracted_sections": {
            "Details": "The issue affects approximately 15% of our user base who have special characters in their passwords. This is blocking production access.",
            "Description": "When users attempt to log in with passwords containing symbols like @, #, $, %, the authentication fails with a generic \"Invalid credentials\" error.",
            "Steps": "1. Create account with password containing special characters\n2. Log out\n3. Attempt to log in",
            "Expected": "User should be able to log in successfully",
            "Actual": "Login fails with error message",
            "Environment": "Production. Affects all browsers. Multiple client versions.",
            "Test Details": "Test with various special characters, Test with different password lengths, Verify token generation, Test session management"
        },
        "xray_fields": {},
        "custom_metadata": {
            "labels": ["authentication", "bug", "production"],
            "assignee": "John Doe",
            "reporter": "Jane Smith",
            "components": ["Backend", "Auth Service"]
        }
    }


def print_example_basic():
    """Print example of basic extraction."""
    print("\n" + "="*70)
    print("EXAMPLE: Basic Extraction Output")
    print("="*70)
    
    example = example_extracted_data()
    print(json.dumps(example, indent=2))


def print_example_advanced():
    """Print example of advanced extraction."""
    print("\n" + "="*70)
    print("EXAMPLE: Advanced Extraction Output")
    print("="*70)
    
    example = example_advanced_data()
    print(json.dumps(example, indent=2))


def print_workflow_example():
    """Print example workflow."""
    print("\n" + "="*70)
    print("EXAMPLE WORKFLOW")
    print("="*70)
    
    steps = [
        ("1. Run Basic Agent", "python jira_agent.py"),
        ("2. Enter Jira URL", "https://jira.company.com"),
        ("3. Enter Credentials", "username and API token"),
        ("4. Select Project", "TEST (or leave blank for all)"),
        ("5. Set Limit", "50 tickets"),
        ("6. Review Output", "jira_tickets_YYYYMMDD_HHMMSS.json"),
        ("7. Run Advanced Agent", "python jira_agent_advanced.py"),
        ("8. Get Detailed Report", "Advanced extraction with CSV export"),
    ]
    
    for step, description in steps:
        print(f"\n{step}")
        print(f"   → {description}")


def usage_examples():
    """Print usage examples."""
    print("\n" + "="*70)
    print("QUICK START EXAMPLES")
    print("="*70)
    
    examples = {
        "Basic Usage": """
# Install dependencies
pip install -r requirements.txt

# Run basic agent
python jira_agent.py
""",
        "Advanced Usage": """
# Run advanced agent with comprehensive extraction
python jira_agent_advanced.py
""",
        "Using Utils": """
# Import and use utility functions
from utils import TextProcessor, JiraDataFormatter, JiraFilter

# Extract markdown sections
text = "## Details\\nSome content\\n## Description\\nMore content"
details = TextProcessor.extract_markdown_section(text, "Details")

# Format data as markdown report
report = JiraDataFormatter.format_markdown_report(tickets_data)

# Filter tickets
critical_bugs = JiraFilter.filter_by_type(tickets, "Bug")
open_tickets = JiraFilter.filter_by_status(tickets, "Open")
"""
    }
    
    for title, code in examples.items():
        print(f"\n{title}:")
        print(code)


def tips_and_best_practices():
    """Print tips and best practices."""
    print("\n" + "="*70)
    print("TIPS & BEST PRACTICES")
    print("="*70)
    
    tips = [
        "🔐 Use API tokens instead of passwords for authentication",
        "⚙️ Set reasonable limits (50-100 tickets) to avoid timeouts",
        "📁 Store credentials in .env file (never commit to version control)",
        "📊 Use advanced agent for comprehensive extraction and reports",
        "🔍 Filter results using utility functions for specific analysis",
        "💾 Export to both JSON and CSV for different use cases",
        "⚡ Check Jira permissions if tickets are not fetched",
        "🛠️ Customize section extraction for your ticket format",
    ]
    
    for i, tip in enumerate(tips, 1):
        print(f"\n{i}. {tip}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "basic":
            print_example_basic()
        elif command == "advanced":
            print_example_advanced()
        elif command == "workflow":
            print_workflow_example()
        elif command == "examples":
            usage_examples()
        elif command == "tips":
            tips_and_best_practices()
        else:
            print("Unknown command")
    else:
        # Print all examples
        print("\n" + "🤖 JIRA AGENT - EXAMPLES & USAGE GUIDE")
        print_example_basic()
        print_example_advanced()
        print_workflow_example()
        usage_examples()
        tips_and_best_practices()
        
        print("\n\n" + "="*70)
        print("Commands:")
        print("  python examples.py basic     - Show basic extraction example")
        print("  python examples.py advanced  - Show advanced extraction example")
        print("  python examples.py workflow  - Show example workflow")
        print("  python examples.py examples  - Show usage examples")
        print("  python examples.py tips      - Show tips and best practices")
        print("="*70)
