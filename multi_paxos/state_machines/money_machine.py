def state_machine(state, val):
    command, key = val[0], val[1]
    print(state.get(key, 0) ,' HERE')

    if command == 'balance':
        return state, state.get(key, 0)

    elif command == 'deposit':
        state[key] = state.get(key) + val[2]

        return state, val[2]

    elif command == 'withdraw':
        state[key] = state.get(key) - val[2]

        return state, val[2]
