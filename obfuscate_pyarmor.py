import os
import shutil
import subprocess
import re

def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    if process.returncode != 0:
        print(f"Error executing command: {command}")
        print(error.decode())
    return output.decode()

def update_setup_py(file_path, package_name):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add package_data and include_package_data
    setup_args = re.search(r'setup\((.*?)\)', content, re.DOTALL).group(1)
    if 'package_data' not in setup_args:
        setup_args += f",\n    package_data={{'{package_name}': ['*.so', '*.dylib', '*.dll', '*.pyd', 'pytransform.key']}}"
    if 'include_package_data' not in setup_args:
        setup_args += ",\n    include_package_data=True"
    
    content = re.sub(r'setup\((.*?)\)', f'setup({setup_args})', content, flags=re.DOTALL)
    
    with open(file_path, 'w') as f:
        f.write(content)

def obfuscate_package(source_dir, dest_dir):
    package_name = os.path.basename(source_dir)
    obfuscated_path = os.path.join(dest_dir, package_name)

    print(f"Source directory: {source_dir}")
    print(f"Destination directory: {dest_dir}")
    print(f"Package name: {package_name}")
    print(f"Obfuscated package path: {obfuscated_path}")

    if os.path.exists(obfuscated_path):
        print(f"Removing existing obfuscated package at {obfuscated_path}")
        shutil.rmtree(obfuscated_path)

    os.makedirs(obfuscated_path, exist_ok=True)

    # Copy the entire package to the destination
    shutil.copytree(source_dir, obfuscated_path, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('build', 'test', 'dist', '*.pyc', '__pycache__'))

    src_path = os.path.join(obfuscated_path, 'src')

    # Obfuscate the package
    obfuscate_command = f"pyarmor gen --recursive --output {os.path.join(src_path, package_name)} {os.path.join(src_path, package_name)}"
    print(f"Running PyArmor command: {obfuscate_command}")
    output = run_command(obfuscate_command)
    print(f"PyArmor output: {output}")

    # Update setup.py
    setup_py_path = os.path.join(obfuscated_path, 'setup.py')
    update_setup_py(setup_py_path, package_name)
    print(f"Updated setup.py at {setup_py_path}")

    print(f"Final obfuscated package structure:")
    for root, dirs, files in os.walk(obfuscated_path):
        level = root.replace(obfuscated_path, '').count(os.sep)
        indent = ' ' * 4 * level
        print(f"{indent}{os.path.basename(root)}/")
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            print(f"{sub_indent}{f}")

    print(f"Obfuscated package created at: {obfuscated_path}")

if __name__ == "__main__":
    source_package = "/home/gazi/Desktop/Work/custom_packages/optimization"
    obfuscated_package = "/home/gazi/Desktop/Work/custom_packages_obf"
    obfuscate_package(source_package, obfuscated_package)