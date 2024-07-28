# Refminer-extractvariable

This CLI tool uses [RefactoringMiner](https://github.com/tsantalis/RefactoringMiner) to identify and extract `extract method` refactorings in a project history.

### Dependencies

- [Java 11 or higher](https://www.oracle.com/java/technologies/downloads/)
- [Maven](https://maven.apache.org/download.cgi) 

Currently this tool uses RefactoringMiner version [3.0.1](https://github.com/tsantalis/RefactoringMiner/releases/tag/3.0.1)

### Steps to run

- Clone the repo or add it as a `submodule` in your project
- Navigate to the root of the project using `cd <project_path>`
- Install the package using the following command:

    ```bash
    mvn clean install
    ```
- The executable jar file will be created inside the `target`. It should be named with the following format `*-with-dependencies.jar`
- To run the jar file execute the following:

    ```bash
    java -jar <path_to_jar> <repository_url> <output_file_path> <default_branch>
    ```
  `repository_url`: The clone url for the repository to be analyzed. 
  `output_file_path`: The absolute or relative path to the output `jsonl` file in which the extracted methods are stored.
  `default_branch`: The default branch name for which the analysis is supposed to be performed. Usually, `master` or `main`

### Output json format

The generated output will be of the following format:

```json
    {
        "Smelly Sample" : "...",
        "Refactored Sample" : "...",
        "lineNo" : ...
    }
```

`Smelly Sample` have the code with long statement. 

`Refactored Sample` have the code with refactoring performed and having variable extracted. 

`lineNo` is an integer value of the line number where the variable has been extracted.