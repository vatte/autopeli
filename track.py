import cv2
import numpy as np

class Track:
    def __init__(self, filename, callback):
        self.img = cv2.cvtColor(cv2.imread(filename), cv2.COLOR_BGR2RGB)[:][::-1]
        targets = [250] # targets are reds with r value 250, 245, 240...and so on
        while True:
            target = targets[-1] - 5
            if np.any(np.all(self.img == np.array([target, 0, 0]), axis=2)): #find if color exists in image
                targets.append(target)
            else:
                break
        self.targets = targets
        self.hitTargets = np.array([False for _ in self.targets])
        self.laps = 0
        yellow = np.argwhere(np.all(self.img == np.array([255, 255, 0]), axis=2))[0][::-1]
        yellow2 = np.argwhere(np.all(self.img == np.array([200, 200, 0]), axis=2))[0][::-1]
        self.beginPosition = yellow #yellow is starting position
        self.beginOrientation = np.arctan2(yellow[0] - yellow2[0], yellow[1] - yellow2[1])
        self.lapFunction = callback
        self.onTrack = True
    
    def isWall(self, position):
        if np.all(self.img[position[1]][position[0]] == np.array([0, 0, 255])): #blue is wall
            return True
        return False
    
    def isSlowTerrain(self, position):
        if np.all(self.img[position[1]][position[0]] == np.array([0, 0, 0])): #black is slow
            return True
        return False
    
    def inPosition(self, position):
        c = self.img[position[1]][position[0]]
        if c[0] == 0 and c[1] == 0 and c[2] == 0:
            if self.onTrack:
                self.onTrack = False
                return 44 #out of track trigger
        elif not self.onTrack:
            self.onTrack = True
            return 43 #back on track trigger
        elif c[0] != 0 and c[1] == 0 and c[2] == 0:
            if c[0] != self.targets[-1]:
                self.isLap()
            if not np.all(self.hitTargets):
                idx = np.argwhere(False == self.hitTargets)[0][0]
                next_idx = min(len(self.targets)-1, idx+1) #ok to miss one target
                if c[0] == self.targets[idx] and not self.hitTargets[idx]:
                    self.hitTargets[idx] = True
                    return self.targets[idx]
                elif c[0] == self.targets[next_idx] and not self.hitTargets[next_idx]:
                    self.hitTargets[idx] = True
                    self.hitTargets[next_idx] = True
                    return self.targets[next_idx]
        return 0
    
    def isLap(self):
        if np.all(self.hitTargets):
            self.laps += 1
            self.hitTargets = np.array([False for _ in self.targets])
            self.lapFunction()
            return True
        return False

if __name__ == "__main__":
    track = Track('Track1.png', None)