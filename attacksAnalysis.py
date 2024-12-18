import concurrent.futures
from itertools import combinations
from typing import List, Tuple


AWS_REGIONS = {
    '3.26.48.107': 'ap-southeast-2', 
    '65.0.109.23': 'ap-south-1',      
    '18.193.43.217': 'eu-central-1', 
    '13.39.150.177': 'eu-west-3',    
    '3.249.92.195': 'eu-west-1',      
    '18.191.200.1': 'us-east-2',     
    '54.151.109.202': 'us-west-1',    
    '13.212.34.211': 'ap-southeast-1',
    '16.170.221.119': 'eu-north-1',  
    '13.208.34.172': 'ap-northeast-3',
    '3.34.184.164': 'ap-northeast-2',
    '54.191.71.146': 'us-west-2',   
    '99.79.9.134': 'ca-central-1'
}

GCA_PREMIUM_REGIONS = {
    "34.106.15.202": "us-west3",
    "34.124.154.125": "asia-southeast",
    "34.125.3.165": "us-west4",
    "34.131.135.215": "asia-south2",
    "34.148.238.226": "us-east1",
    "34.154.252.52": "europe-west8",
    "34.155.191.189": "europe-west9",
    "34.165.66.189": "me-west1",
    "34.169.111.162": "us-west1",
    "34.17.90.248": "europe-west12",
    "34.18.91.250": "me-central1",
    "34.28.117.49": "us-central1",
    "34.32.83.145": "europe-west10",
    "34.51.15.202": "northamerica-south1",
    "34.81.204.66": "asia-east1",
    "34.88.186.236": "europe-north1",
    "35.187.168.103": "europe-west1",
    "34.101.65.201": "asia-southeast2",
    "34.118.89.192": "europe-central2",
    "34.129.96.93": "australia-southeast2",
    "34.130.173.246": "northamerica-northeast2",
    "34.151.97.99": "australia-southeast1",
    "34.162.59.9": "us-east5",
    "34.174.120.63": "us-south1",
    "34.175.191.8": "europe-southwest1",
    "34.176.62.137": "southamerica-west1",
    "34.32.183.103": "europe-west4",
    "34.35.34.237": "africa-south1",
    "34.47.216.25": "asia-south1",
    "34.64.167.185": "asia-northeast3",
    "34.65.86.145": "europe-west6",
    "34.84.143.218": "asia-northeast1",
    "34.89.228.29": "europe-west3",
    "34.89.80.161": "europe-west2",
    "34.97.245.169": "asia-northeast2",
    "35.188.244.163": "us-east4",
    "35.203.26.123": "northamerica-northeast1",
    "35.220.224.243": "asia-east2",
    "35.236.27.133": "us-west2",
    "35.247.193.103": "southamerica-east1"
}


def calculate_resilience(results, N_Minus_Quorum, relevant_regions, type):
    if type == 'mpic':
        regions = AWS_REGIONS
    if type == 'gca-p':
        regions = GCA_PREMIUM_REGIONS

    resilience_points = 0

    for pair in results:
        count = 0
        for perspective in results[pair]:
            if perspective in relevant_regions:
                count += 1

        # check if attack succeeded based on quorum policy
        if count > N_Minus_Quorum:
            resilience_points += 1

    average_resilience = resilience_points / (32*31)
    return average_resilience



# def bestDeployments(results, type, N_Minus_Quorum: int, perspectiveSize: int) -> list:
#     all_combinations = []
#     if type == 'mpic':
#         regions = AWS_REGIONS  # Define AWS_REGIONS if necessary
#         # all_combinations = list(combinations(regions, perspectiveSize))
#     elif type == 'gca-p':
#         regions = GCA_PREMIUM_REGIONS  # Define GCA_PREMIUM_REGIONS if necessary
#         # all_combinations = list(getCombs(regions, perspectiveSize))
#     all_combinations = list(combinations(regions, perspectiveSize))

#     # Generate all combinations of regions
#     resilience_scores = []
    
#     for combination in all_combinations:
#         avg_resilience = calculate_resilience(results, N_Minus_Quorum, list(combination), type)
#         resilience_scores.append((list(combination), avg_resilience))

#     # Sort combinations by resilience value in descending order
#     resilience_scores.sort(key=lambda x: x[1], reverse=True)

#     # Return the top 10 combinations
#     return resilience_scores[:10]

# process each combination within the chunk and calculate its average resilience
def process_combinations(chunk, results, N_Minus_Quorum, type):
    resilience_scores = []
    for combination in chunk:
        avg_resilience = calculate_resilience(results, N_Minus_Quorum, list(combination), type)
        if(avg_resilience > 0.5): 
            resilience_scores.append((list(combination), avg_resilience))
    return resilience_scores

# returns the top 10 best performing combiantions 
def bestDeployments(results, type, N_Minus_Quorum: int, perspectiveSize: int) -> list:
    all_combinations = []
    if type == 'mpic':
        regions = AWS_REGIONS
    elif type == 'gca-p':
        regions = GCA_PREMIUM_REGIONS

    # generate all possible combinations
    all_combinations = list(combinations(regions, perspectiveSize))  



    # determine how to split the combinations into num_chunks
    num_chunks = 4
    chunk_size = total_combinations // num_chunks 
    # remaining combinations to distribute to each chunk
    remainder = total_combinations % num_chunks 

    chunks = []
    start_idx = 0
    for i in range(num_chunks):
        # if there is a remainder, distribute one extra combination to the chunk
        end_idx = start_idx + chunk_size + (1 if i < remainder else 0)
        chunks.append(all_combinations[start_idx:end_idx])
        start_idx = end_idx

    resilience_scores = []

    # use ProcessPoolExecutor for parallel processing
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_chunks) as executor:
        futures = []
        for chunk in chunks:
            future = executor.submit(process_combinations, chunk, results, N_Minus_Quorum, type)
            futures.append(future)

        for future in futures:
            resilience_scores.extend(future.result())  

    # sort combinations by resilience value in descending order
    resilience_scores.sort(key=lambda x: x[1], reverse=True)
    return resilience_scores[:10]
