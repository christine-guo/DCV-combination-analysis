import json
import attacksAnalysis as aa
import os
import concurrent.futures
from itertools import combinations

# download the data
def openFiles(ggp_file, om_file):
    with open(ggp_file, 'r') as file:
        ggp_data = json.load(file)
    with open(om_file, 'r') as file:
        om_data = json.load(file)

    return[ggp_data, om_data]

# re-format the data into attack pairs
def formatData(files):
    data = []
    for jsonFile in files:
        attackDict = {}
        for attacker in jsonFile:
            for victim in jsonFile[attacker]:
                attackDict[(attacker, victim)] = jsonFile[attacker][victim]
        data.append(attackDict)
    return data


files = openFiles('ggp_results.json', 'om_results.json')
ggp, om = formatData(files)


def run_multiple_deployments():
    results = {}  
    # arguments for each deployment call 
    args_list = [
        (ggp, 'gca-p', 2, 7),
        (ggp, 'gca-p', 2, 6),  
        (ggp, 'gca-p', 1, 5),
        (om, 'mpic', 2, 7),
        (om, 'mpic', 2, 6),
        (om, 'mpic', 1, 5)
    ]

    # run each call in parallel
    Use ProcessPoolExecutor to parallelize the calls to bestDeployments
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(aa.bestDeployments, *args)
            for args in args_list
        ]
        
        results = [future.result() for future in futures]

    return results


print('Finding Best Sets from Each')


# run the parallel function calls
all_results = run_multiple_deployments()

if __name__ == '__main__':

    # print the results
    with open('results.txt', 'w') as f:
        for result in all_results:
            f.write(str(result) + '\n')
