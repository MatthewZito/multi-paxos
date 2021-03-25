def test_machine(state, val):
    if val[0] == 'get':
        return state, state.get(val[1], None)

    elif val[0] == 'set':
        state[val[1]] = val[2]

        return state, val[2]
