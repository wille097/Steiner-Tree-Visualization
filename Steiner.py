#!/usr/local/bin/python

# Author: Clint Cooper
# Date: 12/05/14
# The code that follows is not good, is not well organized, is not my best work
# but it does work. It solves the Minimum Steiner Problem in relatively small time
# with Rectilinear in O(n^3 * logn) and Graphical in O(n^4 * logn)
# If you are reading this or using this, please enjoy!

from Tkinter import *
import random
import math
import sys

tk = Tk()
tk.wm_title("Steiner Trees")

global OriginalPoints
OriginalPoints = []
global RectSteinerPoints
RectSteinerPoints = []
global GraphSteinerPoints
GraphSteinerPoints = []
global RMST
RMST = []
global RSMT
RSMT = []
global GMST
GMST = []
global GSMT
GSMT = []

class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.d = 0
		self.deg = 0
		self.edges = []
		self.MSTedges = []
	def update(self, edge):
		self.d += 1
		self.edges.append(edge)
	def reset(self):
		self.d = 0
		self.edges = []
		self.deg = 0
		self.MSTedges = []
	def MSTupdate(self, edge):
		self.deg += 1
		self.MSTedges.append(edge)

class Line:
	def __init__(self, p1, p2, w):
		self.points = []
		self.points.append(ref(p1))
		self.points.append(ref(p2))
		self.w = w
	def getOther(self, pt):
		if pt == self.points[0].get():
			return self.points[1]
		elif pt == self.points[1].get():
			return self.points[0]
		else:
			print "This is an Error. The line does not contain points that make sense."
	def getFirst(self):
		return self.points[0]
	def getLast(self):
		return self.points[1]

class ref:
	def __init__(self, obj): 
		self.obj = obj
	def get(self):	
		return self.obj
	def set(self, obj):	  
		self.obj = obj

class UnionFind: # I didn't write this. It was imported from somewhere on the internet. Sorry...
	"""Union-find data structure.

	Each unionFind instance X maintains a family of disjoint sets of
	hashable objects, supporting the following two methods:

	- X[item] returns a name for the set containing the given item.
	  Each set is named by an arbitrarily-chosen one of its members; as
	  long as the set remains unchanged it will keep the same name. If
	  the item is not yet part of a set in X, a new singleton set is
	  created for it.

	- X.union(item1, item2, ...) merges the sets containing each item
	  into a single larger set.  If any item is not yet part of a set
	  in X, it is added to X as one of the members of the merged set.
	"""

	def __init__(self):
		"""Create a new empty union-find structure."""
		self.weights = {}
		self.parents = {}

	def __getitem__(self, object):
		"""Find and return the name of the set containing the object."""

		# check for previously unknown object
		if object not in self.parents:
			self.parents[object] = object
			self.weights[object] = 1
			return object

		# find path of objects leading to the root
		path = [object]
		root = self.parents[object]
		while root != path[-1]:
			path.append(root)
			root = self.parents[root]

		# compress the path and return
		for ancestor in path:
			self.parents[ancestor] = root
		return root
		
	def __iter__(self):
		"""Iterate through all items ever found or unioned by this structure."""
		return iter(self.parents)

	def union(self, *objects):
		"""Find the sets containing the objects and merge them all."""
		roots = [self[x] for x in objects]
		heaviest = max([(self.weights[r],r) for r in roots])[1]
		for r in roots:
			if r != heaviest:
				self.weights[heaviest] += self.weights[r]
				self.parents[r] = heaviest

def addMousePoint(event):
	addpt = True
	if OriginalPoints == []:
		if (event.x < 10) and (event.x >= 500) and (event.y < 10) and (event.y >= 500):
				addpt = False
	else:
		for pt in OriginalPoints:
			dist = math.sqrt(pow((event.x - pt.x),2) + pow((event.y - pt.y),2))
			if dist < 11:
				addpt = False
			if (event.x < 10) and (event.x >= 500) and (event.y < 10) and (event.y >= 500):
				addpt = False
	if addpt ==  True:
			addPoint(event.x, event.y)

def addPoint(x, y):
	global RMST
	del RMST[:]
	global RSMT
	del RSMT[:]
	global GMST
	del GMST[:]
	global GSMT
	del GSMT[:]
	canvas.create_oval(x-5,y-5,x+5,y+5, outline="black", fill="white", width=1)
	point = Point(x, y)
	global OriginalPoints
	OriginalPoints.append(point)

