import maya.cmds as cmds
import maya.mel as mel
import random
import math
import vectorMath
import pathfinding
reload(pathfinding)

class Agent:
	
	def __init__(self):
		x=random.randint(0,14)
		y=0
		z=random.randint(0,14)
		position = [x,y,z]
		while(pathfinding.point_on_obstacle(position)):
			x=random.randint(0,14)
			z=random.randint(0,14)
			position = [x,y,z]
		
		self.m_goal = position
		
		self.m_path = [[]]
		
		acone = cmds.polyCone()
		cmds.scale(20,20,20, acone)
		cmds.rotate( '90deg', 0, 0, acone )
		cmds.rename( 'agent' )
		self.m_cone = cmds.ls(sl=True)
		
		for cone in self.m_cone:
			# set the initial position
			cmds.addAttr(cone, longName="initialPositionX", defaultValue=0.0, keyable=True)
			cmds.setAttr(cone+".initialPositionX", position[0])
			cmds.addAttr(cone, longName="initialPositionY", defaultValue=0.0, keyable=True)
			cmds.setAttr(cone+".initialPositionY", position[1])
			cmds.addAttr(cone, longName="initialPositionZ", defaultValue=0.0, keyable=True)
			cmds.setAttr(cone+".initialPositionZ", position[2])
			
			cmds.setAttr(cone+".translateX", cmds.getAttr(cone+".initialPositionX"))
			cmds.setAttr(cone+".translateY", cmds.getAttr(cone+".initialPositionY"))
			cmds.setAttr(cone+".translateZ", cmds.getAttr(cone+".initialPositionZ"))
			
			cmds.addAttr(cone, longName="initialHeading", defaultValue=0.0, keyable=True)
			cmds.setAttr(cone+".initialHeading", cmds.getAttr(cone+".rotateY"))
			
			cmds.setAttr(cone+".rotateY", cmds.getAttr(cone+".initialHeading"))
			
			# add speed attribute if we need it
			cmds.addAttr(cone, longName="initialSpeed", defaultValue=3.0, keyable=True)
			cmds.addAttr(cone, longName="speed", defaultValue=cmds.getAttr(cone+".initialSpeed"), keyable=True)
			
			#set the initial speed
			cmds.setAttr(cone+".speed", cmds.getAttr(cone+".initialSpeed"))
		

	def reset(self):
		pass

	def __del__(self):
		cmds.delete(self.m_cone)

	def new_goal(self):
		self.m_goal[0]=random.randint(0,14)
		self.m_goal[2]=random.randint(0,14)
		
		pos = self.get_rounded_pos()
		
		while(pathfinding.point_on_obstacle(self.m_goal) or pathfinding.point_at_pos(self.m_goal,pos)):
			self.m_goal[0]=random.randint(0,14)
			self.m_goal[2]=random.randint(0,14)
		
		pathfinding.pathfind(pos,self.m_goal,self.m_path)
		
		self.m_step = 0

	def check_step(self):
		pos = self.get_rounded_pos()
		
		if(pathfinding.point_at_pos(pos,self.m_path[self.m_step])):
			self.m_step += 1

	def get_current_step(self):
		return self.m_path[self.m_step]

	def get_path(self):
		return self.m_path

	def get_agent(self):
		return self.m_cone[0]

	def get_goal(self):
		return self.m_goal

	def get_rounded_pos(self):
		pos = self.get_agent_position()
		pos[0] = int(round(pos[0])) #round the position to nearest int for use with pathfind
		pos[1] = int(round(pos[1]))
		pos[2] = int(round(pos[2]))
		return pos

	def get_agent_position(self):
		position = []
		for cone in self.m_cone:
			position.append(cmds.getAttr(cone+".translateX"))
			position.append(cmds.getAttr(cone+".translateY"))
			position.append(cmds.getAttr(cone+".translateZ"))
		return position

	def get_agent_heading_vector(self):
		for cone in self.m_cone:
			# get agent heading angle
			heading_angle = cmds.getAttr(cone+".rotateY")
			
			# convert heading angle to a heading vector
			heading_vector = vectorMath.get_vector_from_heading_angle(heading_angle)
		
		return heading_vector

	def get_agent_heading(self):
		for cone in self.m_cone:
			return cmds.getAttr(cone+".rotateY")

	def set_agent_heading(self, heading):
		for cone in self.m_cone:
			cmds.setAttr(cone+".rotateY", heading)

	def agent_move(self, frame_time):
		# get the heading angle
		for cone in self.m_cone:
			heading = cmds.getAttr(cone+".rotateY");
			
			# get the speed (in units per second)
			speed = cmds.getAttr(cone+".speed")
			
			# calculate the overall distance moved between frames
			overall_distance = speed*frame_time
			
			# calculate the direction to go in
			distanceX = overall_distance*math.sin(math.radians(heading));
			distanceZ = overall_distance*math.cos(math.radians(heading));
			
			# update the position based on the calculated direction and speed
			cmds.setAttr(cone+".translateX", cmds.getAttr(cone+".translateX")+distanceX)
			cmds.setAttr(cone+".translateZ", cmds.getAttr(cone+".translateZ")+distanceZ)

	# def turn_towards_heading(self, target_heading):
		# for cone in self.m_cone:
			# current_heading = self.get_agent_heading()
			
			# difference = target_heading - current_heading
			# #-360--180 +, 0--180 -, 0-180 +, 180-360 -,
			# if(difference > 180):
				# #+
				# cmds.setAttr(cone+".rotateY", current_heading-1)
			# elif(difference > 0):
				# #-
				# cmds.setAttr(cone+".rotateY", current_heading+1)
			# elif(difference == 0):
				# pass
			# elif(difference > -180):
				# #+
				# cmds.setAttr(cone+".rotateY", current_heading-1)
			# elif(difference > -360):
				# #-
				# cmds.setAttr(cone+".rotateY", current_heading+1)
			# else:
				# ##print "unexpected angle"
				# pass

	def reset_agent_position():
		for cone in self.m_cone:
			if cmds.objExists(cone+".initialPositionX") is False:
				cmds.addAttr(cone, longName="initialPositionX", defaultValue=0.0, keyable=True)
			if cmds.objExists(cone+".initialPositionY") is False:
				cmds.addAttr(cone, longName="initialPositionY", defaultValue=0.0, keyable=True)
			if cmds.objExists(cone+".initialPositionZ") is False:
				cmds.addAttr(cone, longName="initialPositionZ", defaultValue=0.0, keyable=True)
			
			cmds.setAttr(cone+".initialPositionX", cmds.getAttr(cone+".translateX"))
			cmds.setAttr(cone+".initialPositionY", cmds.getAttr(cone+".translateY"))
			cmds.setAttr(cone+".initialPositionZ", cmds.getAttr(cone+".translateZ"))        

			if cmds.objExists(cone+".initialHeading") is False:
				cmds.addAttr(cone, longName="initialHeading", defaultValue=0.0, keyable=True)
			cmds.setAttr(cone+".initialHeading", cmds.getAttr(cone+".rotateY"))

			if cmds.objExists(cone+".initialSpeed") is False:
				cmds.addAttr(cone, longName="initialSpeed", defaultValue=1.0, keyable=True)
			if cmds.objExists(cone+".speed") is False:
				cmds.addAttr(cone, longName="speed", defaultValue=cmds.getAttr(cone+".initialSpeed"), keyable=True)
			cmds.setAttr(cone+".initialSpeed", cmds.getAttr(cone+".speed"))