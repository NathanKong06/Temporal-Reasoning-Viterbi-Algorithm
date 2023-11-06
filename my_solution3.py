answer = []

def read_state_weights():
    data = []
    with open("state_weights.txt","r") as f:
        _ = f.readline() #Ignore first line
        state_and_weights = f.readline() 
        state_and_weights = state_and_weights.split()
        num_states = state_and_weights[0]
        for _ in range(int(num_states)):
            line = f.readline().strip() #Remove new line symbols
            data.append(line)
    return data

def read_state_action_state_weights():
    data = []
    with open("state_action_state_weights.txt","r") as f:
        _ = f.readline() #Ignore first line
        infos = f.readline()
        num_triplets,num_unique_states,num_unique_actions,default_weights = infos.split()
        for _ in range(int(num_triplets)):
            line = f.readline().strip() #Remove new line symbols
            data.append(line)
    return data,num_unique_states,num_unique_actions,default_weights

def read_state_observation_weights():
    data = []
    with open("state_observation_weights.txt","r") as f:
        _ = f.readline() #Ingore first line
        infos = f.readline()
        num_pairs,num_unique_states,num_unique_observations,default_weights = infos.split()
        for _ in range(int(num_pairs)):
            line = f.readline().strip() #Remove newline symbols
            data.append(line)
    return data,num_unique_states,num_unique_observations,default_weights

def read_observation_actions():
    data = []
    with open("observation_actions.txt","r") as f:
        _ = f.readline() #Ignore first line
        num_pairs = f.readline()
        for _ in range(int(num_pairs)):
            line = f.readline().strip() #Remove newline symbols
            data.append(line)
    return data

def write_output(output):
    with open("states.txt","w") as f:
        f.write("states\n")
        f.write(str(len(output)) + "\n")
        for index,_ in enumerate(output):
            f.write("\"" + output[index] + "\"") #Add quotation marks and value
            if index != len(output) -1: #Do not write newline to last line
                f.write("\n")

def calculate_state_probabilities():
    state_weights = read_state_weights()
    state_probabilities = {}
    total_weight = 0
    for state_and_weight in state_weights:
        state,weight = state_and_weight.split()
        state = state.strip('"') #Remove quotation marks
        weight = int(weight)
        total_weight = total_weight + weight #Track total weight
        state_probabilities[state] = weight #Set the weight for the corresponding state

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

def calculate_start_position(state_probabilities,state_observation_probabilities,observation_actions,all_states):
    start_state = "" 
    start_observation = observation_actions[0]
    best_value = -100000
    for state in all_states: #Calculate Start -> Every State
        value = state_probabilities[state] * state_observation_probabilities[state][start_observation] #P(State)*P(Observation|State)
        if value > best_value: #Track best state
            start_state = state
            best_value = value
        
    answer.append(start_state)
    return start_state,best_value

def calculate_hidden_states(curr_state,curr_value,curr_index,state_observation_probabilities,state_transition_probabilities,observation_actions,all_states):
    if curr_index == len(observation_actions): #Done iterating through observations and actions
        return 0
    next_state = ""
    action_observation = observation_actions[curr_index]
    action,observation = action_observation.split()
    best_value = -100000
    for state in all_states: #Calculate Current State -> Every other state
        value = curr_value * state_observation_probabilities[state][observation] * state_transition_probabilities[curr_state,action][state] #Previous Value * P(Observation | State) * P(Next State | State, Action)
        if value > best_value: #Track best state
            best_value = value
            next_state = state
    answer.append(next_state)
    calculate_hidden_states(next_state,best_value,curr_index+1,state_observation_probabilities,state_transition_probabilities,observation_actions,all_states) #Recursively calculate every step

def change_format_observation_action():
    observation_actions = read_observation_actions() #Looks like ['"Apple" "Turnaround"', '"Apple" "Forward"', '"Volcano"']
    observation_actions = [' '.join(observation_actions)] #Looks like ['"Apple" "Turnaround" "Apple" "Forward" "Volcano"']
    observation_actions = observation_actions[0].split() #Looks like ['"Apple"', '"Turnaround"', '"Apple"', '"Forward"', '"Volcano"']
    observation_actions = [observation_actions[0]] + [observation_actions[i] + " " + observation_actions[i+1] for i in range(1, len(observation_actions), 2)] #Looks like ['"Apple"', '"Turnaround" "Apple"', "Forward" "Volcano"']
    observation_actions = [action.replace('"', '') for action in observation_actions] #Remove quotation marks
    return observation_actions

def main():
    state_probabilities = calculate_state_probabilities()
    state_observation_probabilities = calculate_state_observation_probabilities()
    state_transition_probabilities = calculate_transition_probabilities()
    all_states = [state for state in state_probabilities]
    observation_actions = change_format_observation_action()
    start_state,start_state_value = calculate_start_position(state_probabilities,state_observation_probabilities,observation_actions,all_states)
    calculate_hidden_states(start_state,start_state_value,1,state_observation_probabilities,state_transition_probabilities,observation_actions,all_states)
    write_output(answer)

if __name__ == "__main__":
    main()