#!/usr/bin/env python3
"""
Test script for the File Integrity Monitoring Alert System
This allows you to test the alert functionality independently from the monitoring component
"""

import sys
import os
import argparse
from datetime import datetime

# Import the alert mechanism module
# Assuming the alert code is saved as fim_alert.py
try:
    from fim_alert import FIMAlertManager, handle_watchdog_event
except ImportError:
    print("Error: Could not import the FIM alert module.")
    print("Make sure fim_alert.py is in the same directory or in your PYTHONPATH.")
    sys.exit(1)

def main():
    """Main function to run the test"""
    parser = argparse.ArgumentParser(description="Test the FIM Alert System")
    parser.add_argument(
        "--event-type", 
        choices=["modified", "created", "deleted", "permission_changed", "ownership_changed", "moved"],
        default="modified",
        help="Type of file event to simulate"
    )
    parser.add_argument(
        "--file-path",
        default="/etc/passwd",
        help="Path of the file for the simulated event"
    )
    parser.add_argument(
        "--old-hash",
        default="e9c5bed524d19046bd99082a63b0b00356b9e587caaecd319cde21b630cbb348",
        help="Previous hash value for modified files"
    )
    parser.add_argument(
        "--new-hash",
        default="a72b4df5b53805a00c8bf26eb4227a3d4280420ad7dea3d8a4c059ca0a0e7c1c",
        help="New hash value for modified files"
    )
    parser.add_argument(
        "--details",
        action="store_true",
        help="Include additional details with the alert"
    )

    args = parser.parse_args()
    
    print(f"Testing FIM Alert System with {args.event_type} event on {args.file_path}")
    
    # Additional details for the alert
    details = None
    if args.details:
        details = {
            "Previous Hash": args.old_hash,
            "Current Hash": args.new_hash,
            "User": os.environ.get("USER", "unknown"),
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Process ID": os.getpid()
        }
    
    # Send test alert
    handle_watchdog_event(args.event_type, args.file_path, args.old_hash, args.new_hash)
    print("Test alert sent. Check your email and the log file.")

if __name__ == "__main__":
    main()