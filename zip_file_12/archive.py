import os
import re
import time
import sys
import json
import zipfile
import hashlib
from base64 import standard_b64encode as b64encode


def base64sha256(zip_path):
    with open(zip_path, 'rb') as zip_file:
        sha256 = hashlib.sha256()
        sha256.update(zip_file.read())
        base64sha256 = b64encode(sha256.digest()).decode('utf-8')
    return base64sha256


def get_all_file_paths(directory):
    file_paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append({"filepath": filepath, "filename": filename})
    return file_paths


def create_zip_files(data, file_paths):
    try:
        with zipfile.ZipFile(data['output_path'], mode='w') as zf:
            for file_path in sorted(file_paths, key=lambda d: d['filename']):
                file_path = file_path['filepath']
                file_bytes = open(file_path, 'rb').read()
                file_bytes = file_bytes.replace(b'\r\n', b'\n')
                file_path = re.sub('^' + data['source_dir'], '', file_path)
                file_path = re.sub('^' + '/', '', file_path)
                file_path = re.sub('^' + r'\\', '', file_path)
                info = zipfile.ZipInfo(
                    str(file_path),
                    date_time=(1980, 1, 1, 00, 00, 00),
                )
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 0
                info.external_attr = 0o777 << 16
                zf.writestr(info, file_bytes)
            zf.close()
        zip_data = {
            "output_path":
            str(data['output_path']),
            "output_absolute_path":
            str(os.path.abspath(data['output_path'])),
            "output_size":
            str(os.stat(data['output_path']).st_size),
            "output_md5":
            str(
                hashlib.md5(open(data['output_path'],
                                 'rb').read()).hexdigest()),
            "output_base64sha256":
            str(base64sha256(data['output_path']))
        }
        return zip_data

    except Exception as e:
        sys.stderr.write(str(e))
        sys.exit(1)


def main():
    # Read JSON data from stdin
    data = json.load(sys.stdin)

    # Create build directory if it doesn't exist
    build_directory = os.path.dirname(data['output_path'])
    if not os.path.exists(build_directory):
        os.makedirs(build_directory)

    file_paths = get_all_file_paths(data['source_dir'])

    zip_data = create_zip_files(data, file_paths)

    # Output result to stdout
    print(json.dumps(zip_data))


if __name__ == "__main__":
    main()
