from __future__ import division 
import sys 
import random
import math 
import numpy as np
from where_mod import *
from models import *
from options import *
from utilities import *
sys.dont_write_bytecode = True

#say = Utilities().say


class SearchersBasic():
  tempList=[]
  def display(self,score,printChar=''):
    self.tempList.append(score)
    if(self.displayStyle=="display1"):
      print(printChar),
  
  def display2(self):
    if(self.displayStyle=="display2"):
      #print xtile(self.tempList,width=25,show=" %1.6f")
      self.tempList=[]

class MaxWalkSat(SearchersBasic):
  model = None
  minR=0
  maxR=0
  random.seed(40)
  def __init__(self,modelName,displayS,bmin,bmax):
    self.model = modelName
    self.model.minVal = bmin
    self.model.maxVal = bmax
    self.displayStyle=displayS

      

  def evaluate(self):
    model = self.model
    #print "Model used: %s"%model.info()
    minR=model.minR
    maxR=model.maxR
    maxTries=int(myoptions['MaxWalkSat']['maxTries'])
    maxChanges=int(myoptions['MaxWalkSat']['maxChanges'])
    n=model.n
    threshold=float(myoptions['MaxWalkSat']['threshold'])
    probLocalSearch=float(myoptions['MaxWalkSat']['probLocalSearch'])
    bestScore=100
    bestSolution=[]


    #print "Value of p: %f"%probLocalSearch
   # model = Fonseca()
    #model.baseline(minR,maxR)
    #print model.maxVal,model.minVal
    
    for i in range(0,maxTries): #Outer Loop
      solution=[]
      for x in range(0,n):
        solution.append(minR[x] + random.random()*(maxR[x]-minR[x]))
      #print "Solution: ",
      #print solution  
      for j in range(1,maxChanges):      #Inner Loop
         score = model.evaluate(solution)
         #print score
         # optional-start
         if(score < bestScore):
           bestScore=score
           bestSolution=solution
           
         # optional-end
         if(score < threshold):
           #print "threshold reached|Tries: %d|Changes: %d"%(i,j)
           self.display(".",score),
           self.display2()
           self.model.evalBetter()    
           revN = model.maxVal-model.minVal
           return bestSolution,bestScore,self.model
         
         if(random.random() > probLocalSearch):
             c = int((self.model.n)*random.random())
             solution[c]=model.neighbour(minR,maxR,c)
             self.display(score,"+"),
         else:
             tempBestScore=score
             tempBestSolution=solution             
             c = int(self.model.n*random.random())
             interval = (maxR[c]-minR[c])/10
             for itr in range(0,10):                
                solution[c] = minR[c] + (itr*interval)*random.random()
                tempScore = model.evaluate(solution)
                if(tempBestScore > tempScore):     # score is correlated to max?
                  tempBestScore=tempScore
                  tempBestSolution=solution
             solution=tempBestSolution
             self.display(tempBestScore,"!"),
         self.display(score,"."),
         if(self.model.lives == 1):
           #print "DEATH"
           self.display2()
           self.model.evalBetter()
           revN = model.maxVal-model.minVal
           return bestSolution,bestScore,self.model
         
         if(j%50==0):
            #print "here"
            self.display2()
            self.model.evalBetter()
    revN = model.maxVal-model.minVal
    return bestSolution,bestScore,self.model      

def probFunction(old,new,t):
   return np.exp(1 *(old-new)/t)

class SA(SearchersBasic): #minimizing
  model = None
  minR=0
  maxR=0
  random.seed(1)
  def __init__(self,modelName,displayS,bmin,bmax):
    self.model = modelName
    self.model.minVal = bmin
    self.model.maxVal = bmax
    self.displayStyle=displayS


  def neighbour(self,solution,minR,maxR):
    returnValue = []
    n=len(solution)
    for i in range(0,n):
      tempRand = random.random()
      if tempRand <(1/self.model.n):
        returnValue.append(minR[i] + (maxR[i] - minR[i])*random.random())
      else:
        returnValue.append(solution[i])
    return returnValue

  def evaluate(self):
    model=self.model
    #print "Model used: %s"%(model.info())
    minR = model.minR
    maxR = model.maxR
    #model.baseline(minR,maxR)
    #print "MaxVal: %f MinVal: %f"%(model.maxVal, model.minVal)

    s = [minR[z] + (maxR[z] - minR[z])*random.random() for z in range(0,model.n)]
    #print s
    e = model.evaluate(s)
    emax = int(myoptions['SA']['emax'])
    sb = s                       #Initial Best Solution
    eb = e                       #Initial Best Energy
    k = 1
    kmax = int(myoptions['SA']['kmax'])
    count=0
    while(k <= kmax and e > emax):
      #print k,e
      sn = self.neighbour(s,minR,maxR)
      en = model.evaluate(sn)
      if(en < eb):
        sb = sn
        eb = en
        self.display(en,"."),#we get to somewhere better globally
      tempProb = probFunction(e,en,k/kmax)
      tempRand = random.random()
#      print " tempProb: %f tempRand: %f " %(tempProb,tempRand)
      if(en < e):
        s = sn
        e = en
        self.display(en,"+"), #we get to somewhere better locally
      elif(tempProb > tempRand):
        jump = True
        s = sn
        e = en
        self.display(en,"?"), #we are jumping to something sub-optimal;
        count+=1
      self.display(en,"."),
      k += 1
      if(self.model.lives == 0):
        self.display2()
        self.model.emptyWrapper()
        #print "out1" 
        revN = model.maxVal-model.minVal
        return sb,eb,self.model 
      
      if(k % 50 == 0):
         self.display2()
         self.model.evalBetter()
       #  print "%f{%d}"%(sb,count),
         count=0
    #print "out2"
    self.model.emptyWrapper()
    revN = model.maxVal-model.minVal
    return sb,eb,self.model

class GA(SearchersBasic):
  model = None
  minR=0
  maxR=0
  population={}
  random.seed(1)
  def __init__(self,modelName,displayS,bmin,bmax):
    self.model = modelName
    self.model.minVal = bmin
    self.model.maxVal = bmax
    self.displayStyle=displayS
    self.crossoverRate = float(myoptions['GA']['crossOverRate'])
    self.mutationRate = 1/self.model.n
    self.elitismrank = int(myoptions['GA']['elitism'])
    self.generation = int(myoptions['GA']['generation'])

  def crossOver(self,listdaddy,listmommy):
    rate=self.crossoverRate
    #assert(len(listdaddy)==len(listmommy)),"Something's messed up"
    if(random.random()<rate):
      minR,maxR=0,len(listdaddy)
      tone = int(minR + random.random()*((maxR)-minR))
      ttwo = int(minR + random.random()*(maxR-(minR)))
      one,two=min(tone,ttwo),max(tone,ttwo)
      #print "CrossOver: %d %d "%(one,two)
      #if(one==two):two+=2+(minR+random.random()*(maxR-minR-two-2))
      newDaddy=listdaddy[:one]+listmommy[one:two]+listdaddy[two:]
      newMommy=listmommy[:one]+listdaddy[one:two]+listmommy[two:]
      return newDaddy,newMommy
    return listdaddy,listmommy

  def mutation(self,listdaddy,listmommy):
     rate=1#self.mutationRate
     #assert(len(listdaddy)==len(listmommy)),"Something's messed up"
     if(random.random() < rate):
       #print "MUTATION"
       mutant = listdaddy[:]
       minR,maxR=0,min(len(listdaddy),len(listmommy))
       mutationE = int(minR + (random.random()*(maxR-minR)))
       mutationH = int(minR + (random.random()*(maxR-minR)))
       #print "++ %f %f"%(len(listdaddy),len(listmommy))
       #print ">> %f %f"%(mutationE,mutationH)
       mutant[mutationE]=listmommy[mutationH]
       return mutant
     return listdaddy
  
  #Changes a list of numbers to a stream of numbers
  #eg. [0.234,0.54,0.54325] -> [2345454325]
  def singleStream(self,listpoints):
     singlelist=[]
     for i in listpoints:
       tempstr = str(i)[2:]
       for x in tempstr:
         singlelist.append(x)
     #print singlelist
     return singlelist 

  def generate(self):
    minR = self.model.minR
    maxR = self.model.maxR
    #http://stackoverflow.com/questions/4119070/
    #how-to-divide-a-list-into-n-equal-parts-python
    lol = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)]
    model=self.model
    minR = model.minR
    maxR = model.maxR
    #model.baseline(minR,maxR)
    temps1 = self.Roulette(self.population)
    temps2 = self.Roulette(self.population)
    #workaround: Bug: was getting e in temp2 so,
    #whenever I see anything other than 0-9
    #I replace it
    try:
      import re 
      temps1 = re.sub('[^0-9]', '', temps1)
      temps2 = re.sub('[^0-9]', '', temps2)
    except:
      print temps1
      print temps2
      raise Exception("Ouch!")
    s1 = map(int, temps1)[:self.model.n]
    s2 = map(int, temps2)[:self.model.n]
    #print "S1,S2: %d %d " %(len(s1),len(s2))
    c1,c2=self.crossOver(s1,s2)
    #print "C1,C2: %d %d " %(len(c1),len(c2))
    m1 = self.mutation(c1,c2)
    m2 = self.mutation(c2,c1)
    #print "M1,M2: %d %d " %(len(m1),len(m2))
    #print "self.model.n: %d"%model.n
    normalc1 = [int(''.join(map(str,x)))/10**len(x) for x in lol(m1,1)]
    normalc2 = [int(''.join(map(str,x)))/10**len(x) for x in lol(m2,1)]
    #print "normalc1,normalc2: %d %d"%(len(normalc1),len(normalc2))
    #normalc1 = map(lambda x:minR+x*(maxR-minR),normalc1)    
    #normalc2 = map(lambda x:minR+x*(maxR-minR),normalc2)
    if(len(normalc1)>=self.model.n and len(normalc2)>=self.model.n):
      return normalc1[:self.model.n],normalc2[:self.model.n]  #workaround
    else:
      #print "eeeeeeeeeeee>>>>>>>>>>>>>>>>>>>>>>>>eeeeeeehaha"
      str1 = [random.random() for z in range(0,self.model.n)]
      normalc1,normalc2=[],[]
      for ij in xrange(len(str1)):
        normalc1.append(minR[ij]+str1[ij]*(maxR[ij]-minR[ij]))
      str2 = [random.random() for z in range(0,self.model.n)]  
      for ij in xrange(len(str2)):
        normalc2.append(minR[ij]+str1[ij]*(maxR[ij]-minR[ij]))
      #normalc2 = map(lambda x:minR+x*(maxR-minR),str2)
      return normalc1,normalc2

  #http://stackoverflow.com/questions/10324015
  #/fitness-proportionate-selection-roulette-wheel-selection-in-python
  def Roulette(self,choices):
    maxN = sum(choices.values())
    pick = random.uniform(0, maxN)
    current = 0
    for key, value in choices.items():
        current += abs(value)
        if current > abs(pick):
            return key
    print "Ouch!!"
    print pick,maxN
  
  def keyTransform(self,s):
    minR = self.model.minR
    maxR = self.model.maxR
    strs = self.singleStream(s)
    strs = (''.join(map(str,strs)))
    temp=[]
    for i in xrange(len(s)):
      temp.append(minR[i]+s[i]*(maxR[i]-minR[i]))
    fitness = self.model.evaluate(temp)
    return strs,fitness

  def initialPopulation(self):
    model=self.model
    for i in xrange(50):
      s = [random.random() for z in range(0,model.n)]
      strs,fitness = self.keyTransform(s)
      self.population[strs]=fitness

  def elitism(self):
    rank = self.elitismrank
    #print len(self.population),
    #This controls whether this GA maximizes
    #or minimizes
    l = sorted(self.population.values())
    l = l[rank:]
    # TODO: not at all efficient
    for i in l:
      self.population = {key: value \
      for key, value in self.population.items() \
             if value is not i}
    #print len(self.population)
     

  def evaluate(self):
    #print "evaluate>>>>>>>>>>>>>>>>>>>>>>>>>"
    bestSolution=[]
    bestScore = 1e6
    done=False
    model=self.model
    #print "Model used: %s"%(model.info())
    minR = model.minR
    maxR = model.maxR
    #model.baseline(minR,maxR)
    #print "MaxVal: %f MinVal: %f"%(model.maxVal, model.minVal)
    #print "n: %d"%model.n
    self.initialPopulation()
    #print "initial population generated"
    for x in xrange(self.generation):
      #print "Generation: %d"%x
      #print "#",
      for i in xrange(20):
        s1,s2 = self.generate()
        #TODO: dirty
        strs,fitness = self.keyTransform(s1)
        self.population[strs]=fitness
        strs,fitness = self.keyTransform(s2)
        self.display(score=fitness)
        self.population[strs]=fitness
        if(fitness<bestScore):
          bestScore=fitness
          bestSolution=strs
        #print "child born"
      self.model.evalBetter()
      self.elitism()
      #self.display2()
      if(self.model.lives == 0):
        self.display2()
        self.model.emptyWrapper()
        lol = lambda lst, sz: [lst[i:i+sz] \
        for i in range(0, len(lst), sz)]
        tempSolution = [int(''.join(map(str,x)))/10**len(x)\
        for x in lol(bestSolution,int(len(bestSolution)/model.n))]
        solution=[]
        for ij in xrange(len(tempSolution)):
          solution.append(minR[ij]+tempSolution[ij]*(maxR[ij]-minR[ij]))
        #solution= map(lambda x:minR+x*(maxR-minR),tempSolution) 
        return solution,bestScore,self.model

      
    #print sorted(self.population.values())
    self.model.emptyWrapper()
    lol = lambda lst, sz: [lst[i:i+sz] \
    for i in range(0, len(lst), sz)]
    tempSolution = [int(''.join(map(str,x)))/10**len(x)\
     for x in lol(bestSolution,int(len(bestSolution)/model.n))]
    solution= map(lambda x:minR+x*(maxR-minR),tempSolution) 
    return solution,bestScore,self.model