def Kruskal(SetOfPoints, type): # I actually did write this :D
	"""Kruskal's algorithm: sort edges by weight, and add them one at a time while avoiding cycles
	Takes any set of Point instances and converts to a dictonary via edge crawling 
	Takes the dictonary and iterates through each level to discover neighbors and weights
	Takes list of point index pairs and converts to list of Lines then returns
	"""

	for i in xrange(0,len(SetOfPoints)):
		SetOfPoints[i].reset()
	for i in xrange(0,len(SetOfPoints)):
		for j in xrange(i,len(SetOfPoints)):
			if i != j:
				if type == "R":
					dist = (abs(SetOfPoints[i].x-SetOfPoints[j].x) 
						+ abs(SetOfPoints[i].y - SetOfPoints[j].y))
				elif type == "G":
					dist = math.sqrt(pow((SetOfPoints[i].x-SetOfPoints[j].x),2) + 
					pow((SetOfPoints[i].y - SetOfPoints[j].y),2))
				else: 
					"All of the Errors!"
				line = Line(SetOfPoints[i], SetOfPoints[j], dist)
				SetOfPoints[i].update(line)
				SetOfPoints[j].update(line)
			else:
				dist = 100000
				line = Line(SetOfPoints[i], SetOfPoints[j], dist)
				SetOfPoints[i].update(line)
			
	G = {}
	for i in xrange(0,len(SetOfPoints)):
		off = 0
		subset = {}
		for j in xrange(0,len(SetOfPoints[i].edges)):
			subset[j] = SetOfPoints[i].edges[j].w
		G[i] = subset

	subtrees = UnionFind()
	tree = []
	for W,u,v in sorted((G[u][v],u,v) for u in G for v in G[u]):
		if subtrees[u] != subtrees[v]:
			tree.append([u,v])
			subtrees.union(u,v)

	MST = []
	for i in xrange(0,len(tree)):
		point1 = SetOfPoints[tree[i][0]]
		point2 = SetOfPoints[tree[i][1]]
		for j in xrange(0,len(point1.edges)):
			if point2 == point1.edges[j].getOther(point1).get():
				point1.MSTupdate(point1.edges[j])
				point2.MSTupdate(point1.edges[j])
				MST.append(point1.edges[j])
	return MST  

def DeltaMST(SetOfPoints, TestPoint, type):

	if type == "R":
		MST = Kruskal(SetOfPoints, "R")
	else:
		MST = Kruskal(SetOfPoints, "G")

	cost1 = 0
	for i in xrange(0,len(MST)):
		cost1 += MST[i].w

	combo = SetOfPoints + [TestPoint]

	if type == "R":
		MST = Kruskal(combo, "R")
	else:
		MST = Kruskal(combo, "G")

	cost2 = 0
	for i in xrange(0,len(MST)):
		cost2 += MST[i].w
	return cost1 - cost2

def HananPoints(SetOfPoints):
	totalSet = SetOfPoints
	SomePoints = []
	for i in xrange(0,len(totalSet)):
		for j in xrange(i,len(totalSet)):
			if i != j:
				SomePoints.append(Point(totalSet[i].x, totalSet[j].y))
				SomePoints.append(Point(totalSet[j].x, totalSet[i].y))
	return SomePoints 

def BrutePoints(SetOfPoints):
	if SetOfPoints != []:
		SomePoints = []
		xmax = (max(SetOfPoints,key=lambda x: x.x)).x
		xmin = (min(SetOfPoints,key=lambda x: x.x)).x
		ymax = (max(SetOfPoints,key=lambda x: x.y)).y
		ymin = (min(SetOfPoints,key=lambda x: x.y)).y

		rangex = range(xmin,xmax)
		rangey = range(ymin,ymax)
		for i in rangex[::10]:
			for j in rangey[::10]:
				SomePoints.append(Point(i,j))
		return SomePoints
	else:
		return []

def computeRMST():
	canvas.delete("all")
	global RMST
	if RMST == []:
		
		RMST = Kruskal(OriginalPoints, "R")

	RMSTminDist = 0
	for i in xrange(0,len(RMST)):
		RMSTminDist += RMST[i].w
		decision = random.randint(0,1)
		if decision == 0:
			canvas.create_line(RMST[i].points[0].get().x, RMST[i].points[0].get().y, 
				RMST[i].points[0].get().x, RMST[i].points[1].get().y, width=2)
			canvas.create_line(RMST[i].points[0].get().x, RMST[i].points[1].get().y, 
				RMST[i].points[1].get().x, RMST[i].points[1].get().y, width=2)
		else:
			canvas.create_line(RMST[i].points[0].get().x, RMST[i].points[0].get().y, 
				RMST[i].points[1].get().x, RMST[i].points[0].get().y, width=2)
			canvas.create_line(RMST[i].points[1].get().x, RMST[i].points[0].get().y,
			 	RMST[i].points[1].get().x, RMST[i].points[1].get().y, width=2)

	for i in xrange(0,len(OriginalPoints)):
		canvas.create_oval(OriginalPoints[i].x-5,OriginalPoints[i].y-5,
			OriginalPoints[i].x+5,OriginalPoints[i].y+5, outline="black", fill="white", width=1)
	RMSTtext.set(str(RMSTminDist))

