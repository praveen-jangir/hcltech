from sshtunnel import SSHTunnelForwarder
from ollama import Client
import paramiko

ssh_config = {
    "ssh_address_or_host": "192.168.43.114",
    "ssh_username": "ollama_ssh",
    "ssh_password": "SecurePass123!",
    "remote_bind_address": ("127.0.0.1", 11434) 
}

def query_secure_server(prompt):
    print(f" Connecting to SSH Tunnel as '{ssh_config['ssh_username']}'...")
    
    try:
        with SSHTunnelForwarder(
            (ssh_config["ssh_address_or_host"], 22),
            ssh_username=ssh_config["ssh_username"],
            ssh_password=ssh_config["ssh_password"],
            remote_bind_address=ssh_config["remote_bind_address"],
            local_bind_address=("127.0.0.1", 0),
            
            ssh_pkey=None,
            allow_agent=False,
            host_pkey_directories=[],
        ) as tunnel:
            
            print(f" Tunnel Established! (Port {tunnel.local_bind_port})")
            
            client = Client(host=f'http://127.0.0.1:{tunnel.local_bind_port}')
            
            print(f" Sending query: '{prompt}'")
            response = client.chat(model='mistral', messages=[
                {'role': 'user', 'content': prompt},
            ])
            return response['message']['content']

    except paramiko.AuthenticationException:
        return " Authentication Failed: Check username/password."
    except Exception as e:
        return f" Connection Failed: {str(e)}"
