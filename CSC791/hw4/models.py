from __future__ import division 
import sys 
import random
import math 
import numpy as np
sys.dont_write_bytecode = True

sqrt=math.sqrt

class Log(): #only 1 attribute can be stored here
  listing =None
  def __init__(self):
    listing=[]
    lo,hi,median,iqr=1e6,-1e6,0,0
    changed=True

  def add(self,num): 
    if num==None: return num
    self.lo=min(self.lo,num)
    self.hi=max(self.hi,num)
    self.changed=True

  def stats(self):
    temp=sorted(listing)
    n=len(temp)
    p=n//2
    if n%2 : return temp[p]
    q = max(0,(min(p+1,n)))
    self.iqr=temp[int(n*.75)] - temp[int(n*.25)]
    self.median=(temp[p]+temp[q])/2
    self.changed=False
    return self.median,self.iqr
    

  def report(self):
    if changed == False: return median,iqr
    return self.stats()
    
        

class ModelBasic():
  pastLogf1 = Log()
  pastLogf2 = Log()
  presentLogf1 = Log()
  presentLogf2 = Log()
  lives=myModeloptions[Lives]

  #From Dr. M's files: a12.py
  def a12slow(lst1,lst2):
    more = same = 0.0
    for x in sorted(lst1):
      for y in sorted(lst2):
        if   x==y : 
          same += 1
        elif x > y : 
          more += 1
    return (more + 0.5*same) / (len(lst1)*len(lst2))


  """
  Given two logs, it would maintain states of lives etc
  """
  def better(self,past,present):
    if list(past.listing) == 0: return
    betteriqr = past.iqr > present.iqr
    bettermedian = past.median > present.median
    return (bettermedian | betteriqr),a12slow(past.listing,present.listing)<= myModeloptions[a12]

  def evalBetter(self):
    better1,same1=self.better(pastLogf1,presentLogf1)
    better2,same2=self.better(pastLogf2,presentLogf2)
    
    if(same1&same2 == True): lives-=1
    lives = myModeloptions[Lives]
    
    pastLogf1.listing[:]=[]
    pastLogf2.listing[:]=[]
    import copy
    pastLogf1.listing = copy.copy(presentLogf1.listing)
    pastLogf2.listing = copy.copy(presentLogf2.listing)
    presentLogf1.listing[:]=[]
    presentLogf2.listing[:]=[]

  def returnMin(self,num):
    if(num<self.minVal):
      self.minVal=num
      return num
    else:
      return self.minVal

  def returnMax(self,num):
    if(num>self.maxVal):
      self.maxVal=num
      return num
    else:
      return self.maxVal

  def evaluate(self,listpoint):
    f1 = self.f1(listpoint)
    f2 = self.f2(listpoint)
    presentLogf1.
    energy = f1+f2
    return (energy-self.minVal)/(self.maxVal-self.minVal)



  def  neighbour(self,minN,maxN):
    return minN + (maxN-minN)*random.random()

class Fonseca(ModelBasic):
  maxVal=-10000
  minVal=10000

  def __init__(self,minR=-4,maxR=4,n=3):
    self.minR=minR
    self.maxR=maxR
    self.n=n
    self.minVal=10000000
    self.maxVal=-1e6

  def f1(self,listpoint):
    n=len(listpoint)
    rootn=(n**0.5)**-1
    sum=0
    for i in range(0,n):
        sum+=(listpoint[i]-rootn)**2
    return (1 - math.exp(-sum))
  
  def f2(self,listpoint):
    n=len(listpoint)
    rootn=(n**0.5)**-1
    sum=0
    for i in range(0,n):
        sum+=(listpoint[i]+rootn)**2
    return (1 - math.exp(-sum))
 
  def info(self):
    return "Fonseca~"

  def baseline(self,minR,maxR):
    for x in range(0,50000):
      solution = [(minR + random.random()*(maxR-minR)) for z in range(0,3)]
      self.returnMax(self.f1(solution)+ self.f2(solution))
      self.returnMin(self.f1(solution)+ self.f2(solution))


class Kursawe(ModelBasic):
  def __init__(self,minR=-5,maxR=5,n=3):
    self.minR=minR
    self.maxR=maxR
    self.n=n
    self.minVal=10000000
    self.maxVal=-1e6

 
  def f1(self,listpoint):
    n=len(listpoint)
    #inspired by 'theisencr'
    return np.sum([-10*math.exp(-0.2*(np.sqrt(listpoint[i]**2 + listpoint[i+1]**2))) for i in range (0, n-1)])
    return sum

  def f2(self,listpoint):
    a=0.8
    b=3
    n=len(listpoint)
    #inspired by 'theisencr'
    return np.sum([math.fabs(listpoint[i])**a + 5*np.sin(listpoint[i])**b for i in range (0, n)])
    
  def info(self):
    return "Kursawe~"

  def baseline(self,minR,maxR):
    for x in range(0,50000):
      solution = [(minR + random.random()*(maxR-minR)) for z in range(0,3)]
      self.returnMax(self.f1(solution)+ self.f2(solution))
      self.returnMin(self.f1(solution)+ self.f2(solution))

