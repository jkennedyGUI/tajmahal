# Camera object for parametric surface viewer!
# Stores position, forward, up and projection matrix for a
# camera object.

import numpy as N

class Camera:
    def __init__(self, forward, left, up):
        self.forward = forward
        self.left = left
        self.up = up
        self.pMatrix = projectionMatrix(1.0, 10.0, 1.0, 1.0)
        self.eye = N.eye(4, dtype=N.float32)


    def rotateBy(x, y):
        """Rotate by given x and y changes in the mouse coordinates."""
        

        

    
