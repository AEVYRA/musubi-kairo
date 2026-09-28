"""Cross-slice behavior through the JSON dispatcher; time/auth remain fixtures."""
from copy import deepcopy
import itertools
import json
import unittest

from model.entry import EntryModel, PROFILE, Rejected
from model.authority import AuthorityModel


class GovernanceTests(unittest.TestCase):
    def setUp(self):
        self.n = EntryModel()
        self.sessions, self.actors = {}, {}
        self.op = 0
        for name in ('owner', 'successor', 'peer', 'outsider'):
            self.n.register_principal(name, persistent=True)
            s, identity = self.n.identify(name)
            self.sessions[name], self.actors[name] = s, identity['actor']
        r = self.send('owner', 'create_project', {
            'expected_admission_rev': '1', 'title': 'Three actors',
            'goal': {'objective': 'Share work', 'constraints': [],
                     'criteria': ['A successor can govern']}})
        self.pid = r['result']['project']
        self.p = self.n.projects[self.pid]
        self.a = self.p.authority
        for who in ('successor', 'peer'):
            self.admit('owner', who)

    def wire(self, action, body, op=None):
        self.op += 1
        return json.dumps({'profile': PROFILE, 'node': self.n.node,
                           'incarnation': self.n.incarnation,
                           'operation_id': op or f'op:{self.op}',
                           'action': action, 'payload': body}).encode()

    def send(self, who, action, body, op=None):
        return self.n.command(self.sessions[who], self.wire(action, body, op))

    def admit(self, caller, who):
        return self.send(caller, 'admit', {'project': self.pid,
            'expected_membership_rev': str(self.p.membership_rev),
            'subject': self.actors[who], 'actions': ['review']})

    def brief(self, who='owner'):
        return self.n.enter(self.sessions[who], self.pid)

    def plan_body(self, rid='rule', successor='successor'):
        return {'project': self.pid, 'scope': self.n.SCOPE, 'rule_id': rid,
                'successor': self.actors[successor], 'timeout': 5,
                'expected_control': self.brief()['governance_control']}

    def rule_body(self, rid='rule'):
        rule = next(r for r in self.brief('peer')['successions']
                    if r['record']['rule_id'] == rid)
        return {'project': self.pid, 'scope': self.n.SCOPE, 'rule_id': rid,
                'expected_rule': rule['fingerprint']}

    def arm(self):
        self.assertEqual(self.send('owner', 'plan_succession', self.plan_body())['status'], 'applied')
        self.assertEqual(self.send('successor', 'accept_succession', self.rule_body())['status'], 'applied')

    def test_three_actor_transfer_retains_membership_and_enables_new_owner(self):
        self.arm()
        members, revision = set(self.p.members), self.p.membership_rev
        self.a.advance(5)
        r = self.send('peer', 'activate_succession', self.rule_body())
        self.assertEqual(r['status'], 'applied')
        self.assertEqual(self.brief('successor')['owner'], self.actors['successor'])
        self.assertEqual(self.brief()['direct_actions'], [])
        self.assertEqual((self.p.members, self.p.membership_rev), (members, revision))
        self.assertEqual(self.admit('owner', 'outsider')['code'], 'FORBIDDEN')
        self.assertEqual(self.admit('successor', 'outsider')['status'], 'applied')
        self.assertEqual(r['result']['transfer']['not_transferred'], [])

    def test_nonmember_never_becomes_bound_successor(self):
        r = self.send('owner', 'plan_succession', self.plan_body(successor='outsider'))
        self.assertEqual(r['code'], 'SUBJECT_INELIGIBLE')
        self.assertEqual(self.a.successions, {})
        self.assertEqual(self.p.rule_revisions, {})
        self.a.enroll(self.actors['outsider'])  # Inner enrollment is insufficient.
        r = self.send('owner', 'plan_succession', self.plan_body(successor='outsider'))
        self.assertEqual(r['code'], 'SUBJECT_INELIGIBLE')

    def test_control_and_actor_guards_precede_effects(self):
        b = self.plan_body()
        b['expected_control']['owner_epoch'] = '99'
        self.assertEqual(self.send('owner', 'plan_succession', b)['code'], 'CONTROL_CONFLICT')
        self.assertEqual(self.send('peer', 'plan_succession', self.plan_body())['code'],
                         'SUCCESSION_AUTHORITY')
        self.assertEqual(self.a.successions, {})
        self.send('owner', 'plan_succession', self.plan_body())
        self.assertEqual(self.send('peer', 'accept_succession', self.rule_body())['code'],
                         'SUCCESSION_ACCEPTANCE')
        self.assertEqual(self.a.accepted_successions, set())

    def test_successor_credential_revocation_blocks_activation_but_not_cancel(self):
        self.arm()
        b = self.rule_body()
        self.n.revoke_credential('successor')
        self.a.advance(5)
        self.assertEqual(self.send('peer', 'activate_succession', b)['code'], 'SUBJECT_INELIGIBLE')
        self.assertEqual(self.a.owners[self.n.SCOPE], self.actors['owner'])
        self.assertEqual(self.send('owner', 'cancel_succession', b)['status'], 'applied')

    def test_membership_removed_by_environment_blocks_activation(self):
        self.arm()
        b = self.rule_body()
        self.p.members.remove(self.actors['successor'])  # No removal command yet.
        self.a.advance(5)
        self.assertEqual(self.send('peer', 'activate_succession', b)['code'], 'SUBJECT_INELIGIBLE')
        self.assertEqual(self.a.fired_successions, set())

    def test_revoked_absent_owner_does_not_prevent_transfer(self):
        self.arm()
        b = self.rule_body()
        self.n.revoke_credential('owner')
        self.a.advance(5)
        self.assertEqual(self.send('peer', 'activate_succession', b)['status'], 'applied')
        self.assertEqual(self.brief('successor')['owner'], self.actors['successor'])

    def test_heartbeat_replay_and_stale_new_operation_never_renew(self):
        self.arm()
        self.a.advance(2)
        b = self.rule_body()
        raw = self.wire('heartbeat', b, 'heartbeat-once')
        first = self.n.command(self.sessions['owner'], raw)
        self.assertEqual(self.a.successions['rule'].deadline, 7)
        self.a.advance(4)
        self.assertEqual(self.n.command(self.sessions['owner'], raw), first)
        self.assertEqual(self.a.successions['rule'].deadline, 7)
        self.assertEqual(self.send('owner', 'heartbeat', b)['code'], 'RULE_CONFLICT')
        changed = self.wire('heartbeat', self.rule_body(), 'heartbeat-once')
        with self.assertRaisesRegex(Rejected, '^OPERATION_ID_REUSED$'):
            self.n.command(self.sessions['owner'], changed)
        self.a.advance(7)
        self.send('peer', 'activate_succession', self.rule_body())
        self.assertEqual(self.n.command(self.sessions['owner'], raw), first)
        self.assertEqual(self.a.successions['rule'].deadline, 7)
        self.n.revoke_credential('owner')
        with self.assertRaisesRegex(Rejected, '^UNAUTHENTICATED$'):
            self.n.command(self.sessions['owner'], raw)

    def test_same_time_heartbeat_still_changes_snapshot(self):
        self.arm()
        b = self.rule_body()
        self.assertEqual(self.send('owner', 'heartbeat', b)['status'], 'applied')
        self.assertEqual(self.send('owner', 'heartbeat', b)['code'], 'RULE_CONFLICT')

    def test_both_heartbeat_activation_orders_through_one_dispatcher(self):
        for order in itertools.permutations(('heartbeat', 'activate_succession')):
            with self.subTest(order=order):
                self.setUp()
                self.arm()
                self.a.advance(5)
                b = self.rule_body()
                for i, action in enumerate(order):
                    who = 'owner' if action == 'heartbeat' else 'peer'
                    r = self.send(who, action, b)
                    self.assertEqual(r.get('code', r['status']), 'applied' if i == 0 else 'RULE_CONFLICT')
                expected = 'owner' if order[0] == 'heartbeat' else 'successor'
                self.assertEqual(self.a.owners[self.n.SCOPE], self.actors[expected])

    def test_rejected_activation_receipt_stays_rejected_and_success_replays_once(self):
        self.arm()
        b = self.rule_body()
        raw = self.wire('activate_succession', b)
        early = self.n.command(self.sessions['peer'], raw)
        self.assertEqual(early['code'], 'NOT_DUE')
        self.a.advance(5)
        self.assertEqual(self.n.command(self.sessions['peer'], raw), early)
        raw = self.wire('activate_succession', b)
        first = self.n.command(self.sessions['peer'], raw)
        events = deepcopy(self.a.events)
        self.assertEqual(self.n.command(self.sessions['peer'], raw), first)
        self.assertEqual(self.a.events, events)
        self.assertEqual(len(events), 1)

    def test_unrelated_admission_and_lobby_activity_do_not_heartbeat_or_stale_rule(self):
        self.arm()
        b = self.rule_body()
        self.a.advance(4)
        self.admit('owner', 'outsider')
        self.send('owner', 'speak', {'room': 'lobby', 'text': 'Present'})
        self.brief()
        self.assertEqual(self.rule_body(), b)
        self.assertEqual(self.a.successions['rule'].deadline, 5)
        self.a.advance(5)
        self.assertEqual(self.send('peer', 'activate_succession', b)['status'], 'applied')

    def test_rule_capacity_and_receipt_capacity_stop_before_effects(self):
        self.n.LIMITS = dict(self.n.LIMITS, receipts=64)
        for i in range(8):
            rid = f'rule:{i}'
            self.assertEqual(self.send('owner', 'plan_succession', self.plan_body(rid))['status'], 'applied')
            self.send('owner', 'cancel_succession', self.rule_body(rid))
        self.assertEqual(self.send('owner', 'plan_succession', self.plan_body('extra'))['code'], 'RULE_CAPACITY')
        self.assertEqual(len(self.brief()['successions']), 8)
        self.setUp()
        self.arm()
        self.a.advance(5)
        self.n.LIMITS = dict(self.n.LIMITS, receipts=len(self.n.receipts))
        with self.assertRaisesRegex(Rejected, '^RECEIPT_CAPACITY$'):
            self.send('peer', 'activate_succession', self.rule_body())
        self.assertEqual(self.a.fired_successions, set())

    def test_restore_and_uncertain_clock_block_new_governance(self):
        for mode in ('clock', 'restore'):
            with self.subTest(mode=mode):
                self.setUp()
                self.arm()
                b = self.rule_body()
                if mode == 'clock':
                    self.a.restart(clock_verified=False)
                else:
                    self.a.restore_boundary()
                    self.a.recover_clock(0)
                self.assertEqual(self.send('owner', 'heartbeat', b)['code'], 'CONTROL_UNAVAILABLE')

    def test_recovery_changes_snapshot_and_preserves_bound_consent(self):
        self.arm()
        b = self.rule_body()
        self.a.advance(4)
        self.a.restart(clock_verified=False)
        self.a.recover_clock(8)
        self.assertEqual(self.a.successions['rule'].deadline, 13)
        self.assertEqual(self.send('owner', 'heartbeat', b)['code'], 'RULE_CONFLICT')
        self.a.advance(13)
        self.assertEqual(self.send('peer', 'activate_succession', self.rule_body())['status'], 'applied')

    def test_unbound_rule_not_exposed_as_a_bound_command(self):
        self.a.plan_succession('internal', self.actors['owner'], self.actors['successor'],
                               self.n.SCOPE, timeout=5)
        b = {'project': self.pid, 'scope': self.n.SCOPE, 'rule_id': 'internal',
             'expected_rule': '0' * 64}
        self.assertEqual(self.send('successor', 'accept_succession', b)['code'], 'UNKNOWN_RULE')

    def test_foreign_project_scope_and_forged_actor_rejected(self):
        self.arm()
        b = self.rule_body()
        self.assertEqual(self.send('outsider', 'heartbeat', b)['code'], 'NOT_ACCESSIBLE')
        for change in ({'scope': 'artifact:other'}, {'actor': self.actors['owner']}):
            with self.subTest(change=change), self.assertRaisesRegex(Rejected, '^MALFORMED_COMMAND$'):
                self.send('peer', 'heartbeat', {**b, **change})

    def test_transfer_receipt_exposes_rights_not_transferred(self):
        self.a.set_rights(self.actors['owner'], self.n.SCOPE, {'approve', 'review'})
        self.arm()
        self.a.set_rights(self.actors['owner'], self.n.SCOPE, {'approve', 'review', 'publish'})
        self.a.advance(5)
        r = self.send('peer', 'activate_succession', self.rule_body())
        self.assertEqual(r['result']['transfer']['not_transferred'], ['publish'])
        self.assertEqual(r['result']['transfer']['transferred'], ['approve', 'review'])
        self.assertNotIn('publish', self.brief('successor')['direct_actions'])

    def test_plan_accept_cancel_replays_preserve_original_revision(self):
        commands = [('owner', 'plan_succession', self.plan_body())]
        for who, action, b in commands:
            raw = self.wire(action, b)
            first = self.n.command(self.sessions[who], raw)
            revision = dict(self.p.rule_revisions)
            self.assertEqual(self.n.command(self.sessions[who], raw), first)
            self.assertEqual(self.p.rule_revisions, revision)
            if action == 'plan_succession':
                commands.append(('successor', 'accept_succession', self.rule_body()))
            elif action == 'accept_succession':
                commands.append(('owner', 'cancel_succession', self.rule_body()))

    def test_demo_uses_all_governance_commands(self):
        from model.governance_demo import run
        trace = run()['trace']
        actions = {step['command']['action'] for step in trace if 'command' in step}
        self.assertTrue({'plan_succession', 'accept_succession', 'heartbeat',
                         'cancel_succession', 'activate_succession'} <= actions)

    def test_rule_fingerprint_is_project_bound(self):
        self.arm()
        first = self.rule_body()['expected_rule']
        created = self.send('owner', 'create_project', {
            'expected_admission_rev': '1', 'title': 'Second project',
            'goal': {'objective': 'Other work', 'constraints': [], 'criteria': ['Done']}})
        self.pid = created['result']['project']
        self.p = self.n.projects[self.pid]
        self.a = self.p.authority
        self.admit('owner', 'successor')
        self.admit('owner', 'peer')
        self.arm()
        b = self.rule_body()
        self.assertNotEqual(first, b['expected_rule'])
        self.assertEqual(self.send('owner', 'heartbeat', {**b, 'expected_rule': first})['code'],
                         'RULE_CONFLICT')

    def test_membership_alone_does_not_authorize_heartbeat_or_cancel(self):
        self.arm()
        for action, error in (('heartbeat', 'STALE_GOVERNANCE'),
                              ('cancel_succession', 'SUCCESSION_AUTHORITY')):
            with self.subTest(action=action):
                self.assertEqual(self.send('peer', action, self.rule_body())['code'], error)
        self.assertEqual(self.a.successions['rule'].deadline, 5)
        self.assertEqual(self.a.cancelled_successions, set())


