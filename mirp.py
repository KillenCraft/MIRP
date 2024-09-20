import argparse
import os
import zipfile

from tqdm import tqdm


def list_and_extract_zip_contents(tag, zip_file_path, extract_to):
    # Check if the file is a zip file
    if zipfile.is_zipfile(zip_file_path):
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                # List all the contents of the zip file
                print(f"Contents of {zip_file_path}:")
                for file_info in tqdm(zip_ref.infolist(), desc="Extracting files", unit="file"):
                    # Skip directories
                    if not file_info.is_dir():
                        # Create a subfolder based on the file's name (excluding the extension)
                        subfolder_name = os.path.splitext(file_info.filename)[0]
                        subfolder_path = os.path.join(extract_to, subfolder_name)
                        os.makedirs(subfolder_path, exist_ok=True)

                        # Read the file contents from the zip archive
                        file_data = zip_ref.read(file_info.filename)

                        # Determine the new file path
                        file_extension = os.path.splitext(file_info.filename)[1]
                        new_file_name = f"{tag}{file_extension}"
                        new_file_path = os.path.join(subfolder_path, new_file_name)

                        # Write the file contents to the new file path
                        with open(new_file_path, 'wb') as new_file:
                            new_file.write(file_data)

                print(f"All files extracted to {extract_to}")
        except zipfile.BadZipFile:
            print(f"Error: {zip_file_path} is not a valid zip file.")
        except Exception as e:
            print(f"Error processing {zip_file_path}: {e}")
    else:
        print(f"Error: {zip_file_path} is not a zip file.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a zip file, list its contents, and extract them.")
    parser.add_argument("tag", help="Tag to rename the extracted files to")
    parser.add_argument("zip_file_path", help="Path to the zip file to be processed")
    parser.add_argument("extract_to", help="Directory to extract the contents to")

    args = parser.parse_args()
    list_and_extract_zip_contents(args.tag, args.zip_file_path, args.extract_to)
