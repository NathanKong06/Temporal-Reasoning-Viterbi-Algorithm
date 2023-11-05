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

def write_output(output):
    with open("states.txt","w") as f:
        f.write("states\n")
        f.write(str(len(output)) + "\n")
        for index,_ in enumerate(output):
            f.write("\"" + output[index] + "\"")
            if index != len(output) -1:
                f.write("\n")

def calculate_state_probabilities():
    state_weights,_ = read_state_weights()
    state_probabilities = {}
    total_weight = 0
    for state_and_weight in state_weights:
        line = state_and_weight.split()
        state = line[0].strip('"') #Remove quotation marks
        weight = int(line[1])
        total_weight = total_weight + weight #Track total weight
        state_probabilities[state] = weight

    for state,weight in state_probabilities.items():
        state_probabilities[state] = weight/total_weight #Calculate probability 

    return state_probabilities

def calculate_state_observation_probabilities(): #Need to account for missing data later
    state_observation_weights,unique_states,unique_observations,default_value = read_state_observation_weights()
    state_observation_probabilities = {}

    for state_and_observation_weight in state_observation_weights:
        state,observation,weight = state_and_observation_weight.split()
        state = state.strip('"') #Remove quotation marks
        observation = observation.strip('"') #Remove quotation marks
        if state not in state_observation_probabilities:
            state_observation_probabilities[state] = {} #Create dictionary for every state
        state_observation_probabilities[state][observation] = int(weight) #Set observation's weights

    for state_observation_probability in state_observation_probabilities:
        totals = sum(state_observation_probabilities[state_observation_probability].values()) #Total weights for specific state
        for observation in state_observation_probabilities[state_observation_probability]:
            state_observation_probabilities[state_observation_probability][observation] = state_observation_probabilities[state_observation_probability][observation]/totals #Calculate probability 
    return state_observation_probabilities

def calculate_transition_probabilities(): #Need to account for missing data later
    state_transition_weights,unique_states,unique_actions,default_value = read_state_action_state_weights()
    temp_probabilities = {}
    transition_probabilities = {}

    for state_and_transition in state_transition_weights:
        curr_state,transition,next_state,weight = state_and_transition.split()
        curr_state = curr_state.strip('"') #Remove quotation marks
        transition = transition.strip('"')
        next_state = next_state.strip('"')
        given = (curr_state,transition) #Used as a key for the dictionary
        if given not in temp_probabilities:
            temp_probabilities[given] = {}
        temp_probabilities[given][next_state] = int(weight)

    for given,next_state in temp_probabilities.items():
        totals = sum(next_state.values())
        transition_probabilities[given] = {nexts: weight / totals for nexts, weight in next_state.items()} #Calculate probabilities

    return transition_probabilities

def main():
    state_probabilities = calculate_state_probabilities()
    state_observation_probabilities = calculate_state_observation_probabilities()
    state_transition_probabilities = calculate_transition_probabilities()
    all_states = [state for state in state_probabilities]
    print("All States", all_states)
    print("State Probabilities", state_probabilities)
    print("State Observation Probabilities", state_observation_probabilities)
    print("State Transition Probabiltiies", state_transition_probabilities)

if __name__ == "__main__":
    main()