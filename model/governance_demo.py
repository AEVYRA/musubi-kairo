"""Three actors use entry JSON commands; only identity/time are trusted fixtures."""
import json

from model.entry import EntryModel, PROFILE


def run():
    n = EntryModel()
    sessions, actors, trace = {}, {}, []
    for name in ('owner', 'successor', 'peer'):
        n.register_principal('fixture:' + name, persistent=True)
        sessions[name], identity = n.identify('fixture:' + name)
        actors[name] = identity['actor']

    def send(who, action, payload, op):
        command = {'profile': PROFILE, 'node': n.node, 'incarnation': n.incarnation,
                   'operation_id': op, 'action': action, 'payload': payload}
        receipt = n.command(sessions[who], json.dumps(command).encode())
        trace.append({'actor': actors[who], 'command': command, 'receipt': receipt})
        assert receipt['status'] == 'applied', receipt
        return receipt

    created = send('owner', 'create_project', {'expected_admission_rev': '1',
        'title': 'Three-agent guide', 'goal': {'objective': 'Keep shared work governable',
        'constraints': ['Explicit consent'], 'criteria': ['Successor enters after transfer']}}, 'create')
    pid = created['result']['project']
    for i, name in enumerate(('successor', 'peer'), 1):
        send('owner', 'admit', {'project': pid, 'expected_membership_rev': str(i),
                              'subject': actors[name], 'actions': ['review']}, 'admit:' + name)

    def brief(who):
        return n.enter(sessions[who], pid)

    def body():
        return {'project': pid, 'scope': n.SCOPE, 'rule_id': 'rule:1',
                'expected_rule': brief('peer')['successions'][0]['fingerprint']}

    send('owner', 'plan_succession', {'project': pid, 'scope': n.SCOPE,
        'rule_id': 'rule:1', 'successor': actors['successor'], 'timeout': 5,
        'expected_control': brief('owner')['governance_control']}, 'plan')
    send('successor', 'accept_succession', body(), 'accept')
    a = n.projects[pid].authority
    a.advance(2)
    trace.append({'trusted_environment': 'advance authority model time to 2'})
    heartbeat_body = body()
    heartbeat = send('owner', 'heartbeat', heartbeat_body, 'heartbeat')
    a.advance(4)
    trace.append({'trusted_environment': 'advance authority model time to 4'})
    assert send('owner', 'heartbeat', heartbeat_body, 'heartbeat') == heartbeat
    assert a.successions['rule:1'].deadline == 7
    a.advance(7)
    trace.append({'trusted_environment': 'advance authority model time to 7'})
    activation_body = body()
    activation = send('peer', 'activate_succession', activation_body, 'activate')
    assert send('peer', 'activate_succession', activation_body, 'activate') == activation
    assert len(a.events) == 1
    trace.append({'successor_entry': brief('successor'), 'previous_owner_entry': brief('owner')})
    assert brief('successor')['owner'] == actors['successor']
    assert brief('owner')['direct_actions'] == []
    # The new owner can govern without additional trusted authority calls.
    send('successor', 'plan_succession', {'project': pid, 'scope': n.SCOPE,
        'rule_id': 'rule:2', 'successor': actors['peer'], 'timeout': 5,
        'expected_control': brief('successor')['governance_control']}, 'plan-next')
    next_rule = next(r for r in brief('successor')['successions']
                     if r['record']['rule_id'] == 'rule:2')
    send('successor', 'cancel_succession', {'project': pid, 'scope': n.SCOPE,
        'rule_id': 'rule:2', 'expected_rule': next_rule['fingerprint']}, 'cancel-next')
    return {'kind': 'in-memory-governance-binding-trace', 'actors': actors,
            'authentication': 'trusted synthetic verifier fixtures',
            'time': 'trusted model advances; no scheduler, disk or real clock recovery',
            'trace': trace}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
