import os

def scan_pdf(folder: str) -> list | None:
    disk_path = [chr(i) + ':/' for i in range(ord('A'), ord('Z') + 1)]
    disk_path.append('/')
    if folder.upper() in disk_path:
        return None
    paths = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith('.pdf'):
                paths.append(os.path.join(root, file).replace('\\', '/'))
    return paths
