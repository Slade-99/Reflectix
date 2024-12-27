##### Circle Drawing Algo ##########
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import time
import random

class Circle_Drawing:
    def __init__(self,x1, y1, r,width,col):
        self.x1 = x1
        self.y1 = y1
        self.r = r
        self.width = width
        self.col = col
        self.zone = 0
        self.points_to_be_drawn = [ ]



    def draw_points(self,x, y, s=1,col='b'):
        if(col=='g'):
            glColor3f(0,1,0)
        elif(col=='r'):
            glColor3f(1,0,0)
        elif(col=='or'):
            glColor3f(1,0.647,0)
        elif(col=='w'):
            glColor3f(1,1,1)
        elif(col=='b'):
            glColor3f(0,0,1)
        else:
            glColor3f(0,0,0)

        glPointSize(s) #pixel size. by default 1 thake
        glBegin(GL_POINTS)
        glVertex2f(x,y) #jekhane show korbe pixel
        glEnd()



    def octant_adjustment(self):

        points_list = self.points_to_be_drawn

        for i in range(len(points_list)):
            x = points_list[i][0]
            y = points_list[i][1]
            self.points_to_be_drawn.append([y,x])
            self.points_to_be_drawn.append([-1*x,y])
            self.points_to_be_drawn.append([-1*y,x])
            self.points_to_be_drawn.append([-1*y,-1*x])
            self.points_to_be_drawn.append([-1*x,-1*y])
            self.points_to_be_drawn.append([x,-1*y])
            self.points_to_be_drawn.append([y,-1*x])



    def center_adjustment(self):

        for i in range(len(self.points_to_be_drawn)):
            x = self.points_to_be_drawn[i][0]
            y = self.points_to_be_drawn[i][1]
            self.points_to_be_drawn[i][0] += self.x1
            self.points_to_be_drawn[i][1] += self.y1 



    def mid_point_circle_algo(self):
        #### Implementing for octant 1 ######

        d = 1 - self.r
        x = 0
        y = self.r

        self.points_to_be_drawn.append([x,y])
        while(x<y):
            if( d>=0):
                x = x+1
                y = y-1
                d = d + 2*x - 2*y + 5
                self.points_to_be_drawn.append([x,y])

            else:
                x = x + 1
                d = d + 2*x + 3
                self.points_to_be_drawn.append([x,y])
        



    def draw_circle(self):
        
        self.mid_point_circle_algo()
        self.octant_adjustment()
        self.center_adjustment()

        for i in self.points_to_be_drawn:
            self.draw_points(i[0],i[1],self.width,self.col)
