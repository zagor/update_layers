import hashlib
import json
import subprocess

docid = '1rsOSmBak413f7bmcQ3wmGqSXDKjO6LMBtqCag8w3pDw'
cells = 'B4:F99'
url = f'https://docs.google.com/spreadsheets/d/{docid}/gviz/tq?tqx=out:csv&range={cells}'
csv_file = 'layers.csv'
cfg_file = 'LayerRotation.cfg'
cfg_hash_file = cfg_file + '.hash'
secrets_file = 'secrets.json'


def download():
    subprocess.check_call(['curl', '--fail', '--silent', '--output', csv_file, url])


def convert():
    lines = []
    with open(csv_file) as inf:
        for line in inf.readlines():
            line = line.replace('"', '').strip()
            lines.append(line.split(','))
        # write one column at a time, so we don't mix them
        with open(cfg_file, 'w') as outf:
            for column in range(len(lines[0])):
                for line in lines:
                    if line[column]:
                        print(line[column], file=outf)


def upload():
    with open(secrets_file) as f:
        secrets = json.load(f)
    with open(cfg_file, 'rb') as f:
        layers_hash = hashlib.file_digest(f, 'sha256').hexdigest()
    last_uploaded_hash = ''
    try:
        last_uploaded_hash = open(cfg_hash_file).readline()
    except FileNotFoundError:
        pass
    if layers_hash != last_uploaded_hash:
        try:
            subprocess.check_call(['sshpass', '-p', secrets['password'],
                                   'scp', '-P', secrets['port'], cfg_file, secrets['path']])
        except subprocess.CalledProcessError as e:
            if e.returncode == 1:
                # for unknown reasons, oasis ssh server always returns error 1
                pass
            else:
                raise e
        with open(cfg_hash_file, 'w') as f:
            f.write(layers_hash)


if __name__ == '__main__':
    download()
    convert()
    upload()
