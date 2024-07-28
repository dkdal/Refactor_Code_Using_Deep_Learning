import os
import subprocess
import requests

import re
import csv

import re
import subprocess

from git import Repo
import git

import subprocess
import time
import base64
import sys
import json
import ast
import random

# Increase the field size limit
# csv.field_size_limit(sys.maxsize)

GITHUB_ACCESS_TOKEN = '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'
GIT_FILE_LIMIT = 30


def find_constant_declaration(content, constant_name):
    # Check if the constant declaration is present in the content
    pattern = re.compile(r'\b(?:final\s+)?\w+\s+' + constant_name + r'\s*(?:=\s*[^;]+)?\s*;')
    
    # Store the lines where the constant declaration is found
    found_lines = [line.strip() for line in content.split('\n') if pattern.search(line)]

    return found_lines

def get_git_differences(commit_sha, repo_full_name):
    # Get the diff using GitHub API
    url = f"https://api.github.com/repos/{repo_full_name}/commits/{commit_sha}"
    headers = {
        'Authorization': f'Token {GITHUB_ACCESS_TOKEN}',
    }

    # Send the request
    response = requests.get(url, headers=headers)
    # response = requests.get(url)
    processed_entries = set()
    if response.status_code != 200:
        return None

    commit_data = response.json()
    
    differences = []
    print("file count is: ", len(commit_data.get('files', [])))
    files = commit_data.get('files', [])

    for file_data in files[:GIT_FILE_LIMIT]:
        if file_data.get('filename', '').endswith('.java'):
            differences.append((file_data.get('filename', '')))                

    # Filter differences based on your conditions
    filtered_differences = []
    for file_path in differences:
        entry_key = (commit_sha, file_path)
        if entry_key not in processed_entries:
            processed_entries.add(entry_key)
            after_file_content = get_file_content_at_commit(commit_sha, file_path, repo_full_name, '')
            if after_file_content is not None:
                with_magic_number = introduce_magic_numbers_java(after_file_content)
                if with_magic_number is not None:
                    filtered_differences.append((file_path, with_magic_number, after_file_content))

    return filtered_differences
    # return []

def introduce_magic_numbers_java(input_code):
    # Regular expression to match Java constant declarations with assigned values, including comments
    constant_declaration_pattern = re.compile(r'(?:(?:\s*//.)*(?:private|protected|public)\s+(?:static\s+)?\s*final\s+(?:int|double|float|long|short|byte)\s+(\w+)\s*=\s*([^;]+)\s*;.*?\n)')

    # Find the first constant declaration in the Java code
    match = constant_declaration_pattern.search(input_code)

    if match:
        print(match)
        # Extract constant type, name, and its assigned value from the match
        constant_name, constant_value = match.groups()

        # Check if the assigned value is a primitive type or String
        if not constant_value.startswith("("):
            # Remove only the first constant declaration line that has been replaced
            input_code = re.sub(fr'{re.escape(match.group(0))}', '\n', input_code, count=1)
            # Check if the constant is used anywhere else in the class
            if re.search(fr'\b{constant_name}\b', input_code):
                # Replace all occurrences of the constant with a variable throughout the code
                # Replace all occurrences of the constant with its value throughout the code
                input_code = re.sub(fr'\b{constant_name}\b', constant_value, input_code)

                return input_code

    return None

class ConstantReplacement(ast.NodeTransformer):
    def __init__(self, constant_name, constant_value):
        self.constant_name = constant_name
        self.constant_value = constant_value
        self.replace_first_occurrence = True

    def visit_Assign(self, node):
        if self.replace_first_occurrence:
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == self.constant_name:
                    self.replace_first_occurrence = False
                    return ast.Assign(targets=[target], value=ast.NameConstant(value=self.constant_value))
        return node