def computeRSMT():
	canvas.delete("all")
	global RSMT
	if RSMT == []:
		global RectSteinerPoints
		del RectSteinerPoints[:]
		Candidate_Set = [0]

		while Candidate_Set != []:
			maxPoint = Point(0,0)
			Candidate_Set = [x for x in HananPoints(OriginalPoints + RectSteinerPoints) if DeltaMST(OriginalPoints + RectSteinerPoints,x, "R") > 0]
			cost = 0
			for pt in Candidate_Set:
				DeltaCost = DeltaMST(OriginalPoints + RectSteinerPoints, pt, "R")
				if DeltaCost > cost:
					maxPoint = pt
					cost = DeltaCost
			if (maxPoint.x != 0 and maxPoint.y != 0):
				RectSteinerPoints.append(maxPoint)
			for pt in RectSteinerPoints:
				if pt.deg <= 2:
					RectSteinerPoints.remove(pt)
				else:
					pass

		RSMT = Kruskal(OriginalPoints+RectSteinerPoints, "R")

	RSMTminDist = 0
	for i in xrange(0,len(RSMT)):
		RSMTminDist += RSMT[i].w
		decision = random.randint(0,1)
		if decision == 0:
			canvas.create_line(RSMT[i].points[0].get().x, RSMT[i].points[0].get().y, 
				RSMT[i].points[0].get().x, RSMT[i].points[1].get().y, width=2)
			canvas.create_line(RSMT[i].points[0].get().x, RSMT[i].points[1].get().y, 
				RSMT[i].points[1].get().x, RSMT[i].points[1].get().y, width=2)
		else:
			canvas.create_line(RSMT[i].points[0].get().x, RSMT[i].points[0].get().y, 
				RSMT[i].points[1].get().x, RSMT[i].points[0].get().y, width=2)
			canvas.create_line(RSMT[i].points[1].get().x, RSMT[i].points[0].get().y, 
				RSMT[i].points[1].get().x, RSMT[i].points[1].get().y, width=2)

	for i in xrange(0,len(RectSteinerPoints)):
		canvas.create_oval(RectSteinerPoints[i].x-5,RectSteinerPoints[i].y-5,
			RectSteinerPoints[i].x+5,RectSteinerPoints[i].y+5, outline="black", fill="black", width=1)

	for i in xrange(0,len(OriginalPoints)):
		canvas.create_oval(OriginalPoints[i].x-5,OriginalPoints[i].y-5,
			OriginalPoints[i].x+5,OriginalPoints[i].y+5, outline="black", fill="white", width=1)

	RSMTtext.set(str(RSMTminDist))

def computeGMST():
	canvas.delete("all")
	global GMST
	if GMST == []:

		GMST = Kruskal(OriginalPoints, "G")

	GMSTminDist = 0
	for i in xrange(0,len(GMST)):
		GMSTminDist += GMST[i].w
		canvas.create_line(GMST[i].points[0].get().x, GMST[i].points[0].get().y, 
			GMST[i].points[1].get().x, GMST[i].points[1].get().y, width=2)
		
	for i in xrange(0,len(OriginalPoints)):
		canvas.create_oval(OriginalPoints[i].x-5,OriginalPoints[i].y-5,
			OriginalPoints[i].x+5,OriginalPoints[i].y+5, outline="black", fill="white", width=1)

	GMSTtext.set(str(round(GMSTminDist, 2)))

