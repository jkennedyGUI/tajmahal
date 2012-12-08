import os

from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
import pygame
from pygame.locals import *

import numpy as N
from ctypes import c_void_p

from transforms import *
from camera import *
from surface import *

    
def loadFile(filename):
    with open(os.path.join(os.getcwd(), filename)) as fp:
        return fp.read()

def compileShaderProgram(vertexShader, fragmentShader):
    """
    Instead of calling OpenGL's shader compilation functions directly
    (glShaderSource, glCompileShader, etc), we use PyOpenGL's wrapper
    functions, which are much simpler to use.
    """
    myProgram = compileProgram(
        compileShader(vertexShader, GL_VERTEX_SHADER),
        compileShader(fragmentShader, GL_FRAGMENT_SHADER)
    )
    return myProgram

class PositionNormalTextureBuffer():
    """Loads a vetex attribute array in init, enables it in Start
       and disables it in Stop"""
    def __init__(self, shader, data):
        self.data = N.array(data, dtype=N.float32)                       
        self.shader = shader
        self.position = glGetAttribLocation(shader, 'position')
        self.normal = glGetAttribLocation(shader, 'normal')
        self.texCoord = glGetAttribLocation(shader, 'texCoord')
        self.n = len(data)/10
        self.bufferObject = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.bufferObject)
        glBufferData(GL_ARRAY_BUFFER, self.data, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def Start(self):
        # do this with a vao next time?
        bytesPerFloat = 4
        
        glBindBuffer(GL_ARRAY_BUFFER, self.bufferObject)
        glEnableVertexAttribArray(self.position)
        glEnableVertexAttribArray(self.normal)
        # Stride is start to start:
        glEnableVertexAttribArray(self.texCoord)

        glVertexAttribPointer(self.position, 4,
                              GL_FLOAT, False,
                              10*bytesPerFloat,
                              c_void_p(0))
        glVertexAttribPointer(self.normal, 4,
                              GL_FLOAT, False,
                              10*bytesPerFloat,
                              c_void_p(4*bytesPerFloat))
        glVertexAttribPointer(self.texCoord, 2,
                              GL_FLOAT, False,
                              10*bytesPerFloat,
                              c_void_p(8*bytesPerFloat))
        glDrawArrays(GL_TRIANGLES, 0, self.n)

    def Stop(self):
        glDisableVertexAttribArray(self.position)
        glDisableVertexAttribArray(self.normal)
        glDisableVertexAttribArray(self.texCoord)

class Uniforms():
    """Takes a shader and a list of uniforms, types and items
       and loads them into shader memory on Start.
       Also has a convenience function for premultiplying the
       model matrix by a rotation."""
    def __init__(self, shader, unifs):
        self.shader = shader
        self.unifs = unifs
        self.locations = {}
        self.kinds = {}
        self.items = {}
        for unif in unifs:
            name, kind, item = unif
            self.items[name] = item
            self.kinds[name] = kind
            self.locations[name] = glGetUniformLocation(shader, name)
            if name == 'modelMatrix':
                self.modelMatrix = item
        self.UIRotation = N.eye(4, dtype=N.float32)

    #def UpdateRotation(self, cam):
    #   # rotate given camera's rotation
    #   self.UIRotation = N.dot(rotationXMatrix(cam.rotation[0],
    #                           N.dot(rotationYMatrix(cam.rotation[1],
    #                                 rotationZMatrix(cam.rotation[3])))
      
      

    def UpdateRotation(self, rotX, rotY, rotZ):
        # Update the user requested rotations:
        self.UIRotation = N.dot(rotationXMatrix(rotX),
                                N.dot(rotationYMatrix(rotY),
                                      rotationZMatrix(rotZ)))

    def Start(self):
        glUseProgram(self.shader)
        for name in self.items:
            loc = self.locations[name]
            kind = self.kinds[name]
            item = self.items[name]
            if kind == 'vec4':
                glUniform4fv(loc, 1, item)
            elif kind == 'mat4':
                glUniformMatrix4fv(loc, 1, True, item)
            elif kind == 'int':
                glUniform1i(loc, item)
        # premultiply the model translation by the UI rotation:
        newMatrix = N.dot(self.items['modelMatrix'], self.UIRotation)
        glUniformMatrix4fv(self.locations['modelMatrix'],
                           1, True,
                           newMatrix)
        # Remember numpy arrays have to be transposed to column major order

        
    def Stop(self):
        glUseProgram(0)

theBuffer = None
theUniforms = None
theShader = None

# Surfaces that the user can view!
surf1 = Ring()
surf2 = Cylinder()
surf3 = Spiral()
surf4 = Squiggle()
surf = surf1

def init():
    global theBuffer, theUniforms, theShader
    # Normal OpenGL initializations
    glClearColor(0.5,0.5,0.5,1.0)
    glEnable(GL_DEPTH_TEST)
    
    # Create the buffer and uniform objects for our saddle surface
    vertexShader = loadFile('saddleshader.vert')
    fragmentShader = loadFile('saddleshader.frag')
    theShader = compileShaderProgram(vertexShader, fragmentShader)
    theBuffer = PositionNormalTextureBuffer(theShader,
                                            surf.createSurfacePosNormTex())
    pMatrix = projectionMatrix(1.0, 10.0, 1.0, 1.0)
    tMatrix = translationMatrix(0.0, 0.0, -5.0)
    theUniforms = Uniforms(theShader,
                           [('light', 'vec4',
                             N.array((10,10,10,1), dtype=N.float32)),
                            ('color', 'vec4',
                             N.array((1,0,1), dtype=N.float32)),
                            ('modelMatrix', 'mat4',
                             N.eye(4, dtype=N.float32)),
                            ('viewMatrix', 'mat4',
                             tMatrix),
                            ('projectionMatrix', 'mat4',
                             pMatrix),
                            ('showLines', 'int',
                             0)])

def display():
    global theBuffer, theUniforms
    # OpenGL necessities
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # The rest of this functionality should probably be wrapped in
    # a "drawable object" class.
    
    # Set the uniforms in their shader:
    theUniforms.Start()
    # Buffers actually do the drawing, so start them last:
    theBuffer.Start()
    # Shut down everything in case we want to draw something else:
    theBuffer.Stop()
    theUniforms.Stop()
                           
def main():
    global rotX, rotY, rotZ, theUniforms, theBuffer, theShader, surf, surf1, surf2
    rotX, rotY, rotZ = 0.0,0.0,0.0
    pygame.init()
    screen = pygame.display.set_mode((512,512), OPENGL|DOUBLEBUF)
    # Don't need a clock since there's no animation in this example.
    #clock = pygame.time.Clock()

    init()
    while True:
        #clock.tick(30)
        lastMouseX = None
        lastMouseY = None
        distX = 0
        distY = 0
        
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == KEYUP and event.key == K_ESCAPE:
                return
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    n = theUniforms.items['showLines']
                    theUniforms.items['showLines'] = (n+1)%2
                    
            if event.type == MOUSEMOTION and pygame.mouse.get_pressed()[0]:
                if lastMouseX is not None and lastMouseY is not None:
                    distX = event.pos[0] - lastMouseX
                    distY = event.pos[1] - lastMouseY
                # Now we have to rotate around the object by X and Y's diff.
                lastMouseX = event.pos[0]
                lastMouseY = event.pos[1]
                
        # We need to rotate the CAMERA around origin, not the object
        pressed = pygame.key.get_pressed()
        rotX += 0.02 * distY
        rotY -= 0.02 * distX
        
        if pressed[K_w]:
            rotX -= 0.02
            distX = -2
        if pressed[K_s]:
            rotY += 0.02
            distY = 2
        if pressed[K_a]:
            rotY += 0.02
            distX = -2
        if pressed[K_d]:
            rotY -= 0.02
            distX = 2
        if pressed[K_q]:
            rotZ -= 0.02
        if pressed[K_e]:
            rotZ += 0.02
        if pressed[K_1] and surf != surf1:
            surf = surf1
            theBuffer = PositionNormalTextureBuffer(theShader,
                                            surf1.createSurfacePosNormTex())
        if pressed[K_2] and surf != surf2:
            surf = surf2
            theBuffer = PositionNormalTextureBuffer(theShader,
                                            surf2.createSurfacePosNormTex())
        if pressed[K_3] and surf != surf3:
            surf = surf3
            theBuffer = PositionNormalTextureBuffer(theShader,
                                                    surf3.createSurfacePosNormTex())
        if pressed[K_4] and surf != surf4:
            surf = surf4
            theBuffer = PositionNormalTextureBuffer(theShader,
                                                    surf4.createSurfacePosNormTex())

        theUniforms.UpdateRotation(rotX, rotY, rotZ)

        display()
        pygame.display.flip()

if __name__ == '__main__':
    try:
        main()
    finally:
        pygame.quit()
        