class PreOutageTests(unittest.TestCase):
    def test_due_before_restart_or_outage_never_gets_grace(self):
        for start, recover in ((5, None), (9, None), (5, 12), (9, 12)):
            with self.subTest(start=start, recover=recover):
                a = AuthorityModel()
                a.enroll('owner'); a.enroll('successor')
                a.bootstrap_scope('doc', 'owner')
                a.plan_succession('r', 'owner', 'successor', 'doc', timeout=5)
                a.accept_succession('r', 'successor')
                a.advance(start)
                a.restart(clock_verified=recover is None)
                if recover is not None:
                    a.restart()
                    a.recover_clock(recover)
                self.assertEqual(a.successions['r'].deadline, 5)
                a.activate_succession('r')
                self.assertEqual(a.owners['doc'], 'successor')

    def test_unaccepted_window_still_expires_during_outage(self):
        a = AuthorityModel()
        a.enroll('owner'); a.enroll('successor')
        a.bootstrap_scope('doc', 'owner')
        a.plan_succession('r', 'owner', 'successor', 'doc', timeout=5)
        a.advance(4); a.restart(clock_verified=False); a.recover_clock(8)
        with self.assertRaisesRegex(Rejected, '^SUCCESSION_ACCEPTANCE$'):
            a.accept_succession('r', 'successor')
