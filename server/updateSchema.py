import os
import subprocess
from objects import *
import json


if not os.path.exists(os.path.join(os.getcwd(), 'client', 'next.config.ts')):
    print("
NextJs is not installed. Please install next.js in the client directory
")
    exit()

# List of classes to generate JSON schemas for
classes = []

cwd = os.getcwd()
input_dir = os.path.join(os.getcwd() + '//server//schemas')
output_dir = os.path.join(os.getcwd() + '//client//app//schemas')

for x in classes:
    className = x.__name__
    schema = x.model_json_schema()
    schema['additionalProperties'] = False
    writeDirectory = os.path.join(input_dir + '//' + className + 'Schema.json')
    with open(writeDirectory, 'w') as json_file:
        json.dump(schema, json_file, indent=4)

# Set the directories for input JSON files and output TypeScript files

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

inputFileNames = os.listdir(input_dir)

#if file name is not json remove from list
for fileName in inputFileNames:
    if not fileName.endswith('.json'):
        inputFileNames.remove(fileName)

# Function to modify the output file by adding imports
def add_imports(output_path, imports):
    with open(output_path, 'r') as file:
        content = file.read()

    # Add imports at the top of the file if not already included
    for imp in imports:
        if imp not in content:
            content = f"{imp}\n" + content

    with open(output_path, 'w') as file:
        file.write(content)

# Iterate over each JSON file in the input directory
for filename in inputFileNames:
    input_path = os.path.join(input_dir, filename)
    output_filename = os.path.splitext(filename)[0] + '.ts'
    output_path = os.path.join(output_dir, output_filename)

    imports = []
    if 'Memo' in filename:
        imports = [
            "import { Employee } from './employeeSchema.ts';",
            "import { Offense } from './offenseSchema.ts';"
        ]

    # Run the json-schema-to-typescript command
    command = f'json2ts -i "{input_path}" -o "{output_path}"'
    try:
        os.system(command)
        print(f"Generated TypeScript type for {filename} at {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating TypeScript for {filename}: {e}")
    