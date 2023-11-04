def read_state_weights():
    data = []
    with open("state_weights.txt","r") as f:
        _ = f.readline()
        state_and_weights = f.readline()
        state_and_weights = state_and_weights.split()
        num_states = state_and_weights[0]
        default_weight = state_and_weights[1]
        for _ in range(int(num_states)):
            line = f.readline().strip()
            data.append(line)
    return data,default_weight

def read_state_action_state_weights():
    data = []
    with open("state_action_state_weights.txt","r") as f:
        _ = f.readline()
        infos = f.readline()
        infos = infos.split()
        num_triplets = infos[0]
        num_unique_states = infos[1]
        num_unique_actions = infos[2]
        default_weights = infos[3]
        for _ in range(int(num_triplets)):
            line = f.readline().strip()
            data.append(line)
    return data,num_unique_states,num_unique_actions,default_weights

def read_state_observation_weights():
    data = []
    with open("state_observation_weights.txt","r") as f:
        _ = f.readline()
        infos = f.readline()
        infos = infos.split()
        num_pairs = infos[0]
        num_unique_states = infos[1]
        num_unique_observations = infos[2]
        default_weights = infos[3]
        for _ in range(int(num_pairs)):
            line = f.readline().strip()
            data.append(line)
    return data,num_unique_states,num_unique_observations,default_weights

def read_observation_actions():
    data = []
    with open("observation_actions.txt","r") as f:
        _ = f.readline()
        num_pairs = f.readline()
        for _ in range(int(num_pairs)):
            line = f.readline().strip()
            data.append(line)
    return data

def main():
    a = 1

if __name__ == "__main__":
    main()