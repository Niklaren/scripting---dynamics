import maya.cmds as cmds
import maya.mel as mel
import math
import time
import Node
reload (Node)
import vectorMath
reload(vectorMath)

map_width = 15
map_height = 15

trinket = [9, 0, 9]

#lists
locator_nodes = []
node_list = [[0 for y in xrange(map_height)] for x in xrange(map_width)]
#node_list = [[]]
open_list = []
#path = []
map = [ ['o','o','o','o','o','i','o','i','o','o','o','i','o','o','o'],
		['o','o','i','o','o','i','o','o','o','i','o','i','o','o','o'],
		['o','i','o','i','i','i','o','i','o','i','o','i','o','o','o'],
		['o','o','o','o','o','o','o','i','o','i','o','o','o','o','o'],
		['i','i','i','i','o','o','o','i','o','i','o','i','i','i','i'],
		['o','o','o','o','i','i','o','i','i','i','o','o','o','o','o'],
		['o','i','o','i','i','o','o','o','o','i','i','i','i','i','o'],
		['o','i','o','o','i','i','i','i','o','i','o','o','o','i','o'],
		['o','i','o','o','i','o','o','i','o','i','o','i','o','i','o'],
		['o','i','o','i','i','i','o','i','o','o','o','i','o','o','o'],
		['o','o','o','o','o','i','o','i','o','i','o','i','o','i','o'],
		['o','i','o','o','o','o','o','i','o','o','o','i','i','i','o'],
		['o','i','i','i','o','i','i','i','o','i','i','i','o','i','o'],
		['o','i','o','o','o','o','o','i','o','i','o','i','o','i','o'],
		['o','i','o','o','i','o','o','o','o','o','o','i','o','o','o']
		]

# this function is used to initialise the pathfinding map
def initialise():
	#print "Initialising Map"
	for x in range(0,map_width):
		for z in range(0,map_height):
			walkable = True
			if map[x][z] == "i" :
				walkable = False
			
			node_list[x][z] = Node.Node(x,z,walkable)

def reset(path):
	#print "reset"
	global open_list
	global node_list
	
	for x in range(0,map_width):
		for z in range(0,map_height):
			node_list[x][z].reset()
	open_list = []
	
	del path[:]


def cornersOK (pX,pZ,xIter,zIter):
	# If there's no corner to be cut it's obviously fine
	if xIter == 0 or zIter == 0:
		return True
	
	if xIter == -1 and zIter == -1:			#bottom left corner
		if node_list[pX-1][pZ].isWalkable() == False or node_list[pX][pZ-1].isWalkable() == False :
			return False
	elif xIter == 1 and zIter == -1:		#bottom right corner
		if node_list[pX+1][pZ].isWalkable() == False or node_list[pX][pZ-1].isWalkable() == False :
			return False
	elif xIter == -1 and zIter == 1:		#top left corner
		if node_list[pX-1][pZ].isWalkable() == False or node_list[pX][pZ+1].isWalkable() == False :
			return False
	elif xIter == 1 and zIter == 1:		#top right corner
		if node_list[pX+1][pZ].isWalkable() == False or node_list[pX][pZ+1].isWalkable() == False :
			return False
	
	return True

def need_new_goal(goal,pos):
	#print "goal check"
	if (point_at_pos(goal, pos)):
		return True
	# if target is unreachable
	if (node_list[goal[0]][goal[2]].isWalkable()==False):
		return True
	return False

def point_at_pos(point,pos):
	#print "p at p"
	if (point[0]==pos[0] and point[2]==pos[2]):
		return True
	return False

def point_on_obstacle(point):
	#print "p on o"
	if (node_list[point[0]][point[2]].isWalkable()==False):
		return True
	return False

def pathfind(start,goal,path):
	global open_list
	global node_list
	
	reset(path)
	
	#could have a bounds check here if i wanted
	#if start.x<0 : start.x = 0
	
	# Add the starting square (or node) to the open list.
	open_list.insert(0,node_list[start[0]][start[2]])

	# Repeat the following:
	searching = True
	
	while(searching):
		#print("in open_list")
		# Pop the first item off the open list. (as it's the one with lowest f)
		pNode = open_list.pop(0)
		pNode.setClosed()		# Switch it to the closed list.
		
		# For each of the 8 squares adjacent to this current node
		for xIter in range (-1, 2):		#for -1,0,1
			for zIter in range (-1, 2):
				iX=pNode.getX()+xIter
				iZ=pNode.getZ()+zIter
				if ((iZ<0 or iZ>map_height-1) or (iX<0 or iX>map_width-1)): #if out of array bounds
					#print "out of bounds"
					pass
				else:
					cNode = node_list[iX][iZ]
					# If it is not walkable or if it is on the closed list, ignore it. 
					if ( (xIter==0 and zIter==0) or (cNode.isWalkable() == False) or (cNode.whichList() == "closed") ) :
						#print "ignore"
						pass
					elif (cornersOK(pNode.getX(),pNode.getZ(),xIter,zIter) == True):	#Otherwise do the following.
						# If it isnt on the open list, add it to the open list. set the parent also
						if cNode.whichList() != "open" :
							#print("new node")
							cNode.setOpen()
							open_list.append(cNode)
							cNode.setParent(pNode.getpos())
							# Record the F, G, and H costs of the square. 
							#G = the movement cost to move from the starting point A to a given square on the grid, following the path generated to get there.
							g = pNode.getG() + math.sqrt((abs(xIter)+abs(zIter)))
							#H = the estimated movement cost to move from that given square on the grid to the final destination, point B.
							h = vectorMath.get_vector_length(vectorMath.get_vector_between_points(goal,cNode.getpos()))
							#F = The combined total of g and h
							f = g + h
							#print(f,g,h)
							cNode.setFGH(f,g,h)
						else:# If it is on the open list already,
							# using G cost as the measure. A lower G cost means that this is a better path.
							#G = the movement cost to move from the starting point A to a given square on the grid, following the path generated to get there.
							g = pNode.getG() + math.sqrt((abs(xIter)+abs(zIter)))
							# check to see if this path to that square is better,
							if g < cNode.getG():
								# If so, change the parent of the square to the current square,
								cNode.setParent(pNode.getpos())
								# and recalculate the F score of the square.
								f = g + h
								cNode.setFGH(f,g,h)
					else:
						#print ("bad corner")
						pass
		# end searching through neighbours
		
		# resort the list to account for the change.
		# sorting by h can be faster computatationally, but is less
		# likely to give the fastest path
		open_list.sort(key=lambda x: x.m_f)
		
		# Stop when you:
		# Add the target square to the closed list, in which case the path has been found
		if node_list[goal[0]][goal[2]].whichList() == 'closed' :
			#print("goal found")
			searching = False
		# Fail to find the target square, and the open list is empty. In this case, there is no path.
		if len(open_list) == 0 :
			#print("open list empty")
			searching = False
			return start # no path so path to finish is where we are. we will not move.
	
	# Save the path. Working backwards from the target square, go from each square to its parent square until you reach the starting square. That is your path.
	path.insert(0,node_list[goal[0]][goal[2]].getpos())
	while path[0] != start:
		p_pos = node_list[path[0][0]][path[0][2]].getParent()
		path.insert(0,p_pos)
	

