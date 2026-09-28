"""Bounded entry model composed with AuthorityModel, not a network/auth service.

Trusted adapter inputs register principals and call identify. Opaque session objects
are simulation handles, not tokens to send over a transport. All calls serialize.
"""
from copy import deepcopy
from dataclasses import asdict, dataclass, field
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from model.authority import AuthorityModel, Rejected, require

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / 'schemas/entry-command.schema.json').read_text())
VALIDATOR = Draft202012Validator(SCHEMA)
PROFILE = 'kairo-entry-candidate/0.2'


@dataclass
class Principal:
    persistent: bool
    enabled: bool = True
    actor: str | None = None


@dataclass
class Project:
    title: str
    goal: dict
    authority: AuthorityModel
    project_id: str = ''
    membership_rev: int = 1
    members: set = field(default_factory=set)
    rule_revisions: dict = field(default_factory=dict)


class EntryModel:
    # Small finite-model bounds, not recommended production quotas.
    LIMITS = {'principals': 8, 'projects': 3, 'projects_per_actor': 2,
              'messages': 8, 'messages_per_actor': 2, 'receipts': 32,
              'command_bytes': 8192, 'sessions': 16, 'rules_per_project': 8}
    SCOPE = 'artifact:main'

    def __init__(self):
        self.node = 'node:demo'
        self.incarnation = 'incarnation:1'
        self.admission_rev = 1
        self.creation_enabled = True
        self.principals = {}
        self.sessions = {}
        self.projects = {}
        self.messages = []
        self.receipts = {}
        self.events = []
        self.actor_count = 0

    def register_principal(self, credential, *, persistent):
        """Trusted verifier fixture. Not a public command or a signature check."""
        require(credential not in self.principals, 'PRINCIPAL_EXISTS')
        require(type(persistent) is bool, 'PERSISTENCE')
        require(len(self.principals) < self.LIMITS['principals'], 'CAPACITY')
        self.principals[credential] = Principal(persistent)

    def identify(self, verified_credential):
        """Adapter has verified credential control; the model does not do so."""
        p = self.principals.get(verified_credential)
        require(p is not None and p.enabled, 'UNAUTHENTICATED')
        require(len(self.sessions) < self.LIMITS['sessions'], 'CAPACITY')
        if p.actor is None:
            self.actor_count += 1
            p.actor = f'actor:{self.actor_count}'
        session = object()
        self.sessions[session] = verified_credential
        return session, {'actor': p.actor, 'continuity':
                         'credential-bound' if p.persistent else 'ephemeral'}

    def authenticate(self, session):
        credential = self.sessions.get(session)
        p = self.principals.get(credential)
        require(p is not None and p.enabled, 'UNAUTHENTICATED')
        return p

    def close_session(self, session):
        self.sessions.pop(session, None)

    def revoke_credential(self, credential):
        """Trusted environment transition, not a self-service recovery path."""
        require(credential in self.principals, 'UNKNOWN')
        self.principals[credential].enabled = False

    def change_admission(self, *, creation_enabled):
        require(type(creation_enabled) is bool, 'POLICY')
        self.creation_enabled = creation_enabled
        self.admission_rev += 1

    def welcome(self):
        # No live project/member/message counts or private state.
        schema_bytes = json.dumps(SCHEMA, sort_keys=True, separators=(',', ':')).encode()
        return {'profile': PROFILE, 'node': self.node, 'incarnation': self.incarnation,
                'admission_rev': str(self.admission_rev),
                'schema': {'id': 'entry-command',
                           'sha256': hashlib.sha256(schema_bytes).hexdigest()},
                'limits': dict(self.LIMITS),
                'actions': [
                    {'name': 'identify', 'requires': 'verified adapter principal'},
                    {'name': 'speak', 'requires': 'identified actor; public lobby'},
                    {'name': 'create_project', 'requires':
                     'persistent credential; current admission revision; capacity'},
                    {'name': 'admit', 'requires': 'current scoped project owner'},
                    {'name': 'enter', 'requires': 'current project member'},
                    {'name': 'plan_succession', 'requires': 'owner; admitted persistent successor'},
                    {'name': 'accept_succession', 'requires': 'named eligible successor; current rule'},
                    {'name': 'heartbeat', 'requires': 'rule owner; current accepted rule'},
                    {'name': 'cancel_succession', 'requires': 'current owner; current rule'},
                    {'name': 'activate_succession', 'requires': 'persistent member; due accepted rule'}],
                'creation_enabled': self.creation_enabled,
                'next': 'Read entry-command schema; identify through the adapter.'}

    def schema(self, schema_id):
        require(schema_id == 'entry-command', 'UNSUPPORTED_SCHEMA')
        return deepcopy(SCHEMA)

    @staticmethod
    def decode(raw):
        require(type(raw) is bytes and len(raw) <= EntryModel.LIMITS['command_bytes'],
                'COMMAND_SIZE')

        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError('duplicate key')
                result[key] = value
            return result

        def nonfinite(value):
            raise ValueError('nonfinite number')

        try:
            command = json.loads(raw.decode('utf-8'), object_pairs_hook=unique,
                                 parse_constant=nonfinite)
            # Reject unpaired surrogate escapes too, before schema/fingerprint.
            normalized = json.dumps(command, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode('utf-8')
            require(VALIDATOR.is_valid(command), 'MALFORMED_COMMAND')
            return command, hashlib.sha256(normalized).hexdigest()
        except (ValueError, UnicodeError, RecursionError) as e:
            raise Rejected('MALFORMED_COMMAND') from e

    def command(self, session, raw):
        principal = self.authenticate(session)  # Also before cached receipts.
        c, fingerprint = self.decode(raw)
        require(c['node'] == self.node, 'WRONG_NODE')
        require(c['incarnation'] == self.incarnation, 'STALE_INCARNATION')
        key = (principal.actor, c['operation_id'])
        if key in self.receipts:
            old_fingerprint, receipt = self.receipts[key]
            require(old_fingerprint == fingerprint, 'OPERATION_ID_REUSED')
            return deepcopy(receipt)
        require(len(self.receipts) < self.LIMITS['receipts'], 'RECEIPT_CAPACITY')
        # Domain handlers validate all conditions before their first mutation.
        try:
            result = getattr(self, '_' + c['action'])(principal, c['payload'])
            receipt = {'operation_id': c['operation_id'], 'status': 'applied',
                       'result': result}
        except Rejected as e:
            receipt = {'operation_id': c['operation_id'], 'status': 'rejected',
                       'code': str(e)}
        # Model-only atomic boundary; no process crash/persistence claim.
        self.receipts[key] = (fingerprint, deepcopy(receipt))
        return deepcopy(receipt)

    def _speak(self, p, body):
        require(len(self.messages) < self.LIMITS['messages'], 'LOBBY_CAPACITY')
        require(sum(m['author'] == p.actor for m in self.messages)
                < self.LIMITS['messages_per_actor'], 'ACTOR_QUOTA')
        message = {'id': f'message:{len(self.messages) + 1}', 'author': p.actor,
                   'room': 'lobby', 'text': body['text']}
        self.messages.append(message)
        self.events.append(('speak', message['id']))
        return {'message': message['id'], 'meaning': 'recorded, not endorsed'}

    def lobby(self, session):
        self.authenticate(session)
        return {'messages': deepcopy(self.messages), 'complete': True}

    def _create_project(self, p, body):
        require(body['expected_admission_rev'] == str(self.admission_rev), 'STALE_ADMISSION')
        require(p.persistent, 'PERSISTENT_CREDENTIAL_REQUIRED')
        require(self.creation_enabled, 'CREATION_DISABLED')
        require(len(self.projects) < self.LIMITS['projects'], 'PROJECT_CAPACITY')
        # Count founded projects even if ownership later transfers.
        require(sum(e[0] == 'create_project' and e[2] == p.actor for e in self.events)
                < self.LIMITS['projects_per_actor'], 'ACTOR_QUOTA')
        project_id = f'project:{len(self.projects) + 1}'
        authority = AuthorityModel()
        authority.enroll(p.actor)
        authority.bootstrap_scope(self.SCOPE, p.actor)
        self.projects[project_id] = Project(body['title'], deepcopy(body['goal']),
                                           authority, project_id=project_id, members={p.actor})
        self.events.append(('create_project', project_id, p.actor))
        return {'project': project_id, 'scope': self.SCOPE, 'goal_rev': '1',
                'policy_rev': '1', 'membership_rev': '1', 'owner': p.actor}

    def _admit(self, p, body):
        project = self.projects.get(body['project'])
        # Unknown and inaccessible IDs deliberately yield the same outcome.
        require(project is not None and p.actor in project.members, 'NOT_ACCESSIBLE')
        require(project.authority.incarnation == 1 and project.authority.clock_ready,
                "CONTROL_UNAVAILABLE")
        require(project.authority.owners[self.SCOPE] == p.actor, 'FORBIDDEN')
        require(body['expected_membership_rev'] == str(project.membership_rev),
                'MEMBERSHIP_CONFLICT')
        subject = body['subject']
        require(any(x.actor == subject and x.enabled and x.persistent
                    for x in self.principals.values()), 'SUBJECT_INELIGIBLE')
        require(subject not in project.members, 'ALREADY_MEMBER')
        project.authority.enroll(subject)
        project.authority.set_rights(subject, self.SCOPE, body['actions'])
        project.members.add(subject)
        project.membership_rev += 1
        self.events.append(('admit', body['project'], subject))
        return {'project': body['project'], 'subject': subject,
                'membership_rev': str(project.membership_rev)}

    def enter(self, session, project_id):
        p = self.authenticate(session)
        project = self.projects.get(project_id)
        require(project is not None and p.actor in project.members, 'NOT_ACCESSIBLE')
        a = project.authority
        # Goal/policy replacement bodies are outside this entry slice.
        require(a.goal == 1 and a.policy == 1 and a.incarnation == 1
                and a.clock_ready, "CONTROL_UNAVAILABLE")
        require(a.owners[self.SCOPE] in project.members, "CONTROL_UNAVAILABLE")
        return {'project': project_id, 'title': project.title,
                'goal': deepcopy(project.goal), 'goal_rev': str(a.goal),
                'policy_rev': str(a.policy), 'membership_rev': str(project.membership_rev),
                'scope': self.SCOPE, 'owner': a.owners[self.SCOPE],
                'direct_actions': sorted(a.rights.get((p.actor, self.SCOPE), ())),
                'authority_epoch': str(a.epoch(p.actor, self.SCOPE)),
                'governance_control': self._control(project),
                'successions': [self._rule_view(project, rid)
                                for rid in sorted(project.rule_revisions)],
                'coverage': {'control': 'complete', 'work': 'not_implemented',
                             'obligations': 'not_implemented'}}

    def _control(self, project):
        a = project.authority
        owner = a.owners[self.SCOPE]
        return {'goal_rev': str(a.goal), 'policy_rev': str(a.policy),
                'authority_incarnation': str(a.incarnation), 'owner': owner,
                'owner_epoch': str(a.epoch(owner, self.SCOPE))}

    def _eligible_member(self, project, actor):
        return actor in project.members and any(
            p.actor == actor and p.enabled and p.persistent
            for p in self.principals.values())

    def _governance_project(self, p, body):
        project = self.projects.get(body['project'])
        require(project is not None and p.actor in project.members, 'NOT_ACCESSIBLE')
        a = project.authority
        require(a.goal == 1 and a.policy == 1 and a.incarnation == 1
                and a.clock_ready and a.owners[self.SCOPE] in project.members,
                'CONTROL_UNAVAILABLE')
        require(self._eligible_member(project, p.actor), 'SUBJECT_INELIGIBLE')
        return project

    def _rule_view(self, project, rule_id):
        a = project.authority
        record = asdict(a.successions[rule_id])
        record['actions'] = sorted(record['actions'])
        record.update(project=project.project_id, rule_id=rule_id,
                      binding_revision=project.rule_revisions[rule_id],
                      accepted=rule_id in a.accepted_successions,
                      cancelled=rule_id in a.cancelled_successions,
                      fired=rule_id in a.fired_successions)
        digest = hashlib.sha256(json.dumps(record, ensure_ascii=False, sort_keys=True,
                                          separators=(',', ':')).encode()).hexdigest()
        return {'record': record, 'fingerprint': digest}

    def _bound_rule(self, project, body):
        rid = body['rule_id']
        require(rid in project.rule_revisions, 'UNKNOWN_RULE')
        require(body['expected_rule'] == self._rule_view(project, rid)['fingerprint'],
                'RULE_CONFLICT')
        return project.authority.successions[rid]

    def _governance_result(self, project, body, action):
        rid = body['rule_id']
        project.rule_revisions[rid] += 1
        self.events.append((action, body['project'], rid))
        return {'project': body['project'], 'rule': self._rule_view(project, rid),
                'governance_control': self._control(project)}

    def _plan_succession(self, p, body):
        project = self._governance_project(p, body)
        require(body['expected_control'] == self._control(project), 'CONTROL_CONFLICT')
        require(self._eligible_member(project, body['successor']), 'SUBJECT_INELIGIBLE')
        require(len(project.authority.successions) < self.LIMITS['rules_per_project'],
                'RULE_CAPACITY')
        project.authority.plan_succession(body['rule_id'], p.actor, body['successor'],
                                         body['scope'], timeout=body['timeout'])
        project.rule_revisions[body['rule_id']] = 0
        return self._governance_result(project, body, 'plan_succession')

    def _accept_succession(self, p, body):
        project = self._governance_project(p, body)
        rule = self._bound_rule(project, body)
        require(self._eligible_member(project, rule.successor), 'SUBJECT_INELIGIBLE')
        project.authority.accept_succession(body['rule_id'], p.actor)
        return self._governance_result(project, body, 'accept_succession')

    def _heartbeat(self, p, body):
        project = self._governance_project(p, body)
        self._bound_rule(project, body)
        project.authority.heartbeat(body['rule_id'], p.actor)
        return self._governance_result(project, body, 'heartbeat')

    def _cancel_succession(self, p, body):
        project = self._governance_project(p, body)
        self._bound_rule(project, body)
        project.authority.cancel_succession(body['rule_id'], p.actor)
        return self._governance_result(project, body, 'cancel_succession')

    def _activate_succession(self, p, body):
        project = self._governance_project(p, body)
        rule = self._bound_rule(project, body)
        require(self._eligible_member(project, rule.successor), 'SUBJECT_INELIGIBLE')
        project.authority.activate_succession(body['rule_id'])
        result = self._governance_result(project, body, 'activate_succession')
        result['transfer'] = deepcopy(project.authority.events[-1][4])
        return result
