import re
import json
import javalang

# def extract_code_around_constant_declaration(input_code, num_lines_around_declaration, num_lines_above_first_usage, num_lines_below_first_usage):
#     # Regular expression to match Java constant declarations with assigned values, including comments
#     constant_declaration_pattern = re.compile(r'(?:(?:\s*//.)*(?:private|protected|public)\s+(?:static\s+)?\s*final\s+(?:int|double|float|long|short|byte)\s+(\w+)\s*=\s*([^;]+)\s*;.*?\n)')

#     # Find the first constant declaration in the Java code
#     match = constant_declaration_pattern.search(input_code)

#     if match:
#         # Extract constant type, name, and its assigned value from the match
#         constant_name, constant_value = match.groups()

#         # Check if the assigned value is a primitive type or String
#         if not constant_value.startswith("("):
#             # Find the line numbers of the constant declaration and usage
#             lines = [m.start(0) for m in re.finditer('\n', input_code)]
#             declaration_line_number = input_code.count('\n', 0, match.start(0)) + 1

#             # Find the first constant usage after the declaration
#             usage_match = re.search(fr'\b{constant_name}\b', input_code[match.end(0):])
#             if usage_match:
#                 usage_line_number = input_code.count('\n', 0, match.end(0) + usage_match.start(0)) + 1

#                 # Extract the constant declaration line
#                 declaration_line = input_code.split('\n')[declaration_line_number - 1]

#                 # Calculate the start and end line numbers for the specified range around the first constant usage
#                 start_line = max(1, usage_line_number - num_lines_above_first_usage)
#                 end_line = min(lines[-1], usage_line_number + num_lines_below_first_usage)

#                 # Extract the specified lines around the first constant usage
#                 selected_lines = input_code.split('\n')[start_line - 1:end_line]
#                 selected_code = '\n'.join(selected_lines)

#                 return declaration_line, selected_code

#     return None, None

def extract_code_around_constant_declaration(input_code, num_lines_around_declaration, num_lines_above_first_usage, num_lines_below_first_usage):
    # Regular expression to match Java constant declarations with assigned values, including comments
    constant_declaration_pattern = re.compile(r'(?:(?:\s*//.)*(?:private|protected|public)\s+(?:static\s+)?\s*final\s+(?:int|double|float|long|short|byte)\s+(\w+)\s*=\s*([^;]+)\s*;.*?\n)')

    # Find the first constant declaration in the Java code
    match = constant_declaration_pattern.search(input_code)

    if match:
        # Extract constant type, name, and its assigned value from the match
        constant_name, constant_value = match.groups()
        try:

            # Check if the assigned value is a primitive type or String
            if not constant_value.startswith("("):
                # Find the line numbers of the constant declaration and usage
                lines = [m.start(0) for m in re.finditer('\n', input_code)]
                declaration_line_number = input_code.count('\n', 0, match.start(0)) + 1

                # Find the first constant usage after the declaration
                usage_match = re.search(fr'\b{constant_name}\b', input_code[match.end(0):])
                if usage_match:
                    usage_line_number = input_code.count('\n', 0, match.end(0) + usage_match.start(0)) + 1

                    # Extract the constant declaration line
                    declaration_line = input_code.split('\n')[declaration_line_number - 1]

                    # Calculate the start and end line numbers for the specified range around the first constant usage
                    start_line = max(1, usage_line_number - num_lines_above_first_usage)
                    end_line = min(lines[-1], usage_line_number + num_lines_below_first_usage)

                    # Extract the specified lines around the first constant usage
                    selected_lines = input_code.split('\n')[start_line - 1:end_line]
                    selected_code = '\n'.join(selected_lines)

                    # Find method boundaries based on the constant usage line
                    # method_code = find_method(input_code, usage_line_number)
                    # if(selected_code is not None and declaration_line is not None and method_code is None):
                    #     print("selected code: ", selected_code)
                    #     print("declaration Line ", declaration_line)
                    #     print("input code", input_code)

                    return declaration_line, selected_code#, method_code
        except Exception as e:
            print("An error occurred:", e)
            # print("Input code:")
            # print(input_code)
            # return None

    return None, None#, None


