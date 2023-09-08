#!/usr/bin/env python3
### ReleaseTheHounds.py ###
import argparse
import zipfile, os

from api import *
from constants import *

def parse_args():
    parser = argparse.ArgumentParser(description="Process JSON files in chunks for BHCE and upload via API.")    
    parser.add_argument('-l', '--location', required=True, help='File system location (zip file or recursively for a directory) of JSON files. Will unzip if needed.')
    parser.add_argument('-u', '--url', type=str, help='[Can be specified in constants.py.] Base API URL to connect to. Ex. https://bloodhound.absalom.net:443')
    parser.add_argument('-k', '--tokenkey', type=str, help='[Can be specified in constants.py.] BloodHound token key  (Looks like a B64 blob: https://support.bloodhoundenterprise.io/hc/en-us/articles/11311053342619-Working-with-the-BloodHound-API#heading-2)')
    parser.add_argument('-i', '--tokenid', type=str, help='BloodHound token ID  (Looks like a GUID: https://support.bloodhoundenterprise.io/hc/en-us/articles/11311053342619-Working-with-the-BloodHound-API#heading-2)')
    parser.add_argument('-c', '--chunkobjects', type=int, default=250, help='Number of objects in each chunk (default: 250)')
    parser.add_argument('-j', '--chunksinjob', type=int, default=50, help='Number of chunks in each job (default: 50)')
    
    return parser.parse_args()
    

def banner():
    banner = '''

          __________       .__                                  
          \______   \ ____ |  |   ____ _____    ______ ____   
           |       __/ __ \|  | _/ __ \\__  \  /  ____/ __ \  
           |    |   \  ___/|  |_\  ___/ / __ \_\___ \\  ___/  
           |____|_  /\___  |____/\___  (____  /____  >\___  > 
                  \/     \/          \/     \/     \/     \/  
      __  .__               ___ ___                         .___      
    _/  |_|  |__   ____    /   |   \  ____  __ __  ____   __| _/______
    \   __|  |  \_/ __ \  /    ~    \/  _ \|  |  \/    \ / __ |/  ___/
     |  | |   Y  \  ___/  \    Y    (  <_> |  |  |   |  / /_/ |\___ \ 
     |__| |___|  /\___  >  \___|_  / \____/|____/|___|  \____ /____  >
               \/     \/         \/                   \/     \/    \/ 

    '''
    print(banner)
    
    return
    

def extract_zip(filename) -> list:
    '''
    Extracts a zip file and returns a list of extracted files
    '''
    extracted_files = []
    try:
        with zipfile.ZipFile(filename, 'r') as zip_ref:
            zip_ref.extractall()
            # Get the names of the extracted files
            extracted_files = zip_ref.namelist()
    except:
        print(f"Error extracting JSON data from zip: {filename} may not be a valid zip file.")

    return extracted_files


def list_files_in_directory(directory) -> list:
    '''
    Returns a list of all the files in the location provided in args.location
    '''
    file_list = []
    try:
        # List all files in the specified directory
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.json'):
                    file_list.append(os.path.join(root, file))
    except FileNotFoundError:
        print(f"Error: Directory '{directory}' not found.")

    return file_list
    

def validate_json(json_data) -> bool:
    '''
    Checks if the data generally conforms to documentation
    '''
    print('[*] Checking if the data is valid')
    if all(key in json_data for key in ("data", "meta")):
        return True
    else:
        print('[-] This data does not look like valid BloodHound data! Troubleshoot ideas:')
        print('    -> Did you use the most recent collector?')
        print('    -> Are you using "data" as the key for objects (old collectors used "computers", "users", etc.)')
        print('    -> Check out https://support.bloodhoundenterprise.io/hc/en-us/articles/17303881735963-BloodHound-JSON-Formats')
        return False
        
        
def load_file(filename) -> dict:
    '''
    Load JSON data from file. Use UTF-8 BOM encoding if needed (sometimes this format happens with Windows)
    '''
    try:
        with open(filename, 'r') as f:
            large_json_data = json.load(f)
    except:
        with open(filename, 'r', encoding='utf-8-sig') as f:
            large_json_data = json.load(f)
    return large_json_data


def main():
    # Set up args
    args = parse_args()
    if args.tokenid:
        BHCE_TOKEN_ID  = args.tokenid
    else:
        BHCE_TOKEN_ID = api_info["BHCE_TOKEN_ID"]
    if args.tokenkey:
        BHCE_TOKEN_KEY = args.tokenkey 
    else:
        BHCE_TOKEN_KEY = api_info["BHCE_TOKEN_KEY"]
    if args.url:
        if len(args.url.split(':')) != 3:
            print('[*] URL parameter must include protocol scheme and port. Example: https://bloodhound.absalom.org:443')
            exit()
        BHCE_DOMAIN = args.url.split(':')[1].split('/')[2]
        BHCE_PORT   = args.url.split(":")[2]
        BHCE_SCHEME = args.url.split(":")[0]
    else:
        BHCE_DOMAIN = api_info["BHCE_DOMAIN"]
        BHCE_PORT   = api_info["BHCE_PORT"]
        BHCE_SCHEME = api_info["BHCE_SCHEME"]
    # End args setup
    
    chunk_object_count = args.chunkobjects if args.chunkobjects else 250
    num_chunks_per_job = args.chunksinjob if args.chunksinjob else 50
    # Configure Credentials object for auth
    credentials = Credentials(token_id=BHCE_TOKEN_ID, token_key=BHCE_TOKEN_KEY)

    banner()

    # Create the client and perform a sample call using token request signing
    print("<#######################################################################>")
    print("<-=-=-=-=-=-=-=-=- Initiating the BloodHound CE client -=-=-=-=-=-=-=-=->")
    print(f'[*] Connecting to: {BHCE_SCHEME}://{BHCE_DOMAIN}:{BHCE_PORT}')
    client = Client(scheme=BHCE_SCHEME, host=BHCE_DOMAIN, port=BHCE_PORT, credentials=credentials)
    print('[*] Testing credentials by getting API version ...')
    try:
        version = client.get_version()
        print(f'[+] Successfully authenticated to the API! Version: {version.api_version} - Server version: {version.server_version}')
        print("")
    except:
        print('[-] Failed to authenticate to the target API. Exiting ...')
        exit()

    ### UPLOADING DATA TO API ###
    
    files = extract_zip(args.location) if args.location.endswith('.zip') else list_files_in_directory(args.location)
    for f in files:
        print(f'[*] LOADING SHARPHOUND DATA FILE: {f} -->')
        bhjson = load_file(f) 
        client.chunk_and_submit_data(data_to_chunk=bhjson, num_objs_in_chunk=chunk_object_count, num_chunks_per_job=num_chunks_per_job)


if __name__ == "__main__":
    main()