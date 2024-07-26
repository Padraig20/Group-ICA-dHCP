import paramiko
from scp import SCPClient
import os
import fnmatch
from tqdm import tqdm

def create_ssh_client_from_config(alias):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    config = paramiko.SSHConfig()
    user_config_file = os.path.expanduser('~/.ssh/config')
    
    with open(user_config_file) as f:
        config.parse(f)
    
    cfg = config.lookup(alias)
    hostname = cfg['hostname']
    username = cfg.get('user')
    key_filename = cfg.get('identityfile')

    ssh.connect(hostname, username=username, key_filename=key_filename)
    return ssh

def list_local_files(local_folder):
    return os.listdir(local_folder)

def list_remote_files(ssh, remote_folder):
    stdin, stdout, stderr = ssh.exec_command(f"ls {remote_folder}")
    files = stdout.read().splitlines()
    return [file.decode('utf-8') for file in files]

def download_files(ssh, subject_ids, remote_folder, local_folder):
    remote_files = list_remote_files(ssh, remote_folder)
    local_files = list_local_files(local_folder)
    
    with SCPClient(ssh.get_transport()) as scp:
        for subject_id, ses_id in tqdm(subject_ids):

            pattern = f"{subject_id}_ses-{ses_id}_*.nii.gz"

            if any(fnmatch.fnmatch(file, pattern) for file in local_files):
                print(f"Files for {subject_id} already exist in the local directory. Skipping download.")
                continue

            matching_files = fnmatch.filter(remote_files, pattern)
            
            if matching_files:
                file = matching_files[0]
                remote_path = f"{remote_folder}/{file}"
                try:
                    scp.get(remote_path, local_path=local_folder)
                except Exception as e:
                    print(f"Failed to download {file}: {e}")
            else:
                print(f"No files found for {subject_id}")

def main():
    ssh_alias = "connectome"
    
    subject_ids_folder = "metadata/healthy_subjects"
    remote_folder = "/storage/bigdata/dHCP/fmriprep/1.rs_fmri/4.cleaned_image"
    local_folder = "./input/"

    if not os.path.exists(local_folder):
        os.makedirs(local_folder)
        print(f"Created local folder: {local_folder}")
    
    for ga in range(36, 45):

        with open(os.path.join(subject_ids_folder, f"ga_{ga}.txt"), 'r') as f:
            subject_ids = [tuple(line.strip().split('\t')) for line in f.readlines()[1:]]
        
        if not os.path.exists(os.path.join(local_folder, f"ga_{ga}")):
            os.makedirs(os.path.join(local_folder, f"ga_{ga}"))
            print(f"Created local folder: {local_folder}")

        ssh = create_ssh_client_from_config(ssh_alias)
        download_files(ssh, subject_ids, remote_folder, os.path.join(local_folder, f"ga_{ga}"))

        ssh.close()
        
        print(f"\nDownloaded files for GA {ga}!\n")

if __name__ == "__main__":
    main()

