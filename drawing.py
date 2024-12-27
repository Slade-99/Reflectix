from line_drawing import Line_Drawing
from circle_drawing import Circle_Drawing
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import time
import random

Resolution = [ (1500,1000) , (750,500)]
Width , Height = 0,0
scaling = 0
def set_resolution(quality):
    global Width,Height,scaling

    if(quality=="lower"):
        Width , Height = Resolution[1][0] , Resolution[1][1]
        scaling = 2
    elif(quality=="higher"):
        Width , Height = Resolution[0][0] , Resolution[0][1]
        scaling = 1



set_resolution("lower")  ## write "lower" or "higher" to set the resolution






#### THis Class is used for drawing all sort of objects necessary for the task ######
class Drawing:


    def __init__(self):
        self.enemies = [ ]
        self.bullets = [ ]
        self.Width, self.Height = Width,Height  ## Screen
        self.New_Game_Box_coordinates = [0.35*self.Width,0.59*self.Height,0.65*self.Width,0.65*self.Height]
        self.Level2_Box_Box_coordinates = [0.35*self.Width,0.49*self.Height,0.65*self.Width,0.55*self.Height]
        self.Level3_Box_Box_coordinates = [0.35*self.Width,0.39*self.Height,0.65*self.Width,0.45*self.Height]
        self.Rules_Box_coordinates = [0.35*self.Width,0.29*self.Height,0.65*self.Width,0.35*self.Height]
        self.Exit_Box_coordinates = [0.35*self.Width,0.19*self.Height,0.65*self.Width,0.25*self.Height]


    def draw_all(self, game_state):
        glBegin(GL_LINES)
        for line in game_state.lines_to_draw:
            glVertex2f(line[0], line[1])
            glVertex2f(line[2], line[3])
        glEnd()

    def draw_line(self,x1, y1, x2, y2,width,col):

        line_1 = Line_Drawing(x1, y1, x2, y2,width,col)
        line_1.draw_line()


    def draw_circle(self,x1,y1,r,width,col):

        circle_1 = Circle_Drawing(x1,y1,r,width,col)
        circle_1.draw_circle()





    def draw_pause_button(self,position,pause_state):
        x1 = position[0]
        y1 = position[1]
        x2 = position[2]
        y2 = position[3]
        if(scaling==1):
            t = 6
        else:
            t = 2

        self.draw_line(x1,y1,x1,y2,t,'amb')
        self.draw_line(x1,y1,x2,y1,t,'amb')
        self.draw_line(x2,y1,x2,y2,t,'amb')
        self.draw_line(x1,y2,x2,y2,t,'amb')

        
        if(pause_state):
            self.draw_line(x1,y2,x2,(y1+y2)*0.5,t,'amb')
            self.draw_line(x1,y1,x2,(y1+y2)*0.5,t,'amb')
        else:
            self.draw_line(x1+0.33*(x2-x1),y1,x1+0.33*(x2-x1),y2,t,'amb')
            self.draw_line(x1+0.67*(x2-x1),y1,x1+0.67*(x2-x1),y2,t,'amb')

        




    def draw_return_button(self,position):
        x1 = position[0]
        y1 = position[1]
        x2 = position[2]
        y2 = position[3]

        if(scaling==1):
            t = 6
        else:
            t = 2

        self.draw_line(x1,y1,x1,y2,t,'r')
        self.draw_line(x1,y1,x2,y1,t,'r')
        self.draw_line(x2,y1,x2,y2,t,'r')
        self.draw_line(x1,y2,x2,y2,t,'r')

        self.draw_line(x1,(y1+y2)/2,x2,(y1+y2)/2,t,'r')


        self.draw_line(x1,(y1+y2)/2,x1+(x2-x1)*0.3,y2,t,'r')
        self.draw_line(x1,(y1+y2)/2,x1+(x2-x1)*0.3,y1,t,'r')




    def draw_boundary(self,position):


        x1 , y1 , x2 , y2 = position[0] , position[1] , position[2] , position[3]

        self.draw_line(x1,y1,x1,y2,5,'b')
        self.draw_line(x2,y1,x2,y2,5,'b')

        self.draw_line(x1,y1,x2,y1,5,'b')
        self.draw_line(0,y2,self.Width,y2,5,'b')
        self.draw_filled_rect(0,0,x1,y2,(0,0,1))
        self.draw_filled_rect(x1,0,x2,y1,(0,0,1))
        self.draw_filled_rect(self.Width,0,x2,y2,(0,0,1))


    def draw_hud(self,return_button,pause_button,pause_state,score,mirror,state):
        self.draw_pause_button(pause_button,pause_state)
        self.draw_return_button(return_button)
        

        glColor3f(1,0,0) if mirror == 0 else glColor3f(0,1,0) #Show number of mirrors in red if 0 else green
        text_x = 0.15*self.Width
        text_y = 0.95*self.Height
        self.draw_text_glut(text_x, text_y, f'Mirrors: {mirror}', scale= 0.4)


        text_x = 0.45*self.Width 
        text_y = 0.95*self.Height
        self.draw_text_glut(text_x, text_y, f'Score: {score}' , scale= 0.4)


        text_x = 0.75*self.Width 
        text_y = 0.95*self.Height
        self.draw_text_glut(text_x, text_y, f'{state}' , scale= 0.4)

        #Show number of mirrors in red



    def draw_filled_rect(self, x1, y1, x2, y2, color):
        """
        Draw a filled rectangle using GL_POINTS.
        """

        glColor3f(color[0], color[1], color[2])  # Set color for the rectangle

        glBegin(GL_POINTS)
        for x in range(int(x1), int(x2) + 1):
            for y in range(int(y1), int(y2) + 1):
                glVertex2f(x, y)
        glEnd()

        """glColor3f(color[0], color[1], color[2])  # Set color for the rectangle

        glBegin(GL_QUADS)
        glVertex2f(x1, y1)  # Bottom-left corner
        glVertex2f(x2, y1)  # Bottom-right corner
        glVertex2f(x2, y2)  # Top-right corner
        glVertex2f(x1, y2)  # Top-left corner
        glEnd()"""



    def spawn_striker1(self, coordinates):
        x1 = coordinates[0]
        y1 = coordinates[1]
        
        if(scaling==1):
            self.draw_circle(x1,y1,15,3,'g')
        else:
            self.draw_circle(x1,y1,7.5,3,'g')



    def spawn_striker2(self, coordinates):
        x1 = coordinates[0]
        y1 = coordinates[1]
        

        if(scaling==1):
            self.draw_circle(x1,y1,15,3,'g')
        else:
            self.draw_circle(x1,y1,7.5,3,'g')



    def spawn_target(self, coordinates):

        x1,y1,x2,y2 = coordinates[0] ,  coordinates[1] , coordinates[2] , coordinates[3] 
        


        self.draw_line(x1,y2,x2,y2,5,'amb')
        self.draw_line(x1,y1,x2,y1,5,'amb')

        self.draw_line(x1,y2,x1,y1,5,'amb')
        self.draw_line(x2,y2,x2,y1,5,'amb')



    def spawn_mirror(self, coordinates):

        x1,y1,x2,y2 = coordinates[0] ,  coordinates[1] , coordinates[2] , coordinates[3] 

        self.draw_line(x1,y1,x2,y2,3,'amb')


    def spawn_point_of_failure1(self, coordinates):

        x1,y1,x2,y2 = coordinates[0] ,  coordinates[1] , coordinates[2] , coordinates[3] 
        


        self.draw_line(x1,y1,x2,y2,5,'r')
        self.draw_line(x1,y2,x2,y1,5,'r')




    def spawn_point_of_failure2(self, coordinates):
        x1,y1,x2,y2 = coordinates[0] ,  coordinates[1] , coordinates[2] , coordinates[3] 
        


        self.draw_line(x1,y1,x2,y2,5,'r')
        self.draw_line(x1,y2,x2,y1,5,'r')



    def spawn_barrier1(self, coordinates):

        x1,y1,x2,y2 = coordinates[0] ,  coordinates[1] , coordinates[2] , coordinates[3] 
        


        self.draw_line(x1,y2,x2,y2,3,'ash')
        self.draw_line(x1,y1,x2,y1,3,'ash')

        self.draw_line(x1,y2,x1,y1,3,'ash')
        self.draw_line(x2,y2,x2,y1,3,'ash')
        self.draw_filled_rect(x1,y1,x2,y2,(0.698, 0.745, 0.710))




    def spawn_barrier2(self, coordinates):
        x1,y1,x2,y2 = coordinates[0] ,  coordinates[1] , coordinates[2] , coordinates[3] 
        


        self.draw_line(x1,y2,x2,y2,3,'ash')
        self.draw_line(x1,y1,x2,y1,3,'ash')

        self.draw_line(x1,y2,x1,y1,3,'ash')
        self.draw_line(x2,y2,x2,y1,3,'ash')
        self.draw_filled_rect(x1,y1,x2,y2,(0.698, 0.745, 0.710))



    def draw_New_Game_Box(self):


        x1 , y1 , x2 , y2 = self.New_Game_Box_coordinates[0] , self.New_Game_Box_coordinates[1] , self.New_Game_Box_coordinates[2] , self.New_Game_Box_coordinates[3]

        self.draw_line(x1,y2,x2,y2,5,'amb')
        self.draw_line(x1,y1,x2,y1,5,'amb')

        self.draw_line(x1,y2,x1,y1,5,'amb')
        self.draw_line(x2,y2,x2,y1,5,'amb')

        text_x = 0.914*x1 +  (x2 - x1) / 2.5  
        text_y = (y2 + y1) / 2.03
        self.draw_text_glut(text_x, text_y, 'New Game')







    def draw_comments(self,score,previous_level):





        if(previous_level==1 or previous_level==2):
            glColor3f(1,0.749,0)
            text_x = 0.05*self.Width 
            text_y = 0.75*self.Height
            self.draw_text_glut(text_x, text_y, f'Congratulations: Your Score is {score}.', scale=0.6)

            glColor3f(1,0.749,0)
            text_x = 0.30*self.Width 
            text_y = 0.55*self.Height
            self.draw_text_glut(text_x, text_y, f'Moving to level {previous_level+1}.', scale=0.4)
        else:

            glColor3f(1,0.749,0)
            text_x = 0.05*self.Width 
            text_y = 0.75*self.Height
            self.draw_text_glut(text_x, text_y, f'Congratulations: Your Score is {score}.', scale=0.6)

            glColor3f(1,0.749,0)
            text_x = 0.30*self.Width 
            text_y = 0.55*self.Height
            self.draw_text_glut(text_x, text_y, 'Returning to Main Menu', scale=0.4)


    def draw_gameover_comments(self,score):



        
            glColor3f(1,0.749,0)
            text_x = 0.3*self.Width 
            text_y = 0.75*self.Height
            self.draw_text_glut(text_x, text_y, f'Game Over', scale=0.8)

            glColor3f(1,0.749,0)
            text_x = 0.20*self.Width 
            text_y = 0.55*self.Height
            
            self.draw_text_glut(text_x, text_y, f' Your Score is {score}.', scale=0.6)




    def draw_extras1(self):


        glColor3f(1,0.749,0)
        text_x = 0.75*self.Width 
        text_y = 0.05*self.Height
        self.draw_text_glut(text_x, text_y, 'Powered by: OpenGL', scale=0.2)

    def draw_extras2(self):


        glColor3f(1,0.749,0)
        text_x = 0.05*self.Width 
        text_y = 0.05*self.Height
        self.draw_text_glut(text_x, text_y, 'Version: 1.0.1', scale=0.2)


    def draw_Title(self):


        glColor3f(1,0.749,0)
        text_x = 0.22*self.Width 
        text_y = 0.75*self.Height
        self.draw_text_glut(text_x, text_y, 'Reflectix', scale=1.8)


    def draw_how_to_play(self):


        glColor3f(1,0.749,0)
        text_x = 0.29*self.Width 
        text_y = 0.75*self.Height
        self.draw_text_glut(text_x, text_y, 'How To Play', scale=0.8)



    def draw_best_of_luck(self):


        glColor3f(1,0.749,0)
        text_x = 0.39*self.Width 
        text_y = 0.05*self.Height
        self.draw_text_glut(text_x, text_y, 'Best of Luck', scale=0.4)

    def draw_rule1(self):


        glColor3f(1,0.749,0)
        text_x = 0.05*self.Width 
        text_y = 0.65*self.Height
        self.draw_text_glut(text_x, text_y, '1) The task of this game is to send the striker into the target square using mirrors for reflection.', scale=0.2)


    def draw_rule2(self):


        glColor3f(1,0.749,0)
        text_x = 0.05*self.Width 
        text_y = 0.55*self.Height
        self.draw_text_glut(text_x, text_y, '2)Use LMB to place mirror . Use Up and Down arrow key to rotate the mirror. ', scale=0.2)



    def draw_rule3(self):


        glColor3f(1,0.749,0)
        text_x = 0.05*self.Width 
        text_y = 0.45*self.Height
        self.draw_text_glut(text_x, text_y, '3) When a new mirror is generated the previous one will be removed.', scale=0.2)



    def draw_rule4(self):


        glColor3f(1,0.749,0)
        text_x = 0.05*self.Width 
        text_y = 0.35*self.Height
        self.draw_text_glut(text_x, text_y, '4) Level 1,2 or 3 will awards points 1,2 or 3 for each unused mirror. .', scale=0.2)



    def draw_rule5(self):


        glColor3f(1,0.749,0)
        text_x = 0.05*self.Width 
        text_y = 0.25*self.Height
        self.draw_text_glut(text_x, text_y, '5) Player must finish the task with a given number of mirrors.', scale=0.2)



    def draw_rule6(self):


        glColor3f(1,0.749,0)
        text_x = 0.05*self.Width 
        text_y = 0.15*self.Height
        self.draw_text_glut(text_x, text_y, '6) A player will lose immediately if the striker lands on the point of failure', scale=0.2)




    def draw_Level2_Box(self):

        x1 , y1 , x2 , y2 = self.Level2_Box_Box_coordinates[0] , self.Level2_Box_Box_coordinates[1] , self.Level2_Box_Box_coordinates[2] , self.Level2_Box_Box_coordinates[3]

        self.draw_line(x1,y2,x2,y2,5,'amb')
        self.draw_line(x1,y1,x2,y1,5,'amb')

        self.draw_line(x1,y2,x1,y1,5,'amb')
        self.draw_line(x2,y2,x2,y1,5,'amb')

        text_x = 0.943*x1 +  (x2 - x1) / 2.3  # 
        text_y = (y2 + y1) /  2.03
        self.draw_text_glut(text_x, text_y, 'Level 2')

    
    def draw_Level3_Box(self):

        x1 , y1 , x2 , y2 = self.Level3_Box_Box_coordinates[0] , self.Level3_Box_Box_coordinates[1] , self.Level3_Box_Box_coordinates[2] , self.Level3_Box_Box_coordinates[3]

        self.draw_line(x1,y2,x2,y2,5,'amb')
        self.draw_line(x1,y1,x2,y1,5,'amb')

        self.draw_line(x1,y2,x1,y1,5,'amb')
        self.draw_line(x2,y2,x2,y1,5,'amb')

        text_x = 0.943*x1 +  (x2 - x1) / 2.3  
        text_y =  (y2 + y1) /  2.03
        self.draw_text_glut(text_x, text_y, 'Level 3')




    def draw_Rules_Box(self):

        x1 , y1 , x2 , y2 = self.Rules_Box_coordinates[0] , self.Rules_Box_coordinates[1] , self.Rules_Box_coordinates[2] , self.Rules_Box_coordinates[3]

        self.draw_line(x1,y2,x2,y2,5,'amb')
        self.draw_line(x1,y1,x2,y1,5,'amb')

        self.draw_line(x1,y2,x1,y1,5,'amb')
        self.draw_line(x2,y2,x2,y1,5,'amb')

        text_x = 0.957*x1 +  (x2 - x1) / 2.2  
        text_y = (y2 + y1) /  2.03
        self.draw_text_glut(text_x, text_y, 'Rules')


    def draw_Exit_Box(self):

        x1 , y1 , x2 , y2 = self.Exit_Box_coordinates[0] , self.Exit_Box_coordinates[1] , self.Exit_Box_coordinates[2] , self.Exit_Box_coordinates[3]

        self.draw_line(x1,y2,x2,y2,5,'amb')
        self.draw_line(x1,y1,x2,y1,5,'amb')

        self.draw_line(x1,y2,x1,y1,5,'amb')
        self.draw_line(x2,y2,x2,y1,5,'amb')


        text_x = 0.971*x1 +  (x2 - x1)  / 2.15  # X-coordinate for the center of the box
        text_y = (y2 + y1) /  2.04
        self.draw_text_glut(text_x, text_y, 'Exit')



    def draw_text_glut(self, x, y, text, scale=0.3):
        """
        Draw scalable text using stroke fonts.

        Parameters:
            x (float): X-coordinate.
            y (float): Y-coordinate.
            text (str): The text to render.
            scale (float): Scaling factor for text size.
        """
        scale = scale/scaling
        glPushMatrix()
        glTranslatef(x, y, 0)
        glScalef(scale, scale, scale)  # Scale the text
        for char in text:
            glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(char))
        glPopMatrix()