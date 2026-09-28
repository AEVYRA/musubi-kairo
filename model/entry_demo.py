"""Run with python -m model.entry_demo after installing requirements-dev.txt."""
import json

from model.entry import EntryModel, PROFILE


def run():
    n = EntryModel()
    trace = [{'step': 'welcome', 'value': n.welcome()}]
    n.schema('entry-command')
    n.register_principal('fixture:alpha', persistent=True)
    n.register_principal('fixture:beta', persistent=True)
    alpha, a = n.identify('fixture:alpha')
    beta, b = n.identify('fixture:beta')
    trace.append({'step': 'identify', 'actors': [a, b]})

    def command(action, payload, op):
        return json.dumps({'profile': PROFILE, 'node': n.node,
                           'incarnation': n.incarnation, 'operation_id': op,
                           'action': action, 'payload': payload}).encode()

    speech = command('speak', {'room': 'lobby', 'text': 'Let us write a guide.'}, 'op:speak')
    trace.append({'step': 'speak', 'receipt': n.command(alpha, speech)})
    creation = command('create_project', {'expected_admission_rev': '1',
        'title': 'Shared guide', 'goal': {'objective': 'Write an installation guide',
        'constraints': ['Local setup'], 'criteria': ['Peer reproduces setup']}}, 'op:create')
    receipt = n.command(alpha, creation)
    assert n.command(alpha, creation) == receipt and len(n.projects) == 1
    trace.append({'step': 'create_and_retry', 'receipt': receipt, 'project_count': 1})
    project_id = receipt['result']['project']
    admission = command('admit', {'project': project_id, 'expected_membership_rev': '1',
                                 'subject': b['actor'], 'actions': ['review']}, 'op:admit')
    trace.append({'step': 'admit', 'receipt': n.command(alpha, admission)})
    trace.append({'step': 'enter', 'brief': n.enter(beta, project_id)})
    authority = n.projects[project_id].authority
    authority.approve('decision:1', a['actor'], b['actor'], n.SCOPE)
    lease = authority.claim(a['actor'], n.SCOPE)
    authority.publish('decision:1', a['actor'], lease.generation, lease.term)
    trace.append({'step': 'trusted_authority_composition',
                  'artifact_head': authority.heads[n.SCOPE]})
    return {'kind': 'in-memory-model-trace',
            'authentication': 'trusted synthetic fixtures; no signature verification',
            'publication': 'counter transition; proposal/review content assumed',
            'trace': trace}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
