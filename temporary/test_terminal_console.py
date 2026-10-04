import sys
import os
sys.path.insert(0, os.path.abspath("."))

from src.cli.terminal_ui import ForensicConsole

print("[*] Initializing ForensicConsole...")
console = ForensicConsole()

print("\n--- Testing 'summary' ---")
console.onecmd("summary")

print("\n--- Testing 'alerts CRITICAL' ---")
console.onecmd("alerts CRITICAL")

print("\n--- Testing 'inspect 1' ---")
console.onecmd("inspect 1")

print("\n--- Testing 'graph 1' ---")
console.onecmd("graph 1")

print("\n--- Testing 'taint 1' ---")
console.onecmd("taint 1")

print("\n--- Testing 'syndicates' ---")
console.onecmd("syndicates")

print("\n--- Testing 'tag 1 SEIZURE \"Test terminal seizure note\"' ---")
console.onecmd("tag 1 SEIZURE \"Test terminal seizure note\"")

print("\n--- Testing 'notes' ---")
console.onecmd("notes")

print("\n--- Testing 'scenario peeling_chain' ---")
console.onecmd("scenario peeling_chain")

print("\n[✔] All Terminal Forensic Console commands executed successfully!")