class ZDT1(ModelBasic):
  maxVal=-10000
  minVal=10000

  def __init__(self,minR=0,maxR=1,n=30):
    self.minR=minR
    self.maxR=maxR
    self.n=n

  def f1(self,lst):
    assert(len(lst)==self.n),"Something's Messed up"
    return lst[0]
 
  def gx(self,lst):
    n=self.n
    assert(len(lst) == n),"Something's Messed up"
    return (1+ 9*np.sum([lst[i] for i in range(1,n)])/(n-1))

  def f2(self,lst):
    n=self.n
    assert(len(lst)==n),"Something's Messed up"
    gx=self.gx(lst)
    assert(gx!=0),"Ouch! it hurts"
    return gx * (1- sqrt(lst[0]/gx))

 
  def baseline(self,minR=0,maxR=1):
    for x in range(0,90000):
      solution = [(minR + random.random()*(maxR-minR)) for z in range(0,30)]
      self.returnMax(self.f1(solution)+ self.f2(solution))
      self.returnMin(self.f2(solution)+ self.f2(solution))

  def info(self):
    return "ZDT1~"


class Schaffer(ModelBasic):

  def __init__(self,minR=-1e4,maxR=1e4,n=1):
    self.minR=minR
    self.maxR=maxR
    self.n=n
    self.minVal=10000000
    self.maxVal=-1e6
 
  def evaluate(self,listpoint):
    assert(len(listpoint) == 1),"Something's Messed up"
    var=listpoint[0]
    rawEnergy = (var**2 +(var-2)**2)
    energy = (rawEnergy -self.minVal)/(self.maxVal-self.minVal)
    return energy


  def info(self):
    return "Schaffer~"

  def baseline(self,minR,maxR):
    low = self.minR
    high = self.maxR
    for index in range(0,1000000):
      inputRand =(low + (high-low)*random.random())
      #print "inputRand: %s"%inputRand
      temp = (inputRand**2 +(inputRand-2)**2)
      self.minVal=self.returnMin(temp)
      self.maxVal=self.returnMax(temp)
    print("Max: %d Min: %d"%(self.maxVal,self.minVal))

class ZDT3(ModelBasic):
  
  def __init__(self,minR=0,maxR=1,n=30):
    self.minR=minR
    self.maxR=maxR
    self.n=n
    self.minVal=1e6
    self.maxVal=-1e6

  def f1(self,listpoint):
    return listpoint[0];

  def gx(self,listpoint):
    return 1+((9/29)*sum([listpoint[i] for i in range(1,len(listpoint))]))

  def hx(self,listpoint):
    temp2 = (self.f1(listpoint)/self.gx(listpoint))**0.5
    temp32 = math.sin(10*math.pi*self.f1(listpoint))
    temp3 = (self.f1(listpoint)/self.gx(listpoint))* temp32
    return 1-temp2-temp3

  def f2(self,listpoint):
    return self.gx(listpoint)*self.hx(listpoint)

  def baseline(self,minR,maxR):
    for x in range(0,180000):
      solution = [(self.minR + random.random()*(self.maxR-self.minR)) for z in range(0,30)]
      self.returnMax(self.f1(solution)+ self.f2(solution))
      self.returnMin(self.f1(solution)+ self.f2(solution))

  def info(self):
    return "ZDT3~"

class Viennet(ModelBasic):
  def __init__(self,minR=-3,maxR=3,n=2):
    self.minR=minR
    self.maxR=maxR
    self.n=n
    self.minVal=1e6
    self.maxVal=-1e6

  def f1(self,listpoint):
    x=listpoint[0]
    y=listpoint[1]
    return 0.5*(x**2+y**2)+math.sin(x**2+y**2)

  def f2(self,listpoint):
    x=listpoint[0]
    y=listpoint[1]
    temp1=(3*x-2*y+4)**2/8
    temp2=(x-y+1)**2/27
    return temp1+temp2+15

  def f3(self,listpoint):
    x=listpoint[0]
    y=listpoint[1]
    temp1=(x**2+y**2+1)**-1 
    temp2=1.1*math.exp(-(x**2+y**2))
    return temp1+temp2

  def evaluate(self,listpoint):
    return f1(listpoint)+f2(listpoint)+f3(listpoint)

  def baseline(self):
    for x in range(0,90000):
      solution = [(self.minR + random.random()*(self.maxR-self.minR)) for z in range(0,self.n)]
      self.returnMax(self.f1(solution)+ self.f2(solution)+self.f3(solution))
      self.returnMin(self.f1(solution)+ self.f2(solution)+self.f3(solution))
  