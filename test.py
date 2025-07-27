import re


a = """+375 29 265 87 40"""
b = """+372(29) 2658740"""

print( ''.join(re.findall(r"\d+", a)))
print( ''.join(re.findall(r"\d+", b)))

from mimesis import Person

p = Person()
print( p.first_name())
print( p.username())
print( p.email())
print( p.last_name())