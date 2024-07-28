import javalang
import sys
import os
import json

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

    
if __name__=="__main__":
    print("start processing...")
    # read the directory path from the argument passed from the command line
    directory_path = sys.argv[1]
    # iterate throught all the .jsonl files in the directory
    for file in os.listdir(directory_path):
        if file.endswith(".jsonl"):
            # variable to store the cotent of the file
            file_results = []
            with open(os.path.join(directory_path, file), 'r') as f:
                # read the content of the file
                lint = 0

                lines = f.readlines()
                # split the content by new line
                # lines = content.split('\n')
                # iterate through each line
                for line in lines:
                    # parse the json line
                    data = json.loads(line.strip())
                    #ignore the line if it has no content or like this {}
                    if not data:
                        print("no data")
                        continue
                    # get the java code from the json data
                    java_code = data['Smelly Sample']
                    # get the line number from the json data
                    java_refactored = data['Refactored Sample']
                    line_number = data['lineNo']
                    # print("java code: ", java_code)
                    # print("java refactored: ", java_refactored)
                    # find the method containing the line number
                    smelly_method_content = find_method(java_code, line_number)
                    refactored_method_content = find_method(java_refactored, line_number)
                    if refactored_method_content and smelly_method_content:
                        file_results.append({
                            'smelly_method': smelly_method_content,
                            'refactored_method': refactored_method_content
                        })
            with open(os.path.join("data", "output", "analyzed_dataset.jsonl"), 'a') as f:
                for result in file_results:
                    f.write(json.dumps(result) + '\n')

    print("processing completed!")


