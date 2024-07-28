# data processsing similarly implemented from the refactoring candidate identification from lab 6 
#(https://git.cs.dal.ca/courses/2024-winter/csci4130-6314/tutorials/lab-6-refactoring-candidate-identification/-/blob/main/src/dataprocessing/data.py?ref_type=heads)

import subprocess
import os
import threading
import time
import json
import logging
import sys
import concurrent.futures


def generate_repository_details(input_file, start_index=0, end_index=None):
    '''Generate repository details in a specified range from the input file'''
    with open(input_file, 'r', errors='ignore') as f: #pylint: disable=unspecified-encoding
        data = json.load(f)
        items = data.get('items', [])
        if end_index is None:
            end_index = len(items)
        for i in range(start_index, min(end_index, len(items))):
            yield items[i]


lock = threading.Lock()

def process_repositories(item):
    '''Process the repository'''
    GITHUB_BASE_URL = "https://github.com/"
    # GITHUB_BASE_URL= "git@github.com:"
    name = item.get('name')
    repository_name = name.split('/')[-1]
    default_branch = item.get('defaultBranch')

    jar_path = os.path.join(os.getcwd(),"resources","extract-variable-extractor-1.0-jar-with-dependencies.jar")
    output_path = os.path.join(os.getcwd(),"data","output", "backup", repository_name+".jsonl")
    repo_url = f"{GITHUB_BASE_URL}{name}.git"

    os.makedirs(os.path.join(os.getcwd(),"data","output","logs"),exist_ok=True)
    log_file = os.path.join(os.getcwd(),"data","output","logs", "log.txt")
    logging.basicConfig(filename=log_file, level=logging.INFO)
    print("default branch: ", default_branch)
    print("repo url: ", repo_url)
    print("processing %s", name)
    try:
        result = subprocess.run(['java','-jar',jar_path,repo_url,output_path,default_branch],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        with lock:
            if result.returncode == 0:
                logging.info("Successfully processed %s", name)
                print("Successfully processed %s", name)
            else:
                logging.error(result.stderr.decode())
    except subprocess.CalledProcessError as e:
        with lock:
            logging.error(e.stderr.decode())
        return {"result":e.returncode, "name":name}

    return {"result":result.returncode, "name":name}

if __name__=="__main__":

    print("Start processing")
    ti = time.time()
    input_file_path = sys.argv[1]
    json_file_path = os.path.join(os.getcwd(), input_file_path)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        repository_generator = generate_repository_details(json_file_path, 86, 116)
        output = executor.map(process_repositories, repository_generator)

    output_file_path = os.path.join(os.getcwd(), "data", "output", "output.json")

    with open(output_file_path, 'w') as fp:
        json.dump(list(output), fp)

    print("Time taken: ", time.time()-ti)

    print("Output saved as:", output_file_path)


# python src\dataprocessing\data.py M:\Data\Dal\Term2\ML\Lab\lab-6-refactoring-candidate-identification\data\input\result11.json