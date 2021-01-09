import math

hullsize = 4  # hull size aof weapon and turret gear without armor
armorlevel = 12  # armor tech level is 2 + (tech level * 2), so ceramic composite armor is level 4 -> armorlevel = # 2+(2*4) = 10
turretarmorlevel = 10 # how much armor is on the turret. this is the armor nuber you usually put in the interface

armorSize = turretarmorlevel * (math.pow(math.pow(hullsize * 0.75 / math.pi, 1.0 / 3.0), 2.0) * 4 * math.pi / 4.0) / armorlevel
print("%.2f" % armorSize)