def get_file_content_at_commit(commit_sha, file_path, repo_full_name, suffix):
    url = f"https://api.github.com/repos/{repo_full_name}/contents/{file_path}?ref={commit_sha}{suffix}"
    # print("get content url", url)

    headers = {
        'Authorization': f'Token {GITHUB_ACCESS_TOKEN}',
    }
    print("url is", url)
    # Send the request
    response = requests.get(url, headers=headers)
    # print("response code", response.status_code)

    if response.status_code == 200:
        file_data = response.json()
        file_content = base64.b64decode(file_data['content'])
        file_content_str = file_content.decode('utf-8')  # Decode using the appropriate character encoding
        # print("content", file_content_str)
        return file_content_str
    else:
        print(response.text)  # Print the response text for further debugging
        return None

def remove_comments(content):
    # Remove block comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Remove line comments
    content = re.sub(r'//.*', '', content)
    
    return content
def find_replacement_constant(before_content, after_content):
    # Find the replacement constant introduced in the "after" content
    magic_positions = []

    # Identify the positions of magic numbers in the "before" content
    for i, before_line in enumerate(before_content):
        stripped_before_line = before_line.strip()  # Strip leading and trailing spaces
        if re.search(r'\b\d+\b', stripped_before_line):
            magic_positions.append(i)

    # Check the corresponding positions in the "after" content for the presence of a constant
    for position in magic_positions:
        if position < len(after_content):
            magic_number = re.search(r'\b(\d+)\b', before_content[position]).group()
            stripped_after_line = after_content[position].strip()  # Strip leading and trailing spaces
            if magic_number in stripped_after_line:
                match = re.search(r'\b(?:[A-Z_]+)\b', stripped_after_line)
                if match:
                    constant_name = match.group().strip()  # Trim leading and trailing spaces
                    print(f"Magic number {magic_number} is replaced by constant {constant_name}")
                    return constant_name

    return None

def replace_newlines_with_placeholder(text):
    return text.replace('\n', '<newline>')

def replace_placeholder_with_newlines(text):
    return text.replace('<newline>', '\n')

