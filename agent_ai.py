#!/usr/bin/env python3
"""
Jira Agent - Interactive ticket replication.
Fetches a ticket, shows the data, asks for confirmation, then creates a copy.
"""

import os
import sys
from dotenv import load_dotenv

try:
    from jira import JIRA
    from jira.exceptions import JIRAError
except ImportError:
    print("ERROR: jira library not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

load_dotenv()


# ── Jira connection ────────────────────────────────────────────────────────────

def connect_jira() -> JIRA:
    url = os.getenv("JIRA_URL")
    pat = os.getenv("JIRA_PAT")
    username = os.getenv("JIRA_USERNAME")
    token = os.getenv("JIRA_API_TOKEN")

    if not url:
        print("ERROR: JIRA_URL not set in .env")
        sys.exit(1)

    if pat:
        return JIRA(server=url, token_auth=pat)
    elif username and token:
        return JIRA(server=url, basic_auth=(username, token))
    else:
        print("ERROR: No Jira credentials found in .env (JIRA_PAT or JIRA_USERNAME+JIRA_API_TOKEN)")
        sys.exit(1)


# ── Jira operations ────────────────────────────────────────────────────────────

def fetch_ticket(jira: JIRA, ticket_key: str) -> dict | None:
    try:
        issue = jira.issue(ticket_key.strip().upper())
        return {
            "key": issue.key,
            "project": issue.fields.project.key,
            "summary": issue.fields.summary,
            "type": issue.fields.issuetype.name,
            "status": issue.fields.status.name,
            "priority": issue.fields.priority.name if issue.fields.priority else "None",
            "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
            "reporter": issue.fields.reporter.displayName if issue.fields.reporter else "Unknown",
            "labels": list(issue.fields.labels) if issue.fields.labels else [],
            "description": issue.fields.description or "",
        }
    except JIRAError as e:
        print(f"\n  ERROR: {e.text if hasattr(e, 'text') else str(e)}")
        return None
    except Exception as e:
        print(f"\n  ERROR: {e}")
        return None


def create_ticket(jira: JIRA, ticket: dict, target_project: str) -> str | None:
    try:
        fields = {
            "project": {"key": target_project.strip().upper()},
            "summary": ticket["summary"],
            "issuetype": {"name": ticket["type"]},
        }
        if ticket["description"]:
            fields["description"] = ticket["description"]

        new_issue = jira.create_issue(fields=fields)
        return new_issue.key
    except JIRAError as e:
        print(f"\n  ERROR: {e.text if hasattr(e, 'text') else str(e)}")
        return None
    except Exception as e:
        print(f"\n  ERROR: {e}")
        return None


# ── Display ────────────────────────────────────────────────────────────────────

def display_ticket(ticket: dict):
    desc = ticket["description"]
    if len(desc) > 300:
        desc = desc[:300] + "..."

    print()
    print("  ┌─ Ticket Data " + "─" * 44)
    print(f"  │  Key        : {ticket['key']}")
    print(f"  │  Project    : {ticket['project']}")
    print(f"  │  Summary    : {ticket['summary']}")
    print(f"  │  Type       : {ticket['type']}")
    print(f"  │  Status     : {ticket['status']}")
    print(f"  │  Priority   : {ticket['priority']}")
    print(f"  │  Assignee   : {ticket['assignee']}")
    print(f"  │  Reporter   : {ticket['reporter']}")
    print(f"  │  Labels     : {', '.join(ticket['labels']) if ticket['labels'] else 'None'}")
    if desc:
        print(f"  │  Description: {desc}")
    print("  └" + "─" * 57)


# ── Main loop ──────────────────────────────────────────────────────────────────

def run():
    print()
    print("=" * 60)
    print("  JIRA TICKET REPLICATION AGENT")
    print("=" * 60)

    print("\nConnecting to Jira...", end="", flush=True)
    try:
        jira = connect_jira()
        print(" OK\n")
    except SystemExit:
        raise
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)

    while True:
        # Step 1: source ticket
        try:
            ticket_key = input("Source ticket key (or 'exit' to quit): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye!")
            break

        if ticket_key.lower() in ("exit", "quit", "bye"):
            print("\nGoodbye!")
            break

        if not ticket_key:
            continue

        # Step 2: fetch and display
        print(f"\n  Fetching {ticket_key.upper()}...", end="", flush=True)
        ticket = fetch_ticket(jira, ticket_key)
        if not ticket:
            print("  Try again.\n")
            continue
        print(" OK")
        display_ticket(ticket)

        # Step 3: target project
        try:
            target = input("\nTarget project key: ").strip().upper()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye!")
            break

        if not target:
            print("  No project entered. Skipping.\n")
            continue

        # Step 4: confirm
        try:
            confirm = input(f"\nCreate ticket '{ticket['summary']}' in {target}? (yes / no): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye!")
            break

        if confirm not in ("yes", "y"):
            print("\n  Cancelled. No ticket was created.\n")
        else:
            # Step 5: create
            print(f"\n  Creating ticket in {target}...", end="", flush=True)
            new_key = create_ticket(jira, ticket, target)
            if new_key:
                print(" OK")
                print(f"\n  Ticket {ticket['key']} in {ticket['project']} has been created as {new_key} in {target}.\n")
            else:
                print("  Failed. See error above.\n")

        # Step 6: another?
        try:
            again = input("Do you want to replicate another ticket? (yes / no): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye!")
            break

        if again not in ("yes", "y"):
            print("\nGoodbye!")
            break

        print()


def main():
    run()


if __name__ == "__main__":
    main()
