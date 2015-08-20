import maya.cmds as cmds
import maya.mel as mel
import math
import random
import time
import vectorMath
import pathfinding
reload(pathfinding)
import Agent
reload(Agent)

# GLOBAL VARIABLES

last_frame_number = 1
initialized = False

#store the agents
Agents = []
numberOfAgents = 20

#the exit target of all agents
trinket = [10, 0, 1]

#the distance to determine if an agent is nearby
agent_near_distance = 1.5
#weightings for each heading
goal_weight = 2.0
separation_weight = 1.0
cohesion_weight = 0.0
alignment_weight = 0.0

# this function is used to initialise the simulation
def init():
	print "Custom simulation initialised"
	# reset last frame counter
	global last_frame_number
	last_frame_number = 1
	
	global Agents
	global numberOfAgents
	for iter in range (0, numberOfAgents):
		new_agent = Agent.Agent()
		Agents.append(new_agent)
	

# this function is called every frame the simulation is run
def run(frame_number):
	# get the frame rate by using an internal MEL script
	frame_rate = mel.eval("currentTimeUnitToFPS")
	
	# calculate the amount of time in seconds between each frame
	frame_time = 1.0 / frame_rate
	
	# special case if we are on the first frame then initialise the simulation
	global initialized
	global last_frame_number
	if initialized == False:
		if frame_number == 1:
			initialized = True
			pathfinding.initialise()
			init()
			trink = cmds.polySphere()
			cmds.xform(trink,t=(trinket[0],0,trinket[2]))
			cmds.scale(50,50,50, trink)
			cmds.rename( 'trinket' )
	elif initialized == True:
		if frame_number == 1:
			last_frame_number = 1
	
	# check to see if we have an event to process this frame
	if (frame_number - last_frame_number) == 1:
		for agent in Agents:
			#print agent
			if (pathfinding.point_at_pos(trinket,agent.get_rounded_pos())==False):
				do_flocking_behaviour(agent)
				agent.agent_move(frame_time)
		
		print "Custom simulation run successfully at frame: "+str(frame_number)
		
		# we have successfully completed a run of the simulation
		# update the last frame number
		last_frame_number = frame_number

def do_flocking_behaviour(agent):
	# initialise our heading to 0
	agent_heading_vector = [0, 0, 0]
	#find all the neighbours of this agent
	neighbours = find_agents_within_distance(agent,agent_near_distance)
	#only get a new heading if there any agents close by
	
	if len(neighbours):
		agent_heading_vector = get_flocking_heading(agent, neighbours)
	#even if we have no neighbours we still want to move towards the goal
	goal_heading_vector = get_goal_heading(agent)
	global goal_weight
	goal_heading_vector = vectorMath.vector_scale(goal_heading_vector, goal_weight)
	agent_heading_vector = vectorMath.vector_add(agent_heading_vector, goal_heading_vector)
	#we now have the desired heading
	agent_heading_angle = vectorMath.get_heading_angle_from_vector(agent_heading_vector)
	##print agent,agent_heading_angle
	
	#agent.turn_towards_heading(agent_heading_angle)# decided not to use this
	agent.set_agent_heading(agent_heading_angle) #used this instead. better.

def get_flocking_heading(agent_name, neighbours):
	# initialise the heading vector for this agent
	heading_vector = [0, 0, 0]
	
	separation_heading_vector = get_separation_heading(agent_name, neighbours)
	cohesion_heading_vector = get_cohesion_heading(agent_name, neighbours)
	alignment_heading_vector = get_alignment_heading(neighbours)
	
	# apply the weighting to each heading vector and then add them altogether
	# to get the overall heading vector
	global separation_weight
	global cohesion_weight
	global alignment_weight
	separation_heading_vector = vectorMath.vector_scale(separation_heading_vector, separation_weight)
	cohesion_heading_vector = vectorMath.vector_scale(cohesion_heading_vector, cohesion_weight)
	alignment_heading_vector = vectorMath.vector_scale(alignment_heading_vector, alignment_weight)
	heading_vector = vectorMath.vector_add(heading_vector, separation_heading_vector)
	heading_vector = vectorMath.vector_add(heading_vector, cohesion_heading_vector)
	heading_vector = vectorMath.vector_add(heading_vector, alignment_heading_vector)
	
	return heading_vector

def find_agents_within_distance(agent, distance):
	# neighbours is a list that will contain a list of nearby agents
	neighbours = []
	# get the position of the agent
	agent_pos = agent.get_agent_position()
	# FOR every agent
	global Agents
	for otherAgent in Agents:
		# get the agent position of the potential neighbour
		neighbour_pos = otherAgent.get_agent_position()
		# calculate the distance between the potential neighbour and the agent
		Ndistance = vectorMath.get_distance_between_points(agent_pos, neighbour_pos)
		#if the agent we're checking is the one we passed in it cant be its own neighbour
		if(agent.get_agent() == otherAgent.get_agent()):
			pass
		# if this distance is less than distance passed into the function [this is the distance that defines the agent "awareness circle"] then add it to the neighbours list
		elif Ndistance < distance:
			neighbours.append(otherAgent)
	
	return neighbours