def write_to_csv(commits, csv_filename):
    fieldnames = ['Commit SHA', 'Commit Message', 'File Path', 'Before Content', 'After Content']

    # Check if the CSV file already exists
    file_exists = os.path.exists(csv_filename)

    with open(csv_filename, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header only if the file is created in this call
        if not file_exists:
            writer.writeheader()

        processed_entries = set()

        for commit_info in commits:
            commit_sha = commit_info['sha']
            commit_message = commit_info['message']

            for file_info in commit_info['differences']:
                file_path, before_content, after_content = file_info
                entry_key = (commit_sha, file_path, tuple(before_content), tuple(after_content))

                # Check if the entry has been processed before
                if entry_key in processed_entries:
                    continue

                writer.writerow({
                    'Commit SHA': commit_sha,
                    'Commit Message': commit_message,
                    'File Path': file_path,
                    'Before Content': before_content,
                    'After Content': after_content
                })

                processed_entries.add(entry_key)

    print(f"Data written to {csv_filename}")

def write_to_jsonl(commits, jsonl_filename):
    processed_entries = set()

    with open(jsonl_filename, mode='a', newline='', encoding='utf-8') as jsonlfile:
        for commit_info in commits:
            commit_sha = commit_info['sha']
            # commit_message = commit_info['message']

            for file_info in commit_info['differences']:
                file_path, before_content, after_content = file_info
                entry_key = (commit_sha, file_path, tuple(before_content), tuple(after_content))

                # Check if the entry has been processed before
                if entry_key in processed_entries:
                    continue

                entry_data = {
                    # 'Commit SHA': commit_sha,
                    # 'Commit Message': commit_message,
                    # 'File Path': file_path,
                    'before': before_content,
                    'after': after_content
                }

                # Write each entry as a JSON object on a new line
                jsonlfile.write(json.dumps(entry_data) + '\n')

                processed_entries.add(entry_key)

    # print(f"Data written to {jsonl_filename}")
    

def read_jsonl(jsonl_filename):
    with open(jsonl_filename, mode='r', encoding='utf-8') as jsonlfile:
        # Read the first line from the JSONL file
        first_line = jsonlfile.readline().strip()

        # Check if the first line is not empty before attempting to parse
        if first_line:
            # Parse the JSON data from the first line
            first_row = json.loads(first_line)
            return first_row
        else:
            # Handle the case where the first line is empty
            print("The JSONL file is empty.")
            return None
def print_jsonl(jsonl_filename) :
    first_row = read_jsonl(jsonl_filename)
    if first_row is not None:
        print("First Row:")
        print(first_row)

def read_csv(csv_filename):
    if not os.path.exists(csv_filename):
        print(f"Error: {csv_filename} does not exist.")
        return

    with open(csv_filename, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Print header
        print("CSV Header:", reader.fieldnames)

        # Print content row-wise
        for row in reader:
            print("\nRow:")
            for key, value in row.items():
                print(f"{key}: {value}")

def read_csv_repo_set(file_path):
    result_list = []

    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)

        # Skip header if present
        next(reader, None)

        for row in reader:
            repo_name = row[0].strip()
            sha_ids = [sha.strip() for sha in row[1].split(';') if sha.strip()] if len(row) > 1 else []

            result_list.append((repo_name, sha_ids))

    return result_list


def get_java_repositories_with_commits(keywords, stars_threshold=50):
    repositories_data = ['apache/jmeter']


    # Step 2: Get commits for each Java repository
    commits_with_magic_number = []
    print("repository data", repositories_data)

    for repository_data in repositories_data:
        # repository_full_name = repository_data['full_name']
        commits_url = f'https://api.github.com/repos/{repository_data}/commits'
        commits_params = {
            'q': f'message:"{" ".join(keywords)}"',
            'per_page': 3  # Adjust as needed
        }

        commits_response = requests.get(commits_url, params=commits_params)
        commits_response.raise_for_status()
        commits_data = commits_response.json()

        for commit_data in commits_data:
            commit_message = commit_data['commit']['message'].lower()
            if all(keyword.lower() in commit_message for keyword in keywords):
                commits_with_magic_number.append({
                    'repository': repository_data,
                    'sha': commit_data['sha'],
                    'message': commit_message,
                    'author': commit_data['commit']['author']['name'],
                    'date': commit_data['commit']['author']['date'],
                })

    return commits_with_magic_number
def clone_or_open_repo(repo_name, repository_full_name, repo_path):
    try:
        
        if os.path.exists(repo_path+"/"+repo_name):
            # repo = Repo(repo_path)
            print("already exists")
        else:
            Repo.clone_from(f'https://github.com/{repository_full_name}.git', repo_path+"/"+repo_name)
    except:
        print("something went wrong...", repo_name)
    
    # return repo

# Final
def get_commits_with_magic_number(repository_full_name, keywords):

    
    # Create the search query
    search_query = f'repo:{repository_full_name}+{"+".join(keywords)}'

    # GitHub Search API endpoint for commits
    search_url = f'https://api.github.com/search/commits?q={search_query}'

    # Add the access token to the headers if provided
    headers = {
        'Authorization': f'Token {GITHUB_ACCESS_TOKEN}',
    }

    # response = requests.get(search_url, headers=headers)

    # Send the request
    response = requests.get(search_url, headers=headers)

    response.raise_for_status()
    commits_data = response.json()
    print("commitsData in", commits_data.get('items'))
    # Use a unique temporary directory for each clone
    # repo = clone_or_open_repo(repository_full_name)

    commits_with_differences = []
    for commit_data in commits_data.get('items'):
        commit = commit_data.get('commit')
        commit_message = ""
        if commit is not None:
            commit_message = commit.get('message')
        # if all(keyword.lower() in commit_message for keyword in keywords):
        commit_sha = commit_data.get('sha')
        print("sha:", commit_sha)
        differences = get_git_differences(commit_sha, repository_full_name)
        # magic_number_refactoring_changes = filter_magic_number_refactoring_changes(differences)
        # if magic_number_refactoring_changes:
        commits_with_differences.append({
            'sha': commit_sha,
            'message': commit_message,
            'differences': differences,
            'date': commit.get('committer').get('date'),
        })

    return commits_with_differences

def get_data_with_magic_number(repo_with_sha):

    commits_with_differences = []
    repo_full_name = repo_with_sha[0]
    print(f"preparing the dataset for the repo {repo_full_name}")
    for sha_id in repo_with_sha[1]:
        differences = get_git_differences(sha_id, repo_full_name)
        if differences is not None:
            commits_with_differences.append({
                'sha': sha_id,
                'differences': differences,
            })
        else:
            print("nothing to prepare")

    print(f"dataset prepared for the repo {repo_with_sha[0]}")
    return None if len(commits_with_differences) == 0 else commits_with_differences


    return commits_with_differences

def get_repo_names_from_csv(csv_filename):
    repo_names = []

    with open(csv_filename, mode='r', newline='', encoding='latin-1') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            # Assuming the column name is 'name', modify it if needed
            repo_name = row['FullName']
            repo_names.append(repo_name)

    return repo_names

def get_repos_with_magic_number(repos, keywords, csv_filepath, csv_without_path):
    existing_repos = get_existing_repo_names(csv_filepath)
    existing_non_repos = get_existing_repo_names(csv_without_path)
    print("existing_non_repos", existing_non_repos)
    # repo_names = get_repo_names_from_csv()
    headers = {
        'Authorization': f'Token {GITHUB_ACCESS_TOKEN}',
    }

    repos_with_magic_number = {}
    repos_without_magic_number = set()

    try:
        for repo in repos:
            if (repo not in existing_repos) and (repo not in existing_non_repos):
                search_query = f'repo:{repo}+{"+".join(keywords)}'
                search_url = f'https://api.github.com/search/commits?q={search_query}'

                response = requests.get(search_url, headers=headers)
                if response.status_code == 422:
                    print("Error occured: ", repo)
                    continue
                commits_data = response.json()
                # print("commits_data", commits_data.get('items'))
                if commits_data.get('items') is not None and len(commits_data.get('items')) > 0:

                    sha_ids = [commit['sha'] for commit in commits_data.get('items')]
                    sha_ids_str = ';'.join(sha_ids)

                    print(f"{repo}: added ({len(sha_ids)} SHA IDs)")
                    repos_with_magic_number[repo] = sha_ids_str
                else:
                    repos_without_magic_number.add(repo)

                time.sleep(2)
            else:
                print(f"{repo} is already in list")
    finally:
        write_repos_to_csv(repos_with_magic_number, csv_filepath)
        write_unaccepted_repos_to_csv(repos_without_magic_number, csv_without_path)
        print("CSV file updated")

    return repos_with_magic_number

def write_repos_to_csv(repos, csv_filepath):
    if not repos:
        print("No repositories with magic numbers found.")
        return

    fieldnames = ['repo_name', 'sha_ids']

    # Check if the CSV file already exists
    file_exists = os.path.exists(csv_filepath)

    with open(csv_filepath, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header only if the file is created in this call
        if not file_exists:
            writer.writeheader()

        # Write repo names and SHA IDs to CSV
        writer.writerows({'repo_name': repo, 'sha_ids': sha_ids} for repo, sha_ids in repos.items())

    print(f"Repositories with magic numbers written to {csv_filepath}")

def write_unaccepted_repos_to_csv(repos, csv_filepath):
    if not repos:
        print("No repositories with magic numbers found.")
        return

    fieldnames = ['repo_name']

    # Check if the CSV file already exists
    file_exists = os.path.exists(csv_filepath)

    with open(csv_filepath, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header only if the file is created in this call
        if not file_exists:
            writer.writeheader()

        # Write repo names to CSV
        writer.writerows({'repo_name': repo} for repo in repos)

    print(f"Repositories with magic numbers written to {csv_filepath}")

def get_existing_repo_names(csv_filepath):
    existing_repo_names = set()

    if not os.path.exists(csv_filepath):
        return existing_repo_names

    with open(csv_filepath, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            existing_repo_names.add(row['repo_name'])

    return existing_repo_names

def filter_magic_number_refactoring_changes(differences):
    magic_number_refactoring_changes = []
    
    for file_info in differences:
        file_path, before_content, after_content = file_info
        
        # Add custom logic to identify changes involving magic number refactoring
        if is_magic_number_refactoring(before_content, after_content):
            magic_number_refactoring_changes.append((file_path, before_content, after_content))
    
    return magic_number_refactoring_changes

def is_magic_number_refactoring(before_content, after_content):
    # Custom logic to identify magic number refactoring changes
    # Check if a numeric value in before_content is replaced with a variable in after_content
    
    before_str = ' '.join(before_content)
    after_str = ' '.join(after_content)

    # Extract numeric values from before_content
    before_numbers = [token for token in before_str.split() if token.isdigit()]

    # Check if any numeric value in before_content is replaced with a variable in after_content
    for number in before_numbers:
        if number in after_str and after_str.split().count(number) == 1:
            return True

    return False



def get_commits_with_keywords_global_search(keywords):
    url = 'https://api.github.com/search/commits'

    params = {'q': 'magic+number+language:java+stars:>=50 in:commit', 'per_page': 100}  # Adjust as needed


    response = requests.get(url, params=params)
    response.raise_for_status()

    commits_data = response.json().get('items', [])

    commits_with_keywords = []

    for commit_data in commits_data:
        commit_message = commit_data['commit']['message'].lower()
        if all(keyword.lower() in commit_message for keyword in keywords):
            commits_with_keywords.append({
                'sha': commit_data['sha'],
                'message': commit_message,
                'author': commit_data['commit']['author']['name'],
                'date': commit_data['commit']['author']['date'],
                'repository': commit_data['repository']['full_name'],
            })

    return commits_with_keywords

def find_magic_numbers(code):
    # Match any numeric literals
    magic_number_pattern = re.compile(r'\b\d+(\.\d+)?\b')
    return magic_number_pattern.findall(code)

def refactor_magic_numbers(code, magic_numbers):
    for magic_number in magic_numbers:
        # Your refactoring logic here (replace with named constants, etc.)
        refactored_number = f"CONST_{magic_number}"
        code = code.replace(magic_number, refactored_number)

    return code

def format_java_code(code):
    # Use an external tool like google-java-format for code formatting
    formatted_code = subprocess.run(
        ['google-java-format', '-'],
        input=code.encode('utf-8'),
        stdout=subprocess.PIPE,
        text=True
    ).stdout.strip()

    return formatted_code

def process_java_file(input_file, output_csv):
    with open(input_file, 'r', encoding='utf-8') as file:
        java_code = file.read()

    # Find magic numbers
    magic_numbers = find_magic_numbers(java_code)

    if magic_numbers:
        # Refactor magic numbers
        refactored_code = refactor_magic_numbers(java_code, magic_numbers)

        # Format the refactored code
        formatted_code = format_java_code(refactored_code)

        # Save results to CSV
        with open(output_csv, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['Before Refactoring', 'After Refactoring'])
            csv_writer.writerow([java_code, formatted_code])

        print(f"Magic numbers found and refactored. Results saved in {output_csv}")
    else:
        print("No magic numbers found in the Java code.")

def download_repo(repo_name, repos_base_path):
    repo_fullname = repo_name.strip('\n')
    if not repo_fullname == "":
        project_url = "https://github.com/" + repo_fullname + ".git"
        folder_name = repo_fullname.replace("/", "_")
        folder_path_new = os.path.join(repos_base_path, folder_name)

        if not os.path.exists(folder_path_new):
            _download_with_url(project_url, folder_path_new)
        else:
            print(folder_name + " already exists. skipping ...")


def _download_with_url(project_url, folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    print("cloning... " + project_url)
    try:
        # depth=1 is only to get the current snapshot (rather than all commits)
        subprocess.call(["git", "clone", "--depth=1", project_url, folder_path])
    except Exception as ex:
        print("Exception occurred!!" + str(ex))
        return
    print("cloning done.")


def search_commits_with_keywords(repository_name, keywords):
    access_token = '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'

    # Create the search query
    search_query = f'repo:{repository_name}+{"+".join(keywords)}'

    # GitHub Search API endpoint for commits
    search_url = f'https://api.github.com/search/commits?q={search_query}'

    # Add the access token to the headers if provided
    headers = {}
    if access_token:
        headers['Authorization'] = f'Bearer {access_token}'

    # Send the request
    response = requests.get(search_url, headers=headers)

    # Check the status code
    if response.status_code == 200:
        commits_data = response.json()
        return commits_data.get('items', [])  # Extract the 'items' list from the response
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return []
    
def get_random_records(jsonl_file, num_records=5):
    random_records = []

    with open(jsonl_file, 'r') as file:
        # Read each line from the JSONL file
        lines = file.readlines()
        
        # Shuffle the lines randomly
        random.shuffle(lines)

        # Iterate through the first 'num_records' lines and parse them as JSON
        for line in lines[:num_records]:
            record = json.loads(line)
            random_records.append(record)

    return random_records

def introduce_magic_numbers_jsonl(input_file_path, output_file_path):
    # Create a list to store modified JSON objects
    modified_records = []

    # Iterate over each line in the JSONL content
    with open(input_file_path, 'r') as file:
        for line in file:
            # Skip empty lines
            if not line.strip():
                continue

            # Parse the JSON object from the line
            data = json.loads(line)

            # Extract 'before' and 'after' fields
            # before_code = data.get('before', '')
            after_code = data.get('after', '')

            # Implement your logic to modify 'before_code' and 'after_code' as needed
            # For now, it just uses 'after_code' as 'before_code'
            modified_before_code = introduce_magic_numbers_java(after_code)
            if modified_before_code is not None:
            # Update the 'before' and 'after' fields in the JSON object
                data['before'] = modified_before_code
                data['after'] = after_code

                # Append the modified record to the list
                modified_records.append(data)

    # Write the modified records to the new JSONL file
    with open(output_file_path, 'w') as output_file:
        for modified_record in modified_records:
            output_file.write(json.dumps(modified_record) + '\n')

def iterate_java_files(directory_path):
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        print("Invalid directory path")
        return
    filtered_differences = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".java"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r") as f:
                        after_file_content = f.read()
                        with_magic_number = introduce_magic_numbers_java(after_file_content)
                        if with_magic_number is not None:
                            filtered_differences.append((file_path, with_magic_number, after_file_content))
                        # Do something with the processed content
                        # print(processed_content)
                except Exception as e:
                    print("Error processing file:", file_path, "-", e)

    return filtered_differences

def insert_java_files(data, jsonl_filename):
    with open(jsonl_filename, mode='a', newline='', encoding='utf-8') as jsonlfile:
        for file_info in data:
            file_path, before_content, after_content = file_info

            entry_data = {
                'before': before_content,
                'after': after_content
            }

            # Write each entry as a JSON object on a new line
            jsonlfile.write(json.dumps(entry_data) + '\n')

def generate_repository_details(input_file, start_index=0, end_index=None):
    '''Generate repository details in a specified range from the input file'''
    with open(input_file, 'r', errors='ignore') as f: #pylint: disable=unspecified-encoding
        data = json.load(f)
        items = data.get('items', [])
        if end_index is None:
            end_index = len(items)
        for i in range(start_index, min(end_index, len(items))):
            yield items[i]