answer = []
time_transition_list = []

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

def calculate_missing_state_observations(state_observation_weights,unique_observations,state_check): #Calculate how many lines are missing for a specific state for state observations
    unique_observations = int(unique_observations)
    counter = 0
    for element in state_observation_weights: #For every state that is present in state_observation_weights.txt
        state,_,_ = element.split()
        if state.strip('"') == state_check: #Count how many times it appears
            counter = counter + 1
        if counter == unique_observations: #Exit if all state observations are found already
            return 0
    return unique_observations - counter #Calculate how many missing elements for that state there are

def calculate_state_observation_probabilities():
    state_observation_weights,_,unique_observations,default_value = read_state_observation_weights()
    state_observation_probabilities = {}
    state_and_totals = {}

    for state_and_observation_weight in state_observation_weights:
        state,observation,weight = state_and_observation_weight.split()
        state = state.strip('"') #Remove quotation marks
        observation = observation.strip('"') #Remove quotation marks
        if state not in state_observation_probabilities:
            state_observation_probabilities[state] = {} #Create dictionary for every state
        state_observation_probabilities[state][observation] = int(weight) #Set observation's weights

    for state_observation_probability in state_observation_probabilities:
        totals = sum(state_observation_probabilities[state_observation_probability].values()) + (calculate_missing_state_observations(state_observation_weights,unique_observations,state_observation_probability) * int(default_value)) #Total weights for specific state
        state_and_totals[state_observation_probability] = totals #Keep track of total weights for states
        for observation in state_observation_probabilities[state_observation_probability]:
            state_observation_probabilities[state_observation_probability][observation] = state_observation_probabilities[state_observation_probability][observation]/totals #Calculate probability 
    return state_observation_probabilities,default_value,state_and_totals,unique_observations

def calculate_missing_transitions(state_transition_weights,unique_states,unique_actions,given):
    unique_states = int(unique_states)
    unique_actions = int(unique_actions)
    counter = 0
    for element in state_transition_weights: #For every state and action that is present in state_action_state_weights.txt
        curr_state,action,_,_ = element.split()
        if curr_state.strip('"') == given[0] and action.strip('"') == given[1]: #Count how many times it state and action appears
            counter = counter + 1
        if counter == unique_actions: #Exit if all state and actions are found already
            return 0
    return unique_actions - counter #Calculate how many missing elements for that state and action there are

def calculate_transition_probabilities():
    state_transition_weights,unique_states,unique_actions,default_value = read_state_action_state_weights()
    default_value = int(default_value)
    temp_probabilities = {}
    transition_probabilities = {}
    state_action_totals = {}

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
        totals = sum(next_state.values()) + (calculate_missing_transitions(state_transition_weights,unique_states,unique_actions,given) * default_value)
        state_action_totals[given] = totals
        transition_probabilities[given] = {nexts: weight / totals for nexts, weight in next_state.items()} #Calculate probabilities

    return transition_probabilities,default_value,state_action_totals,unique_states

def calculate_start_position(state_probabilities,state_observation_probabilities,observation_actions,all_states,state_observation_default,state_and_totals,unique_observations):
    start_observation = observation_actions[0]
    state_observation_default = int(state_observation_default)
    start_state_values = {}
    for state in all_states: #Calculate Start -> Every State

        if state not in state_observation_probabilities: #If a state is not in the state_observation_weights.txt file
            state_observation_probabilities[state] = {}
        if state not in state_and_totals: #If a state is not in the state_observation_weights.txt file calcluate its total (All observations are default weights)
            state_and_totals[state] = int(unique_observations) * state_observation_default
        if start_observation not in state_observation_probabilities[state]: #If observation not in state_observation_weights.txt for that state, calculate probability
            state_observation_probabilities[state][start_observation] = state_observation_default/state_and_totals[state]

        value = state_probabilities[state] * state_observation_probabilities[state][start_observation] #P(State)*P(Observation|State)
        start_state_values[state] = value

    return start_state_values

