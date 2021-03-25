def state_machine(state, val):
    command, key = val[0], val[1]

    if command == 'get':
        return state, state.get(key, None)

    elif command == 'set':
        state[key] = val[2]

        return state, val[2]
