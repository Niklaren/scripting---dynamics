# scripting & dynamics
Coursework for scripting & dynamics module. pathfinding/flocking algorithm. written in python.

Application is a maze search where agents use pathfinding to navigate and flocking to avoid overlapping.
The scripts are designed to work with the provided maya binary file, running the scripts in the expression editor will initialize the map and set the agents to navigate the maze.
The maze is modeled as a number of nodes, and the pathfinding uses the A* method with 8 directional movement.
Agents determine a random location on the map, and use the pathfinding algorithm to calculate the route they should take.
As they move they also adhere to a flocking behavior so that they do not occupy the same space and run into each other as they navigate.
