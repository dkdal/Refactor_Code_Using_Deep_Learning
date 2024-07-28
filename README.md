
# Code Refactoring Using Tranformer
Deep learning based techniques to refactor the Magic number and long statement smells.


## Project Overview

This project has the 2 main modules with 2 seperate tasks.
1. `magic_number_refactoring` for task realted to the Magic Number Refactoring using the Deep Learning.

2. `long_statement_refactoring` for refactoring of the long statement using Deep Learning.

3. `refminer-extractvariable` to identify and generate the long statement refactroing data

4. `CodeRefactorApp` interactive web application to use with the trained model.

To know more about each taks, refer to the documentation present in respective directories.

## Pre-requisites

Before you begin, you will need to have the following tools installed on your machine:

- [Git](https://git-scm.com)
- [Python 3.5 or higher](https://www.python.org/downloads/)
- [Java 11 or higher](https://www.oracle.com/java/technologies/downloads/)
- [Maven](https://maven.apache.org/download.cgi) 

### Preferred IDE

- [VS Code](https://code.visualstudio.com/download)

### Clone

Clone the repository 

```bash
git clone https://git.cs.dal.ca/courses/2024-winter/csci4130-6314/Group01.git

```


[Build & Run Magic Number Refactoring Project](#magic-number-refactoring)

[Build & Run Long Statement Refactoring Project](#long-statement-refactoring)



## Magic Number Refactoring Implementation

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

### Setup the Environment and Install the Dependencies

```bash    
# Access the project folder in your terminal
cd magic_number_refactoring
```

To execute the notebooks it's advised to set up a virtual environment and install the dependencies from the `requirements.txt` file. 

```sh
python -m venv <venv_name>
```

On Linux/Mac, activate it using `source ./<venv_name>/bin/activate`
On Windows, activate it using `.\<venv_name>\Scripts\activate.bat`

Finally, install the dependencies using:

```sh
pip install -r requirements.txt
```

### Prepare DataSet


#### Step 1
Get the GitHub API to preapre the datset while working with git repo remotely. [Follow documentation from GitHub](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)

- Copy the token and initialize the constant `GITHUB_ACCESS_TOKEN` in `downlaod.py` file.
The current `repos.csv` which have the repository list is generated on the filter of 
```
Min 500 commits
Min 50 stars
Java programming language
```

#### Step 2
Set up the jupyter environment to run jupyter notebook.

To work with Python in Jupyter Notebooks, you must activate an environment in VS Code. To select an environment, use the Python: Select Interpreter command from the Command Palette (Ctrl+Shift+P) ( In windows ).

Run the jupyter notebook with name `1_repo_download.ipynb`. Either run all the cell or run from first cell to last cell in order to generate the dataset.

This might take some time. So please be patient 😊.

### Output

```json
    {
        "before" : "...",
        "after" : "...",
    }
```
Here, `before` dataset will have the whole code with containg magic number smell present in it. While, `after` contains the code with magic number smell refactored.

### Preprocess data

Similarly, run `2_analyze_code.ipynb` to generate the preprocessed dataset.

Please note, in preprocessing, we have selected the default 3 line above and below of where the magic number is refactored. You can change it in the first cell of the notebook before running all cell.

### Output
```json
    {
        "magic_number_smell" : "...",
        "refactored_code" : "...",
    }
```

`magic_number_smell` field will contain the line with magic number presnent and above, below lines with number present in the configuration, whereas, `refactored_code` will contain the line declaration + the rest of the code with magic number replaced with constant name.

### Model Training, evaluate and matrix visualization

Run `3_prep_for_model_train.ipynb` notebook to split the dataset in train, validation and test, train the pre_trained CodeT5, evaluate it and generate the performance matrix score.

## Long Statement Refactoring Implementation

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



## Refminer-extractvariable

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



## Code-Refactor-App

### Pre-requisites
Before you begin, you will need to have the following tools installed on your machine:

- [Python 3.5 or higher](https://www.python.org/downloads/)


- [Java 11 or higher](https://www.oracle.com/java/technologies/downloads/)

### Dependencies

    blinker==1.7.0
    certifi==2024.2.2
    charset-normalizer==3.3.2
    click==8.1.7
    colorama==0.4.6
    filelock==3.13.3
    Flask==3.0.2
    fsspec==2024.3.1
    huggingface-hub==0.22.1
    idna==3.6
    importlib_metadata==7.1.0
    itsdangerous==2.1.2
    joblib==1.3.2
    MarkupSafe==2.1.5
    mpmath==1.3.0
    networkx==3.2.1
    numpy==1.26.4
    packaging==24.0
    pillow==10.2.0
    PyYAML==6.0.1
    regex==2023.12.25
    requests==2.31.0
    safetensors==0.4.2
    sentencepiece==0.2.0
    sympy==1.12
    transformers==4.39.2
    typing_extensions==4.10.0
    urllib3==2.2.1
    Werkzeug==3.0.1
    zipp==3.18.1

Designite Java tool used to detect the smells. Get the [JAR file](https://www.designite-tools.com/assets/DesigniteJava-WEh8Xt46.jar)

### Project Setup and Dependencies

Setup environment

```sh
python -m venv <venv_name>
```

On Linux/Mac, activate it using `source ./<venv_name>/bin/activate`
On Windows, activate it using `.\<venv_name>\Scripts\activate.bat`

Finally, install the dependencies using:

```sh
pip install -r requirements.txt
```

### Host Application On Local

To run the application on local, execute the command

```sh
python -m flask run
```

The application will be hosted on the port `5000`.

### Deploy App on [PythonAnywhere.com](https://www.pythonanywhere.com/)

#### Step 1
Login/Signup on the [PythonAnywhere](https://www.pythonanywhere.com/)

#### Step 2: crate application

- Click on `Web` on navigation bar button.
- Add a new web app and then select the `Flask` and Python version.
- Click next until you reach the `Configuration for <your-webapp-name>`

#### Step 3: deploy local application to the cloud

- Go to the directory where the project is created.
- Upload all the file present in the `Code-Refactor-App` directory locally.
- Creat the `template` directory and copy the `index.html` file from the local path to the cloud path.
- Delete `flask_app.py` in root directory in cloud.
- Go to the WSGI configuration file localtion, present at `var/www/<your-app-name>_wsgi.py` and replace the `flask_app` with `app`.

#### Step 4

- Go to the hosted URL of your application, the two input box where most left one should accept the code and on presse of the `Refactor` button. On press of it, the HuggingFace inference api of the deployed model will be hit and return the refactored code.


## Run trained model locally

Example of the code snippet, to run the model and generate the response at local

```
from transformers import T5ForConditionalGeneration, T5Tokenizer

model = T5ForConditionalGeneration.from_pretrained('<path_of_model>')
tokenizer = T5Tokenizer.from_pretrained('t5-small') #instead of the t5-small, replace with other correspoiding model's name
ids = tokenizer(code, return_tensors='pt').input_ids
result = model.generate(ids, max_length=512, num_beams=5, no_repeat_ngram_size=2, early_stopping=True)
predictions = tokenizer.decode(result[0], skip_special_tokens=True)

print(predictions)

```

## Deploy Trained Model on the HuggingFace

### Step 1

Create an account on the [HuggingFace](https://huggingface.co/login)

### Step 2

Create the model repository using the appropriate repo name.

### Step 3

Setup Git LFS at local, required to push the large size files to git.

- Download the [Git LFS](https://git-lfs.com/)
- Run command
  
  ```sh
  git lfs install
  ```

### Step 4

Clone the repo from the huggingFace.

```sh
git lfs install

git clone https://huggingface.co/<your-username>/<your-reponame>
```

### Step 5

Copy the trained model and corresponding files to the cloned file location.

### Step 6

Track the large file and tell the Git LFS which files to manged by tracking them.

```
git lfs track "<model-filename>"
```

### Step 7

Push the changes to the huggingFace repository

```
git push origin <branch-name>
```

In case, facing the authorized failed error, generate the `ssh key` locally if not present

```
ssh-keygen
<enter file in which to save the key> or press enter to save at the default location.
```

copy the public key and create the key into the huggingface under the `ssh key` section then follow the step 7 again.

Use the ssh key to push the changes to the repo, and try to push.
```
git remote set-url origin git@hf.co:<user-name>/<repo-name> 
```

### Use deployed model on huggingface using serverless inference API

```
import requests

API_URL = "https://api-inference.huggingface.co/models/<user-name>/<model-name>"
headers = "Authorization": "Bearer <API-token>"

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()
	
output = query({
	"inputs": "<your-input>",
})
```

Note: you can generate the `API-token` from HuggingFace user setting page under [`Access Tokens`](https://huggingface.co/settings/tokens).

The above code is for Python language, and similar way, you can utilize this API for other programming language as well.



## References

1. Y. Choi, S. Kim and J. -H. Lee, "Source Code Summarization Using Attention-Based Keyword Memory Networks," 2020 IEEE International Conference on Big Data and Smart Computing (BigComp), Busan, Korea (South), 2020, pp. 564-570, doi: 10.1109/BigComp48618.2020.00011.

2. P. Blazek, K. Venkatesh, M. Lin, “Deep Distilling: automated code generation using explainable deep learning”, Cornell University, [Online]. Available: http: https://arxiv.org/abs/2111.08275. [Accessed: March 30, 2024].




## Authors

- [Harsh Mehta](https://www.linkedin.com/in/harshmehta19/)
- [Dhruv Kapoor](https://www.linkedin.com/in/kapoor-dhruv/)

