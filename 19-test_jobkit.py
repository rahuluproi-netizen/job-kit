import csv
import json
import tempfile
import unittest
from pathlib import Path
from jobkit import draft, load_profile, track, safe_cell

class JobKitTests(unittest.TestCase):
    def test_draft_uses_only_supplied_claims(self):
        text=draft({'name':'Asha','summary':'I build web tools.','skills':'Python'},'Example Co','Developer')
        self.assertIn('Developer role at Example Co',text)
        self.assertIn('I build web tools.',text)
        self.assertNotIn('years',text)
    def test_blank_role_rejected(self):
        with self.assertRaises(ValueError): draft({},'Co',' ')
    def test_invalid_profile(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'p.json';p.write_text('{"name":"X"}')
            with self.assertRaises(ValueError): load_profile(p)
    def test_valid_profile(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'p.json';p.write_text(json.dumps({'name':'X','summary':'Y','skills':'Z'}))
            self.assertEqual(load_profile(p)['name'],'X')
    def test_track_appends_one_header(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'jobs.csv'
            track(p,'Company, Inc','Developer');track(p,'Other','Designer',status='applied')
            with p.open() as f: rows=list(csv.DictReader(f))
            self.assertEqual(len(rows),2);self.assertEqual(rows[0]['company'],'Company, Inc')
    def test_bad_header_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'jobs.csv';p.write_text('wrong,header\n')
            with self.assertRaises(ValueError):track(p,'Co','Role')
            self.assertEqual(p.read_text(),'wrong,header\n')
    def test_bad_status(self):
        with self.assertRaises(ValueError):track('/does/not/write','Co','Role',status='unknown')
    def test_formula_safe(self):
        self.assertEqual(safe_cell('=1+2'),"'=1+2")
        self.assertEqual(safe_cell('  @SUM(A1)'),"'  @SUM(A1)")
        self.assertEqual(safe_cell('Normal'),'Normal')

if __name__=='__main__':unittest.main()
