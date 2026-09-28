"""Behavior examples and bounded order exploration; no runtime conformance claim."""
import itertools
import unittest

from model.authority import AuthorityModel, Rejected


def setup():
    m = AuthorityModel()
    for actor in ('founder', 'reviewer', 'executor', 'delegate', 'successor'):
        m.enroll(actor)
    for scope in ('guide', 'code'):
        m.bootstrap_scope(scope, 'founder')
        m.set_rights('reviewer', scope, {'review'})
        m.set_rights('executor', scope, {'publish'})
    return m


def ready(m, decision='d', caller='founder', grant=None):
    m.approve(decision, caller, 'reviewer', 'guide', grant=grant)
    return m.claim('executor', 'guide')


def publish(m, lease, decision='d'):
    m.publish(decision, 'executor', lease.generation, lease.term)


class AuthorityTests(unittest.TestCase):
    def rejected(self, code, fn, *args, **kwargs):
        with self.assertRaisesRegex(Rejected, '^' + code + '$'):
            fn(*args, **kwargs)

    def test_guest_and_unrelated_membership_preserve_approval(self):
        for member in (False, True):
            with self.subTest(member=member):
                m = setup()
                lease = ready(m)
                old_roster = m.roster_revision
                m.enroll('newcomer')
                if member:
                    m.set_rights('newcomer', 'guide', {'review'})
                self.assertGreater(m.roster_revision, old_roster)
                publish(m, lease)
                self.assertEqual(m.heads['guide'], 1)

    def test_same_reviewer_changed_in_other_scope_preserves_approval(self):
        m = setup()
        lease = ready(m)
        m.set_rights('reviewer', 'code', ())
        publish(m, lease)
        self.assertEqual(m.heads['guide'], 1)

    def test_relevant_revocation_and_restore_do_not_resurrect_approval(self):
        for actor, rights in [('reviewer', {'review'}), ('founder', AuthorityModel.ACTIONS)]:
            with self.subTest(actor=actor):
                m = setup()
                lease = ready(m)
                m.set_rights(actor, 'guide', ())
                m.set_rights(actor, 'guide', rights)
                self.rejected('STALE_AUTHORITY', publish, m, lease)
                self.assertEqual((m.heads['guide'], m.events), (0, []))

    def test_all_six_guest_revoke_publish_orders(self):
        for order in itertools.permutations(('guest', 'revoke', 'publish')):
            with self.subTest(order=order):
                m = setup()
                lease = ready(m)
                published_first = order.index('publish') < order.index('revoke')
                for op in order:
                    if op == 'guest':
                        m.enroll('newcomer')
                    elif op == 'revoke':
                        m.set_rights('reviewer', 'guide', ())
                    elif published_first:
                        publish(m, lease)
                    else:
                        self.rejected('STALE_AUTHORITY', publish, m, lease)
                self.assertEqual(m.heads['guide'], int(published_first))
                self.assertEqual(len(m.events), int(published_first))

    def test_goal_and_policy_change_fence_decisions(self):
        for change in ('change_goal', 'change_policy'):
            with self.subTest(change=change):
                m = setup()
                lease = ready(m)
                getattr(m, change)()
                self.rejected('STALE_CONTROL', publish, m, lease)
                self.assertEqual(m.heads['guide'], 0)

    def test_recognition_is_directed_contextual_and_not_authority(self):
        m = setup()
        m.recognize('founder', 'delegate', 'editing', 'record:a')
        m.recognize('delegate', 'successor', 'editing', 'record:b')
        self.assertTrue(m.recognizes('founder', 'delegate', 'editing'))
        self.assertFalse(m.recognizes('delegate', 'founder', 'editing'))
        self.assertFalse(m.recognizes('founder', 'delegate', 'deployment'))
        self.assertFalse(m.recognizes('founder', 'successor', 'editing'))
        self.rejected('APPROVAL_AUTHORITY', m.approve,
                      'd', 'delegate', 'reviewer', 'guide')

    def test_approval_requires_distinct_authorized_reviewer(self):
        m = setup()
        self.rejected('INDEPENDENT_REVIEW', m.approve,
                      'd', 'founder', 'founder', 'guide')
        self.rejected('REVIEW_AUTHORITY', m.approve,
                      'd', 'founder', 'delegate', 'guide')
        self.assertEqual(m.decisions, {})

    def test_same_base_two_decisions_only_one_publishes(self):
        m = setup()
        lease = ready(m)
        m.approve('d2', 'founder', 'reviewer', 'guide')
        publish(m, lease)
        second = m.claim('executor', 'guide')
        self.rejected('BASE_CONFLICT', publish, m, second, 'd2')
        self.rejected('CONSUMED', publish, m, second)
        self.assertEqual((m.heads['guide'], len(m.events)), (1, 1))

    def root_grant(self, m, **kwargs):
        m.delegate('g', 'founder', 'delegate', 'guide', {'approve'},
                   expires=10, **kwargs)

    def test_default_grant_cannot_redelegate(self):
        m = setup()
        self.root_grant(m)
        self.rejected('NO_REDELEGATION', m.delegate, 'child', 'delegate',
                      'successor', 'guide', {'approve'}, expires=9, parent='g')
        lease = ready(m, caller='delegate', grant='g')
        publish(m, lease)
        self.assertEqual(m.heads['guide'], 1)

    def test_explicit_child_grant_and_attenuation(self):
        for scope, actions, expires in [('code', {'approve'}, 9),
                                        ('guide', {'approve', 'publish'}, 9),
                                        ('guide', {'approve'}, 11)]:
            with self.subTest(scope=scope, actions=actions, expires=expires):
                m = setup()
                self.root_grant(m, may_delegate=True)
                self.rejected('AMPLIFICATION', m.delegate, 'child', 'delegate',
                              'successor', scope, actions, expires=expires, parent='g')
                self.assertNotIn('child', m.grants)
        m = setup()
        self.root_grant(m, may_delegate=True)
        m.delegate('child', 'delegate', 'successor', 'guide', {'approve'},
                   expires=9, parent='g')
        lease = ready(m, caller='successor', grant='child')
        publish(m, lease)
        self.assertEqual(m.heads['guide'], 1)

    def test_ancestor_revocation_or_authority_change_fences_child(self):
        for op in ('revoke', 'rights', 'goal', 'policy', 'expire'):
            with self.subTest(op=op):
                m = setup()
                self.root_grant(m, may_delegate=True)
                m.delegate('child', 'delegate', 'successor', 'guide', {'approve'},
                           expires=9, parent='g')
                lease = ready(m, caller='successor', grant='child')
                if op == 'revoke':
                    m.revoke('g', 'founder')
                elif op == 'rights':
                    m.set_rights('founder', 'guide', ())
                elif op == 'goal':
                    m.change_goal()
                elif op == 'policy':
                    m.change_policy()
                else:
                    m.advance(9)
                self.assertFalse(m.live_grant('child'))
                with self.assertRaises(Rejected):
                    publish(m, lease)
                self.assertEqual(m.heads['guide'], 0)

    def test_grant_subject_scope_action_and_revoker_checked(self):
        m = setup()
        self.root_grant(m)
        for actor, scope in [('successor', 'guide'), ('delegate', 'code')]:
            self.rejected('GRANT_SCOPE', m.approve, 'd', actor, 'reviewer', scope, grant='g')
        self.rejected('FORBIDDEN', m.revoke, 'g', 'executor')
        m.delegate('r', 'founder', 'delegate', 'guide', {'review'}, expires=10)
        self.rejected('GRANT_SCOPE', m.approve,
                      'd', 'delegate', 'reviewer', 'guide', grant='r')

    def test_chain_limit_is_eight_and_old_id_cannot_be_rebound(self):
        m = setup()
        m.delegate('g0', 'founder', 'delegate', 'guide', {'approve'},
                   expires=10, may_delegate=True)
        for i in range(1, 8):
            m.delegate(f'g{i}', 'delegate', 'delegate', 'guide', {'approve'},
                       expires=10, may_delegate=True, parent=f'g{i-1}')
        self.assertTrue(m.live_grant('g7'))
        self.rejected('CHAIN_LIMIT', m.delegate, 'g8', 'delegate', 'delegate',
                      'guide', {'approve'}, expires=10, parent='g7')
        self.rejected('ID_EXISTS', m.delegate, 'g0', 'founder', 'successor',
                      'guide', {'approve'}, expires=10)

    def test_unexpired_lease_is_exclusive(self):
        m = setup()
        m.claim('executor', 'guide')
        self.rejected('BUSY', m.claim, 'founder', 'guide')

    def test_expiry_boundary_reclaim_and_late_writer(self):
        m = setup()
        old = ready(m)
        m.advance(old.deadline)
        self.rejected('STALE_LEASE', publish, m, old)
        fresh = m.claim('executor', 'guide')
        self.assertGreater(fresh.generation, old.generation)
        self.rejected('STALE_LEASE', publish, m, old)
        publish(m, fresh)
        self.assertEqual(m.heads['guide'], 1)

    def test_renewal_before_boundary_but_not_after(self):
        m = setup()
        old = ready(m)
        m.advance(4)
        renewed = m.renew('executor', 'guide', old.generation, old.term)
        self.assertEqual(renewed.deadline, 9)
        m.advance(5)
        self.rejected('BUSY', m.claim, 'founder', 'guide')
        m.advance(9)
        self.rejected('STALE_LEASE', m.renew, 'executor', 'guide', old.generation, old.term)
        m.claim('founder', 'guide')
        self.rejected('STALE_LEASE', m.renew, 'executor', 'guide', old.generation, old.term)

    def test_restart_and_executor_revocation_fence_old_leases(self):
        for op in ('restart', 'revoke_restore'):
            with self.subTest(op=op):
                m = setup()
                old = ready(m)
                if op == 'restart':
                    m.restart()
                else:
                    m.set_rights('executor', 'guide', ())
                    m.set_rights('executor', 'guide', {'publish'})
                fresh = m.claim('executor', 'guide')
                self.rejected('STALE_LEASE', publish, m, old)
                publish(m, fresh)
                self.assertEqual(m.heads['guide'], 1)

    def test_registry_clock_and_duration_bounds(self):
        m = setup()
        m.advance(2)
        self.rejected('CLOCK_BACKWARD', m.advance, 1)
        for invalid in (-1, 0, 11, True):
            self.rejected('DURATION', m.claim, 'executor', 'guide', duration=invalid)
        self.assertEqual(m.leases, {})

    def arm(self, m):
        m.plan_succession('s', 'founder', 'successor', 'guide', timeout=5)
        m.accept_succession('s', 'successor')

    def test_succession_requires_prior_plan_and_successor_acceptance(self):
        m = setup()
        self.rejected('UNKNOWN', m.activate_succession, 'absent')
        m.plan_succession('s', 'founder', 'successor', 'guide', timeout=5)
        m.advance(5)
        self.rejected('SUCCESSION_INELIGIBLE', m.activate_succession, 's')
        self.rejected('SUCCESSION_ACCEPTANCE', m.accept_succession, 's', 'successor')
        self.assertEqual(m.owners['guide'], 'founder')

    def test_succession_is_scoped_one_shot_and_creates_no_decision(self):
        m = setup()
        self.root_grant(m)
        self.arm(m)
        self.rejected('NOT_DUE', m.activate_succession, 's')
        m.advance(5)
        m.activate_succession('s')
        self.assertEqual(m.owners, {'guide': 'successor', 'code': 'founder'})
        self.assertFalse(m.direct('founder', 'guide', 'approve'))
        self.assertTrue(m.direct('successor', 'guide', 'approve'))
        self.assertFalse(m.live_grant('g'))
        self.assertEqual((m.decisions, m.heads['guide']), ({}, 0))
        self.rejected('SUCCESSION_INELIGIBLE', m.activate_succession, 's')
        self.assertEqual(m.events, [('succession', 's', 'successor', 'guide')])

    def test_heartbeat_extends_before_deadline_and_cannot_resurrect(self):
        m = setup()
        self.arm(m)
        m.advance(4)
        m.heartbeat('s', 'founder')
        m.advance(5)
        self.rejected('NOT_DUE', m.activate_succession, 's')
        m.advance(9)
        self.rejected('STALE_GOVERNANCE', m.heartbeat, 's', 'founder')
        m.activate_succession('s')

    def test_stale_rules_need_cancel_and_new_acceptance(self):
        for op in ('goal', 'policy', 'restart', 'owner', 'successor'):
            with self.subTest(op=op):
                m = setup()
                self.arm(m)
                if op in ('owner', 'successor'):
                    actor = 'founder' if op == 'owner' else 'successor'
                    m.set_rights(actor, 'guide', m.rights.get((actor, 'guide'), ()))
                else:
                    getattr(m, {'goal': 'change_goal', 'policy': 'change_policy',
                                'restart': 'restart'}[op])()
                self.rejected('SUCCESSION_ACCEPTANCE', m.accept_succession, 's', 'successor')
                m.advance(5)
                self.rejected('SUCCESSION_INELIGIBLE', m.activate_succession, 's')
                m.cancel_succession('s', 'founder')
                m.plan_succession('s2', 'founder', 'successor', 'guide', timeout=5)
                m.advance(10)
                self.rejected('SUCCESSION_INELIGIBLE', m.activate_succession, 's2')

    def test_restart_rule_can_be_rearmed_with_fresh_acceptance(self):
        m = setup()
        self.arm(m)
        m.restart()
        m.cancel_succession('s', 'founder')
        m.plan_succession('s2', 'founder', 'successor', 'guide', timeout=5)
        m.accept_succession('s2', 'successor')
        m.advance(5)
        m.activate_succession('s2')
        self.assertEqual(m.owners['guide'], 'successor')

    def test_cancelled_succession_stays_cancelled(self):
        m = setup()
        self.arm(m)
        self.rejected('SUCCESSION_AUTHORITY', m.cancel_succession, 's', 'delegate')
        m.cancel_succession('s', 'founder')
        self.rejected('SUCCESSION_ACCEPTANCE', m.accept_succession, 's', 'successor')
        self.rejected('STALE_GOVERNANCE', m.heartbeat, 's', 'founder')
        m.advance(5)
        self.rejected('SUCCESSION_INELIGIBLE', m.activate_succession, 's')


if __name__ == '__main__':
    unittest.main()
