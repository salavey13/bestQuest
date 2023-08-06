import csv

def convert_lists_as_columns_to_csv(questions, answers):
    # Sample data for demonstration
    #questions = ['What is the capital of France?', 'Who painted the Mona Lisa?']
    #answers = ['Paris', 'Leonardo da Vinci']

    # Create a list of dictionaries, where each dictionary represents a row in the CSV table
    data = []
    for i in range(len(questions)):
        row = {'Question': questions[i], 'Answer': answers[i]}
        data.append(row)

    # Define the CSV file path
    csv_file = 'data.csv'

    # Write the data to the CSV file
    with open(csv_file, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['Question', 'Answer'])
        writer.writeheader()
        writer.writerows(data)

# takes a list of strings in the format "some_text (another_text)" as input and performs the following actions:

# 1. Creates a similar list, but with items reversed as "another_text (some_text)" and saves it to another file with the suffix "vice".
# 2. Saves the separate lists of some_text and another_text to separate files.

# Here's an example script that accomplishes these tasks:

def process_strings(input_file):
    some_text_list = []
    another_text_list = []

    # Read the input file
    with open(input_file, 'r', encoding="utf-8") as f:
        lines = f.readlines()

    # Process each line
    for line in lines:
        # Split the line into some_text and another_text
        some_text, another_text = line.strip().split(' (', 1)
        another_text = another_text[:-1]  # Remove the closing parenthesis

        # Append some_text and another_text to their respective lists
        some_text_list.append(some_text)
        another_text_list.append(another_text)

    # Write the reversed list to a file with the suffix "vice"
    with open(input_file + "_vice", 'w') as f:
        for another_text, some_text in zip(another_text_list, some_text_list):
            f.write(f"{another_text} ({some_text})\n")

    # Write some_text and another_text lists to separate files
    with open(input_file + "some_text_file.txt", 'w') as f:
        for item in some_text_list:
            f.write(item + "\n")

    with open(input_file + "another_text_file.txt", 'w') as f:
        for item in another_text_list:
            f.write(item + "\n")

# Usage example
#process_strings("input_file.txt")