from psychopy import *
import numpy as np

class Car:
    def __init__(self, win, track, keys, acceleration = 0.1, max_velocity = 20, turn_strength = 0.1, friction = 0.02):
        self.track = track
        self.keys = keys
        self.velocity = 0.0 #in pixels/frame
        self.velocity_dir = 0.0 #in radian
        self.direction = track.beginOrientation #in radian 
        self.max_velocity = max_velocity
        self.turn_strength = turn_strength
        self.acceleration = acceleration
        self.friction = friction
        self.stimulus = visual.ImageStim(win, image="car_2.png", interpolate = True)
        self.stimulus.setAutoDraw(True)
        self.stimulus.pos = self.trackToWindowCoordinates(track.beginPosition)
        self.stimulus.ori = 360 * track.beginOrientation / (2 * np.pi)
    
    def setSpeedFromVector(self, m_vector):
        self.velocity_dir = np.arctan2(m_vector[0], m_vector[1])
        self.velocity = np.sqrt(m_vector[0]*m_vector[0] + m_vector[1]*m_vector[1])
    
    def accelerate(self):
        m_vector = np.array([self.velocity * np.sin(self.velocity_dir), self.velocity * np.cos(self.velocity_dir)])
        a_vector = np.array([self.acceleration * np.sin(self.direction), self.acceleration * np.cos(self.direction)])
        m_vector += a_vector
        self.setSpeedFromVector(m_vector)
                    
    def decelerate(self):
        self.velocity = max(0, self.velocity - self.acceleration)
    
    def turnLeft(self):
        self.direction -= self.turn_strength
        
    def turnRight(self):
        self.direction += self.turn_strength
    
    def update(self, pressed_keys):
        if self.keys['right'] in pressed_keys:
            self.turnRight()
        if self.keys['left'] in pressed_keys:
            self.turnLeft()
        if self.keys['backward'] in pressed_keys:
            self.decelerate()
        if self.keys['forward'] in pressed_keys:
            self.accelerate()
        return self.updatePosition()

    
    def updatePosition(self):
        twopi = 2 * np.pi
        
        if(self.track.isSlowTerrain(self.windowToTrackCoordinates(self.stimulus.pos))):
            self.friction = 0.2
        else:
            self.friction = 0.02

        
        self.velocity = min(self.max_velocity, self.velocity * (1.0 - self.friction))
        
        m_vector = (self.velocity * np.sin(self.velocity_dir), self.velocity * np.cos(self.velocity_dir))
        
        previous_pos = [self.stimulus.pos[0], self.stimulus.pos[1]]
        
        self.stimulus.pos += m_vector
        
        #collisions

        #keep stimulus on screen
        win_size = self.stimulus.win.size
        self.stimulus.pos = ( max(-0.5 * win_size[0], min(0.5 * win_size[0], self.stimulus.pos[0])), max(-0.5 * win_size[1], min(0.5 * win_size[1], self.stimulus.pos[1])))
        
        #obstacles
        if(self.track.isWall(self.windowToTrackCoordinates(self.stimulus.pos))):
            original_target = self.stimulus.pos
            while(self.track.isWall(self.windowToTrackCoordinates(self.stimulus.pos))):
                self.stimulus.pos -= m_vector / np.linalg.norm(m_vector)
            self.stimulus.pos = np.rint(self.stimulus.pos)
        
        m_vector = self.stimulus.pos - previous_pos
        self.velocity = np.linalg.norm(m_vector)
        self.velocity_dir = np.arctan2(m_vector[0], m_vector[1])
        
        self.stimulus.ori = 360 * self.direction / (twopi)
        
        if self.direction < 0.0:
            self.direction += twopi
        elif self.direction > twopi:
            self.direction -= twopi
        if self.velocity_dir < 0.0:
            self.velocity_dir += twopi
        elif self.velocity_dir > twopi:
            self.velocity_dir -= twopi
        if self.velocity_dir < np.pi * 0.5 and self.direction > 1.5 * np.pi:
            self.direction -= twopi
        if self.direction < np.pi * 0.5 and self.velocity_dir > 1.5 * np.pi:
            self.direction += twopi
        if self.velocity > 0:
            self.velocity_dir = self.velocity_dir * (1.0 - self.friction) + self.direction * self.friction
        
        return self.track.inPosition(self.windowToTrackCoordinates(self.stimulus.pos))

    def trackToWindowCoordinates(self, coord):
        return coord - self.stimulus.win.size * 0.5
        
    def windowToTrackCoordinates(self, coord):
        return np.rint(coord + self.stimulus.win.size * 0.5 - (1.0, 1.0) ).astype(int)
