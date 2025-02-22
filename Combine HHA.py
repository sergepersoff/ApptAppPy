import os
import csv

# Define the directory where the input files are located
input_directory = r'C:\Users\serge\Desktop\DOV\2023'

# List of input file names
input_files = [
    'HHA 2023 RDP.csv',
    'HHA 2023 OFF.csv',
    'HHA 2023 MFL.csv',
    'HHA 2023 IPA.csv',
    'HHA 2023 ICF.csv',
    'HHA 2023 FFP.csv',
    'HHA 2023 EVO.csv'
]

# Output file path
output_path = r'C:\Users\serge\Desktop\DOV\2023\HHA_Dov_2023.csv'

# Initialize a flag to indicate whether we need to write the header                
write_header = True

# Open the output file for writing
with open(output_path, 'w', newline='') as output_file:
    output_writer = csv.writer(output_file)

    # Loop through the input files and append their data to the output file
    for input_file in input_files:
        input_file_path = os.path.join(input_directory, input_file)

        with open(input_file_path, 'r', newline='') as input_file:
            input_reader = csv.reader(input_file)

            # Skip the header row if it's not the first file
            if not write_header:
                next(input_reader)

            # Loop through the rows in the input file and write them to the output file
            for row in input_reader:
                output_writer.writerow(row)

        # After the first file, set the flag to False so we don't write the header again
        write_header = False

print(f'Merged files into {output_path}')
