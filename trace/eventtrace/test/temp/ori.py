#from eventtrace.injection import t_interface, t_trace

def a():
    b()

def b():
    c()

def c():
    d()

def d():
    pass

if __name__=="__main__":
    a()