def calculate_hidden_states(start_state_values,curr_index,state_observation_probabilities,state_transition_probabilities,observation_actions,all_states,state_observation_default,state_and_totals,unique_observations,state_action_default,state_action_totals,unique_states):
    if curr_index == len(observation_actions): 
        return
    action_observation = observation_actions[curr_index]
    action,observation = action_observation.split() #Current Action and Observation
    state_action_default = int(state_action_default)
    state_transition_list = []

    for next_state in all_states:
        best_transition_value = -100000
        best_transition = ""
        for curr_state in all_states:
            if next_state not in state_observation_probabilities:
                state_observation_probabilities[next_state] = {}
            if next_state not in state_and_totals: 
                state_and_totals[next_state] = int(unique_observations) * state_observation_default
            if observation not in state_observation_probabilities[next_state]:
                state_observation_probabilities[next_state][observation] = int(state_observation_default)/state_and_totals[next_state]

            if (curr_state,action) not in state_transition_probabilities:
                state_transition_probabilities[curr_state,action] = {}
            if (curr_state,action) not in state_action_totals:
                state_action_totals[curr_state,action] = int(unique_states) * state_action_default
            if next_state not in state_transition_probabilities[curr_state,action]:
                state_transition_probabilities[curr_state,action][next_state] = state_action_default/state_action_totals[curr_state,action] #Default probability

            value = start_state_values[curr_state] * state_observation_probabilities[next_state][observation] * state_transition_probabilities[curr_state,action][next_state] #Previous Value * P(Observation | State) * P(Next State | State, Action)
            if value > best_transition_value: #Track Best Transition at this level and value
                best_transition_value = value
                best_transition = (curr_state,next_state)

        state_transition_list.append((best_transition,best_transition_value))  #At this time, track best transitions (len(state_transition) == unique_states)
    time_transition_list.append(state_transition_list)
    for state_transition in state_transition_list:
        start_state_values[state_transition[0][1]] = state_transition[1] #Update the start_state_values to the max values at this time
    calculate_hidden_states(start_state_values,curr_index+1,state_observation_probabilities,state_transition_probabilities,observation_actions,all_states,state_observation_default,state_and_totals,unique_observations,state_action_default,state_action_totals,unique_states)
    
def change_format_observation_action():
    observation_actions = read_observation_actions() #Looks like ['"Apple" "Turnaround"', '"Apple" "Forward"', '"Volcano"']
    observation_actions = [' '.join(observation_actions)] #Looks like ['"Apple" "Turnaround" "Apple" "Forward" "Volcano"']
    observation_actions = observation_actions[0].split() #Looks like ['"Apple"', '"Turnaround"', '"Apple"', '"Forward"', '"Volcano"']
    observation_actions = [observation_actions[0]] + [observation_actions[i] + " " + observation_actions[i+1] for i in range(1, len(observation_actions), 2)] #Looks like ['"Apple"', '"Turnaround" "Apple"', "Forward" "Volcano"']
    observation_actions = [action.replace('"', '') for action in observation_actions] #Remove quotation marks
    return observation_actions

def backtrack_for_path():
    answer = []
    max_value = -10000
    last_two_states = ""
    for transition_data in time_transition_list[-1]: #Information at the last time
        two_states,value = transition_data
        if value > max_value: #Find the max value from the last time
            max_value = value
            last_two_states = two_states
    second_last_state,last_state = last_two_states
    prev_state = second_last_state
    answer.append(last_state) #Last 2 states in the answer
    answer.append(second_last_state)
    for data in reversed(time_transition_list[:-1]): #Backtrack
        for transitions in data:
            if transitions[0][1] == prev_state:
                prev_state = transitions[0][0]
                answer.append(prev_state)
                break #Break when you find your answer and continue backtracking
    return answer

def main():
    state_probabilities = calculate_state_probabilities()
    state_observation_probabilities,state_observation_default,state_and_totals,unique_observations = calculate_state_observation_probabilities()
    state_transition_probabilities,state_action_default,state_action_totals,unique_states = calculate_transition_probabilities()
    all_states = [state for state in state_probabilities]
    observation_actions = change_format_observation_action()
    start_state_values = calculate_start_position(state_probabilities,state_observation_probabilities,observation_actions,all_states,state_observation_default,state_and_totals,unique_observations)
    calculate_hidden_states(start_state_values,1,state_observation_probabilities,state_transition_probabilities,observation_actions,all_states,state_observation_default,state_and_totals,unique_observations,state_action_default,state_action_totals,unique_states)
    answer = backtrack_for_path()
    answer.reverse() #Reverse the answer due to backtracking
    write_output(answer)
    
if __name__ == "__main__":
    main()