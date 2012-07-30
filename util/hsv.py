import random

def hsvtorgb(h, s, v):
  h = h % 360
  c = s*v
  m = (v-c) *255
  x = (c * (1 - abs( ((h % 120) - 60 ) /60.0 ) ))  *255
  c = c*255
  if h<60: return  (int(c+m), int(x+m), int(m))
  if h<120: return (int(x+m), int(c+m), int(m))
  if h<180: return (int(m), int(c+m), int(x+m))
  if h<240: return (int(m), int(x+m), int(c+m))
  if h<300: return (int(x+m), int(m), int(c+m))
  return (int(c+m), int(m), int(x+m))

def randomrgb(h=None, s=None, v=None):
    if h is None:
        h = random.randrange(360)
    if s is None:
        s = random.random()
    if v is None:
        v = random.random()
    return hsvtorgb(h,s,v)

