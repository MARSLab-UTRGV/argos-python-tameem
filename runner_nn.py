import subprocess
import os
import re

class SimConfig:
    def __init__(self):
        self.random_seed = 2400
        self.max_sim_time = 1800
        self.num_robots = 2
        self.food_items = 70

    def modify_xml(self):
        try:
            with open('experiments/iAnt.xml', 'r') as f:
                xml_content = f.read()
            
            # Modify simulation parameters
            modified_content = xml_content.replace('"2400"', f'"{self.random_seed}"')
            modified_content = modified_content.replace('"1800"', f'"{self.max_sim_time}"')
            modified_content = modified_content.replace('quantity="2"', f'quantity="{self.num_robots}"')
            modified_content = modified_content.replace('FoodItemCount    = "70"', f'FoodItemCount    = "{self.food_items}"')
            
            with open('experiments/gant.xml', 'w') as f:
                f.write(modified_content)
                
            return True
            
        except Exception as e:
            print(f"Error modifying XML: {e}")
            return False

def run_simulation():
    try:
        result = subprocess.run(['./build/source/iant_main'],
                              capture_output=True,
                              text=True,
                              check=True)
        
        match = re.search(r'Fitness:(\d+\.?\d*)', result.stdout)
        if match:
            return float(match.group(1))
        else:
            return 0.0
            
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        print(f"Error output: {e.stderr}")
        return 0.0

def main():
    population_size = 20
    num_generations = 100
    
    for generation in range(num_generations):
        print(f"Generation {generation + 1}/{num_generations}")
        
        generation_fitness = []
        
        for individual in range(population_size):
            config = SimConfig()
            config.random_seed = config.random_seed + individual  # Ensure different random seed for each run
            if not config.modify_xml():
                print("Failed to modify XML file")
                continue
            
            fitness = run_simulation()
            generation_fitness.append(fitness)
            print(f"Individual {individual + 1}, Fitness: {fitness}")
        
        # Calculate statistics for this generation
        avg_fitness = sum(generation_fitness) / len(generation_fitness)
        best_fitness = max(generation_fitness)
        
        # Save the results of this generation
        with open('evolution_results.txt', 'a') as f:
            f.write(f"Generation {generation + 1}, Avg Fitness: {avg_fitness}, Best Fitness: {best_fitness}\n")
        
        print(f"Generation {generation + 1} complete.")
        print(f"Average Fitness: {avg_fitness}")
        print(f"Best Fitness: {best_fitness}")
        print("------------------------")

if __name__ == "__main__":
    main()