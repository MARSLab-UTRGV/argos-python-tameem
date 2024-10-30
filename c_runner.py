import subprocess
import os
import re

MAIN_FILE_PATH = './build/source/iant_main'

try:
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{env.get('LD_LIBRARY_PATH', '')}:{os.getcwd()}/build/source"
    
    with open('experiments/iAnt.xml', 'r') as f:
        xml_content = f.read()
    
    result = subprocess.run(
        [MAIN_FILE_PATH], 
        input=xml_content,
        capture_output=True,
        text=True,
        check=True,
        env=env
    )

    match = re.search(r'Fitness:(\d+)', result.stdout)
    
    # Parse output to get fitness value
    if match:
        fitness = int(match.group(1))
        print(f"Fitness: {fitness}")
    else:
        print("Fitness value not found in output")
    # match = re.search(r"Fitness:(\d+\.?\d*)", result.stdout)
    # if match:
    #     fitness = float(match.group(1))
    #     print(f"Captured fitness value: {fitness}")
    
except subprocess.CalledProcessError as e:
    print(f"Error occurred: {e}")
    print(f"Error output: {e.stderr}")