def computeGSMT(): 
	canvas.delete("all")
	global GSMT
	if GSMT == []:
		global GraphSteinerPoints
		del GraphSteinerPoints[:]
		Candidate_Set = [0]

		while Candidate_Set != []:
			maxPoint = Point(0,0)
			Candidate_Set = [x for x in BrutePoints(OriginalPoints + GraphSteinerPoints) if DeltaMST(OriginalPoints + GraphSteinerPoints, x, "G") > 0]
			cost = 0
			for pt in Candidate_Set:
				DeltaCost = DeltaMST(OriginalPoints + GraphSteinerPoints, pt, "G")
				if DeltaCost > cost:
					maxPoint = pt
					cost = DeltaCost

			if (maxPoint.x != 0 and maxPoint.y != 0):
				GraphSteinerPoints.append(maxPoint)
			for pt in GraphSteinerPoints:
				if pt.deg <= 2:
					GraphSteinerPoints.remove(pt)
				else:
					pass

		GSMT = Kruskal(OriginalPoints+GraphSteinerPoints, "G")

	GSMTminDist = 0
	for i in xrange(0,len(GSMT)):
		GSMTminDist += GSMT[i].w
		canvas.create_line(GSMT[i].points[0].get().x, GSMT[i].points[0].get().y, 
			GSMT[i].points[1].get().x, GSMT[i].points[1].get().y, width=2)

	for i in xrange(0,len(GraphSteinerPoints)):
		canvas.create_oval(GraphSteinerPoints[i].x-5,GraphSteinerPoints[i].y-5,
			GraphSteinerPoints[i].x+5,GraphSteinerPoints[i].y+5, outline="black", fill="black", width=1)

	for i in xrange(0,len(OriginalPoints)):
		canvas.create_oval(OriginalPoints[i].x-5,OriginalPoints[i].y-5,
			OriginalPoints[i].x+5,OriginalPoints[i].y+5, outline="black", fill="white", width=1)

	GSMTtext.set(str(round(GSMTminDist, 2)))

def clear():
	global OriginalPoints
	del OriginalPoints[:]
	global RectSteinerPoints
	del RectSteinerPoints[:]
	global GraphSteinerPoints
	del GraphSteinerPoints[:]
	global RMST
	del RMST[:]
	global RSMT
	del RSMT[:]
	global GMST
	del GMST[:]
	global GSMT
	del GSMT[:]
	RMSTtext.set("-----")
	RSMTtext.set("-----")
	GMSTtext.set("-----")
	GSMTtext.set("-----")
	canvas.delete("all")

master = Canvas(tk)
but_frame = Frame(master)
button1 = Button(but_frame, text = "RMST", command = computeRMST)
button1.configure(width=9, activebackground = "blue", relief = RAISED)
button1.pack(side=TOP)
var = StringVar()
var.set("Distance:")
Label(but_frame, textvariable=var).pack()
RMSTtext = StringVar()
label1 = Label(but_frame, textvariable=RMSTtext)
label1.pack()
Label(but_frame, textvariable="").pack()
button2 = Button(but_frame, text = "RSMT", command = computeRSMT)
button2.configure(width=9, activebackground = "blue", relief = RAISED)
button2.pack(side=TOP)
Label(but_frame, textvariable=var).pack()
RSMTtext = StringVar()
label2 = Label(but_frame, textvariable=RSMTtext)
label2.pack()
Label(but_frame, textvariable="").pack()
button3 = Button(but_frame, text = "GMST", command = computeGMST)
button3.configure(width=9, activebackground = "blue", relief = RAISED)
button3.pack(side=TOP)
Label(but_frame, textvariable=var).pack()
GMSTtext = StringVar()
label3 = Label(but_frame, textvariable=GMSTtext)
label3.pack()
Label(but_frame, textvariable="").pack()
button4 = Button(but_frame, text = "GSMT", command = computeGSMT)
button4.configure(width=9, activebackground = "blue", relief = RAISED)
button4.pack(side=TOP)
Label(but_frame, textvariable=var).pack()
GSMTtext = StringVar()
label4 = Label(but_frame, textvariable=GSMTtext)
label4.pack()
Label(but_frame, textvariable="").pack()
button5 = Button(but_frame, text = "Reset", command = clear)
button5.configure(width=9, activebackground = "blue", relief = RAISED)
button5.pack(side=TOP)
but_frame.pack(side=RIGHT, expand=0)
canvas = Canvas(master, width = 500, height = 500, bd=2, relief=RIDGE, bg='#F6F5F1')
canvas.bind("<Button-1>", addMousePoint)
canvas.pack(expand=0)
master.pack(expand=0)

RMSTtext.set("-----")
RSMTtext.set("-----")
GMSTtext.set("-----")
GSMTtext.set("-----")

# Testing

# addPoint(161, 88)
# addPoint(103, 222)
# addPoint(310, 143)
# addPoint(256, 282)

# End of testing

tk.mainloop()