def read_jsonl(jsonl_filename):
    with open(jsonl_filename, mode='r', encoding='utf-8') as jsonlfile:
        # Read all lines from the JSONL file
        lines = jsonlfile.readlines()

        # Check if there are lines in the file before attempting to parse
        if lines:
            # Parse the JSON data from all lines
            json_data = []
            for line in lines:
                data = json.loads(line.strip())
                json_data.append({'before': data.get('before', None), 'after': data.get('after', None)})
            
            return json_data
        else:
            # Handle the case where the file is empty
            print("The JSONL file is empty.")
            return None
        
def extract_constant_info(java_line):
    # Define a regex pattern to match constant declarations in Java
    pattern = re.compile(r'\b(public|private|protected|static|final|class|interface|\w+)\s+(\w+)\s*=\s*([^;]+);')
    # constant_declaration_pattern = re.compile(r'(?:(?:\s*//.)*(?:private|protected|public)\s+(?:static\s+)?\s*final\s+(?:int|double|float|long|short|byte|boolean|char|String)\s+(\w+)\s*=\s*([^;]+)\s*;.*?\n)')
    # print("java line: ", java_line)
    # Find matches in the Java line
    match = pattern.search(java_line)

    if match:
        # Retrieve the constant name and value
        constant_name = match.group(2)
        constant_value = match.group(3).strip()

        # Return the constant information as a dictionary
        return {'constant_name': constant_name, 'constant_value': constant_value}
    else:
        # Return None if no constant declaration is found
        return None
    
def replace_constant_with_value(constant_name, constant_value, code):
    # Create a regex pattern with word boundaries for the constant name
    pattern = re.compile(r'\b' + re.escape(constant_name) + r'\b')

    # Replace all occurrences of the constant name with its value in the code
    updated_code = pattern.sub(constant_value, code)

    return updated_code

def replace_constant_with_value_method_code(constant_name, constant_value, code, method_code = None):
    # Create a regex pattern with word boundaries for the constant name
    pattern = re.compile(r'\b' + re.escape(constant_name) + r'\b')

    # Replace all occurrences of the constant name with its value in the code
    updated_code = pattern.sub(constant_value, code)
    if method_code is not None:
        method_updated_code = pattern.sub(constant_value, method_code) 

    return updated_code, method_updated_code

def append_fields_to_jsonl_method(magic_number_smell, refactored_code, magic_number_method, refactord_method, file_path):
    # Create a dictionary with the new fields
    new_entry = {
        "magic_number_smell": magic_number_smell,
        "refactored_code": refactored_code,
        "method_with_magic_number": magic_number_method,
        "refactored_method": refactord_method
    }

    # Convert the dictionary to a JSON string
    json_entry = json.dumps(new_entry)

    # Append the JSON string to the file
    with open(file_path, 'a') as file:
        file.write(json_entry + '\n')

def append_fields_to_jsonl(magic_number_smell, refactored_code, file_path):
    # Create a dictionary with the new fields
    new_entry = {
        "magic_number_smell": magic_number_smell,
        "refactored_code": refactored_code,
    }

    # Convert the dictionary to a JSON string
    json_entry = json.dumps(new_entry)

    # Append the JSON string to the file
    with open(file_path, 'a') as file:
        file.write(json_entry + '\n')

def append_fields_to_jsonl_method_code(magic_number_smell, refactored_code, magic_number_method, refactord_method, file_path):
    # Create a dictionary with the new fields
    new_entry = {
        "magic_number_smell": magic_number_smell,
        "refactored_code": refactored_code,
    }

    # Convert the dictionary to a JSON string
    json_entry = json.dumps(new_entry)

    # Append the JSON string to the file
    with open(file_path, 'a') as file:
        file.write(json_entry + '\n')



    # except Exception as e:
    #     print("An error occurred:", e)
    #     # print("Input code:")
    #     # print(input_code)
    #     return None

    # return None
        # print("method_start_line: ", method_start_line)
        # print("method_end_line: ", method_end_line)

def find_method(java_code, line_number):
    # Parse the Java code into an AST
    # print("usage line number: ", line_number)
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