def get_goal_heading(agent):
	# initialise the heading vector that will hold the  goal heading
	goal_heading_vector = [0, 0, 0]
	
	# if we have reached the end of the path or otherwise require a new goal do it here
	if(pathfinding.need_new_goal(agent.get_goal(),agent.get_rounded_pos())):
		agent.new_goal()
	
	# check if we need to start heading towards the next step in the path
	agent.check_step()
	
	#get goal vector from our current position and the next spot in our path
	goal_heading_vector = vectorMath.get_vector_between_points(agent.get_agent_position(),agent.get_current_step())
	
	# normalise goal vector
	goal_heading_vector = vectorMath.vector_normalise(goal_heading_vector)
	
	return goal_heading_vector

def get_alignment_heading(neighbours):
	# initialise the heading vector that will hold the alignment heading
	alignment_heading_vector = [0, 0, 0]
	neighbour_vector = [0, 0, 0]
	# get the number of neighbouring agents in the neighbours list [find the length of the list]
	number_of_neighbours = len(neighbours)
	# IF we have 1 or more agents in the neighbours list
	if number_of_neighbours > 0:
		# FOR every neighbour in the neighbours list
		for neighbour in neighbours:
			# get the heading of the neighbour as a vector
			neighbour_vector = neighbour.get_agent_heading_vector()
			# add this heading to the alignment_heading_vector
			alignment_heading_vector = vectorMath.vector_add(alignment_heading_vector, neighbour_vector)
		# calculate the averaged alignment_heading_vector
		alignment_heading_vector[0] = alignment_heading_vector[0] / number_of_neighbours
		alignment_heading_vector[1] = alignment_heading_vector[1] / number_of_neighbours
		alignment_heading_vector[2] = alignment_heading_vector[2] / number_of_neighbours
		# normalise alignment vector
		alignment_heading_vector = vectorMath.vector_normalise(alignment_heading_vector)
	
	return alignment_heading_vector

def get_separation_heading(agent_name, neighbours):
	# initialise the heading vector that will hold the separation heading
	separation_heading_vector = [0, 0, 0]
	heading_vector = [0, 0, 0]

	# get the number of neighbouring agents in the neighbours list [find the length of the list]
	number_of_neighbours = len(neighbours)
	# IF we have 1 or more agents in the neighbours list
	if number_of_neighbours > 0:
		# get the position of the agent called agent_name
		agent_pos = agent_name.get_agent_position()
		# FOR every neighbour in the neighbours list
		for neighbour in neighbours:
			# get the position of the neighbour
			neighbour_pos = neighbour.get_agent_position()
			# calculate the heading vector from the neighbours position to the position of our agent
			heading_vector = vectorMath.get_vector_between_points(neighbour_pos, agent_pos)
			# normalise the heading vector to give it a size of 1 [needed so averaging the vector will work as expected
			heading_vector = vectorMath.vector_normalise(heading_vector)
			# add this heading vector to the separation_heading_vector
			separation_heading_vector = vectorMath.vector_add(separation_heading_vector, heading_vector)
		# calculate the averaged separation_heading_vector
		separation_heading_vector[0] = separation_heading_vector[0] / number_of_neighbours
		separation_heading_vector[1] = separation_heading_vector[1] / number_of_neighbours
		separation_heading_vector[2] = separation_heading_vector[2] / number_of_neighbours
		# normalise the separation_heading_vector
		separation_heading_vector = vectorMath.vector_normalise(separation_heading_vector)
	
	return separation_heading_vector

def get_cohesion_heading(agent_name, neighbours):
	# initialise the heading vector that will hold the separation heading
	cohesion_heading_vector = [0, 0, 0]

	# get the number of neighbouring agents in the neighbours list [find the length of the list]
	number_of_neighbours = len(neighbours)
	# IF we have 1 or more agents in the neighbours list
	if number_of_neighbours > 0:
		# get the position of the agent called agent_name
		agent_pos = agent_name.get_agent_position()
		# initialise a a vector to hold the average of all the neighbours positions to [0, 0, 0]
		neighbours_average_vector = [0, 0, 0]
		#FOR every neighbour in the neighbours list
		for neighbour in neighbours:
			# get the neighbours position
			neighbour_pos = neighbour.get_agent_position()
			# add it to the vector to hold the average positions
			neighbours_average_vector = vectorMath.vector_add(neighbours_average_vector, neighbour_pos)
		# calculate the averaged neighbours position
		neighbours_average_vector[0] = neighbours_average_vector[0] / number_of_neighbours
		neighbours_average_vector[1] = neighbours_average_vector[1] / number_of_neighbours
		neighbours_average_vector[2] = neighbours_average_vector[2] / number_of_neighbours
		# calculate the cohesion_heading_vector from the position of the agent called agent_name to the averaged neighbours position
		cohesion_heading_vector = vectorMath.get_vector_between_points(agent_pos, neighbours_average_vector)
		# normalise the cohesion_heading_vector
		cohesion_heading_vector = vectorMath.vector_normalise(cohesion_heading_vector)
	return cohesion_heading_vector
