import javalang
import os
import subprocess
from sys import exit, platform
import csv
import re

def analyze_code(folder_path, result_path, designite_path):
    print("Analyzing " + folder_path + " ...")

    # _build_java_project(folder_path)
    _run_designite_java(folder_path, result_path, designite_path)
    
def _run_designite_java(folder_path, out_path, designite_path):
    print("Analyzing ...")
    proc = subprocess.Popen(
        ["java", "-jar", designite_path, "-i", folder_path, "-o", out_path, "-d"], shell=True if platform == 'win32' else False)
    proc.wait()
    print("done analyzing.")

def check_smell(directory, smell_name):
    csv_file_path = os.path.join(directory, "implementationSmells.csv")
    
    # Check if the CSV file exists
    if os.path.exists(csv_file_path):
        with open(csv_file_path, 'r') as file:
            csv_reader = csv.DictReader(file)
            
            # Check each row for the magic number smell
            for row in csv_reader:
                if row["Implementation Smell"] == smell_name:
                    if smell_name == "Magic Number":
                        return int(row["Method start line no"]), get_last_part(row["Cause of the Smell"])
                    elif smell_name == "Long Statement":
                        return int(row["Method start line no"]), 0
    
    # Return -1 if no magic number smell found or CSV file doesn't exist
    return -1, -1

# delete all the files present in the folder
def delete_files(folder_path):
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)
    print("Deleted all files from " + folder_path)

def extract_lines_around_line(file_path, line_number, line_above, line_below):
    lines_around = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        start_index = max(0, line_number - line_above - 1)  # Starting index for the slice
        end_index = min(len(lines), line_number + line_below)  # Ending index for the slice
        lines_around = lines[start_index:end_index]  # Extract lines around the specified line
    return ''.join(lines_around)

def find_number_below_line(file_path, line_number, number_to_find):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for i in range(line_number, len(lines)):
            line = lines[i].strip()

            if str(number_to_find) in line:
                return i + 1  # Add 1 to convert from 0-indexed to 1-indexed line numbers
    return -1

def get_last_part(string):
    parts = string.split(":")
    if len(parts) > 1:
        return parts[-1].strip()
    else:
        return string.strip()
    

def get_first_line(string):
    parts = string.split(";")
    if len(parts) > 1:
        return parts[0].strip()
    else:
        return None
    
# accept the declaration of variable line in java language and return the variable name
def get_variable_name(declaration_line):
    constant_declaration_pattern = re.compile(r'(?:(?:\s*//.)*(?:private|protected|public)\s+(?:static\s+)?\s*final\s+(?:int|double|float|long|short|byte)\s+(\w+)\s*=\s*([^;]+)\s*;.*?\n)')
    match = constant_declaration_pattern.search(declaration_line)
    if match:
        constant_name, constant_value = match.groups()
        return constant_name
    return None

def extract_variable_name(declaration):
    # Regular expression pattern to match variable name
    pattern = r'\b([A-Za-z_][A-Za-z0-9_]*)\b(?=\s*(?:=|\Z))'
    # Find the last occurrence of the variable name in the declaration
    match = re.search(pattern, declaration)
    # Return the matched variable name
    if match:
        return match.group(1)
    else:
        return None

    
def replace_number_with_variable(file_content, line_number, number_to_replace, variable_name):
    # Split the file content into lines based on newline characters
    lines = file_content.splitlines()
    print("line_number: ", line_number)
    print("line_length", len(lines))
    
    # Check if the line number is valid
    if 1 <= line_number <= len(lines):
        # Find the specified line and replace the number with the variable name
        start_index = file_content.find(lines[line_number - 1])  # Find the start index of the line
        end_index = start_index + len(lines[line_number - 1])  # Find the end index of the line
        modified_line = lines[line_number - 1].replace(str(number_to_replace), variable_name)
        # Replace the line in the file content
        modified_content = file_content[:start_index] + modified_line + file_content[end_index:]
        return modified_content
    else:
        return "Invalid line number"
    

def find_method(java_code, line_number):
    # Parse the Java code into an AST
    # print("usage line number: ", line_number)
    try :
        tree = javalang.parse.parse(java_code)

        # Initialize method content
        method_content = None

        # Iterate through all classes and methods
        for path, node in tree:
            if isinstance(node, javalang.tree.ClassDeclaration):
                # Iterate through the class body declarations
                for member in node.body:
                    if isinstance(member, javalang.tree.MethodDeclaration):
                        # Get the start and end line numbers of the method
                        start_line = member.position.line
                        end_line = find_end_line(java_code, member)
                        # print("start", start_line)
                        # print("end", end_line)

                        # Check if the line number falls within the method's range
                        if start_line <= line_number <= end_line:
                            # Extract method content from the Java code
                            method_content = extract_method_content(java_code, start_line, end_line)
                            return method_content
    except Exception as e:
        return None
    # If no method containing the line number is found
    return None

def find_end_line(java_code, method_node):
    # Get the start line of the method
    start_line = method_node.position.line

    # Find the end line of the method
    end_line = find_matching_closing_brace(java_code, method_node)

    return end_line

def find_matching_closing_brace(java_code, method_node):
    # Initialize brace count to find the matching closing brace
    brace_count = 0

    # Get the start line of the method
    start_line = method_node.position.line

    # Iterate over each line of the code starting from the line where the method begins
    for line_idx, line in enumerate(java_code.split('\n')[start_line - 1:]):
        for char in line:
            # Increment or decrement brace count for each opening or closing brace
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1

                # If brace count becomes 0, we've found the matching closing brace
                if brace_count == 0:
                    # Calculate the end line
                    end_line = start_line + line_idx
                    return end_line

    # If no closing brace is found, return the start line
    return start_line

def extract_method_content(java_code, start_line, end_line):
    # Extract method content
    method_content = '\n'.join(java_code.split('\n')[start_line - 1:end_line])
    return method_content