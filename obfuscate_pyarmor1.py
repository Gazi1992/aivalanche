import os
import shutil
import subprocess

def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    if process.returncode != 0:
        print(f"Error executing command: {command}")
        print(error.decode())
    return output.decode()

def obfuscate_package(source_dir, dest_dir):
    package_name = os.path.basename(source_dir)
    obfuscated_name = f"{package_name}_obf"
    obfuscated_path = os.path.join(dest_dir, obfuscated_name)

    # Remove existing obfuscated package if it exists
    if os.path.exists(obfuscated_path):
        shutil.rmtree(obfuscated_path)

    # Copy the entire package to the destination
    shutil.copytree(source_dir, obfuscated_path)

    # Obfuscate the package
    src_path = os.path.join(obfuscated_path, 'src', package_name)
    obfuscate_command = f"pyarmor gen --recursive --output {src_path} {src_path}"
    print(f"Running PyArmor command: {obfuscate_command}")
    output = run_command(obfuscate_command)
    print(f"PyArmor output: {output}")

    # Update setup.py
    setup_py_path = os.path.join(obfuscated_path, 'setup.py')
    with open(setup_py_path, 'r') as f:
        setup_content = f.read()
    setup_content = setup_content.replace(f"name='{package_name}'", f"name='{obfuscated_name}'")
    setup_content = setup_content.replace("version='0.1'", "version='0.1-obf'")
    setup_content = setup_content.replace("packages=find_packages('src')",
                                          f"packages=find_packages('src'),\n    package_data={{'{package_name}': ['*.so', '*.dylib', '*.dll', '*.pyd']}},\n    include_package_data=True")
    with open(setup_py_path, 'w') as f:
        f.write(setup_content)

    print(f"Obfuscated package created at: {obfuscated_path}")

if __name__ == "__main__":
    base_path = os.path.expanduser("/home/gazi/Desktop/Work/custom_packages")
    source_package = os.path.join(base_path, "dummy_package")
    obfuscated_package = os.path.join(base_path, "obfuscated_packages")
    obfuscate_package(source_package, obfuscated_package)