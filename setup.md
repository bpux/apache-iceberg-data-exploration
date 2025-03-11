##dremio- minioS3

Connection Properties:
"Enable compatibility mode"

fs.s3a.path.style.access 
fs.s3a.endpoint: minio-s3:9000
fs.s3a.access.key
fs.s3a.secret.key

## python in vscode
Clear everything: delete ~/.vscode folder

Auto-Complete:
In your workspace or user settings (settings.json), set:
{
    "python.languageServer": "Pylance"
}

Parameter Hints:
Ensure that parameter hints are enabled. In your settings, verify:
{
    "editor.parameterHints.enabled": true
}
Now, when you type a function name and open a parenthesis, VS Code will display the function signature.
Auto-Completion Settings:
VS Code should automatically show suggestions as you type. To reinforce this, check that:
{
    "editor.quickSuggestions": {
        "other": true,
        "comments": false,
        "strings": true
    },
    "editor.suggestOnTriggerCharacters": true
}

Some libraries (like pyspark, pandas, etc.) may not have type hints.
Install type stub packages for better auto-completion, e.g.:
pip install pyspark-stubs
pip install pandas-stubs