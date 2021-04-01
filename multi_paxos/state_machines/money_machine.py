def state_machine(state, val):
    command, key = val[0], val[1]

    if command == 'balance':
        return state, state.get(key, None)

    elif command == 'deposit':
        state[key] = val[2]

        return state, val[2]

    elif command == 'withdraw':
        state[key] = val[2]

        return state, val[2]
