import argparse
import logging
import os
import zipfile
from concurrent.futures import ThreadPoolExecutor

from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_file(zip_ref, file_info, tag, extract_to):
    try:
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
    except Exception as e:
        logging.error(f"Error extracting {file_info.filename}: {e}")

def list_and_extract_zip_contents(tag, zip_file_path, extract_to):
    if not zipfile.is_zipfile(zip_file_path):
        logging.error(f"Error: {zip_file_path} is not a zip file.")
        return

    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            logging.info(f"Contents of {zip_file_path}:")
            file_infos = [file_info for file_info in zip_ref.infolist() if not file_info.is_dir()]

            with ThreadPoolExecutor() as executor:
                list(tqdm(executor.map(lambda file_info: extract_file(zip_ref, file_info, tag, extract_to), file_infos), total=len(file_infos), desc="Extracting files", unit="file"))

            logging.info(f"All files extracted to {extract_to}")
    except zipfile.BadZipFile:
        logging.error(f"Error: {zip_file_path} is not a valid zip file.")
    except Exception as e:
        logging.error(f"Error processing {zip_file_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a zip file, list its contents, and extract them.")
    parser.add_argument("tag", help="Tag to rename the extracted files to")
    parser.add_argument("zip_file_path", help="Path to the zip file to be processed")
    parser.add_argument("extract_to", help="Directory to extract the contents to")

    args = parser.parse_args()
    list_and_extract_zip_contents(args.tag, args.zip_file_path, args.extract_to)
