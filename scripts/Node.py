import maya.cmds as cmds
import math

class Node:
	
	def __init__(self,x,z,walkable):
		self.m_pos = [x,0,z]
		self.m_f=self.m_g=self.m_h=0
		self.m_whichList = "none"
		self.m_walkable = walkable
		if walkable == True:
			cmds.spaceLocator( p=(x,0,z) )
			cmds.rename( 'node' )
			self.m_locator = cmds.ls(sl=True)
		elif walkable == False:
			cube = cmds.polyCube()
			cmds.xform(cube,t=(x,0,z))
			cmds.scale(50,50,50, cube)
			cmds.rename( 'node' )
			self.m_locator = cmds.ls(sl=True)

	def reset(self):
		self.m_f=self.m_g=self.m_h=0
		self.m_whichList = "none"
		self.m_parent = []

	def __del__(self):
		cmds.delete(self.m_locator)

	def setOpen(self):
		self.m_whichList = "open"

	def setClosed(self):
		self.m_whichList = "closed"

	def whichList(self):
		return self.m_whichList

	def setParent(self,pPos):
		self.m_parent = pPos

	def getParent(self):
		return self.m_parent

	def isWalkable(self):
		return self.m_walkable

	def getX(self):
		return self.m_pos[0]

	def getZ(self):
		return self.m_pos[2]

	def getpos(self):
		return self.m_pos

	def getG(self):
		return self.m_g

	def setFGH(self,f,g,h):
		self.m_f=f
		self.m_g=g
		self.m_h=h
		return
