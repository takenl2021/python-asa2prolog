from pyswip import Prolog
p = Prolog()
p.assertz("father(michael, john)")
p.assertz("father(michael, gina)")
for s in p.query("father(X,Y)"):
   print(s["X"], "is the father of", s["Y"])