class DE(SearchersBasic):
  def __init__(self,modelName,displayS,bmin,bmax):
    self.model=modelName
    self.displayStyle=displayS
    self.model.minVal = bmin
    self.model.maxVal = bmax

  def threeOthers(self,frontier,one):
    #print "threeOthers"
    seen = [one]
    def other():
      #print "other"
      for i in xrange(len(frontier)):
        while True:
          k = random.randint(0,len(frontier)-1)
          #print "%d"%k
          if frontier[k] not in seen:
            seen.append(frontier[k])
            break
        return frontier[k]
    this = other()
    that = other()
    then = other()
    return this,that,then
  
  def trim(self,x,i)  : # trim to legal range
    m=self.model
    return max(m.minR[i], min(x, m.maxR[i]))      

  def extrapolate(self,frontier,one,f,cf):
    #print "Extrapolate"
    two,three,four = self.threeOthers(frontier,one)
    #print two,three,four
    solution=[]
    for d in xrange(self.model.n):
      x,y,z=two[d],three[d],four[d]
      if(random.random() < cf):
        solution.append(self.trim(x + f*(y-z),d))
      else:
        solution.append(one[d]) 
    return solution

  def update(self,f,cf,frontier,total=0.0,n=0):
    def better(old,new):
      assert(len(old)==len(new)),"MOEAD| Length mismatch"
      for i in xrange(len(old)-1): #Since the score is return as [values of all objectives and energy at the end]
        if old[i] >= new[i]: continue
        else: return False
      return True
    #print "update %d"%len(frontier)
    model=self.model
    newF = []
    total,n=0,0
    for x in frontier:
      #print "update: %d"%n
      s = model.evaluate(x)[:-1]
      new = self.extrapolate(frontier,x,f,cf)
      #print new
      newe=model.evaluate(new)[:-1]
      if better(s,newe) == True:
        newF.append(new)
      else:
        newF.append(x)
    return newF
      
  def evaluate(self,repeat=100,np=100,f=0.75,cf=0.3,epsilon=0.01):
    #print "evaluate"
    model=self.model
    minR = model.minR
    maxR = model.maxR
    #model.baseline(minR,maxR)
    frontier = [[model.minR[i]+random.random()*(model.maxR[i]-model.minR[i]) for i in xrange(model.n)]
               for _ in xrange(np)]
    #print frontier
    for i in xrange(repeat):
      frontier = self.update(f,cf,frontier)

      #for zz in frontier:
      #  print "%2.2f "%self.model.evaluate(zz),
      #print 

      #if(total/n < epsilon):
      #  break;
      self.model.evalBetter()
    minR=9e10
    for x in frontier:
      #print x
      energy = self.model.evaluate(x)[-1]
      if(minR>energy):
        minR = energy
        solution=x 
    return solution,minR,self.model

class PSO(SearchersBasic):
  def __init__(self,modelName,displayS,bmin,bmax):
    self.model = modelName
    self.model.minVal = bmin
    self.model.maxVal = bmax
    self.v = []
    self.p = []
    self.lb = []
    self.gb = [self.model.minR[i] + random.random()*(self.model.maxR[i]-self.model.minR[i]) \
    for i in xrange(self.model.n)]
    self.eb=self.model.evaluate(self.gb)
    self.displayStyle=displayS 
    self.phi1=myoptions['PSO']['phi1']
    self.phi2=myoptions['PSO']['phi2']
    self.W=myoptions['PSO']['W']
    self.N=myoptions['PSO']['N']
    self.Repeat=myoptions['PSO']['repeat']    
    self.threshold=myoptions['PSO']['threshold'] 
    for x in xrange(self.N):
      self.v.append([0 for _ in xrange(self.model.n)])
      self.p.append([self.model.minR[i] + random.random()*(self.model.maxR[i]-self.model.minR[i])\
      for i in xrange(self.model.n)])
      self.lb.append(self.p[x])
      if(self.model.evaluate(self.p[x])<self.model.evaluate(self.gb)):
        self.gb = self.p[x]
        self.eb = self.model.evaluate(self.gb)
  
  def trim(self,x,i)  : # trim to legal range
    m=self.model
    return max(m.minR[i], min(x, m.maxR[i]))  
  
  def velocity(self,v,p,lb,gb):

    newv = [self.K*(self.W*v[i]+self.phi1*random.random()*(lb[i]-p[i])\
           +self.phi2*random.random()*(gb[i]-p[i])) for i in xrange(self.model.n)]
    #print "blah1"
    return newv

  def displace(self,v,p):
    newp = [v[i]+p[i] for i in xrange(self.model.n)]
    #print "NEWP: ",newp
    return [self.trim(newp[i],i) for i in xrange(len(newp))] 

  def evaluate(self,N=30,phi1=1.3,phi2=2.8,w=1):

    model=self.model 
    v= self.v
    p= self.p 
    lb= self.lb 
    gb= self.gb
    #print "GB: "%gb
    #print "evaluate"
    phi1=self.phi1
    phi2=self.phi2
    N=self.N
    W=self.W
    Repeat=self.Repeat
    threshold=float(self.threshold)
    eb=10**6
    minR = model.minR
    maxR = model.maxR
    phi = phi1+phi2
    self.K = 2/(abs(2 - (phi) -math.sqrt(phi **2) -4*phi))
    #model.baseline(minR,maxR)

    for i in xrange(Repeat):
      #if(i%998):print "boom"     
      if(eb<threshold):
        return 0,eb,model
      for n in xrange(N):
        v[n]=self.velocity(v[n],p[n],lb[n],gb)
        p[n]=self.displace(v[n],p[n])
        pener= model.evaluate(p[n])
        lener= model.evaluate(lb[n])        
        if(pener<lener):
          lb[n] = p[n]          
          if(pener < model.evaluate(gb)):
            gb = p[n]
      eb = model.evaluate(gb)
    return 0,eb,model


def wait():
  import time 
  time.sleep(1)


class Seive(SearchersBasic): #minimizing
  model = None
  minR=0
  maxR=0
  random.seed(1)
  

  def __init__(self,modelName,displayS,bmin,bmax):
    self.model = modelName
    self.model.minVal = bmin
    self.model.maxVal = bmax
    self.displayStyle=displayS
    self.threshold =int(myoptions['Seive']['threshold'])         #threshold for number of points to be considered as a prospective solution
    self.ncol=8               #number of columns in the chess board
    self.nrow=8               #number of rows in the chess board
    self.intermaxlimit=int(myoptions['Seive']['intermaxlimit'])     #Max number of points that can be created by interpolation
    self.extermaxlimit=int(myoptions['Seive']['extermaxlimit'])     #Max number of points that can be created by extrapolation
    self.evalscores=0

  def getpoints(self,index,dictionary):
    tempL = []
    for x in dictionary[index]:tempL.append(x.dec)
    return tempL

  def convert(self,x,y): return (x*100)+y
  def rowno(self,x): return int(x/100)
  def colmno(self,x): return x%10  

  def gonw(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==1 and self.colmno(x)==1):return self.convert(nrow,ncol)#in the first coulumn and first row
    elif(self.rowno(x)==1): return self.convert(nrow,self.colmno(x)-1)
    elif(self.colmno(x)==1): return self.convert(self.rowno(x)-1,ncol)#in the first column
    else: return (x-101)

  def gow(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.colmno(x)==1): return self.convert(self.rowno(x),ncol)
    else: return (x-1)

  def gosw(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==nrow and self.colmno(x)==1): return self.convert(1,ncol)
    elif(self.rowno(x)==nrow): return self.convert(1,self.colmno(x)-1)
    elif(self.colmno(x)==1): return self.convert(self.rowno(x)+1,ncol)
    else: return (x+99)

  def gos(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==nrow): return self.convert(1,self.colmno(x))
    else: return x+100

  def gose(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==nrow and self.colmno(x)==ncol): return self.convert(1,1)
    elif(self.rowno(x)==nrow): return self.convert(1,self.colmno(x)+1)
    elif(self.colmno(x)==ncol): return self.convert(self.rowno(x)+1,1)
    else: return x+101

  def goe(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.colmno(x)==ncol): return self.convert(self.rowno(x),1)
    else: return x+1

  def gone(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==1 and self.colmno(x)==ncol): return self.convert(nrow,1)
    elif(self.rowno(x)==1): return self.convert(nrow,self.colmno(x)+1)
    elif(self.colmno(x)==ncol): return self.convert(self.rowno(x)-1,1)
    else: return x-99

  def gon(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==1): return self.convert(nrow,self.colmno(x))
    else: return x-100 

  import collections
  compare = lambda x, y: collections.Counter(x) == collections.Counter(y)

  def energy(self,m,xblock,yblock,dictionary):
    def median(lst,ordered=False):
      if not ordered: lst= sorted(lst)
      n = len(lst)
      p = n//2
      if n % 2: return lst[p]
      q = p - 1
      q = max(0,min(q,n))
      return (lst[p] + lst[q])/2

    def stats(listl):
      from scipy.stats import scoreatpercentile
      q1 = scoreatpercentile(listl,25)
      q3 = scoreatpercentile(listl,75)  
      #print "IQR : %f"%(q3-q1)
      #print "Median: %f"%median(listl)
      return median(listl),(q3-q1)

    
    tempIndex=int(100*xblock+yblock)
    #print "energy| xblock: %d yblock: %d"%(xblock,yblock)
    #print "energy| TempIndex: " ,tempIndex
    energy=[]
    try:
      sample_no = int(myoptions['Seive']['subsample'])
      samples = random.sample(dictionary[tempIndex],sample_no)
      #print samples
      for x in samples:
        #if x.obj == [None]*len(objectives(m)):  evalscores+=1
        
       # print "before energy|x.changed: ",x.scores
        x.scores = score(m,x)
        x.changed = False
        #print "after energy|x.changed: ",x.scores,x.changed
        #print "ENERGY| score:",x.obj
        energy.append(x.scores)      
      median,iqr=stats(energy)
      return median,iqr
    except: return 0,0
      #print "Energy Error"
      #import traceback
      #traceback.print_exc()


  """
  Return a list of neighbours:
  """
  def listofneighbours(self,m,xblock,yblock):
    index=self.convert(xblock,yblock)
    #print "listofneighbours| Index passed: ",index
    listL=[]
    listL.append(self.goe(index))
    listL.append(self.gose(index))
    listL.append(self.gos(index))
    listL.append(self.gosw(index))
    listL.append(self.gow(index))
    listL.append(self.gonw(index))
    listL.append(self.gon(index))
    listL.append(self.gone(index))
    return listL


  def searcher(self,m,dictionary):
    def randomC(): 
      return int(1+random.random()*7)
    def randomcell(): 
      return [randomC() for _ in xrange(2)]

    tries=0
    bmean,biqr,lbmean,lbiqr=1e6,1e6,1e6,1e6
    bsoln=[-1,-1]
    lives=int(myoptions['Seive']['lives'])
    while(tries<int(myoptions['Seive']['tries']) and  lives >= 0):
      #print "------------------Tries: %d-------------------"%lives
      #print tries<myoptions['Seive']['tries']
      soln = randomcell()
      tries+=1
      repeat=0
      #print "myoptions['Seive']['repeat']: ",myoptions['Seive']['repeat']
      #print "myoptions['Seive']['tries']: ",myoptions['Seive']['tries']
      #wait()
      while(repeat<int(myoptions['Seive']['repeat']) ):
        #print "Solution being tried: %d %d "%(soln[0],soln[1])
        result = self.generateNew(m,soln[0],soln[1],dictionary)
        if(result == False): 
          print "In middle of the desert"
          break
        else:
          #print "Searcher| Solution being tried: %d %d "%(soln[0],soln[1])
          smean,siqr = self.energy(m,soln[0],soln[1],dictionary)
          #print "Searcher| smean,siqr: %d %d "%(smean,siqr)
          neighbours = self.listofneighbours(m,soln[0],soln[1])
          #print neighbours
          nmean,niqr=1e6,1e6
          for neighbour in neighbours:
            #print "Searcher| neighbour: ",neighbour
            result = self.generateNew(m,int(neighbour/100),neighbour%10,dictionary)
            #print "Searcher| points 
            if(result == True):
              tmean,tiqr = self.energy(m,int(neighbour/100),neighbour%10,dictionary)
              #print "Searcher| tmean,tiqr: ",tmean,tiqr
              if(tmean<nmean or (tmean==nmean and tiqr < niqr)):
                #print "Searcher| tmean: %f mean: %f"%(tmean,mean)
                #print "Searcher| tiqr: %f iqr: %f"%(tiqr,iqr)
                nsoln = [int(neighbour/100),neighbour%10]
                #print "Searcher|btsoln: ",btsoln
                nmean=tmean
                niqr=tiqr
            else:
              print "Searcher|NAAAAAAAAAAAAH"
              pass
          if(nmean<smean or (nmean == smean and nmean<smean)):
            soln=nsoln
            repeat+=1
          else:
            break
          

          #print nmean,smean,bmean,siqr,biqr
          if(min(nmean,smean)<bmean or (min(nmean,smean) == bmean and min(niqr,siqr)<biqr)):
            bmean=min(nmean,smean)
            biqr=min(niqr,siqr)
            if(nmean<smean or (nmean == smean and niqr<siqr)):
              bsoln=nsoln
            else: bsoln=soln
      if(bmean<lbmean or biqr <lbiqr): pass
      else:
        #print "Lost Life" 
        lives-=1
      lbmean=bmean
      lbiqr=biqr
