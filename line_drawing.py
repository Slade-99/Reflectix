##### Line Drawing Algo ##########
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import time
import random

class Line_Drawing:
    def __init__(self,x1, y1, x2, y2,width,col):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.col = col
        self.width = width
        self.dy = self.y2 - self.y1 
        self.dx = self.x2 - self.x1 
        self.zone = 0
        self.points_to_be_drawn = [ ]



    def draw_points(self,x, y, s=1):
        if(self.col=='g'):
            glColor3f(0,1,0)
        elif(self.col=='r'):
            glColor3f(1,0,0)
        elif(self.col=='w'):
            glColor3f(1,1,1)
        elif(self.col=='b'):
            glColor3f(0,0,1)
        elif(self.col=='amb'):
            glColor3f(1,0.749,0)
        elif(self.col=='ash'):
            glColor3f(0.698, 0.745, 0.710)
        else:
            glColor3f(0,0,0)

        glPointSize(s) #pixel size. by default 1 thake

        glBegin(GL_POINTS)
        glVertex2f(x,y) #jekhane show korbe pixel
        glEnd()

    def find_zone(self):
        if(self.dx>=0 and self.dy>=0):
            if( abs(self.dx)>= abs(self.dy) ):
                self.zone = 0
            else:
                self.zone = 1

        elif( self.dx<0 and self.dy>=0 ):
            if( abs(self.dx)>= abs(self.dy) ):
                self.zone = 3
            else:
                self.zone = 2
        elif( self.dx<0 and self.dy<0 ):
            if( abs(self.dx)>= abs(self.dy) ):
                self.zone = 4
            else:
                self.zone = 5
        else:
            if( abs(self.dx)>= abs(self.dy) ):
                self.zone = 7
            else:
                self.zone = 6


    def zone_adjustment(self):

        if(self.zone==0):
            self.mid_point_line_algo()

        elif(self.zone ==1 ):
            self.x1 , self.y1 = self.y1 , self.x1 
            self.x2 , self.y2 = self.y2 , self.x2 
            self.dy = self.y2 - self.y1 
            self.dx = self.x2 - self.x1 
            self.mid_point_line_algo()
            for i in range(len(self.points_to_be_drawn)):
                a ,b = self.points_to_be_drawn[i][0] , self.points_to_be_drawn[i][1]
                self.points_to_be_drawn[i][0] = b
                self.points_to_be_drawn[i][1] = a

        elif(self.zone ==2 ):
            self.x1 , self.y1 = self.y1 , -1*self.x1 
            self.x2 , self.y2 = self.y2 , -1*self.x2 
            self.dy = self.y2 - self.y1 
            self.dx = self.x2 - self.x1 
            self.mid_point_line_algo()
            for i in range(len(self.points_to_be_drawn)):
                a ,b = self.points_to_be_drawn[i][0] , self.points_to_be_drawn[i][1]
                self.points_to_be_drawn[i][0] = -1*b
                self.points_to_be_drawn[i][1] = a


        elif(self.zone ==3 ):
            self.x1 , self.y1 = -1*self.x1 , self.y1 
            self.x2 , self.y2 = -1*self.x2 , self.y2 
            self.dy = self.y2 - self.y1 
            self.dx = self.x2 - self.x1 
            self.mid_point_line_algo()
            for i in range(len(self.points_to_be_drawn)):
                a ,b = self.points_to_be_drawn[i][0] , self.points_to_be_drawn[i][1]
                self.points_to_be_drawn[i][0] = -1*a
                self.points_to_be_drawn[i][1] = b



        elif(self.zone ==4 ):
            self.x1 , self.y1 = -1*self.x1 , -1*self.y1 
            self.x2 , self.y2 = -1*self.x2 , -1*self.y2
            self.dy = self.y2 - self.y1 
            self.dx = self.x2 - self.x1 
            self.mid_point_line_algo()
            for i in range(len(self.points_to_be_drawn)):
                a ,b = self.points_to_be_drawn[i][0] , self.points_to_be_drawn[i][1]
                self.points_to_be_drawn[i][0] = -1*a
                self.points_to_be_drawn[i][1] = -1*b



        elif(self.zone ==5 ):
            self.x1 , self.y1 = -1*self.y1 , -1*self.x1 
            self.x2 , self.y2 = -1*self.y2 , -1*self.x2
            self.dy = self.y2 - self.y1 
            self.dx = self.x2 - self.x1 
            self.mid_point_line_algo()
            for i in range(len(self.points_to_be_drawn)):
                a ,b = self.points_to_be_drawn[i][0] , self.points_to_be_drawn[i][1]
                self.points_to_be_drawn[i][0] = -1*b
                self.points_to_be_drawn[i][1] = -1*a


        elif(self.zone ==6 ):
            self.x1 , self.y1 = -1*self.y1 , self.x1 
            self.x2 , self.y2 = -1*self.y2 , self.x2
            self.dy = self.y2 - self.y1 
            self.dx = self.x2 - self.x1 
            self.mid_point_line_algo()
            for i in range(len(self.points_to_be_drawn)):
                a ,b = self.points_to_be_drawn[i][0] , self.points_to_be_drawn[i][1]
                self.points_to_be_drawn[i][0] = b
                self.points_to_be_drawn[i][1] = -1*a

        elif(self.zone ==7 ):
            self.x1 , self.y1 = self.x1 , -1*self.y1 
            self.x2 , self.y2 = self.x2 , -1*self.y2 
            self.dy = self.y2 - self.y1 
            self.dx = self.x2 - self.x1 
            self.mid_point_line_algo()
            for i in range(len(self.points_to_be_drawn)):
                a ,b = self.points_to_be_drawn[i][0] , self.points_to_be_drawn[i][1]
                self.points_to_be_drawn[i][0] = a
                self.points_to_be_drawn[i][1] = -1*b


    def mid_point_line_algo(self):
        d = 2*self.dy - self.dx
        x = self.x1 
        y = self.y1
        self.points_to_be_drawn.append([x,y])
        while(x!= self.x2):
            if( d>0):
                x = x+1
                y = y+1
                d = d + 2*self.dy - 2*self.dx
                self.points_to_be_drawn.append([x,y])

            else:
                x = x + 1
                d = d + 2*self.dy
                self.points_to_be_drawn.append([x,y])
        #self.points_to_be_drawn.append([self.x2,self.y2])




    ### Line Creations are executed Here ####
    def draw_line(self):
        self.find_zone()
        self.zone_adjustment()

        for i in self.points_to_be_drawn:
            self.draw_points(i[0],i[1],self.width)




