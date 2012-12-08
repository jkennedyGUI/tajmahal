# Defines points and norms for the paramtric surfaces for use
# in saddly.py (which, really, should probably be renamed to "driver.py"
# or some such).

import numpy as N

class ParametricSurface():
    def createSurfacePosNormTex(self):
        """For each quad in a parametric surface, create
           two triangles with position, normal and texture
           coordinates."""
        verts = []
        inc = 0.2
        for s in N.arange(-6,6,inc):
            for t in N.arange(-6,6,inc):
                p00 = self.surfacePoint(s,t)
                n00 = self.surfaceNorm(s,t)
                t00 = self.surfaceTex(s,t)
                p01 = self.surfacePoint(s,t+inc)
                n01 = self.surfaceNorm(s,t+inc)
                t01 = self.surfaceTex(s,t+inc)
                p10 = self.surfacePoint(s+inc,t)
                n10 = self.surfaceNorm(s+inc,t)
                t10 = self.surfaceTex(s+inc,t)
                p11 = self.surfacePoint(s+inc,t+inc)
                n11 = self.surfaceNorm(s+inc,t+inc)
                t11 = self.surfaceTex(s+inc,t+inc)
                
                verts.extend(p00+n00+t00)
                verts.extend(p10+n10+t10)
                verts.extend(p01+n01+t01)

                verts.extend(p01+n01+t01)
                verts.extend(p11+n11+t11)
                verts.extend(p10+n10+t10)

        return N.array(verts, dtype=N.float32)
    def surfaceTex(self, s,t):
        v1,v2 = s*0.5 + 0.5, t*0.5+0.5
        return [s,t]

class Ring(ParametricSurface):
    def surfacePoint(self, s,t):
        return [0.5 * N.cos(s), 1.5 * N.cos(t) + 0.5*N.sin(s),N.sin(t), 1.0]
        #return [s, t, s*s-t*t, 1.0]
    def surfaceNorm(self, s,t):
        #x,y,z = -2*s, 2*t, 1.0
        x, y, z = 0.5*N.sin(s), 1.5 * N.sin(t), N.cos(t)
        mag = N.sqrt(x*x+y*y+z*z)
        return [x/mag, y/mag, z/mag, 0.0]
    

class Cylinder(ParametricSurface):
    def surfacePoint(self, s, t):
        return [N.sin(s), N.cos(s), t, 1.0]
    def surfaceNorm(self, s, t):
        x, y, z = N.cos(s), -N.sin(s), 1
        mag = N.sqrt(x*x + y*y + z*z)
        return [x/mag, y/mag, z/mag, 0.0]

class Spiral(ParametricSurface):
    def surfacePoint(self, s, t):
        return [s*t*N.sin(15*t), t, s*t*N.cos(15*t), 1.0]
    def surfaceNorm(self, s, t):
        x, y, z = t*N.sin(15*t), 1.0, 15*s*t*N.cos(15*t) + s*N.sin(15*t)
        mag = N.sqrt(x*x + y*y + z*z)
        return [x/mag, y/mag, z/mag, 0.0]

##class Astroid(ParametricSurface):
##    def surfacePoint(self, s, t):
##        return [(N.cos(s)*N.cos(t)) ** 3,
##                (N.sin(s)*N.cos(t)) ** 3,
##                (N.sin(t)) ** 3]
##    def surfaceNorm(self, s, t):
##        x = -3*N.sin(s)*N.cos(s)**2 * N.cos(t)**3
##        y = -3*N.sin(s)**3 * N.sin(t) * N.cos(t)**2
##        z = 3 * N.sin(t)**2 * N.cos(t)
##        mag = N.sqrt(x*x + y*y + z*z)
##        return [x/mag, y/mag, z/mag, 0.0]

class Squiggle(ParametricSurface):
    def surfacePoint(self, s, t):
        return [N.sin(s) * N.sin(t),N.cos(s) * N.sin(t),N.cos(s) * N.cos(t)]
    def surfaceNorm(self, s, t):
        x = N.sin(t) * N.cos(s)
        y = N.cos(s) * N.cos(t)
        z = N.sin(s) * N.cos(t)
        z, y, z = 1, 1, 1
        mag = N.sqrt(x*x + y*y + z*z)
        return [x/mag, y/mag, z/mag, 0.0]
    
