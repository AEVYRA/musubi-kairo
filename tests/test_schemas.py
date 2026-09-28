"""Structural checks only; semantic authorization is checked separately."""
import copy
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


class SchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((ROOT / 'schemas/authority-record.schema.json').read_text())
        cls.examples = json.loads((ROOT / 'examples/authority-records.json').read_text())
        cls.validator = Draft202012Validator(cls.schema)

    def test_schema_itself_is_valid(self):
        Draft202012Validator.check_schema(self.schema)

    def test_all_examples_and_closed_required_fields(self):
        self.assertEqual({r['kind'] for r in self.examples},
                         {'recognition', 'delegation', 'succession'})
        for record in self.examples:
            with self.subTest(kind=record['kind']):
                self.validator.validate(record)
                extra = {**record, 'grant_me_admin': True}
                self.assertFalse(self.validator.is_valid(extra))
                for field in record:
                    incomplete = dict(record)
                    del incomplete[field]
                    self.assertFalse(self.validator.is_valid(incomplete), field)

    def test_malformed_or_unbounded_records_rejected(self):
        bad = []
        for key, value in [('goal_rev', 1), ('goal_rev', '01'),
                           ('goal_rev', '-1'), ('goal_rev', '1' * 21),
                           ('actions', []), ('actions', ['admin']),
                           ('actions', ['approve', 'approve']),
                           ('may_delegate', 'false'), ('id', 'x' * 129),
                           ('scope', {'project': 'p', 'resource': 'r', 'wildcard': True}),
                           ('dependencies', [])]:
            bad.append({**self.examples[1], key: value})
        bad.append({**self.examples[0], 'evidence': []})
        bad.append({**self.examples[0], 'audience': ['a'] * 17})
        bad.append({**self.examples[2], 'timeout_ticks': '0'})
        for record in bad:
            with self.subTest(record=record):
                self.assertFalse(self.validator.is_valid(record))

    def test_schema_does_not_claim_semantic_authentication(self):
        # A shape validator cannot know whether this issuer authorized anything.
        forged_claim = copy.deepcopy(self.examples[1])
        forged_claim['issuer'] = 'actor:unproven'
        self.validator.validate(forged_claim)


if __name__ == '__main__':
    unittest.main()
