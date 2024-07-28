## Magic Number Refactoring Implementation

This project is about to generate the dataset, preprocess and train the CodeT5 model to refactor magic number smell.

### Pre-requisites

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