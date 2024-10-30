import numpy as np
import xml.etree.ElementTree as ET
import subprocess
import os
import re

class ChromosomeRL:
    def __init__(self, num_parameters=100, learning_rate=0.01):
        self.num_parameters = num_parameters
        self.learning_rate = learning_rate
        self.chromosome = np.random.randn(num_parameters)  # Initialize random chromosome
        self.best_fitness = float('-inf')
        self.best_chromosome = None
        
    def add_noise(self):
        """Add random noise to create exploration"""
        noise = np.random.normal(0, 0.1, size=self.num_parameters)
        return self.chromosome + noise
    
    def update(self, fitness, tried_chromosome):
        """Update chromosome based on reward (fitness)"""
        if fitness > self.best_fitness:
            self.best_fitness = fitness
            self.best_chromosome = tried_chromosome.copy()
            
        # Move chromosome slightly towards the tried chromosome if it performed well
        self.chromosome += self.learning_rate * (tried_chromosome - self.chromosome) * (fitness / 100.0)
        
    def get_chromosome_string(self, chromosome):
        """Convert chromosome array to the required string format"""
        # Modify this according to your chromosome string format
        chromosome_str = ""
        for i, value in enumerate(chromosome):
            chromosome_str += f"{i+384.0},1,{(i%24)+1},{17+i//24},{value};"
        return chromosome_str.rstrip(';')

def run_simulation(chromosome_str):
    """Run the ARGoS simulation with given chromosome and return fitness"""
    try:
        env = os.environ.copy()
        env['LD_LIBRARY_PATH'] = f"{env.get('LD_LIBRARY_PATH', '')}:{os.getcwd()}/build/source"
        
        # Read the base XML content
        with open('experiments/iAnt.xml', 'r') as f:
            xml_content = f.read()
            
        # Replace the chromosome in XML content
        modified_content = xml_content.replace('{chromosome}', chromosome_str)
        
        # Run simulation
        result = subprocess.run(['./build/source/iant_main'],
                              input=modified_content,
                              capture_output=True,
                              text=True,
                              check=True,
                              env=env)
        
        # Extract fitness
        match = re.search(r'Fitness:(\d+)', result.stdout)
        if match:
            return int(match.group(1))
        else:
            return 0
            
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        print(f"Error output: {e.stderr}")
        return 0

def main():
    # Initialize RL agent
    rl_agent = ChromosomeRL(num_parameters=100)  # Adjust number of parameters as needed
    
    # Training loop
    num_episodes = 1000
    for episode in range(num_episodes):
        # Generate new chromosome with exploration noise
        tried_chromosome = rl_agent.add_noise()
        
        # Convert chromosome to string format
        chromosome_str = rl_agent.get_chromosome_string(tried_chromosome)
        
        # Run simulation and get fitness
        fitness = run_simulation(chromosome_str)
        
        # Update chromosome based on fitness
        rl_agent.update(fitness, tried_chromosome)
        
        # Print progress
        print(f"Episode {episode + 1}/{num_episodes}")
        print(f"Fitness: {fitness}")
        print(f"Best Fitness So Far: {rl_agent.best_fitness}")
        
        # Save best chromosome periodically
        if episode % 10 == 0:
            best_chromosome_str = rl_agent.get_chromosome_string(rl_agent.best_chromosome)
            with open(f'best_chromosome_episode_{episode}.txt', 'w') as f:
                f.write(best_chromosome_str)

if __name__ == "__main__":
    main()

"""
This implementation includes:

A ChromosomeRL class that manages the chromosome and implements the learning algorithm:

Maintains the current chromosome and best chromosome seen
Implements exploration through random noise
Updates the chromosome based on fitness rewards
Helper functions:

run_simulation: Runs the ARGoS simulation with a given chromosome
get_chromosome_string: Converts the chromosome array to the required string format
A main training loop that:

Generates new chromosomes with exploration
Runs simulations to get fitness values
Updates the chromosome based on performance
Saves the best chromosomes periodically
You might need to adjust several parameters:

num_parameters: Set this to match your chromosome length
learning_rate: Controls how quickly the chromosome updates
noise_scale: In add_noise(), adjust the 0.1 value to control exploration
The reward scaling in update() method (currently dividing fitness by 100.0)
The chromosome string format in get_chromosome_string()
To improve this basic implementation, you could:

Add different exploration strategies (e.g., epsilon-greedy)
Implement more sophisticated RL algorithms (e.g., DDPG, PPO)
Add experience replay to learn from past experiences
Implement parallel evaluation of multiple chromosomes
Add early stopping if fitness reaches a target value
Implement adaptive learning rates
Add checkpointing and resume training capability
"""