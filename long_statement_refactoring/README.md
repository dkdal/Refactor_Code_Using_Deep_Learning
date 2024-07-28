# Long Statement Refactoring Implementation


This project is about to generate the dataset, preprocess and train the CodeT5 model to refactor long statement smell by extracting variable.

# Pre-requisites

Before you begin, you will need to have the following tools installed on your machine:

- [Git](https://git-scm.com)
- [Python 3.5 or higher](https://www.python.org/downloads/)

### Preferred IDE
- [VS Code](https://code.visualstudio.com/download)

### Dependencies

    numpy==1.24.2
    pandas==1.5.3
    scikit-learn==1.2.1
    tensorflow==2.15.0
    torch==2.0.0
    matplotlib==3.7.1
    seaborn==0.11.2
    joblib==1.2.0
    jsonschema==4.17.3
    nltk==3.8.1
    requests==2.26.0
    scipy==1.12.0
    tensorboard==2.15.2
    transformers==4.27.1
    xgboost==2.0.3
    javalang==0.13.0

### Setup the Environment and Install the Dependencies

Navigate to the project directory

```bash    
# If present in the magic number refactoring directory, execute
cd ../long_statement_refactoring

# Else present in the root directory, execute
cd long_statement_refactoring
```

### Prepare Dataset

To generate the required data to fine-tune or pre-train the model, please follow the below steps.

#### Step 1

Set the parameters in the [SEART tool](https://seart-ghs.si.usi.ch/) and download the `json` version of the results.

The current file present in `data\results.json` is based on below seach parameters on SEART tool.

```
Language: Java
Minimum Number of Commits: 500
Minimum Number of Contributors: 10
Minimum Number of Pull Requests: 100
Minimum Number of Stars: 50
```

#### Step 2

The repository analysis is done via the Java's JAR file. Which should be available in the projects directory path `resources/extract-variable-extractor-1.0-jar-with-dependencies.jar`. If not available, please check the [repo path] to generate the .JAR file and place at the `resources` directory of this project.

#### Step 3

Place the `json` file generated from the step 1 under the `data` directory. It can be placed anywhere else too. Just make sure to copy the absolute path then. Execute the `data.py` script.


From the project's root directory, execute the following command,

```sh
python data.py <path_to_input_json>
```


Note: If you're processing too many repositories at once you can run the script in background, redirecting the terminal outputs to `/dev/null` via this command. The logs are anyway stored in the `output/logs` folder.


```sh
python data.py <path_to_input_json> > /dev/null 2>&1
```

### Output

For each repository analysed, a `.jsonl` file is created under the `data/output` directory. Each `json` object in this `.jsonl` file is an instance of the `extract variable` refactoring for the `long statement`. The formate is like follows:

```json
    {
        "Smelly Sample" : "...",
        "Refactored Sample" : "...",
        "lineNo" : ...
    }
```

The `Smelly Sample` will have the code with long statement. The `Refactored Sample` will have the code with refactoring performed and having variable extracted. The `lineNo` will be an integer value of the line where the variable has been extracted.


### Data Preprocess

Execute the `analyze_code.py` file.

```sh
python analyze_code.py <directory_path>
```

Note: `<directory_path>` will be the directory where your all repos' dataset prepared. For this case, value is `data\output\dataset`

The preprocessed dataset will be saved in the `output` directory. 

```json
    {
        "smelly_method": "...",
        "refactored_method" : "..."
    }
```

The `smelly_method` will have the method where the long statement smell present whereas `refactored_method` will have the method where the long statemetn smell has been refactored.
