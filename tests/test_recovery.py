"""Regression examples from peer review, plus bounded transition-order checks."""
import itertools
import unittest

from model.authority import AuthorityModel, Rejected


def base():
    m = AuthorityModel()
    for a in ('owner', 'successor', 'reviewer', 'executor', 'delegate', 'approver'):
        m.enroll(a)
    m.bootstrap_scope('doc', 'owner')
    m.set_rights('reviewer', 'doc', {'review'})
    m.set_rights('executor', 'doc', {'publish'})
    m.set_rights('successor', 'doc', {'review'})
    m.set_rights('approver', 'doc', {'approve'})
    return m


def arm(m):
    m.plan_succession('s', 'owner', 'successor', 'doc', timeout=5)
    m.accept_succession('s', 'successor')


def publish(m, decision='d'):
    lease = m.claim('executor', 'doc')
    m.publish(decision, 'executor', lease.generation, lease.term)


class RecoveryTests(unittest.TestCase):
    def rejects(self, code, fn, *args, **kwargs):
        with self.assertRaisesRegex(Rejected, '^' + code + '$'):
            fn(*args, **kwargs)

    def test_restart_preserves_consent_and_fences_execution(self):
        m = base()
        arm(m)
        m.approve('d', 'approver', 'reviewer', 'doc')
        old = m.claim('executor', 'doc')
        m.advance(3)
        m.restart()
        self.assertEqual(m.successions['s'].deadline, 8)
        self.rejects('STALE_LEASE', m.publish, 'd', 'executor', old.generation, old.term)
        m.advance(7)
        self.rejects('NOT_DUE', m.activate_succession, 's')
        m.advance(8)
        m.activate_succession('s')
        self.assertEqual(m.owners['doc'], 'successor')
        publish(m)

    def test_restarts_cannot_repeatedly_postpone_without_owner_contact(self):
        m = base()
        arm(m)
        for moment in (3, 5, 7, 8):
            m.advance(moment)
            m.restart()
            self.assertEqual(m.successions['s'].deadline, 8)
        m.activate_succession('s')
        self.assertEqual(m.owners['doc'], 'successor')

    def test_heartbeat_replenishes_one_grace(self):
        m = base()
        arm(m)
        m.advance(3)
        m.restart()  # deadline 8, grace used
        m.advance(4)
        m.heartbeat('s', 'owner')  # deadline 9, fresh owner contact
        m.advance(6)
        m.restart()  # deadline 11, one new grace
        m.advance(9)
        m.restart()
        self.assertEqual(m.successions['s'].deadline, 11)
        m.advance(11)
        m.activate_succession('s')

    def test_restart_never_arms_unaccepted_cancelled_or_stale_rules(self):
        for mode in ('unaccepted', 'cancelled', 'goal'):
            with self.subTest(mode=mode):
                m = base()
                m.plan_succession('s', 'owner', 'successor', 'doc', timeout=5)
                if mode != 'unaccepted':
                    m.accept_succession('s', 'successor')
                if mode == 'cancelled':
                    m.cancel_succession('s', 'owner')
                elif mode == 'goal':
                    m.change_goal()
                m.advance(4)
                m.restart()
                self.assertEqual(m.successions['s'].deadline, 5)
                m.advance(5)
                self.rejects('SUCCESSION_INELIGIBLE', m.activate_succession, 's')

    def test_pending_rule_cannot_get_new_acceptance_window_by_heartbeat(self):
        m = base()
        m.plan_succession('s', 'owner', 'successor', 'doc', timeout=5)
        m.advance(4)
        self.rejects('STALE_GOVERNANCE', m.heartbeat, 's', 'owner')
        m.advance(5)
        self.rejects('SUCCESSION_ACCEPTANCE', m.accept_succession, 's', 'successor')

    def test_both_late_heartbeat_activation_orders(self):
        for order in itertools.permutations(('heartbeat', 'activate')):
            with self.subTest(order=order):
                m = base()
                arm(m)
                m.advance(7)
                if order[0] == 'heartbeat':
                    m.heartbeat('s', 'owner')
                    self.rejects('NOT_DUE', m.activate_succession, 's')
                    self.assertEqual(m.owners['doc'], 'owner')
                    m.advance(12)
                    m.activate_succession('s')
                else:
                    m.activate_succession('s')
                    self.rejects('STALE_GOVERNANCE', m.heartbeat, 's', 'owner')
                self.assertEqual(m.owners['doc'], 'successor')
                self.assertEqual(len(m.events), 1)

    def test_both_cancel_activation_orders(self):
        for order in itertools.permutations(('cancel', 'activate')):
            with self.subTest(order=order):
                m = base()
                arm(m)
                m.advance(5)
                if order[0] == 'cancel':
                    m.cancel_succession('s', 'owner')
                    self.rejects('SUCCESSION_INELIGIBLE', m.activate_succession, 's')
                    self.assertEqual(m.owners['doc'], 'owner')
                else:
                    m.activate_succession('s')
                    self.rejects('SUCCESSION_AUTHORITY', m.cancel_succession, 's', 'owner')
                    self.assertEqual(m.owners['doc'], 'successor')

    def test_uncertain_clock_fences_writes_until_verified_recovery(self):
        m = base()
        arm(m)
        m.approve('d', 'approver', 'reviewer', 'doc')
        lease = m.claim('executor', 'doc')
        m.advance(3)
        m.restart(clock_verified=False)
        self.rejects('CLOCK_UNCERTAIN', m.advance, 4)
        self.rejects('CLOCK_UNCERTAIN', m.claim, 'executor', 'doc')
        self.rejects('CLOCK_UNCERTAIN', m.publish, 'd', 'executor', lease.generation, lease.term)
        self.rejects('SUCCESSION_INELIGIBLE', m.activate_succession, 's')
        self.rejects('CLOCK_BACKWARD', m.recover_clock, 2)
        m.restart()  # A restart alone cannot turn uncertainty into evidence.
        self.assertFalse(m.clock_ready)
        m.recover_clock(9)
        self.assertEqual(m.successions['s'].deadline, 14)
        self.rejects('STALE_LEASE', m.publish, 'd', 'executor', lease.generation, lease.term)
        self.rejects('CLOCK_ALREADY_READY', m.recover_clock, 10)
        m.advance(14)
        m.activate_succession('s')

    def test_restore_invalidates_old_consent_grants_decisions_and_leases(self):
        m = base()
        arm(m)
        m.delegate('g', 'owner', 'delegate', 'doc', {'approve'}, expires=10)
        m.approve('d', 'delegate', 'reviewer', 'doc', grant='g')
        old = m.claim('executor', 'doc')
        m.restore_boundary()
        self.assertFalse(m.clock_ready)
        m.recover_clock(0)
        self.assertFalse(m.live_grant('g'))
        self.rejects('SUCCESSION_INELIGIBLE', m.activate_succession, 's')
        self.rejects('STALE_INCARNATION', m.publish, 'd', 'executor', old.generation, old.term)
        m.cancel_succession('s', 'owner')
        m.plan_succession('fresh', 'owner', 'successor', 'doc', timeout=5)
        m.accept_succession('fresh', 'successor')
        m.advance(5)
        m.activate_succession('fresh')
        self.assertEqual(m.owners['doc'], 'successor')

    def test_successors_review_survives_but_former_owners_approval_does_not(self):
        for approver, expected in [('approver', 'published'), ('owner', 'stale')]:
            with self.subTest(approver=approver):
                m = base()
                arm(m)
                m.approve('d', approver, 'successor', 'doc')
                m.advance(5)
                m.activate_succession('s')
                if expected == 'published':
                    publish(m)
                    self.assertEqual(m.heads['doc'], 1)
                else:
                    self.rejects('STALE_AUTHORITY', publish, m)
                    self.assertEqual(m.heads['doc'], 0)

    def test_all_additive_review_right_changes_preserve_approval(self):
        options = ('approve', 'publish')
        pairs = 0
        for before_bits in itertools.product((False, True), repeat=2):
            before = {'review'} | {x for x, bit in zip(options, before_bits) if bit}
            for after_bits in itertools.product((False, True), repeat=2):
                after = {'review'} | {x for x, bit in zip(options, after_bits) if bit}
                if not before <= after:
                    continue
                with self.subTest(before=before, after=after):
                    m = base()
                    m.set_rights('reviewer', 'doc', before)
                    m.approve('d', 'approver', 'reviewer', 'doc')
                    old_epoch = m.epoch('reviewer', 'doc')
                    m.set_rights('reviewer', 'doc', after)
                    self.assertEqual(m.epoch('reviewer', 'doc'), old_epoch)
                    publish(m)
                    pairs += 1
        self.assertEqual(pairs, 9)

    def test_mixed_removal_addition_and_restore_cannot_revive_old_review(self):
        m = base()
        m.approve('d', 'approver', 'reviewer', 'doc')
        epoch = m.epoch('reviewer', 'doc')
        m.set_rights('reviewer', 'doc', {'publish'})
        self.assertGreater(m.epoch('reviewer', 'doc'), epoch)
        m.set_rights('reviewer', 'doc', {'review', 'publish'})
        self.rejects('STALE_AUTHORITY', publish, m)

    def test_successor_cannot_inherit_rights_added_after_consent(self):
        m = base()
        m.set_rights('owner', 'doc', {'approve'})
        arm(m)
        m.set_rights('owner', 'doc', AuthorityModel.ACTIONS)
        m.advance(5)
        m.activate_succession('s')
        self.assertEqual(m.rights['successor', 'doc'], {'approve', 'review'})
        self.assertFalse(m.direct('successor', 'doc', 'publish'))
        self.assertEqual(m.rights['owner', 'doc'], frozenset())

    def test_expiry_and_revocation_preserve_history_but_fence_unpublished_grant(self):
        for invalidation in ('expiry', 'revocation'):
            with self.subTest(invalidation=invalidation):
                m = base()
                m.delegate('g', 'owner', 'delegate', 'doc', {'approve'}, expires=4)
                m.approve('delegated', 'delegate', 'reviewer', 'doc', grant='g')
                m.approve('direct', 'approver', 'reviewer', 'doc')
                decision = m.decisions['delegated']
                if invalidation == 'expiry':
                    m.advance(4)
                else:
                    m.revoke('g', 'owner')
                self.rejects('GRANT_INELIGIBLE', publish, m, 'delegated')
                self.assertEqual(m.decisions['delegated'], decision)
                lease = m.leases['doc']
                m.publish('direct', 'executor', lease.generation, lease.term)
                self.assertEqual(m.heads['doc'], 1)

    def test_removal_still_invalidates_ancestor_chain_but_addition_does_not(self):
        m = base()
        m.delegate('g', 'owner', 'delegate', 'doc', {'approve'}, expires=10,
                   may_delegate=True)
        m.delegate('child', 'delegate', 'approver', 'doc', {'approve'}, expires=9,
                   parent='g')
        m.set_rights('delegate', 'doc', {'review'})
        self.assertTrue(m.live_grant('child'))
        m.set_rights('delegate', 'doc', ())
        self.assertFalse(m.live_grant('child'))


if __name__ == '__main__':
    unittest.main()
