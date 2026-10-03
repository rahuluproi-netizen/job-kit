"""Local application drafts and tracker. Python standard library only."""
import argparse
import csv
import json
from datetime import date
from pathlib import Path

FIELDS = ['company', 'role', 'url', 'status', 'date']
STATUSES = ['planned', 'applied', 'interview', 'rejected', 'offer']

def load_profile(path):
    profile = json.loads(Path(path).read_text(encoding='utf-8'))
    for key in ['name', 'summary', 'skills']:
        if not isinstance(profile.get(key), str) or not profile[key].strip():
            raise ValueError(f'Profile needs a non-empty string: {key}')
    return profile

def draft(profile, company, role):
    if not company.strip() or not role.strip():
        raise ValueError('Company and role cannot be blank.')
    return (f"Dear hiring team,\n\nI am applying for the {role.strip()} role at "
            f"{company.strip()}.\n\n{profile['summary'].strip()}\n\n"
            f"My skills include {profile['skills'].strip()}. "
            "I would welcome the chance to discuss how these fit your team's needs.\n\n"
            f"Thank you for considering my application.\n\n{profile['name'].strip()}\n")

def safe_cell(value):
    # Prevent spreadsheet formula injection if CSV is opened in Excel/Sheets.
    text = str(value)
    return "'" + text if text.lstrip().startswith(('=', '+', '-', '@', '\t', '\r', '\n')) else text

def track(path, company, role, url='', status='planned'):
    if status not in STATUSES or not company.strip() or not role.strip():
        raise ValueError('Use a company, role and valid status.')
    path = Path(path)
    exists = path.exists() and path.stat().st_size > 0
    if exists:
        with path.open(newline='', encoding='utf-8') as file:
            if next(csv.reader(file), None) != FIELDS:
                raise ValueError('Tracker has an unexpected CSV header; no changes made.')
    with path.open('a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow(dict(zip(FIELDS, map(safe_cell, [company.strip(), role.strip(), url, status, date.today().isoformat()]))))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    letters = commands.add_parser('draft', help='Print an editable cover-letter draft; never send it.')
    letters.add_argument('--profile', required=True)
    letters.add_argument('--company', required=True)
    letters.add_argument('--role', required=True)
    logs = commands.add_parser('track', help='Append one row to your local CSV tracker.')
    logs.add_argument('--file', default='applications.csv')
    logs.add_argument('--company', required=True)
    logs.add_argument('--role', required=True)
    logs.add_argument('--url', default='')
    logs.add_argument('--status', choices=STATUSES, default='planned')
    args = parser.parse_args()
    try:
        if args.command == 'draft':
            print(draft(load_profile(args.profile), args.company, args.role))
        else:
            track(args.file, args.company, args.role, args.url, args.status)
            print(f'Added one row to {args.file}. No application was sent.')
    except (ValueError, OSError) as error:
        parser.exit(2, f'Error: {error}\n')

if __name__ == '__main__':
    main()