#I need to look at slope now. The number of evaluation is not reducing a lot
#need to put a visited sign somewhere to stop evaluations 


    #print ">>>>>>>>>>>>>>WOW Mean:%f IQR: %f"%(bmean,biqr)
    #print ">>>>>>>>>>>>>>WOW Soultion: ",bsoln
    if(bsoln[0]==-1 and bsoln[1]==-1): raise Exception("No best solution found!")
    return bsoln

  def one(self,m,lst): 
    def any(l,h):
      return (0 + random.random()*(h-l))
    return lst[int(any(0,len(lst) - 1)) ]

  def generateNew(self,m,xblock,yblock,dictionary):
    convert = self.convert
    rowno = self.rowno
    colmno = self.colmno 

    def indexConvert(index):
      return int(index/100),index%10

    def opposite(a,b):
      ax,ay,bx,by=a/100,a%100,b/100,b%100
      if(abs(ax-bx)==2 or abs(ay-by)==2):return True
      else: return False

    def thresholdCheck(index):
      try:
        #print "Threshold Check: ",index
        if(len(dictionary[index])>self.threshold):return True
        else:return False
      except:
        return False

    def interpolateCheck(xblock,yblock):
      returnList=[]
      if(thresholdCheck(self.gonw(convert(xblock,yblock))) and thresholdCheck(self.gose(convert(xblock,yblock))) == True):
        returnList.append(self.gonw(convert(xblock,yblock)))
        returnList.append(self.gose(convert(xblock,yblock)))
      if(thresholdCheck(self.gow(convert(xblock,yblock))) and thresholdCheck(self.goe(convert(xblock,yblock))) == True):
       returnList.append(self.gow(convert(xblock,yblock)))
       returnList.append(self.goe(convert(xblock,yblock)))
      if(thresholdCheck(self.gosw(convert(xblock,yblock))) and thresholdCheck(self.gone(convert(xblock,yblock))) == True):
       returnList.append(self.gosw(convert(xblock,yblock)))
       returnList.append(self.gone(convert(xblock,yblock)))
      if(thresholdCheck(self.gon(convert(xblock,yblock))) and thresholdCheck(self.gos(convert(xblock,yblock))) == True):
       returnList.append(self.gon(convert(xblock,yblock)))
       returnList.append(self.gos(convert(xblock,yblock)))
      return returnList


    def extrapolateCheck(xblock,yblock):
      #TODO: If there are more than one consequetive blocks with threshold number of points how do we handle it?
      #TODO: Need to make this logic more succint
      returnList=[]
      #go North West
      temp = self.gonw(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gonw(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gonw(temp))

      #go North 
      temp = self.gon(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gon(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gon(temp))

      #go North East
      temp = self.gone(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gone(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gone(temp))
  
      #go East
      temp = self.goe(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.goe(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.goe(temp))

      #go South East
      temp = self.gose(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gose(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gose(temp))

      #go South
      temp = self.gos(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gos(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gos(temp))

      #go South West
      temp = self.gosw(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gosw(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gosw(temp))
 
      #go West
      temp = self.gow(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gow(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gow(temp))

      return returnList
  
    newpoints=[]
    #print "generateNew| xblock: %d yblock: %d"%(xblock,yblock)
    #print "generateNew| convert: ",convert(xblock,yblock)
    #print "generateNew| thresholdCheck(convert(xblock,yblock): ",thresholdCheck(convert(xblock,yblock))
    #print "generateNew| points in the block: ",len(dictionary[convert(xblock,yblock)])
    if(thresholdCheck(convert(xblock,yblock))==False):
      #print "generateNew| Cell is relatively sparse: Might need to generate new points"
      listInter=interpolateCheck(xblock,yblock)
      #print "generateNew|listInter: ",listInter
      if(len(listInter)!=0):
        decisions=[]
        assert(len(listInter)%2==0),"listInter%2 not 0"
      #print thresholdCheck(xb),thresholdCheck(yb)
        for i in xrange(int(len(listInter)/2)):
          decisions.extend(self.wrapperInterpolate(m,listInter[i*2],listInter[(i*2)+1],int(self.intermaxlimit/len(listInter))+1,dictionary))
          #print "generateNew| Decisions Length: ",len(decisions)
        #print "generateNew| Decisions: ",decisions
        if convert(xblock,yblock) in dictionary: pass
        else:
          #print convert(xblock,yblock)
          assert(convert(xblock,yblock)>=101),"Something's wrong!" 
          assert(convert(xblock,yblock)<=808),"Something's wrong!" 
          dictionary[convert(xblock,yblock)]=[]
        old = self._checkDictionary(dictionary)
        for decision in decisions:dictionary[convert(xblock,yblock)].append(self.generateSlot(m,decision,xblock,yblock))
        #print "generateNew| Interpolation works!"
        new = self._checkDictionary(dictionary)
        #print "generateNew|Interpolation| Number of new points generated: ", (new-old)
        return True
      else:
        #print "generateNew| Interpolation failed!"
        decisions=[]
        listExter = extrapolateCheck(xblock,yblock)
        if(len(listExter)==0):
          #print "generateNew|Interpolation and Extrapolation failed|In a tight spot..somewhere in the desert RANDOM JUMP REQUIRED"
          return False
        else:
          assert(len(listExter)%2==0),"listExter%2 not 0"
          for i in xrange(int(len(listExter)/2)):
            decisions.extend(self.wrapperextrapolate(m,listExter[2*i],listExter[(2*i)+1],int(self.extermaxlimit)/len(listExter),dictionary))
          if convert(xblock,yblock) in dictionary: pass
          else: 
            assert(convert(xblock,yblock)>=101),"Something's wrong!" 
            assert(convert(xblock,yblock)<=808),"Something's wrong!" 
            dictionary[convert(xblock,yblock)]=[]
          old = self._checkDictionary(dictionary)
          for decision in decisions: dictionary[convert(xblock,yblock)].append(self.generateSlot(m,decision,xblock,yblock))
          new = self._checkDictionary(dictionary)
          #print "generateNew|Extrapolation Worked ",len(dictionary[convert(xblock,yblock)])
          #print "generateNew|Extrapolation| Number of new points generated: ", (new-old)
          return True
    else:
      listExter = extrapolateCheck(xblock,yblock)
      if(len(listExter) == 0):
        #print "generateNew| Lot of points but middle of a desert"
        return False #A lot of points but right in the middle of a deseart
      else:
        return True
    """
    print interpolateCheck(xblock,yblock)
    """
  def wrapperInterpolate(self,m,xindex,yindex,maxlimit,dictionary):
    def interpolate(lx,ly,cr=0.3,fmin=0,fmax=1):
      def lo(m,index)      : return m.minR[index]
      def hi(m,index)      : return m.maxR[index]
      def trim(m,x,i)  : # trim to legal range
        return max(lo(m,i), x%hi(m,i))
      assert(len(lx)==len(ly))
      genPoint=[]
      for i in xrange(len(lx)):
        x,y=lx[i],ly[i]
        #print x
        #print y
        rand = random.random
        if rand < cr:
          probEx = fmin +(fmax-fmin)*rand()
          new = trim(m,min(x,y)+probEx*abs(x-y),i)
        else:
          new = y
        genPoint.append(new)
      return genPoint

    decision=[]
    #print "Number of points in ",xindex," is: ",len(dictionary[xindex])
    #print "Number of points in ",yindex," is: ",len(dictionary[yindex])
    xpoints=self.getpoints(xindex,dictionary)
    ypoints=self.getpoints(yindex,dictionary)
    import itertools
    listpoints=list(itertools.product(xpoints,ypoints))
    count=0
    while True:
      if(count>min(len(xpoints),maxlimit)):break
      x=self.one(m,listpoints)
      temp = interpolate(x[0],x[1])
      decision.append(temp)
      count+=1
    
    return decision


  def generateSlot(self,m,decision,x,y):
    newpoint=Slots(changed = True,
            scores=1e6, 
            xblock=-1, #sam
            yblock=-1,  #sam
            x=-1,
            y=-1,
            obj = [None] * m.objf, #This needs to be removed. Not using it as of 11/10
            dec = [some(m,d) for d in xrange(m.n)])

    #scores(m,newpoint)
    #print "Decision: ",newpoint.dec
    #print "Objectives: ",newpoint.obj
    return newpoint


  #There are three points and I am trying to extrapolate. Need to pass two cell numbers
  def wrapperextrapolate(self,m,xindex,yindex,maxlimit,dictionary):
    def extrapolate(lx,ly,lz,cr=0.3,fmin=0.9,fmax=2):
      def lo(m,index)      : return m.minR[index]
      def hi(m,index)      : return m.maxR[index]
      def trim(m,x,i)  : # trim to legal range
        return max(lo(m,i), x%hi(m,i))
      def indexConvert(index):
        return int(index/100),index%10
      assert(len(lx)==len(ly)==len(lz))
      genPoint=[]
      for i in xrange(len(lx)):
        x,y,z = lx[i],ly[i],lz[i]
        rand = random.random()

        if rand < cr:
          probEx = fmin + (fmax-fmin)*random.random()
          new = trim(m,x + probEx*(y-z),i)
        else:
          new = y #Just assign a value for that decision
        genPoint.append(new)
      return genPoint

    decision=[]
    #TODO: need to put an assert saying checking whether extrapolation is actually possible
    xpoints=self.getpoints(xindex,dictionary)
    ypoints=self.getpoints(yindex,dictionary)
    count=0
    
    while True:
      if(count>min(len(xpoints),maxlimit)):break
      two = self.one(m,xpoints)
      index2,index3=0,0
      while(index2 == index3): #just making sure that the indexes are not the same
        index2=random.randint(0,len(ypoints)-1)
        index3=random.randint(0,len(ypoints)-1)

      three=ypoints[index2]
      four=ypoints[index3]
      temp = extrapolate(two,three,four)
      #decision.append(extrapolate(two,three,four))
      decision.append(temp)
      count+=1
    return decision

  def _checkDictionary(self,dictionary):
    sum=0
    for i in dictionary.keys():
      sum+=len(dictionary[i])
    return sum
  
  def decisions_check(self,dictionary):
    for i in dictionary.keys():
      for i in dictionary[i]:
        print " ",i.scores,
      print 


  def evaluate(self):
    def generate_dictionary():  
      dictionary = {}
      chess_board = whereMain(self.model) #checked: working well
      for i in range(1,9):
        for j in range(1,9):
          temp = [x for x in chess_board if x.xblock==i and x.yblock==j]
          if(len(temp)!=0):
            index=temp[0].xblock*100+temp[0].yblock
            dictionary[index] = temp
            assert(len(temp)==len(dictionary[index])),"something"
      return dictionary

    def find_best_score(index,dictionary):
      mint=10e6
      for x in dictionary[self.convert(index[0],index[1])]:
        #print x.scores
        if(x.scores<mint): 
          mint=x.scores
          return_value = x
      return return_value

    model=self.model
    #print "Model used: %s"%(model.info())
    
    minR = model.minR
    maxR = model.maxR
    #model.baseline(minR,maxR)
    
    dictionary = generate_dictionary()
    bestSolution = self.searcher(self.model,dictionary)
    bestSolution = find_best_score(bestSolution,dictionary)
    #self.decisions_check(dictionary)
    #print "Number of points: ",self._checkDictionary(dictionary)
    return bestSolution.dec,bestSolution.scores,model

   

class Seive3(SearchersBasic): #minimizing
  model = None
  minR=0
  maxR=0
  random.seed(1)



  def wrapperInterpolate(self,m,xindex,yindex,maxlimit,dictionary):
    def interpolate(lx,ly,cr=0.3,fmin=0,fmax=1):
      def lo(m,index)      : return m.minR[index]
      def hi(m,index)      : return m.maxR[index]
      def trim(m,x,i)  : # trim to legal range
        return max(lo(m,i), x%hi(m,i))
      assert(len(lx)==len(ly))
      genPoint=[]
      for i in xrange(len(lx)):
        x,y=lx[i],ly[i]
        #print x
        #print y
        rand = random.random
        if rand < cr:
          probEx = fmin +(fmax-fmin)*rand()
          new = trim(m,min(x,y)+probEx*abs(x-y),i)
        else:
          new = y
        genPoint.append(new)
      return genPoint

    decision=[]
    #print "Number of points in ",xindex," is: ",len(dictionary[xindex])
    #print "Number of points in ",yindex," is: ",len(dictionary[yindex])
    xpoints=self.getpoints(xindex,dictionary)
    ypoints=self.getpoints(yindex,dictionary)
    import itertools
    listpoints=list(itertools.product(xpoints,ypoints))
    #print "Length of Listpoints: ",len(listpoints)
    count=0
    while True:
      if(count>min(len(xpoints),maxlimit)):break
      x=self.one(m,listpoints)
      decision.append(interpolate(x[0],x[1]))
      count+=1
    return decision


  def generateSlot(self,m,decision,x,y):
    newpoint=Slots(changed = True,
            scores=1e6, 
            xblock=-1, #sam
            yblock=-1,  #sam
            x=-1,
            y=-1,
            obj = [None] * m.objf, #This needs to be removed. Not using it as of 11/10
            dec = [some(m,d) for d in xrange(m.n)])

    scores(m,newpoint)
    #print "Decision: ",newpoint.dec
    #print "Objectives: ",newpoint.obj
    return newpoint


  #There are three points and I am trying to extrapolate. Need to pass two cell numbers
  def wrapperextrapolate(self,m,xindex,yindex,maxlimit,dictionary):
    def extrapolate(lx,ly,lz,cr=0.3,fmin=0.9,fmax=2):
      def lo(m,index)      : return m.minR[index]
      def hi(m,index)      : return m.maxR[index]
      def trim(m,x,i)  : # trim to legal range
        return max(lo(m,i), x%hi(m,i))
      def indexConvert(index):
        return int(index/100),index%10
      assert(len(lx)==len(ly)==len(lz))
      genPoint=[]
      for i in xrange(len(lx)):
        x,y,z = lx[i],ly[i],lz[i]
        rand = random.random()

        if rand < cr:
          probEx = fmin + (fmax-fmin)*random.random()
          new = trim(m,x + probEx*(y-z),i)
        else:
          new = y #Just assign a value for that decision
        genPoint.append(new)
      return genPoint

    decision=[]
    #TODO: need to put an assert saying checking whether extrapolation is actually possible
    xpoints=self.getpoints(xindex,dictionary)
    ypoints=self.getpoints(yindex,dictionary)
    count=0
    while True:
      if(count>min(len(xpoints),maxlimit)):break
      two = self.one(m,xpoints)
      index2,index3=0,0
      while(index2 == index3): #just making sure that the indexes are not the same
        index2=random.randint(0,len(ypoints)-1)
        index3=random.randint(0,len(ypoints)-1)

      three=ypoints[index2]
      four=ypoints[index3]
      temp = extrapolate(two,three,four)
      #decision.append(extrapolate(two,three,four))
      decision.append(temp)
      count+=1
    return decision
  

  def __init__(self,modelName,displayS,bmin,bmax):
    self.model = modelName
    self.model.minVal = bmin
    self.model.maxVal = bmax
    self.displayStyle=displayS
    self.threshold =20#int(myoptions['Seive']['threshold'])         #threshold for number of points to be considered as a prospective solution
    self.ncol=8               #number of columns in the chess board
    self.nrow=8               #number of rows in the chess board
    self.intermaxlimit=int(myoptions['Seive']['intermaxlimit'])     #Max number of points that can be created by interpolation
    self.extermaxlimit=int(myoptions['Seive']['extermaxlimit'])     #Max number of points that can be created by extrapolation
    self.evalscores=0
  def convert(self,x,y): return (x*100)+y
  def rowno(self,x): return int(x/100)
  def colmno(self,x): return x%10 

  def gonw(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==1 and self.colmno(x)==1):return self.convert(nrow,ncol)#in the first coulumn and first row
    elif(self.rowno(x)==1): return self.convert(nrow,self.colmno(x)-1)
    elif(self.colmno(x)==1): return self.convert(self.rowno(x)-1,ncol)#in the first column
    else: return (x-101)

  def gow(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.colmno(x)==1): return self.convert(self.rowno(x),ncol)
    else: return (x-1)

  def gosw(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==nrow and self.colmno(x)==1): return self.convert(1,ncol)
    elif(self.rowno(x)==nrow): return self.convert(1,self.colmno(x)-1)
    elif(self.colmno(x)==1): return self.convert(self.rowno(x)+1,ncol)
    else: return (x+99)

  def gos(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==nrow): return self.convert(1,self.colmno(x))
    else: return x+100

  def gose(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==nrow and self.colmno(x)==ncol): return self.convert(1,1)
    elif(self.rowno(x)==nrow): return self.convert(1,self.colmno(x)+1)
    elif(self.colmno(x)==ncol): return self.convert(self.rowno(x)+1,1)
    else: return x+101

  def goe(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.colmno(x)==ncol): return self.convert(self.rowno(x),1)
    else: return x+1

  def gone(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==1 and self.colmno(x)==ncol): return self.convert(nrow,1)
    elif(self.rowno(x)==1): return self.convert(nrow,self.colmno(x)+1)
    elif(self.colmno(x)==ncol): return self.convert(self.rowno(x)-1,1)
    else: return x-99

  def gon(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==1): return self.convert(nrow,self.colmno(x))
    else: return x-100 

  def generateNew(self,m,xblock,yblock,dictionary):
    convert = self.convert
    rowno = self.rowno
    colmno = self.colmno 

    def indexConvert(index):
      return int(index/100),index%10

    def opposite(a,b):
      ax,ay,bx,by=a/100,a%100,b/100,b%100
      if(abs(ax-bx)==2 or abs(ay-by)==2):return True
      else: return False

    def thresholdCheck(index):
      try:
        #print "Threshold Check: ",index
        if(len(dictionary[index])>self.threshold):return True
        else:return False
      except:
        return False

    def interpolateCheck(xblock,yblock):
      returnList=[]
      if(thresholdCheck(self.gonw(convert(xblock,yblock))) and thresholdCheck(self.gose(convert(xblock,yblock))) == True):
        returnList.append(self.gonw(convert(xblock,yblock)))
        returnList.append(self.gose(convert(xblock,yblock)))
      if(thresholdCheck(self.gow(convert(xblock,yblock))) and thresholdCheck(self.goe(convert(xblock,yblock))) == True):
       returnList.append(self.gow(convert(xblock,yblock)))
       returnList.append(self.goe(convert(xblock,yblock)))
      if(thresholdCheck(self.gosw(convert(xblock,yblock))) and thresholdCheck(self.gone(convert(xblock,yblock))) == True):
       returnList.append(self.gosw(convert(xblock,yblock)))
       returnList.append(self.gone(convert(xblock,yblock)))
      if(thresholdCheck(self.gon(convert(xblock,yblock))) and thresholdCheck(self.gos(convert(xblock,yblock))) == True):
       returnList.append(self.gon(convert(xblock,yblock)))
       returnList.append(self.gos(convert(xblock,yblock)))
      return returnList


    def extrapolateCheck(xblock,yblock):
      #TODO: If there are more than one consequetive blocks with threshold number of points how do we handle it?
      #TODO: Need to make this logic more succint
      returnList=[]
      #go North West
      temp = self.gonw(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gonw(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gonw(temp))

      #go North 
      temp = self.gon(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gon(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gon(temp))

      #go North East
      temp = self.gone(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gone(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gone(temp))
  
      #go East
      temp = self.goe(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.goe(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.goe(temp))

      #go South East
      temp = self.gose(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gose(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gose(temp))

      #go South
      temp = self.gos(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gos(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gos(temp))

      #go South West
      temp = self.gosw(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gosw(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gosw(temp))
 
      #go West
      temp = self.gow(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gow(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gow(temp))

      return returnList
  
    newpoints=[]
    #print "generateNew| xblock: %d yblock: %d"%(xblock,yblock)
    #print "generateNew| convert: ",convert(xblock,yblock)
    #print "generateNew| thresholdCheck(convert(xblock,yblock): ",thresholdCheck(convert(xblock,yblock))
    #print "generateNew| points in the block: ",len(dictionary[convert(xblock,yblock)])
    if(thresholdCheck(convert(xblock,yblock))==False):
      #print "generateNew| Cell is relatively sparse: Might need to generate new points"
      listInter=interpolateCheck(xblock,yblock)
      #print "generateNew|listInter: ",listInter
      if(len(listInter)!=0):
        decisions=[]
        assert(len(listInter)%2==0),"listInter%2 not 0"
      #print thresholdCheck(xb),thresholdCheck(yb)
        for i in xrange(int(len(listInter)/2)):
          decisions.extend(self.wrapperInterpolate(m,listInter[i*2],listInter[(i*2)+1],int(self.intermaxlimit/len(listInter))+1,dictionary))
          #print "generateNew| Decisions Length: ",len(decisions)
        #print "generateNew| Decisions: ",decisions
        if convert(xblock,yblock) in dictionary: pass
        else:
          #print convert(xblock,yblock)
          assert(convert(xblock,yblock)>=101),"Something's wrong!" 
          assert(convert(xblock,yblock)<=808),"Something's wrong!" 
          dictionary[convert(xblock,yblock)]=[]
        old = self._checkDictionary(dictionary)
        for decision in decisions:dictionary[convert(xblock,yblock)].append(self.generateSlot(m,decision,xblock,yblock))
        #print "generateNew| Interpolation works!"
        new = self._checkDictionary(dictionary)
        #print "generateNew|Interpolation| Number of new points generated: ", (new-old)
        return True
      else:
        #print "generateNew| Interpolation failed!"
        decisions=[]
        listExter = extrapolateCheck(xblock,yblock)
        if(len(listExter)==0):
          #print "generateNew|Interpolation and Extrapolation failed|In a tight spot..somewhere in the desert RANDOM JUMP REQUIRED"
          return False
        else:
          assert(len(listExter)%2==0),"listExter%2 not 0"
          for i in xrange(int(len(listExter)/2)):
            decisions.extend(self.wrapperextrapolate(m,listExter[2*i],listExter[(2*i)+1],int(self.extermaxlimit)/len(listExter),dictionary))
          if convert(xblock,yblock) in dictionary: pass
          else: 
            assert(convert(xblock,yblock)>=101),"Something's wrong!" 
            assert(convert(xblock,yblock)<=808),"Something's wrong!" 
            dictionary[convert(xblock,yblock)]=[]
          old = self._checkDictionary(dictionary)
          for decision in decisions: dictionary[convert(xblock,yblock)].append(self.generateSlot(m,decision,xblock,yblock))
          new = self._checkDictionary(dictionary)
          #print "generateNew|Extrapolation Worked ",len(dictionary[convert(xblock,yblock)])
          #print "generateNew|Extrapolation| Number of new points generated: ", (new-old)
          return True
    else:
      listExter = extrapolateCheck(xblock,yblock)
      if(len(listExter) == 0):
        #print "generateNew| Lot of points but middle of a desert"
        return False #A lot of points but right in the middle of a deseart
      else:
        return True
    """
    print interpolateCheck(xblock,yblock)
    """
  def wrapperInterpolate(self,m,xindex,yindex,maxlimit,dictionary):
    def interpolate(lx,ly,cr=0.3,fmin=0,fmax=1):
      def lo(m,index)      : return m.minR[index]
      def hi(m,index)      : return m.maxR[index]
      def trim(m,x,i)  : # trim to legal range
        return max(lo(m,i), x%hi(m,i))
      assert(len(lx)==len(ly))
      genPoint=[]
      for i in xrange(len(lx)):
        x,y=lx[i],ly[i]
        #print x
        #print y
        rand = random.random
        if rand < cr:
          probEx = fmin +(fmax-fmin)*rand()
          new = trim(m,min(x,y)+probEx*abs(x-y),i)
        else:
          new = y
        genPoint.append(new)
      return genPoint

    decision=[]
    #print "Number of points in ",xindex," is: ",len(dictionary[xindex])
    #print "Number of points in ",yindex," is: ",len(dictionary[yindex])
    xpoints=self.getpoints(xindex,dictionary)
    ypoints=self.getpoints(yindex,dictionary)
    import itertools
    listpoints=list(itertools.product(xpoints,ypoints))
    #print "Length of Listpoints: ",len(listpoints)
    count=0
    while True:
      if(count>min(len(xpoints),maxlimit)):break
      x=self.one(m,listpoints)
      decision.append(interpolate(x[0],x[1]))
      count+=1
    return decision



  def listofneighbours(self,xblock,yblock):
    index=self.convert(xblock,yblock)
    #print "listofneighbours| Index passed: ",index
    listL=[]
    listL.append(self.goe(index))
    listL.append(self.gose(index))
    listL.append(self.gos(index))
    listL.append(self.gosw(index))
    listL.append(self.gow(index))
    listL.append(self.gonw(index))
    listL.append(self.gon(index))
    listL.append(self.gone(index))
    return listL

  def getpoints(self,index,dictionary):
    tempL = []
    for x in dictionary[index]:tempL.append(x.dec)
    return tempL

  def one(self,model,lst): 
    def any(l,h):
      return (0 + random.random()*(h-l))
    return lst[int(any(0,len(lst) - 1)) ]

  def evaluate(self,points=[],depth=0):
    def generate_dictionary(points=[]):  
      dictionary = {}
      chess_board = whereMain(self.model,points) #checked: working well
      for i in range(1,9):
        for j in range(1,9):
          temp = [x for x in chess_board if x.xblock==i and x.yblock==j]
          if(len(temp)!=0):
            index=temp[0].xblock*100+temp[0].yblock
            dictionary[index] = temp
            assert(len(temp)==len(dictionary[index])),"something"
      return dictionary

    def thresholdCheck(index,dictionary):
      try:
        #print "Threshold Check: ",index
        if(len(dictionary[index])>self.threshold):return True
        else:return False
      except:
        return False

    model = self.model
    minR = model.minR
    maxR = model.maxR
    #if depth == 0: model.baseline(minR,maxR)

    dictionary = generate_dictionary(points)
    #print "Depth: %d #points: %d"%(depth,self._checkDictionary(dictionary))
    from collections import defaultdict
    graph = defaultdict(list)
    matrix = [[0 for x in range(8)] for x in range(8)]
    for i in xrange(1,9):
      for j in xrange(1,9):
        if(thresholdCheck(i*100+j,dictionary)==False):
          result = self.generateNew(model,i,j,dictionary)
          if result == False: 
            #print "in middle of desert"
            continue
        matrix[i-1][j-1] = score(model,self.one(model,dictionary[i*100+j]))[-1]

        
       # print matrix[i-1][j-1],
      #print
    for i in xrange(1,9):
      for j in xrange(1,9):
        sumn=0
        s = matrix[i-1][j-1]
        neigh = self.listofneighbours(i,j)
        sumn = sum([1 for x in neigh if matrix[self.rowno(x)-1][self.colmno(x)-1]>s])
        if (i*100+j) in dictionary:
          graph[int(sumn)].append(i*100+j)
        
    high = 1e6
    bsoln = None
    maxi = max(graph.keys())
    #print graph.keys()
    #print "Number of points: ",len(graph[maxi])
    for x in graph[maxi]:
       if(len(dictionary[x])<10):
          self.generateNew(model,i,j,dictionary)
          #print "Generate New|======================:" ,len(dictionary[x])
       #temp = random.sample(dictionary[x],min(len(dictionary[x]),15))
       for y in dictionary[x]:
         temp2 = score(model,y)[-1]
         #print temp2
         if temp2 < high:
           high = temp2
           bsoln = y
       if(depth <3):
         rsoln,sc,model = self.evaluate(dictionary[x],depth+1)
         #print high,sc,
         high = high if sc > high else sc
         
    return bsoln.dec,high,model

  def _checkDictionary(self,dictionary):
    sum=0
    for i in dictionary.keys():
      sum+=len(dictionary[i])
    return sum

class Seive2(SearchersBasic): #minimizing
  model = None
  minR=0
  maxR=0
  random.seed(1)



  def wrapperInterpolate(self,m,xindex,yindex,maxlimit,dictionary):
    def interpolate(lx,ly,cr=0.3,fmin=0,fmax=1):
      def lo(m,index)      : return m.minR[index]
      def hi(m,index)      : return m.maxR[index]
      def trim(m,x,i)  : # trim to legal range
        return max(lo(m,i), x%hi(m,i))
      assert(len(lx)==len(ly))
      genPoint=[]
      for i in xrange(len(lx)):
        x,y=lx[i],ly[i]
        #print x
        #print y
        rand = random.random
        if rand < cr:
          probEx = fmin +(fmax-fmin)*rand()
          new = trim(m,min(x,y)+probEx*abs(x-y),i)
        else:
          new = y
        genPoint.append(new)
      return genPoint

    decision=[]
    #print "Number of points in ",xindex," is: ",len(dictionary[xindex])
    #print "Number of points in ",yindex," is: ",len(dictionary[yindex])
    xpoints=self.getpoints(xindex,dictionary)
    ypoints=self.getpoints(yindex,dictionary)
    import itertools
    listpoints=list(itertools.product(xpoints,ypoints))
    #print "Length of Listpoints: ",len(listpoints)
    count=0
    while True:
      if(count>min(len(xpoints),maxlimit)):break
      x=self.one(m,listpoints)
      decision.append(interpolate(x[0],x[1]))
      count+=1
    return decision


  def generateSlot(self,m,decision,x,y):
    newpoint=Slots(changed = True,
            scores=1e6, 
            xblock=-1, #sam
            yblock=-1,  #sam
            x=-1,
            y=-1,
            obj = [None] * m.objf, #This needs to be removed. Not using it as of 11/10
            dec = [some(m,d) for d in xrange(m.n)])

    scores(m,newpoint)
    #print "Decision: ",newpoint.dec
    #print "Objectives: ",newpoint.obj
    return newpoint


  #There are three points and I am trying to extrapolate. Need to pass two cell numbers
  def wrapperextrapolate(self,m,xindex,yindex,maxlimit,dictionary):
    def extrapolate(lx,ly,lz,cr=0.3,fmin=0.9,fmax=2):
      def lo(m,index)      : return m.minR[index]
      def hi(m)      : return m.maxR[index]
      def trim(m,x,i)  : # trim to legal range
        return max(lo(m,i), x%hi(m,i))
      def indexConvert(index):
        return int(index/100),index%10
      assert(len(lx)==len(ly)==len(lz))
      genPoint=[]
      for i in xrange(len(lx)):
        x,y,z = lx[i],ly[i],lz[i]
        rand = random.random()

        if rand < cr:
          probEx = fmin + (fmax-fmin)*random.random()
          new = trim(m,x + probEx*(y-z),i)
        else:
          new = y #Just assign a value for that decision
        genPoint.append(new)
      return genPoint

    decision=[]
    #TODO: need to put an assert saying checking whether extrapolation is actually possible
    xpoints=self.getpoints(xindex,dictionary)
    ypoints=self.getpoints(yindex,dictionary)
    count=0
    while True:
      if(count>min(len(xpoints),maxlimit)):break
      two = self.one(m,xpoints)
      index2,index3=0,0
      while(index2 == index3): #just making sure that the indexes are not the same
        index2=random.randint(0,len(ypoints)-1)
        index3=random.randint(0,len(ypoints)-1)

      three=ypoints[index2]
      four=ypoints[index3]
      temp = extrapolate(two,three,four)
      #decision.append(extrapolate(two,three,four))
      decision.append(temp)
      count+=1
    return decision
  

  def __init__(self,modelName,displayS,bmin,bmax):
    self.model = modelName
    self.model.minVal = bmin
    self.model.maxVal = bmax
    self.displayStyle=displayS
    self.threshold =1#int(myoptions['Seive']['threshold'])         #threshold for number of points to be considered as a prospective solution
    self.ncol=8               #number of columns in the chess board
    self.nrow=8               #number of rows in the chess board
    self.intermaxlimit=int(myoptions['Seive']['intermaxlimit'])     #Max number of points that can be created by interpolation
    self.extermaxlimit=int(myoptions['Seive']['extermaxlimit'])     #Max number of points that can be created by extrapolation
    self.evalscores=0
  def convert(self,x,y): return (x*100)+y
  def rowno(self,x): return int(x/100)
  def colmno(self,x): return x%10 

  def gonw(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==1 and self.colmno(x)==1):return self.convert(nrow,ncol)#in the first coulumn and first row
    elif(self.rowno(x)==1): return self.convert(nrow,self.colmno(x)-1)
    elif(self.colmno(x)==1): return self.convert(self.rowno(x)-1,ncol)#in the first column
    else: return (x-101)

  def gow(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.colmno(x)==1): return self.convert(self.rowno(x),ncol)
    else: return (x-1)

  def gosw(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==nrow and self.colmno(x)==1): return self.convert(1,ncol)
    elif(self.rowno(x)==nrow): return self.convert(1,self.colmno(x)-1)
    elif(self.colmno(x)==1): return self.convert(self.rowno(x)+1,ncol)
    else: return (x+99)

  def gos(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==nrow): return self.convert(1,self.colmno(x))
    else: return x+100

  def gose(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==nrow and self.colmno(x)==ncol): return self.convert(1,1)
    elif(self.rowno(x)==nrow): return self.convert(1,self.colmno(x)+1)
    elif(self.colmno(x)==ncol): return self.convert(self.rowno(x)+1,1)
    else: return x+101

  def goe(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.colmno(x)==ncol): return self.convert(self.rowno(x),1)
    else: return x+1

  def gone(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==1 and self.colmno(x)==ncol): return self.convert(nrow,1)
    elif(self.rowno(x)==1): return self.convert(nrow,self.colmno(x)+1)
    elif(self.colmno(x)==ncol): return self.convert(self.rowno(x)-1,1)
    else: return x-99

  def gon(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==1): return self.convert(nrow,self.colmno(x))
    else: return x-100 

  def generateNew(self,m,xblock,yblock,dictionary):
    convert = self.convert
    rowno = self.rowno
    colmno = self.colmno 

    def indexConvert(index):
      return int(index/100),index%10

    def opposite(a,b):
      ax,ay,bx,by=a/100,a%100,b/100,b%100
      if(abs(ax-bx)==2 or abs(ay-by)==2):return True
      else: return False

    def thresholdCheck(index):
      try:
        #print "Threshold Check: ",index
        if(len(dictionary[index])>self.threshold):return True
        else:return False
      except:
        return False

    def interpolateCheck(xblock,yblock):
      returnList=[]
      if(thresholdCheck(self.gonw(convert(xblock,yblock))) and thresholdCheck(self.gose(convert(xblock,yblock))) == True):
        returnList.append(self.gonw(convert(xblock,yblock)))
        returnList.append(self.gose(convert(xblock,yblock)))
      if(thresholdCheck(self.gow(convert(xblock,yblock))) and thresholdCheck(self.goe(convert(xblock,yblock))) == True):
       returnList.append(self.gow(convert(xblock,yblock)))
       returnList.append(self.goe(convert(xblock,yblock)))
      if(thresholdCheck(self.gosw(convert(xblock,yblock))) and thresholdCheck(self.gone(convert(xblock,yblock))) == True):
       returnList.append(self.gosw(convert(xblock,yblock)))
       returnList.append(self.gone(convert(xblock,yblock)))
      if(thresholdCheck(self.gon(convert(xblock,yblock))) and thresholdCheck(self.gos(convert(xblock,yblock))) == True):
       returnList.append(self.gon(convert(xblock,yblock)))
       returnList.append(self.gos(convert(xblock,yblock)))
      return returnList


    def extrapolateCheck(xblock,yblock):
      #TODO: If there are more than one consequetive blocks with threshold number of points how do we handle it?
      #TODO: Need to make this logic more succint
      returnList=[]
      #go North West
      temp = self.gonw(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gonw(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gonw(temp))

      #go North 
      temp = self.gon(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gon(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gon(temp))

      #go North East
      temp = self.gone(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gone(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gone(temp))
  
      #go East
      temp = self.goe(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.goe(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.goe(temp))

      #go South East
      temp = self.gose(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gose(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gose(temp))

      #go South
      temp = self.gos(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gos(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gos(temp))

      #go South West
      temp = self.gosw(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gosw(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gosw(temp))
 
      #go West
      temp = self.gow(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gow(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gow(temp))

      return returnList
  
    newpoints=[]
    #print "generateNew| xblock: %d yblock: %d"%(xblock,yblock)
    #print "generateNew| convert: ",convert(xblock,yblock)
    #print "generateNew| thresholdCheck(convert(xblock,yblock): ",thresholdCheck(convert(xblock,yblock))
    #print "generateNew| points in the block: ",len(dictionary[convert(xblock,yblock)])
    if(thresholdCheck(convert(xblock,yblock))==False):
      #print "generateNew| Cell is relatively sparse: Might need to generate new points"
      listInter=interpolateCheck(xblock,yblock)
      #print "generateNew|listInter: ",listInter
      if(len(listInter)!=0):
        decisions=[]
        assert(len(listInter)%2==0),"listInter%2 not 0"
      #print thresholdCheck(xb),thresholdCheck(yb)
        for i in xrange(int(len(listInter)/2)):
          decisions.extend(self.wrapperInterpolate(m,listInter[i*2],listInter[(i*2)+1],int(self.intermaxlimit/len(listInter))+1,dictionary))
          #print "generateNew| Decisions Length: ",len(decisions)
        #print "generateNew| Decisions: ",decisions
        if convert(xblock,yblock) in dictionary: pass
        else:
          #print convert(xblock,yblock)
          assert(convert(xblock,yblock)>=101),"Something's wrong!" 
          assert(convert(xblock,yblock)<=808),"Something's wrong!" 
          dictionary[convert(xblock,yblock)]=[]
        old = self._checkDictionary(dictionary)
        for decision in decisions:dictionary[convert(xblock,yblock)].append(self.generateSlot(m,decision,xblock,yblock))
        #print "generateNew| Interpolation works!"
        new = self._checkDictionary(dictionary)
        #print "generateNew|Interpolation| Number of new points generated: ", (new-old)
        return True
      else:
        #print "generateNew| Interpolation failed!"
        decisions=[]
        listExter = extrapolateCheck(xblock,yblock)
        if(len(listExter)==0):
          #print "generateNew|Interpolation and Extrapolation failed|In a tight spot..somewhere in the desert RANDOM JUMP REQUIRED"
          return False
        else:
          assert(len(listExter)%2==0),"listExter%2 not 0"
          for i in xrange(int(len(listExter)/2)):
            decisions.extend(self.wrapperextrapolate(m,listExter[2*i],listExter[(2*i)+1],int(self.extermaxlimit)/len(listExter),dictionary))
          if convert(xblock,yblock) in dictionary: pass
          else: 
            assert(convert(xblock,yblock)>=101),"Something's wrong!" 
            assert(convert(xblock,yblock)<=808),"Something's wrong!" 
            dictionary[convert(xblock,yblock)]=[]
          old = self._checkDictionary(dictionary)
          for decision in decisions: dictionary[convert(xblock,yblock)].append(self.generateSlot(m,decision,xblock,yblock))
          new = self._checkDictionary(dictionary)
          #print "generateNew|Extrapolation Worked ",len(dictionary[convert(xblock,yblock)])
          #print "generateNew|Extrapolation| Number of new points generated: ", (new-old)
          return True
    else:
      listExter = extrapolateCheck(xblock,yblock)
      if(len(listExter) == 0):
        #print "generateNew| Lot of points but middle of a desert"
        return False #A lot of points but right in the middle of a deseart
      else:
        return True
    """
    print interpolateCheck(xblock,yblock)
    """
  def wrapperInterpolate(self,m,xindex,yindex,maxlimit,dictionary):
    def interpolate(lx,ly,cr=0.3,fmin=0,fmax=1):
      def lo(m,index)      : return m.minR[index]
      def hi(m,index)      : return m.maxR[index]
      def trim(m,x,i)  : # trim to legal range
        return max(lo(m,i), x%hi(m,i))
      assert(len(lx)==len(ly))
      genPoint=[]
      for i in xrange(len(lx)):
        x,y=lx[i],ly[i]
        #print x
        #print y
        rand = random.random
        if rand < cr:
          probEx = fmin +(fmax-fmin)*rand()
          new = trim(m,min(x,y)+probEx*abs(x-y),i)
        else:
          new = y
        genPoint.append(new)
      return genPoint

    decision=[]
    #print "Number of points in ",xindex," is: ",len(dictionary[xindex])
    #print "Number of points in ",yindex," is: ",len(dictionary[yindex])
    xpoints=self.getpoints(xindex,dictionary)
    ypoints=self.getpoints(yindex,dictionary)
    import itertools
    listpoints=list(itertools.product(xpoints,ypoints))
    #print "Length of Listpoints: ",len(listpoints)
    count=0
    while True:
      if(count>min(len(xpoints),maxlimit)):break
      x=self.one(m,listpoints)
      decision.append(interpolate(x[0],x[1]))
      count+=1
    return decision



  def listofneighbours(self,xblock,yblock):
    index=self.convert(xblock,yblock)
    #print "listofneighbours| Index passed: ",index
    listL=[]
    listL.append(self.goe(index))
    listL.append(self.gose(index))
    listL.append(self.gos(index))
    listL.append(self.gosw(index))
    listL.append(self.gow(index))
    listL.append(self.gonw(index))
    listL.append(self.gon(index))
    listL.append(self.gone(index))
    return listL

  def getpoints(self,index,dictionary):
    tempL = []
    for x in dictionary[index]:tempL.append(x.dec)
    return tempL

  def one(self,model,lst): 
    def any(l,h):
      return (0 + random.random()*(h-l))
    return lst[int(any(0,len(lst) - 1)) ]

  def evaluate(self,points=[],depth=0):
    def generate_dictionary(points=[]):  
      dictionary = {}
      chess_board = whereMain(self.model,points) #checked: working well
      for i in range(1,9):
        for j in range(1,9):
          temp = [x for x in chess_board if x.xblock==i and x.yblock==j]
          if(len(temp)!=0):
            index=temp[0].xblock*100+temp[0].yblock
            dictionary[index] = temp
            assert(len(temp)==len(dictionary[index])),"something"
      return dictionary

    def thresholdCheck(index,dictionary):
      try:
        #print "Threshold Check: ",index
        if(len(dictionary[index])>self.threshold):return True
        else:return False
      except:
        return False

    model = self.model
    minR = model.minR
    maxR = model.maxR
    #if depth == 0: model.baseline(minR,maxR)

    dictionary = generate_dictionary(points)
    #print "Depth: %d #points: %d"%(depth,self._checkDictionary(dictionary))
    from collections import defaultdict
    graph = defaultdict(list)
    matrix = [[0 for x in range(8)] for x in range(8)]
    for i in xrange(1,9):
      for j in xrange(1,9):
        if(thresholdCheck(i*100+j,dictionary)==False):
          result = self.generateNew(self.model,i,j,dictionary)
          if result == False: 
            #print "in middle of desert"
            continue
        matrix[i-1][j-1] = score(model,self.one(model,dictionary[i*100+j]))[-1]

        
       # print matrix[i-1][j-1],
      #print
    for i in xrange(1,9):
      for j in xrange(1,9):
        sumn=0
        s = matrix[i-1][j-1]
        neigh = self.listofneighbours(i,j)
        sumn = sum([1 for x in neigh if matrix[self.rowno(x)-1][self.colmno(x)-1]>s])
        if (i*100+j) in dictionary:
          graph[int(sumn)].append(i*100+j)
        
    high = 1e6
    bsoln = None
    maxi = max(graph.keys())
    #print graph.keys()
    #print "Number of points: ",len(graph[maxi])
    count = 0
    for x in graph[maxi]:
       #print "Seive2:B Number of points in ",maxi," is: ",len(dictionary[x])
       if(len(dictionary[x]) < 15): [self.n_i(model,dictionary,x) for _ in xrange(20)]
       #print "Seive2:A Number of points in ",maxi," is: ",len(dictionary[x])
       for y in dictionary[x]:
         temp2 = score(model,y)[-1]
         count += 1
         if temp2 < high:
           high = temp2
           bsoln = y
    #print count     
    return bsoln.dec,high,model

  def getpoints(self,index,dictionary):
    tempL = []
    for x in dictionary[index]:tempL.append(x.dec)
    return tempL

  #new_interpolate
  def n_i(self,m,dictionary,index):

    def lo(m,index)      : return m.minR[index]
    def hi(m,index)      : return m.maxR[index]
    def trim(m,x,i)  : # trim to legal range
      return max(lo(m,i), x%hi(m,i))
    genPoint=[]
    row = index/100
    col = index%10
    xpoints=self.getpoints(index,dictionary)
    two = self.one(m,xpoints)
    three = self.one(m,xpoints)
    four = self.one(m,xpoints) 
    
    assert(len(two)==len(three)),"Something's wrong!"
    
    for i in xrange(len(two)):
      x,y,z=two[i],three[i],four[i]
      new = trim(m,x+0.1*abs(z-y),i)
      genPoint.append(new)
    dictionary[index].append(self.generateSlot(m,genPoint,row,col))
    return genPoint
   

  def _checkDictionary(self,dictionary):
    sum=0
    for i in dictionary.keys():
      sum+=len(dictionary[i])
    return sum



class Seive4(SearchersBasic): #minimizing
  model = None
  minR=0
  maxR=0
  random.seed(1)



  def wrapperInterpolate(self,m,xindex,yindex,maxlimit,dictionary):
    def interpolate(lx,ly,cr=0.3,fmin=0,fmax=1):
      def lo(m,index)      : return m.minR[index]
      def hi(m,index)      : return m.maxR[index]
      def trim(m,x,i)  : # trim to legal range
        return max(lo(m,i), x%hi(m,i))
      assert(len(lx)==len(ly))
      genPoint=[]
      for i in xrange(len(lx)):
        x,y=lx[i],ly[i]
        #print x
        #print y
        rand = random.random
        if rand < cr:
          probEx = fmin +(fmax-fmin)*rand()
          new = trim(m,min(x,y)+probEx*abs(x-y),i)
        else:
          new = y
        genPoint.append(new)
      return genPoint

    decision=[]
    #print "Number of points in ",xindex," is: ",len(dictionary[xindex])
    #print "Number of points in ",yindex," is: ",len(dictionary[yindex])
    xpoints=self.getpoints(xindex,dictionary)
    ypoints=self.getpoints(yindex,dictionary)
    import itertools
    listpoints=list(itertools.product(xpoints,ypoints))
    #print "Length of Listpoints: ",len(listpoints)
    count=0
    while True:
      if(count>min(len(xpoints),maxlimit)):break
      x=self.one(m,listpoints)
      decision.append(interpolate(x[0],x[1]))
      count+=1
    return decision


  def generateSlot(self,m,decision,x,y):
    newpoint=Slots(changed = True,
            scores=1e6, 
            xblock=-1, #sam
            yblock=-1,  #sam
            x=-1,
            y=-1,
            obj = [None] * m.objf, #This needs to be removed. Not using it as of 11/10
            dec = [some(m,d) for d in xrange(m.n)])

    scores(m,newpoint)
    #print "Decision: ",newpoint.dec
    #print "Objectives: ",newpoint.obj
    return newpoint


  #There are three points and I am trying to extrapolate. Need to pass two cell numbers
  def wrapperextrapolate(self,m,xindex,yindex,maxlimit,dictionary):
    def extrapolate(lx,ly,lz,cr=0.3,fmin=0.9,fmax=2):
      def lo(m,index)      : return m.minR[index]
      def hi(m)      : return m.maxR[index]
      def trim(m,x,i)  : # trim to legal range
        return max(lo(m,i), x%hi(m,i))
      def indexConvert(index):
        return int(index/100),index%10
      assert(len(lx)==len(ly)==len(lz))
      genPoint=[]
      for i in xrange(len(lx)):
        x,y,z = lx[i],ly[i],lz[i]
        rand = random.random()

        if rand < cr:
          probEx = fmin + (fmax-fmin)*random.random()
          new = trim(m,x + probEx*(y-z),i)
        else:
          new = y #Just assign a value for that decision
        genPoint.append(new)
      return genPoint

    decision=[]
    #TODO: need to put an assert saying checking whether extrapolation is actually possible
    xpoints=self.getpoints(xindex,dictionary)
    ypoints=self.getpoints(yindex,dictionary)
    count=0
    while True:
      if(count>min(len(xpoints),maxlimit)):break
      two = self.one(m,xpoints)
      index2,index3=0,0
      while(index2 == index3): #just making sure that the indexes are not the same
        index2=random.randint(0,len(ypoints)-1)
        index3=random.randint(0,len(ypoints)-1)

      three=ypoints[index2]
      four=ypoints[index3]
      temp = extrapolate(two,three,four)
      #decision.append(extrapolate(two,three,four))
      decision.append(temp)
      count+=1
    return decision
  

  def __init__(self,modelName,displayS,bmin,bmax):
    self.model = modelName
    self.model.minVal = bmin
    self.model.maxVal = bmax
    self.displayStyle=displayS
    self.threshold =1#int(myoptions['Seive']['threshold'])         #threshold for number of points to be considered as a prospective solution
    self.ncol=8               #number of columns in the chess board
    self.nrow=8               #number of rows in the chess board
    self.intermaxlimit=int(myoptions['Seive']['intermaxlimit'])     #Max number of points that can be created by interpolation
    self.extermaxlimit=int(myoptions['Seive']['extermaxlimit'])     #Max number of points that can be created by extrapolation
    self.evalscores=0
  def convert(self,x,y): return (x*100)+y
  def rowno(self,x): return int(x/100)
  def colmno(self,x): return x%10 

  def gonw(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==1 and self.colmno(x)==1):return self.convert(nrow,ncol)#in the first coulumn and first row
    elif(self.rowno(x)==1): return self.convert(nrow,self.colmno(x)-1)
    elif(self.colmno(x)==1): return self.convert(self.rowno(x)-1,ncol)#in the first column
    else: return (x-101)

  def gow(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.colmno(x)==1): return self.convert(self.rowno(x),ncol)
    else: return (x-1)

  def gosw(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==nrow and self.colmno(x)==1): return self.convert(1,ncol)
    elif(self.rowno(x)==nrow): return self.convert(1,self.colmno(x)-1)
    elif(self.colmno(x)==1): return self.convert(self.rowno(x)+1,ncol)
    else: return (x+99)

  def gos(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==nrow): return self.convert(1,self.colmno(x))
    else: return x+100

  def gose(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==nrow and self.colmno(x)==ncol): return self.convert(1,1)
    elif(self.rowno(x)==nrow): return self.convert(1,self.colmno(x)+1)
    elif(self.colmno(x)==ncol): return self.convert(self.rowno(x)+1,1)
    else: return x+101

  def goe(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.colmno(x)==ncol): return self.convert(self.rowno(x),1)
    else: return x+1

  def gone(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==1 and self.colmno(x)==ncol): return self.convert(nrow,1)
    elif(self.rowno(x)==1): return self.convert(nrow,self.colmno(x)+1)
    elif(self.colmno(x)==ncol): return self.convert(self.rowno(x)-1,1)
    else: return x-99

  def gon(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==1): return self.convert(nrow,self.colmno(x))
    else: return x-100 

  def generateNew(self,m,xblock,yblock,dictionary):
    convert = self.convert
    rowno = self.rowno
    colmno = self.colmno 

    def indexConvert(index):
      return int(index/100),index%10

    def opposite(a,b):
      ax,ay,bx,by=a/100,a%100,b/100,b%100
      if(abs(ax-bx)==2 or abs(ay-by)==2):return True
      else: return False

    def thresholdCheck(index):
      try:
        #print "Threshold Check: ",index
        if(len(dictionary[index])>self.threshold):return True
        else:return False
      except:
        return False

    def interpolateCheck(xblock,yblock):
      returnList=[]
      if(thresholdCheck(self.gonw(convert(xblock,yblock))) and thresholdCheck(self.gose(convert(xblock,yblock))) == True):
        returnList.append(self.gonw(convert(xblock,yblock)))
        returnList.append(self.gose(convert(xblock,yblock)))
      if(thresholdCheck(self.gow(convert(xblock,yblock))) and thresholdCheck(self.goe(convert(xblock,yblock))) == True):
       returnList.append(self.gow(convert(xblock,yblock)))
       returnList.append(self.goe(convert(xblock,yblock)))
      if(thresholdCheck(self.gosw(convert(xblock,yblock))) and thresholdCheck(self.gone(convert(xblock,yblock))) == True):
       returnList.append(self.gosw(convert(xblock,yblock)))
       returnList.append(self.gone(convert(xblock,yblock)))
      if(thresholdCheck(self.gon(convert(xblock,yblock))) and thresholdCheck(self.gos(convert(xblock,yblock))) == True):
       returnList.append(self.gon(convert(xblock,yblock)))
       returnList.append(self.gos(convert(xblock,yblock)))
      return returnList


    def extrapolateCheck(xblock,yblock):
      #TODO: If there are more than one consequetive blocks with threshold number of points how do we handle it?
      #TODO: Need to make this logic more succint
      returnList=[]
      #go North West
      temp = self.gonw(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gonw(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gonw(temp))

      #go North 
      temp = self.gon(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gon(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gon(temp))

      #go North East
      temp = self.gone(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gone(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gone(temp))
  
      #go East
      temp = self.goe(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.goe(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.goe(temp))

      #go South East
      temp = self.gose(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gose(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gose(temp))

      #go South
      temp = self.gos(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gos(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gos(temp))

      #go South West
      temp = self.gosw(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gosw(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gosw(temp))
 
      #go West
      temp = self.gow(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gow(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gow(temp))

      return returnList
  
    newpoints=[]
    #print "generateNew| xblock: %d yblock: %d"%(xblock,yblock)
    #print "generateNew| convert: ",convert(xblock,yblock)
    #print "generateNew| thresholdCheck(convert(xblock,yblock): ",thresholdCheck(convert(xblock,yblock))
    #print "generateNew| points in the block: ",len(dictionary[convert(xblock,yblock)])
    if(thresholdCheck(convert(xblock,yblock))==False):
      #print "generateNew| Cell is relatively sparse: Might need to generate new points"
      listInter=interpolateCheck(xblock,yblock)
      #print "generateNew|listInter: ",listInter
      if(len(listInter)!=0):
        decisions=[]
        assert(len(listInter)%2==0),"listInter%2 not 0"
      #print thresholdCheck(xb),thresholdCheck(yb)
        for i in xrange(int(len(listInter)/2)):
          decisions.extend(self.wrapperInterpolate(m,listInter[i*2],listInter[(i*2)+1],int(self.intermaxlimit/len(listInter))+1,dictionary))
          #print "generateNew| Decisions Length: ",len(decisions)
        #print "generateNew| Decisions: ",decisions
        if convert(xblock,yblock) in dictionary: pass
        else:
          #print convert(xblock,yblock)
          assert(convert(xblock,yblock)>=101),"Something's wrong!" 
          assert(convert(xblock,yblock)<=808),"Something's wrong!" 
          dictionary[convert(xblock,yblock)]=[]
        old = self._checkDictionary(dictionary)
        for decision in decisions:dictionary[convert(xblock,yblock)].append(self.generateSlot(m,decision,xblock,yblock))
        #print "generateNew| Interpolation works!"
        new = self._checkDictionary(dictionary)
        #print "generateNew|Interpolation| Number of new points generated: ", (new-old)
        return True
      else:
        #print "generateNew| Interpolation failed!"
        decisions=[]
        listExter = extrapolateCheck(xblock,yblock)
        if(len(listExter)==0):
          #print "generateNew|Interpolation and Extrapolation failed|In a tight spot..somewhere in the desert RANDOM JUMP REQUIRED"
          return False
        else:
          assert(len(listExter)%2==0),"listExter%2 not 0"
          for i in xrange(int(len(listExter)/2)):
            decisions.extend(self.wrapperextrapolate(m,listExter[2*i],listExter[(2*i)+1],int(self.extermaxlimit)/len(listExter),dictionary))
          if convert(xblock,yblock) in dictionary: pass
          else: 
            assert(convert(xblock,yblock)>=101),"Something's wrong!" 
            assert(convert(xblock,yblock)<=808),"Something's wrong!" 
            dictionary[convert(xblock,yblock)]=[]
          old = self._checkDictionary(dictionary)
          for decision in decisions: dictionary[convert(xblock,yblock)].append(self.generateSlot(m,decision,xblock,yblock))
          new = self._checkDictionary(dictionary)
          #print "generateNew|Extrapolation Worked ",len(dictionary[convert(xblock,yblock)])
          #print "generateNew|Extrapolation| Number of new points generated: ", (new-old)
          return True
    else:
      listExter = extrapolateCheck(xblock,yblock)
      if(len(listExter) == 0):
        #print "generateNew| Lot of points but middle of a desert"
        return False #A lot of points but right in the middle of a deseart
      else:
        return True
    """
    print interpolateCheck(xblock,yblock)
    """
  def wrapperInterpolate(self,m,xindex,yindex,maxlimit,dictionary):
    def interpolate(lx,ly,cr=0.3,fmin=0,fmax=1):
      def lo(m,index)      : return m.minR[index]
      def hi(m,index)      : return m.maxR[index]
      def trim(m,x,i)  : # trim to legal range
        return max(lo(m,i), x%hi(m,i))
      assert(len(lx)==len(ly))
      genPoint=[]
      for i in xrange(len(lx)):
        x,y=lx[i],ly[i]
        #print x
        #print y
        rand = random.random
        if rand < cr:
          probEx = fmin +(fmax-fmin)*rand()
          new = trim(m,min(x,y)+probEx*abs(x-y),i)
        else:
          new = y
        genPoint.append(new)
      return genPoint

    decision=[]
    #print "Number of points in ",xindex," is: ",len(dictionary[xindex])
    #print "Number of points in ",yindex," is: ",len(dictionary[yindex])
    xpoints=self.getpoints(xindex,dictionary)
    ypoints=self.getpoints(yindex,dictionary)
    import itertools
    listpoints=list(itertools.product(xpoints,ypoints))
    #print "Length of Listpoints: ",len(listpoints)
    count=0
    while True:
      if(count>min(len(xpoints),maxlimit)):break
      x=self.one(m,listpoints)
      decision.append(interpolate(x[0],x[1]))
      count+=1
    return decision



  def listofneighbours(self,xblock,yblock):
    index=self.convert(xblock,yblock)
    #print "listofneighbours| Index passed: ",index
    listL=[]
    listL.append(self.goe(index))
    listL.append(self.gose(index))
    listL.append(self.gos(index))
    listL.append(self.gosw(index))
    listL.append(self.gow(index))
    listL.append(self.gonw(index))
    listL.append(self.gon(index))
    listL.append(self.gone(index))
    return listL

  def getpoints(self,index,dictionary):
    tempL = []
    for x in dictionary[index]:tempL.append(x.dec)
    return tempL

  def one(self,model,lst): 
    def any(l,h):
      return (0 + random.random()*(h-l))
    return lst[int(any(0,len(lst) - 1)) ]

  def evaluate(self,points=[],depth=0,repeat=100,f=0.75,cf=0.3):
    def generate_dictionary(points=[]):  
      dictionary = {}
      chess_board = whereMain(self.model,points) #checked: working well
      for i in range(1,9):
        for j in range(1,9):
          temp = [x for x in chess_board if x.xblock==i and x.yblock==j]
          if(len(temp)!=0):
            index=temp[0].xblock*100+temp[0].yblock
            dictionary[index] = temp
            assert(len(temp)==len(dictionary[index])),"something"
      return dictionary

    def thresholdCheck(index,dictionary):
      try:
        #print "Threshold Check: ",index
        if(len(dictionary[index])>self.threshold):return True
        else:return False
      except:
        return False

    model = self.model
    minR = model.minR
    maxR = model.maxR
    #if depth == 0: model.baseline(minR,maxR)

    dictionary = generate_dictionary(points)
    #print "Depth: %d #points: %d"%(depth,self._checkDictionary(dictionary))
    from collections import defaultdict
    graph = defaultdict(list)
    matrix = [[0 for x in range(8)] for x in range(8)]
    for i in xrange(1,9):
      for j in xrange(1,9):
        if(thresholdCheck(i*100+j,dictionary)==False):
          result = self.generateNew(self.model,i,j,dictionary)
          if result == False: 
            #print "in middle of desert"
            continue
        matrix[i-1][j-1] = score(model,self.one(model,dictionary[i*100+j]))[-1]

        
       # print matrix[i-1][j-1],
      #print
    for i in xrange(1,9):
      for j in xrange(1,9):
        sumn=0
        s = matrix[i-1][j-1]
        neigh = self.listofneighbours(i,j)
        sumn = sum([1 for x in neigh if matrix[self.rowno(x)-1][self.colmno(x)-1]>s])
        if (i*100+j) in dictionary:
          graph[int(sumn)].append(i*100+j)
        
    high = 1e6
    bsoln = None
    maxi = max(graph.keys())
    #print graph.keys()
    #print "Number of points: ",len(graph[maxi])
    count = 0
    #print "Number of islands: ",len(graph[maxi])
    for x in graph[maxi]:
       #print "Seive2:B Number of points in ",maxi," is: ",len(dictionary[x])
       frontier = dictionary[x][:]
       if len(frontier) < 10: 
         #print "Before: ",len(frontier)
         for _ in xrange(20):
           frontier.append(self.n_i(model,frontier,x))
         #print "After: ",len(frontier)
       solution,minE = self.run_de(model,f,cf,frontier,x/100,x%10)
       if minE < high:
         high = minE
         bsoln = solution
    #print count     
    return bsoln.dec,high,model

  def threeOthers(self,frontier,one):
    #print "threeOthers"
    seen = [one]
    def other():
      #print "other"
      for i in xrange(len(frontier)):
        while True:
          k = random.randint(0,len(frontier)-1)
          #print "%d"%k
          if frontier[k] not in seen:
            seen.append(frontier[k])
            break
        return frontier[k]
    this = other()
    that = other()
    then = other()
    return this,that,then
  
  def trim(self,x,i)  : # trim to legal range
    m=self.model
    return max(m.minR[i], min(x, m.maxR[i]))      

  def extrapolate(self,model,frontier,one,f,cf,xb,yb):
    #print "Extrapolate"
    two,three,four = self.threeOthers(frontier,one)
    #print two,three,four
    solution=[]
    for d in xrange(self.model.n):
      x,y,z=two.dec[d],three.dec[d],four.dec[d]
      if(random.random() < cf):
        solution.append(self.trim(x + f*(y-z),d))
      else:
        solution.append(one.dec[d]) 
    #print "blah"
    import sys
    sys.stdout.flush()
    return self.generateSlot(model,solution,xb,yb)
  def run_de(self,model,f,cf,frontier,xb,yb,repeat=100):
    def de(model,c,cf,frontier,xb,yb):
      model=self.model
      newF = []
      total,n=0,0
      for x in frontier:
        #print "update: %d"%n
        s = score(model,x)[-1]
        #print "CHECKKKKKKKED1|: ",s
        new = self.extrapolate(model,frontier,x,f,cf,xb,yb)
        #print new
        #print "CHECKKKKKKKKKKKED| ",score(model,new)
        newe=score(model,new)[-1]
        if(newe<s):
          newF.append(new)
        else:
          newF.append(x)
        total+=min(newe,s)
        n+=1
      return total,n,newF  
    #print repeat
    for _ in xrange(repeat):
      #print ".",
      total,n,frontier = de(model,f,cf,frontier,xb,yb)
    minR=9e10
    for x in frontier:
      #print x
      energy = score(model,x)[-1]
      if(minR>energy):
        minR = energy
        solution=x 
    return solution,minR    

  def getpoints(self,index,dictionary):
    tempL = []
    for x in dictionary[index]:tempL.append(x.dec)
    return tempL

  def getpoints_test(self,frontier):
    tempL = []
    #print frontier
    for x in frontier:
      tempL.append(x.dec)
    return tempL

  #new_interpolate
  def n_i(self,m,frontier,index):

    def lo(m,index)      : return m.minR[index]
    def hi(m,index)      : return m.maxR[index]
    def trim(m,x,i)  : # trim to legal range
      return max(lo(m,i), x%hi(m,i))
    genPoint=[]
    row = index/100
    col = index%10
    xpoints=self.getpoints_test(frontier)
    two = self.one(m,xpoints)
    three = self.one(m,xpoints)
    four = self.one(m,xpoints) 
    
    assert(len(two)==len(three)),"Something's wrong!"
    
    for i in xrange(len(two)):
      x,y,z=two[i],three[i],four[i]
      new = trim(m,x+0.1*abs(z-y),i)
      genPoint.append(new)
    #frontier.append(self.generateSlot(m,genPoint,row,col))
    return self.generateSlot(m,genPoint,row,col)
   

  def _checkDictionary(self,dictionary):
    sum=0
    for i in dictionary.keys():
      sum+=len(dictionary[i])
    return sum


class Seive5(SearchersBasic): #minimizing
  model = None
  minR=0
  maxR=0
  random.seed(1)



  def wrapperInterpolate(self,m,xindex,yindex,maxlimit,dictionary):
    def interpolate(lx,ly,cr=0.3,fmin=0,fmax=1):
      def lo(m,index)      : return m.minR[index]
      def hi(m,index)      : return m.maxR[index]
      def trim(m,x,i)  : # trim to legal range
        return max(lo(m,i), x%hi(m,i))
      assert(len(lx)==len(ly))
      genPoint=[]
      for i in xrange(len(lx)):
        x,y=lx[i],ly[i]
        #print x
        #print y
        rand = random.random
        if rand < cr:
          probEx = fmin +(fmax-fmin)*rand()
          new = trim(m,min(x,y)+probEx*abs(x-y),i)
        else:
          new = y
        genPoint.append(new)
      return genPoint

    decision=[]
    #print "Number of points in ",xindex," is: ",len(dictionary[xindex])
    #print "Number of points in ",yindex," is: ",len(dictionary[yindex])
    xpoints=self.getpoints(xindex,dictionary)
    ypoints=self.getpoints(yindex,dictionary)
    import itertools
    listpoints=list(itertools.product(xpoints,ypoints))
    #print "Length of Listpoints: ",len(listpoints)
    count=0
    while True:
      if(count>min(len(xpoints),maxlimit)):break
      x=self.one(m,listpoints)
      decision.append(interpolate(x[0],x[1]))
      count+=1
    return decision


  def generateSlot(self,m,decision,x,y):
    newpoint=Slots(changed = True,
            scores=1e6, 
            xblock=-1, #sam
            yblock=-1,  #sam
            x=-1,
            y=-1,
            obj = [None] * m.objf, #This needs to be removed. Not using it as of 11/10
            dec = [some(m,d) for d in xrange(m.n)])

    scores(m,newpoint)
    #print "Decision: ",newpoint.dec
    #print "Objectives: ",newpoint.obj
    return newpoint


  #There are three points and I am trying to extrapolate. Need to pass two cell numbers
  def wrapperextrapolate(self,m,xindex,yindex,maxlimit,dictionary):
    def extrapolate(lx,ly,lz,cr=0.3,fmin=0.9,fmax=2):
      def lo(m,index)      : return m.minR[index]
      def hi(m,index)      : return m.maxR[index]
      def trim(m,x,i)  : # trim to legal range
        return max(lo(m,i), x%hi(m,i))
      def indexConvert(index):
        return int(index/100),index%10
      assert(len(lx)==len(ly)==len(lz))
      genPoint=[]
      for i in xrange(len(lx)):
        x,y,z = lx[i],ly[i],lz[i]
        rand = random.random()

        if rand < cr:
          probEx = fmin + (fmax-fmin)*random.random()
          new = trim(m,x + probEx*(y-z),i)
        else:
          new = y #Just assign a value for that decision
        genPoint.append(new)
      return genPoint

    decision=[]
    #TODO: need to put an assert saying checking whether extrapolation is actually possible
    xpoints=self.getpoints(xindex,dictionary)
    ypoints=self.getpoints(yindex,dictionary)
    count=0
    while True:
      if(count>min(len(xpoints),maxlimit)):break
      two = self.one(m,xpoints)
      index2,index3=0,0
      while(index2 == index3): #just making sure that the indexes are not the same
        index2=random.randint(0,len(ypoints)-1)
        index3=random.randint(0,len(ypoints)-1)

      three=ypoints[index2]
      four=ypoints[index3]
      temp = extrapolate(two,three,four)
      #decision.append(extrapolate(two,three,four))
      decision.append(temp)
      count+=1
    return decision
  

  def __init__(self,modelName,displayS,bmin,bmax):
    self.model = modelName
    self.model.minVal = bmin
    self.model.maxVal = bmax
    self.displayStyle=displayS
    self.threshold =1#int(myoptions['Seive']['threshold'])         #threshold for number of points to be considered as a prospective solution
    self.ncol=8               #number of columns in the chess board
    self.nrow=8               #number of rows in the chess board
    self.intermaxlimit=int(myoptions['Seive']['intermaxlimit'])     #Max number of points that can be created by interpolation
    self.extermaxlimit=int(myoptions['Seive']['extermaxlimit'])     #Max number of points that can be created by extrapolation
    self.evalscores=0
  def convert(self,x,y): return (x*100)+y
  def rowno(self,x): return int(x/100)
  def colmno(self,x): return x%10 

  def gonw(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==1 and self.colmno(x)==1):return self.convert(nrow,ncol)#in the first coulumn and first row
    elif(self.rowno(x)==1): return self.convert(nrow,self.colmno(x)-1)
    elif(self.colmno(x)==1): return self.convert(self.rowno(x)-1,ncol)#in the first column
    else: return (x-101)

  def gow(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.colmno(x)==1): return self.convert(self.rowno(x),ncol)
    else: return (x-1)

  def gosw(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==nrow and self.colmno(x)==1): return self.convert(1,ncol)
    elif(self.rowno(x)==nrow): return self.convert(1,self.colmno(x)-1)
    elif(self.colmno(x)==1): return self.convert(self.rowno(x)+1,ncol)
    else: return (x+99)

  def gos(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==nrow): return self.convert(1,self.colmno(x))
    else: return x+100

  def gose(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==nrow and self.colmno(x)==ncol): return self.convert(1,1)
    elif(self.rowno(x)==nrow): return self.convert(1,self.colmno(x)+1)
    elif(self.colmno(x)==ncol): return self.convert(self.rowno(x)+1,1)
    else: return x+101

  def goe(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.colmno(x)==ncol): return self.convert(self.rowno(x),1)
    else: return x+1

  def gone(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==1 and self.colmno(x)==ncol): return self.convert(nrow,1)
    elif(self.rowno(x)==1): return self.convert(nrow,self.colmno(x)+1)
    elif(self.colmno(x)==ncol): return self.convert(self.rowno(x)-1,1)
    else: return x-99

  def gon(self,x):
    nrow=self.nrow
    ncol=self.ncol
    if(self.rowno(x)==1): return self.convert(nrow,self.colmno(x))
    else: return x-100 

  def generateNew(self,m,xblock,yblock,dictionary):
    convert = self.convert
    rowno = self.rowno
    colmno = self.colmno 

    def indexConvert(index):
      return int(index/100),index%10

    def opposite(a,b):
      ax,ay,bx,by=a/100,a%100,b/100,b%100
      if(abs(ax-bx)==2 or abs(ay-by)==2):return True
      else: return False

    def thresholdCheck(index):
      try:
        #print "Threshold Check: ",index
        if(len(dictionary[index])>self.threshold):return True
        else:return False
      except:
        return False

    def interpolateCheck(xblock,yblock):
      returnList=[]
      if(thresholdCheck(self.gonw(convert(xblock,yblock))) and thresholdCheck(self.gose(convert(xblock,yblock))) == True):
        returnList.append(self.gonw(convert(xblock,yblock)))
        returnList.append(self.gose(convert(xblock,yblock)))
      if(thresholdCheck(self.gow(convert(xblock,yblock))) and thresholdCheck(self.goe(convert(xblock,yblock))) == True):
       returnList.append(self.gow(convert(xblock,yblock)))
       returnList.append(self.goe(convert(xblock,yblock)))
      if(thresholdCheck(self.gosw(convert(xblock,yblock))) and thresholdCheck(self.gone(convert(xblock,yblock))) == True):
       returnList.append(self.gosw(convert(xblock,yblock)))
       returnList.append(self.gone(convert(xblock,yblock)))
      if(thresholdCheck(self.gon(convert(xblock,yblock))) and thresholdCheck(self.gos(convert(xblock,yblock))) == True):
       returnList.append(self.gon(convert(xblock,yblock)))
       returnList.append(self.gos(convert(xblock,yblock)))
      return returnList


    def extrapolateCheck(xblock,yblock):
      #TODO: If there are more than one consequetive blocks with threshold number of points how do we handle it?
      #TODO: Need to make this logic more succint
      returnList=[]
      #go North West
      temp = self.gonw(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gonw(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gonw(temp))

      #go North 
      temp = self.gon(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gon(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gon(temp))

      #go North East
      temp = self.gone(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gone(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gone(temp))
  
      #go East
      temp = self.goe(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.goe(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.goe(temp))

      #go South East
      temp = self.gose(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gose(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gose(temp))

      #go South
      temp = self.gos(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gos(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gos(temp))

      #go South West
      temp = self.gosw(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gosw(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gosw(temp))
 
      #go West
      temp = self.gow(convert(xblock,yblock))
      result1 = thresholdCheck(temp)
      if result1 == True:
        result2 = thresholdCheck(self.gow(temp))
        if(result1 == True and result2 == True):
          returnList.append(temp)
          returnList.append(self.gow(temp))

      return returnList
  
    newpoints=[]
    #print "generateNew| xblock: %d yblock: %d"%(xblock,yblock)
    #print "generateNew| convert: ",convert(xblock,yblock)
    #print "generateNew| thresholdCheck(convert(xblock,yblock): ",thresholdCheck(convert(xblock,yblock))
    #print "generateNew| points in the block: ",len(dictionary[convert(xblock,yblock)])
    if(thresholdCheck(convert(xblock,yblock))==False):
      #print "generateNew| Cell is relatively sparse: Might need to generate new points"
      listInter=interpolateCheck(xblock,yblock)
      #print "generateNew|listInter: ",listInter
      if(len(listInter)!=0):
        decisions=[]
        assert(len(listInter)%2==0),"listInter%2 not 0"
      #print thresholdCheck(xb),thresholdCheck(yb)
        for i in xrange(int(len(listInter)/2)):
          decisions.extend(self.wrapperInterpolate(m,listInter[i*2],listInter[(i*2)+1],int(self.intermaxlimit/len(listInter))+1,dictionary))
          #print "generateNew| Decisions Length: ",len(decisions)
        #print "generateNew| Decisions: ",decisions
        if convert(xblock,yblock) in dictionary: pass
        else:
          #print convert(xblock,yblock)
          assert(convert(xblock,yblock)>=101),"Something's wrong!" 
          assert(convert(xblock,yblock)<=808),"Something's wrong!" 
          dictionary[convert(xblock,yblock)]=[]
        old = self._checkDictionary(dictionary)
        for decision in decisions:dictionary[convert(xblock,yblock)].append(self.generateSlot(m,decision,xblock,yblock))
        #print "generateNew| Interpolation works!"
        new = self._checkDictionary(dictionary)
        #print "generateNew|Interpolation| Number of new points generated: ", (new-old)
        return True
      else:
        #print "generateNew| Interpolation failed!"
        decisions=[]
        listExter = extrapolateCheck(xblock,yblock)
        if(len(listExter)==0):
          #print "generateNew|Interpolation and Extrapolation failed|In a tight spot..somewhere in the desert RANDOM JUMP REQUIRED"
          return False
        else:
          assert(len(listExter)%2==0),"listExter%2 not 0"
          for i in xrange(int(len(listExter)/2)):
            decisions.extend(self.wrapperextrapolate(m,listExter[2*i],listExter[(2*i)+1],int(self.extermaxlimit)/len(listExter),dictionary))
          if convert(xblock,yblock) in dictionary: pass
          else: 
            assert(convert(xblock,yblock)>=101),"Something's wrong!" 
            assert(convert(xblock,yblock)<=808),"Something's wrong!" 
            dictionary[convert(xblock,yblock)]=[]
          old = self._checkDictionary(dictionary)
          for decision in decisions: dictionary[convert(xblock,yblock)].append(self.generateSlot(m,decision,xblock,yblock))
          new = self._checkDictionary(dictionary)
          #print "generateNew|Extrapolation Worked ",len(dictionary[convert(xblock,yblock)])
          #print "generateNew|Extrapolation| Number of new points generated: ", (new-old)
          return True
    else:
      listExter = extrapolateCheck(xblock,yblock)
      if(len(listExter) == 0):
        #print "generateNew| Lot of points but middle of a desert"
        return False #A lot of points but right in the middle of a deseart
      else:
        return True
    """
    print interpolateCheck(xblock,yblock)
    """
  def wrapperInterpolate(self,m,xindex,yindex,maxlimit,dictionary):
    def interpolate(lx,ly,cr=0.3,fmin=0,fmax=1):
      def lo(m,index)      : return m.minR[index]
      def hi(m,index)      : return m.maxR[index]
      def trim(m,x,i)  : # trim to legal range
        return max(lo(m,i), x%hi(m,i))
      assert(len(lx)==len(ly))
      genPoint=[]
      for i in xrange(len(lx)):
        x,y=lx[i],ly[i]
        #print x
        #print y
        rand = random.random
        if rand < cr:
          probEx = fmin +(fmax-fmin)*rand()
          new = trim(m,min(x,y)+probEx*abs(x-y),i)
        else:
          new = y
        genPoint.append(new)
      return genPoint

    decision=[]
    #print "Number of points in ",xindex," is: ",len(dictionary[xindex])
    #print "Number of points in ",yindex," is: ",len(dictionary[yindex])
    xpoints=self.getpoints(xindex,dictionary)
    ypoints=self.getpoints(yindex,dictionary)
    import itertools
    listpoints=list(itertools.product(xpoints,ypoints))
    #print "Length of Listpoints: ",len(listpoints)
    count=0
    while True:
      if(count>min(len(xpoints),maxlimit)):break
      x=self.one(m,listpoints)
      decision.append(interpolate(x[0],x[1]))
      count+=1
    return decision



  def listofneighbours(self,xblock,yblock):
    index=self.convert(xblock,yblock)
    #print "listofneighbours| Index passed: ",index
    listL=[]
    listL.append(self.goe(index))
    listL.append(self.gose(index))
    listL.append(self.gos(index))
    listL.append(self.gosw(index))
    listL.append(self.gow(index))
    listL.append(self.gonw(index))
    listL.append(self.gon(index))
    listL.append(self.gone(index))
    return listL

  def getpoints(self,index,dictionary):
    tempL = []
    for x in dictionary[index]:tempL.append(x.dec)
    return tempL

  def one(self,model,lst): 
    def any(l,h):
      return (0 + random.random()*(h-l))
    return lst[int(any(0,len(lst) - 1)) ]

  def evaluate(self,points=[],depth=0,repeat=100,f=0.75,cf=0.3):
    def generate_dictionary(points=[]):  
      dictionary = {}
      chess_board = whereMain(self.model,points) #checked: working well
      for i in range(1,9):
        for j in range(1,9):
          temp = [x for x in chess_board if x.xblock==i and x.yblock==j]
          if(len(temp)!=0):
            index=temp[0].xblock*100+temp[0].yblock
            dictionary[index] = temp
            assert(len(temp)==len(dictionary[index])),"something"
      return dictionary

    def thresholdCheck(index,dictionary):
      try:
        #print "Threshold Check: ",index
        if(len(dictionary[index])>self.threshold):return True
        else:return False
      except:
        return False
    def select_min(model,dictionary,index):
      minval = 1e9
      for _ in xrange(10):
         temp = score(model,self.one(model,dictionary[index]))[-1]
         if temp < minval: minval = temp
      return temp


    model = self.model
    minR = model.minR
    maxR = model.maxR
    #if depth == 0: model.baseline(minR,maxR)

    dictionary = generate_dictionary(points)
    #print "Depth: %d #points: %d"%(depth,self._checkDictionary(dictionary))
    from collections import defaultdict
    graph = defaultdict(list)
    matrix = [[0 for x in range(8)] for x in range(8)]
    for i in xrange(1,9):
      for j in xrange(1,9):
        if(thresholdCheck(i*100+j,dictionary)==False):
          result = self.generateNew(self.model,i,j,dictionary)
          if result == False: 
            #print "in middle of desert"
            continue
        matrix[i-1][j-1] = select_min(model, dictionary,((i*100)+j))

        
       # print matrix[i-1][j-1],
      #print
    for i in xrange(1,9):
      for j in xrange(1,9):
        sumn=0
        s = matrix[i-1][j-1]
        neigh = self.listofneighbours(i,j)
        sumn = sum([1 for x in neigh if matrix[self.rowno(x)-1][self.colmno(x)-1]>s])
        if (i*100+j) in dictionary:
          graph[int(sumn)].append(i*100+j)
        
    high = 1e6
    bsoln = None
    maxi = max(graph.keys())
    #print graph.keys()
    #print "Number of points: ",len(graph[maxi])
    count = 0
    #print "Number of islands: ",len(graph[maxi])
    for x in graph[maxi]:
       #print "Seive2:B Number of points in ",maxi," is: ",len(dictionary[x])
       frontier = dictionary[x][:]
       if len(frontier) < 10: 
         #print "Before: ",len(frontier)
         for _ in xrange(20):
           frontier.append(self.n_i(model,frontier,x))
         #print "After: ",len(frontier)
       solution,minE = self.run_de(model,f,cf,frontier,x/100,x%10)
       if minE < high:
         high = minE
         bsoln = solution
    #print count     
    return bsoln.dec,high,model

  def threeOthers(self,frontier,one):
    #print "threeOthers"
    seen = [one]
    def other():
      #print "other"
      for i in xrange(len(frontier)):
        while True:
          k = random.randint(0,len(frontier)-1)
          #print "%d"%k
          if frontier[k] not in seen:
            seen.append(frontier[k])
            break
        return frontier[k]
    this = other()
    that = other()
    then = other()
    return this,that,then
  
  def trim(self,x,i)  : # trim to legal range
    m=self.model
    return max(m.minR[i], min(x, m.maxR[i]))      

  def extrapolate(self,model,frontier,one,f,cf,xb,yb):
    #print "Extrapolate"
    two,three,four = self.threeOthers(frontier,one)
    #print two,three,four
    solution=[]
    for d in xrange(self.model.n):
      x,y,z=two.dec[d],three.dec[d],four.dec[d]
      if(random.random() < cf):
        solution.append(self.trim(x + f*(y-z),d))
      else:
        solution.append(one.dec[d]) 
    #print "blah"
    import sys
    sys.stdout.flush()
    return self.generateSlot(model,solution,xb,yb)
  def run_de(self,model,f,cf,frontier,xb,yb,repeat=100):
    def better(old,new):
      assert(len(old)==len(new)),"MOEAD| Length mismatch"
      for i in xrange(len(old)-1): #Since the score is return as [values of all objectives and energy at the end]
        if old[i] >= new[i]: continue
        else: return False
      return True
          
    def de(model,c,cf,frontier,xb,yb):
      model=self.model
      newF = []
      total,n=0,0
      for x in frontier:
        #print "update: %d"%n
        s = score(model,x)
        new = self.extrapolate(model,frontier,x,f,cf,xb,yb)
        #print new
        newe=score(model,new)
        if better(s,newe) == True:
          newF.append(new)
        else:
          newF.append(x)
        n+=1
      return newF  
    #print repeat
    for _ in xrange(repeat):
      #print ".",
      frontier = de(model,f,cf,frontier,xb,yb)
    minR=9e10
    for x in frontier:
      #print x
      energy = score(model,x)[-1]
      if(minR>energy):
        minR = energy
        solution=x 
    return solution,minR    

  def getpoints(self,index,dictionary):
    tempL = []
    for x in dictionary[index]:tempL.append(x.dec)
    return tempL

  def getpoints_test(self,frontier):
    tempL = []
    #print frontier
    for x in frontier:
      tempL.append(x.dec)
    return tempL

  #new_interpolate
  def n_i(self,m,frontier,index):

    def lo(m,index)      : return m.minR[index]
    def hi(m,index)      : return m.maxR[index]
    def trim(m,x,i)  : # trim to legal range
      return max(lo(m,i), x%hi(m,i))
    genPoint=[]
    row = index/100
    col = index%10
    xpoints=self.getpoints_test(frontier)
    two = self.one(m,xpoints)
    three = self.one(m,xpoints)
    four = self.one(m,xpoints) 
    
    assert(len(two)==len(three)),"Something's wrong!"
    
    for i in xrange(len(two)):
      x,y,z=two[i],three[i],four[i]
      new = trim(m,x+0.1*abs(z-y),i)
      genPoint.append(new)
    #frontier.append(self.generateSlot(m,genPoint,row,col))
    return self.generateSlot(m,genPoint,row,col)
   

  def _checkDictionary(self,dictionary):
    sum=0
    for i in dictionary.keys():
      sum+=len(dictionary[i])
    return sum


class MOEAD(Seive5):
  
  def evaluate(self,points=[],depth=0,repeat=100,f=0.75,cf=0.3):
    def generate_dictionary(points=[]):  
      dictionary = {}
      chess_board = whereMain(self.model,points) #checked: working well
      for i in range(1,9):
        for j in range(1,9):
          temp = [x for x in chess_board if x.xblock==i and x.yblock==j]
          if(len(temp)!=0):
            index=temp[0].xblock*100+temp[0].yblock
            dictionary[index] = temp
            assert(len(temp)==len(dictionary[index])),"something"
      return dictionary

    def thresholdCheck(index,dictionary):
      try:
        #print "Threshold Check: ",index
        if(len(dictionary[index])>myoptions["MOEAD"]["threshold"]):return True
        else:return False
      except:
        return False
    def select_min(model,dictionary,index):
      minval = 1e9
      for _ in xrange(10):
         temp = score(model,self.one(model,dictionary[index]))[-1]
         if temp < minval: minval = temp
      return temp


    model = self.model
    minR = model.minR
    maxR = model.maxR

    dictionary = generate_dictionary(points)
    from collections import defaultdict
    graph = defaultdict(list)
    matrix = [[0 for x in range(8)] for x in range(8)]
    for i in xrange(1,9):
      for j in xrange(1,9):
        if(thresholdCheck(i*100+j,dictionary)==False):
          result = self.generateNew(self.model,i,j,dictionary)
          if result == False: 
            print "in middle of desert"
            continue

        
    high = 1e6
    bsoln = None

    for i in xrange(1,9):
      for j in xrange(1,9):
       #print "Seive2:B Number of points in ",maxi," is: ",len(dictionary[x])
       frontier = dictionary[i*100+j][:]
       if len(frontier) < 10: 
         #print "Before: ",len(frontier)
         for _ in xrange(20):
           frontier.append(self.n_i(model,frontier,x))
         #print "After: ",len(frontier)
       solution,minE = self.run_de(model,f,cf,frontier,x/100,x%10)
       if minE < high:
         high = minE
         bsoln = solution
    #print count     
    return bsoln.dec,high,model

class Seive2MG(Seive2):
  def evaluate(self,depth=0,repeat=100,lives=10):
    minR = 1e6
    listL,high,model = self.evaluate_wrapper()
    for _ in xrange(repeat):
      #say("#")
      if(minR >= high): minR = high
      else: lives-=1
      if lives == 0: break
      listL,high,model = self.evaluate_wrapper(listL)
    return listL,high,model 

  def evaluate_wrapper(self,points=[]):
    def generate_dictionary(points=[]):  
      dictionary = {}
      chess_board = whereMain(self.model,points) #checked: working well
      for i in range(1,9):
        for j in range(1,9):
          temp = [x for x in chess_board if x.xblock==i and x.yblock==j]
          if(len(temp)!=0):
            index=temp[0].xblock*100+temp[0].yblock
            dictionary[index] = temp
            assert(len(temp)==len(dictionary[index])),"something"
      return dictionary

    def thresholdCheck(index,dictionary):
      try:
        #print "Threshold Check: ",index
        if(len(dictionary[index])>self.threshold):return True
        else:return False
      except:
        return False
    def dicttolist(dictionary):
      listL = []
      for key in dictionary.keys():
        for item in dictionary[key]:
          item.xblock = -1
          item.yblock = -1
          listL.append(item)
      return listL

    model = self.model
    minR = model.minR
    maxR = model.maxR
    #if depth == 0: model.baseline(minR,maxR)

    dictionary = generate_dictionary(points)
    #print "Depth: %d #points: %d"%(depth,self._checkDictionary(dictionary))
    from collections import defaultdict
    graph = defaultdict(list)
    matrix = [[0 for x in range(8)] for x in range(8)]
    for i in xrange(1,9):
      for j in xrange(1,9):
        if(thresholdCheck(i*100+j,dictionary)==False):
          result = self.generateNew(self.model,i,j,dictionary)
          if result == False: 
            #print "in middle of desert"
            continue
        matrix[i-1][j-1] = score(model,self.one(model,dictionary[i*100+j]))[-1]
        
       # print matrix[i-1][j-1],
      #print
    for i in xrange(1,9):
      for j in xrange(1,9):
        sumn=0
        s = matrix[i-1][j-1]
        neigh = self.listofneighbours(i,j)
        sumn = sum([1 for x in neigh if matrix[self.rowno(x)-1][self.colmno(x)-1]>s])
        if (i*100+j) in dictionary:
          graph[int(sumn)].append(i*100+j)
        

    high = 1e6
    bsoln = None
    maxi = max(graph.keys())
    count = 0
    for x in graph[maxi]:
       #print "Seive2:B Number of points in ",maxi," is: ",len(dictionary[x])
       if(len(dictionary[x]) < 15): [self.n_i(model,dictionary,x) for _ in xrange(20)]
       #print "Seive2MG:A Number of points in ",maxi," is: ",len(dictionary[x])
       for y in dictionary[x]:
         temp2 = score(model,y)[-1]
         count += 1
         if temp2 < high:
           high = temp2
           bsoln = y
    #print count     
    return dicttolist(dictionary),high,model

