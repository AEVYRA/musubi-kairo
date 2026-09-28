"""Finite, deterministic authority model. No network, signatures, or persistence.

Calls are serialized transitions. Bootstrap/set_rights/advance/restart represent
trusted environment inputs; caller strings stand for already authenticated actors.
The model is not an authorization library for untrusted requests.
"""
from dataclasses import dataclass


class Rejected(Exception):
    pass


def require(condition, code):
    if not condition:
        raise Rejected(code)


@dataclass(frozen=True)
class Grant:
    issuer: str
    subject: str
    scope: str
    actions: frozenset
    parent: str | None
    may_delegate: bool
    goal: int
    policy: int
    expires: int
    stamps: tuple


@dataclass(frozen=True)
class Decision:
    scope: str
    goal: int
    policy: int
    base: int
    stamps: tuple
    grant: str | None


@dataclass(frozen=True)
class Lease:
    actor: str
    generation: int
    term: int
    deadline: int
    authority_epoch: int
    goal: int
    policy: int


@dataclass(frozen=True)
class Succession:
    owner: str
    successor: str
    scope: str
    goal: int
    policy: int
    owner_epoch: int
    successor_epoch: int
    term: int
    timeout: int
    deadline: int


class AuthorityModel:
    ACTIONS = frozenset({"approve", "review", "publish"})

    def __init__(self):
        self.now = 0
        self.term = self.goal = self.policy = 1
        self.roster_revision = 0
        self.actors = set()
        self.owners = {}
        self.rights = {}
        self.epochs = {}
        self.heads = {}
        self.grants = {}
        self.revoked = set()
        self.decisions = {}
        self.consumed = set()
        self.leases = {}
        self.generations = {}
        self.recognition = []
        self.successions = {}
        self.accepted_successions = set()
        self.fired_successions = set()
        self.cancelled_successions = set()
        self.events = []

    def enroll(self, actor):
        require(actor not in self.actors, "ACTOR_EXISTS")
        self.actors.add(actor)
        self.roster_revision += 1

    def bootstrap_scope(self, scope, owner):
        require(scope not in self.owners and owner in self.actors, "BOOTSTRAP")
        self.owners[scope] = owner
        self.heads[scope] = 0
        self.set_rights(owner, scope, self.ACTIONS)

    def epoch(self, actor, scope):
        return self.epochs.get((actor, scope), 0)

    def set_rights(self, actor, scope, actions):
        require(actor in self.actors and scope in self.owners, "UNKNOWN")
        require(set(actions) <= self.ACTIONS, "ACTION")
        self.rights[actor, scope] = frozenset(actions)
        self.epochs[actor, scope] = self.epoch(actor, scope) + 1

    def direct(self, actor, scope, action):
        return action in self.rights.get((actor, scope), ())

    def stamp(self, *pairs):
        return tuple((a, s, self.epoch(a, s)) for a, s in sorted(set(pairs)))

    def current(self, stamps):
        return all(self.epoch(a, s) == e for a, s, e in stamps)

    def recognize(self, caller, subject, context, evidence):
        require(caller in self.actors and subject in self.actors, "UNKNOWN")
        require(bool(context) and bool(evidence), "EVIDENCE")
        self.recognition.append((caller, subject, context, evidence))

    def recognizes(self, observer, subject, context):
        return any((a, b, c) == (observer, subject, context)
                   for a, b, c, _ in self.recognition)

    def live_grant(self, grant_id, seen=()):
        if grant_id not in self.grants or grant_id in seen or len(seen) >= 8:
            return False
        g = self.grants[grant_id]
        return (grant_id not in self.revoked and g.goal == self.goal
                and g.policy == self.policy and self.now < g.expires
                and self.current(g.stamps)
                and (g.parent is None or self.live_grant(g.parent, seen + (grant_id,))))

    def delegate(self, grant_id, caller, subject, scope, actions,
                 *, expires, parent=None, may_delegate=False):
        require(grant_id not in self.grants, "ID_EXISTS")
        require(caller in self.actors and subject in self.actors, "UNKNOWN")
        require(type(may_delegate) is bool, "DELEGATION_FLAG")
        require(type(expires) is int and expires > self.now, "EXPIRY")
        actions = frozenset(actions)
        require(bool(actions) and actions <= self.ACTIONS, "ACTION")
        if parent is None:
            require(self.owners.get(scope) == caller, "ROOT_AUTHORITY")
            require(actions <= self.rights.get((caller, scope), ()), "AMPLIFICATION")
        else:
            require(self.live_grant(parent), "PARENT_INELIGIBLE")
            p = self.grants[parent]
            require(p.subject == caller and p.may_delegate, "NO_REDELEGATION")
            require(p.scope == scope and actions <= p.actions
                    and expires <= p.expires, "AMPLIFICATION")
            depth, cursor = 1, parent
            while cursor is not None:
                depth += 1
                cursor = self.grants[cursor].parent
            require(depth <= 8, "CHAIN_LIMIT")
        self.grants[grant_id] = Grant(caller, subject, scope, actions, parent,
                                     may_delegate, self.goal, self.policy, expires,
                                     self.stamp((caller, scope), (subject, scope)))

    def revoke(self, grant_id, caller):
        require(grant_id in self.grants, "UNKNOWN")
        g = self.grants[grant_id]
        require(caller in (g.issuer, self.owners[g.scope]), "FORBIDDEN")
        self.revoked.add(grant_id)

    def approve(self, decision_id, caller, reviewer, scope, *, grant=None):
        require(decision_id not in self.decisions, "ID_EXISTS")
        require(caller != reviewer, "INDEPENDENT_REVIEW")
        require(self.direct(reviewer, scope, "review"), "REVIEW_AUTHORITY")
        if grant is None:
            require(self.direct(caller, scope, "approve"), "APPROVAL_AUTHORITY")
        else:
            require(self.live_grant(grant), "GRANT_INELIGIBLE")
            g = self.grants[grant]
            require(g.subject == caller and g.scope == scope
                    and "approve" in g.actions, "GRANT_SCOPE")
        # Exact proposal content and supportive review are assumed by this slice.
        self.decisions[decision_id] = Decision(
            scope, self.goal, self.policy, self.heads[scope],
            self.stamp((caller, scope), (reviewer, scope)), grant)

    def claim(self, caller, scope, *, duration=5):
        require(self.direct(caller, scope, "publish"), "EXECUTOR_AUTHORITY")
        require(type(duration) is int and 0 < duration <= 10, "DURATION")
        old = self.leases.get(scope)
        active = old is not None and self.lease_live(scope, old)
        require(not active, "BUSY")
        generation = self.generations.get(scope, 0) + 1
        lease = Lease(caller, generation, self.term, self.now + duration,
                      self.epoch(caller, scope), self.goal, self.policy)
        self.generations[scope] = generation
        self.leases[scope] = lease
        return lease

    def lease_live(self, scope, lease):
        return (lease.term == self.term and self.now < lease.deadline
                and lease.authority_epoch == self.epoch(lease.actor, scope)
                and lease.goal == self.goal and lease.policy == self.policy
                and self.direct(lease.actor, scope, "publish"))

    def renew(self, caller, scope, generation, term, *, duration=5):
        old = self.leases.get(scope)
        require(old is not None and old.actor == caller and old.generation == generation
                and old.term == term and self.lease_live(scope, old), "STALE_LEASE")
        require(type(duration) is int and 0 < duration <= 10, "DURATION")
        require(self.now + duration > old.deadline, "NO_EXTENSION")
        lease = Lease(caller, generation, term, self.now + duration,
                      old.authority_epoch, self.goal, self.policy)
        self.leases[scope] = lease
        return lease

    def publish(self, decision_id, caller, generation, term):
        require(decision_id in self.decisions, "UNKNOWN")
        d = self.decisions[decision_id]
        require(decision_id not in self.consumed, "CONSUMED")
        require((d.goal, d.policy) == (self.goal, self.policy), "STALE_CONTROL")
        require(self.current(d.stamps), "STALE_AUTHORITY")
        require(d.grant is None or self.live_grant(d.grant), "GRANT_INELIGIBLE")
        lease = self.leases.get(d.scope)
        require(lease is not None and lease.actor == caller
                and lease.generation == generation and lease.term == term
                and self.lease_live(d.scope, lease), "STALE_LEASE")
        require(self.heads[d.scope] == d.base, "BASE_CONFLICT")
        # This indivisible transition models the managed publication boundary.
        self.heads[d.scope] += 1
        self.consumed.add(decision_id)
        del self.leases[d.scope]
        self.events.append(("published", decision_id, self.heads[d.scope]))

    def advance(self, moment):
        require(type(moment) is int and moment >= self.now, "CLOCK_BACKWARD")
        self.now = moment

    def restart(self):
        self.term += 1

    def change_goal(self):
        self.goal += 1

    def change_policy(self):
        self.policy += 1

    def plan_succession(self, rule_id, caller, successor, scope, *, timeout):
        require(rule_id not in self.successions, "ID_EXISTS")
        require(self.owners.get(scope) == caller and successor in self.actors
                and successor != caller, "SUCCESSION_AUTHORITY")
        require(type(timeout) is int and 0 < timeout <= 10, "DURATION")
        require(not any(r.scope == scope and rid not in self.fired_successions
                        and rid not in self.cancelled_successions
                        for rid, r in self.successions.items()), "RULE_EXISTS")
        self.successions[rule_id] = Succession(
            caller, successor, scope, self.goal, self.policy,
            self.epoch(caller, scope), self.epoch(successor, scope),
            self.term, timeout, self.now + timeout)

    def accept_succession(self, rule_id, caller):
        require(rule_id in self.successions, "UNKNOWN")
        r = self.successions[rule_id]
        require(caller == r.successor and self.now < r.deadline
                and rule_id not in self.cancelled_successions
                and self.succession_current(r), "SUCCESSION_ACCEPTANCE")
        self.accepted_successions.add(rule_id)

    def cancel_succession(self, rule_id, caller):
        require(rule_id in self.successions, "UNKNOWN")
        r = self.successions[rule_id]
        require(self.owners.get(r.scope) == caller
                and rule_id not in self.fired_successions, "SUCCESSION_AUTHORITY")
        self.cancelled_successions.add(rule_id)

    def succession_current(self, r):
        return ((r.goal, r.policy, r.term) == (self.goal, self.policy, self.term)
                and self.owners.get(r.scope) == r.owner
                and self.epoch(r.owner, r.scope) == r.owner_epoch
                and self.epoch(r.successor, r.scope) == r.successor_epoch)

    def heartbeat(self, rule_id, caller):
        require(rule_id in self.successions, "UNKNOWN")
        r = self.successions[rule_id]
        require(rule_id not in self.cancelled_successions
                and caller == r.owner and self.succession_current(r)
                and self.now < r.deadline, "STALE_GOVERNANCE")
        self.successions[rule_id] = Succession(
            r.owner, r.successor, r.scope, r.goal, r.policy, r.owner_epoch,
            r.successor_epoch, r.term, r.timeout, self.now + r.timeout)

    def activate_succession(self, rule_id):
        require(rule_id in self.successions, "UNKNOWN")
        r = self.successions[rule_id]
        require(rule_id not in self.fired_successions
                and rule_id not in self.cancelled_successions
                and rule_id in self.accepted_successions
                and self.succession_current(r), "SUCCESSION_INELIGIBLE")
        require(self.now >= r.deadline, "NOT_DUE")
        inherited = self.rights.get((r.owner, r.scope), frozenset())
        self.set_rights(r.owner, r.scope, ())
        self.set_rights(r.successor, r.scope, inherited
                        | self.rights.get((r.successor, r.scope), frozenset()))
        self.owners[r.scope] = r.successor
        self.fired_successions.add(rule_id)
        self.events.append(("succession", rule_id, r.successor, r.scope))
