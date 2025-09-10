import pandas as pd
import os
import glob

def combine_excel_files(folder_path, output_file_name):
    """
    Combines multiple Excel files from a specified folder into a single Excel file.

    It assumes that the first two rows of each file are headers and includes them
    only from the first file processed.

    Args:
        folder_path (str): The path to the folder containing the Excel files.
        output_file_name (str): The name for the combined output Excel file.
    """
    try:
        # Use glob to find all files ending with .xlsx or .xls
        excel_files = glob.glob(os.path.join(folder_path, "*.xlsx")) + \
                      glob.glob(os.path.join(folder_path, "*.xls"))

        if not excel_files:
            print(f"No Excel files found in the directory: {folder_path}")
            return

        print(f"Found {len(excel_files)} Excel files to combine.")

        # List to hold DataFrames from each file
        all_data_frames = []

        # Process the first file to get headers
        first_file = excel_files[0]
        print(f"Processing file: {first_file}")
        df_first = pd.read_excel(first_file, header=None)
        all_data_frames.append(df_first)

        # Process the rest of the files, skipping the first two header rows
        for file in excel_files[2:]:
            print(f"Processing file: {file}")
            # skiprows=2 will skip the first two rows (0-indexed)
            df = pd.read_excel(file, header=None, skiprows=2)
            all_data_frames.append(df)

        # Concatenate all DataFrames into one
        combined_df = pd.concat(all_data_frames, ignore_index=True)

        # Construct the full path for the output file
        output_path = os.path.join(folder_path, output_file_name)

        # Write the combined DataFrame to a new Excel file
        # index=False prevents pandas from writing row indices into the file
        # header=False is used because we've handled headers manually
        combined_df.to_excel(output_path, index=False, header=False)

        print(f"\nSuccessfully combined all files into '{output_path}'")

    except FileNotFoundError:
        print(f"Error: The folder '{folder_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# --- Configuration ---
# Set the path to the folder containing your Excel files
# Using a raw string (r"...") is recommended on Windows to avoid issues with backslashes
input_folder = r"C:\The"

# Set the desired name for the output file
output_file = "Combined_Excel_File.xlsx"

# --- Execution ---
if __name__ == "__main__":
    combine_excel_files(input_folder, output_file)

