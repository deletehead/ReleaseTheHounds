# ReleaseTheHounds
Tool to interact with BloodHound CE API. 

- [x] **Data upload.** I have encountered issues uploading large files to the API -- this project will take a `.zip` file or a directory of JSON data files from `SharpHound.exe` data collector, split the file into workable chunks, and submit them to the BHCE API for ingestion.
- [x] **Path querying.** Currently, there is no easy way to mark users as compromised and query attack paths from a list of users. This tool can take in a list of compromised users (e.g., from a password spray) and query for attack paths.
- [ ] **Raw Cypher querying.** Run a custom cypher query. (TO DO)
- [ ] **Find alternate attack paths.** Find _as many_ attack paths from a source to a dest as possible/reasonable. Sometimes, the shortest path isn't the easiest to exploit :). (TO DO)

The `api.py` code is built from the [sample API client provided by @SpecterOps](https://support.bloodhoundenterprise.io/hc/en-us/articles/11311053342619-Working-with-the-BloodHound-API). You may find this project helpful to reference or expand upon when interacting with the API.

```
$ python3 release_the_hounds.py upload -l 20230907112428_BloodHound.zip

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

<#######################################################################>
<-=-=-=-=-=-=-=-=- Initiating the BloodHound CE client -=-=-=-=-=-=-=-=->
[*] Connecting to: https://bloodhound.absalom.org:443
[*] Testing credentials by getting API version ...
[+] Successfully authenticated to the API! Version: v2 - Server version: v5.0.0

[*] LOADING SHARPHOUND DATA FILE: 20230907112428_computers.json -->
[*] Uploading data for computers
[*] Starting initial job
[*] Starting a new job ... Successfully started Job 45!
[*] Stopping Job 45 ... Job 45 stopped successfully.
[*] Waiting for Job 45 to finish ingesting...NOM NOM NOM
```

```
$ python3 release_the_hounds.py query -s mayhem@absalom.org -d "domain admins@absalom.org"


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

    
[*] Querying BHCE for attack paths!
[*] #######################################################################
[*] -=-=-=-=-=-=-=-=- Initiating the BloodHound CE client -=-=-=-=-=-=-=-=-
[*] Connecting to: https://bloodhound.absalom.org:443
[*] Testing credentials by getting API version ...
[+] Successfully authenticated to the API! Version: v2 - Server version: v5.0.0

[*] QUERYING ATTACK PATHS FROM "MAYHEM@ABSALOM.ORG" TO "DOMAIN ADMINS@ABSALOM.ORG" ->
[MAYHEM@ABSALOM.ORG] 
  ^- <MemberOf> : 
[RDP@ABSALOM.ORG] 
  ^- <CanRDP> : 
[BARDPC.ABSALOM.ORG] 
  ^- <HasSession> : 
[THEBARD@ABSALOM.ORG] 
  ^- <MemberOf> : 
[HELPDESKADMINS@ABSALOM.ORG] 
  ^- <GenericAll> : 
[WIZARDVM.ABSALOM.ORG] 
  ^- <HasSession> : 
[THEWIZARD@ABSALOM.ORG] 
  ^- <MemberOf> : 
[DOMAIN ADMINS@ABSALOM.ORG] 
```

## Installation
This project should be easy to install & set up. You may need to install `requests` if you don't already have it. 

```bash
pip3 install requests
git clone https://github.com/deletehead/ReleaseTheHounds.git
cd ReleaseTheHounds
python3 ReleaseTheHounds -l <BHCE-SharpHound-zip-file>
```

## Usage
- `upload`: Provide the file location (`-l`) of either a SharpHound `.zip` file (in which case it will be extracted) or a directory with already-extracted JSON files.
- `query`: Queryies BHCE for shortest path from source to dest. Can take in a file of sources (e.g., compromised users) or a file of destinations (e.g., Tier 0 assets or target groups).

#### Upload data
```bash
## Just specify the zip
ls *.zip
python3 release_the_hounds.py upload -l bh.zip

## Specify a folder of JSON files
ls bloodhounddata/
python3 release_the_hounds.py upload -l ./bloodhounddata/
```

#### Query Shortest Attack Paths
```bash
python3 release_the_hounds.py query -s "domain users@absalom.org" -d "domain admins@absalom.org"  # single objects
python3 release_the_hounds.py query -s compromised_users.txt -d "domain admins@absalom.org"  # multiple source
python3 release_the_hounds.py query -s "compromised@absalom.org" -d target_objects.txt    # multiple dest
python3 release_the_hounds.py query -s password_sprayed_users.txt -d target_objects.txt   # multiple both
```

### Configuring Authentication
You have two options to authenticate to the API:
  1. Configure your domain & token info in `constants.py`:
  ```
  api_info = {
    "BHCE_DOMAIN"    : "bloodhound.absalom.org",
    "BHCE_PORT"      : 443,
    "BHCE_SCHEME"    : "https",
    "BHCE_TOKEN_ID"  : "4bbe137a-dead-beef-d34d-2dc0ff33aabb",
    "BHCE_TOKEN_KEY" : "1fLUv3Kbd9CkHe6Ea27bTGP1WF3wk45L63dJFNaaNKfPNbXFa7e3Z2=="
  }
  ```
  2. Specify in the command line like so:
  ```bash
  python3 release_the_hounds.py -l ./bh-jsons/ -k "1fLUv3Kbd9CkHe6Ea27bTGP1WF3wk45L63dJFNaaNKfPNbXFa7e3Z2==" -i "4bbe137a-dead-beef-d34d-2dc0ff33aabb" -u https://bloodhound.absalom.org:443
  ```

## Fun GIF
When you run this tool, this happens:

![Release the Hounds](https://media.giphy.com/media/fveEm9uqUas7igLGTU/giphy.gif)
