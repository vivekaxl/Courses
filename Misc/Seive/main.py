from __future__ import division 
import sys 
import random
import math 
import numpy as np
from where_mod import *
sys.dont_write_bytecode = True
rand=random.random
# consist of dictionary where the index is 
# 100*xblock+yblock and 
dictionary ={} 


def neighbourhood(xblock,yblock):
  temp=[[-1,0,1],[-1,0,1]]
  comb=[]
  import itertools
  for e in itertools.product(*temp):
   comb.append(e)
  neigbour ={}
  def neighr(xblock,yblock):
    index=xblock*100+yblock
    try:
      #only return the neighbours who has threshold number of
      #elements in it.
      neigbour[index]=len(dictionary[index])
      #else:print len(dictionary[index])
    except: pass  
  for i in comb:
    neighr((xblock-i[0])%8,(yblock-i[1])%8)
  return neigbour

def stats(listl):
  from scipy.stats import scoreatpercentile
  q1 = scoreatpercentile(listl,25)
  q3 = scoreatpercentile(listl,75)  
  #print "IQR : %f"%(q3-q1)
  #print "Median: %f"%median(listl)
  return median(listl),(q3-q1)

def energy(xblock,yblock):
  tempIndex=int(100*xblock+yblock)
  energy=[]
  try:
    for x in dictionary[tempIndex]:
      energy.append(np.sum(x.obj))      
    median,iqr=stats(energy)
    #print "%d, %f, %f"%(len(dictionary[tempIndex]),median,iqr),
    return median,iqr
  except:
    print "Error"


def getpoints(index):
  tempL = []
  for x in dictionary[index]:tempL.append(x.dec)
  return tempL
    
  

def wrapperInterpolate(m,xindex,yindex):
  def interpolate(lx,ly,cr=1,fmin=0,fmax=1):
    def lo(m)      : return 0.0
    def hi(m)      : return  1.0
    def trim(x)  : # trim to legal range
      return max(lo(x), x%hi(x))
    assert(len(lx)==len(ly))
    genPoint=[]
    for i in xrange(len(lx)):
      x,y=lx[i],ly[i]
      #print x
      #print y
      rand = random.random()
      if rand < cr:
        probEx = fmin +(fmax-fmin)*random.random()
        new = trim(min(x,y)+probEx*abs(x-y))
      else:
        new = y
      genPoint.append(new)
    return genPoint

  decision=[]
  xpoints=getpoints(xindex)
  ypoints=getpoints(yindex)
  import itertools 
  listpoints=list(itertools.product(xpoints,ypoints))
  for x in listpoints:
    decision.append(interpolate(x[0],x[1]))
  return decision


def generateSlot(m,decision,x,y):
  newpoint = Slots(changed = True,
            scores=None, 
            xblock=x, #sam
            yblock=y,  #sam
            x=-1,
            y=-1,
            obj = [None] * len(objectives(m)), #[None]*4
            dec = decision)
  scores(m,newpoint)
  #print "Decision: ",newpoint.dec
  #print "Objectives: ",newpoint.obj
  return newpoint


#There are three points and I am trying to extrapolate. Need to pass two cell numbers
def wrapperextrapolate(m,xindex,yindex):
  def extrapolate(lx,ly,lz,cr=1,fmin=0.9,fmax=2):
    def lo(m)      : return 0.0
    def hi(m)      : return  1.0
    def trim(x)  : # trim to legal range
      return max(lo(x), x%hi(x))
    assert(len(lx)==len(ly)==len(lz))
    genPoint=[]
    for i in xrange(len(lx)):
      x,y,z = lx[i],ly[i],lz[i]
      rand = random.random()

      if rand < cr: 
        probEx = fmin + (fmax-fmin)*random.random()
        new = trim(x + probEx*(y-z))
      else:
        new = y #Just assign a value for that decision
      genPoint.append(new)
    print genPoint
    return genPoint

  decision=[]
  #TODO: need to put an assert saying checking whether extrapolation is actually possible
  xpoints=getpoints(xindex)
  ypoints=getpoints(yindex)
  for ij in xpoints:
    two = ij
    index2,index3=0,0
    while(index2 == index3): #just making sure that the indexes are not the same
      index2=random.randint(0,len(ypoints)-1)
      index3=random.randint(0,len(ypoints)-1)
      print "++index2: ",index2
      print "++index3: ",index3

    print "index2: ",index2
    print "index3: ",index3
    three=ypoints[index2]
    four=ypoints[index3]
    print "Two: ",two
    print "Three: ",three
    print "Four: ",four
    temp = extrapolate(two,three,four)
    print "Extrapolated: ",temp
    print
    #decision.append(extrapolate(two,three,four))
    decision.append(temp)
  return decision






def decisionMaker(m,xblock,yblock):
  def opposite(a,b):
    ax,ay,bx,by=a/100,a%100,b/100,b%100
    if(abs(ax-bx)==2 or abs(ay-by)==2):return True
    else: return False

  newpoints=[]
  threshold=3
  if(len(dictionary[xblock*100+yblock])<threshold):
    print "Cell is relatively sparse: Might need to generate new points"
  neigh = neighbourhood(xblock,yblock)
  neigh = dict((k, v) for k, v in neigh.iteritems() if v>threshold)
  for key, value in neigh.iteritems():
    print key,value,energy(int(key/100),key%10) 
  vallist=neigh.keys()
  import itertools 
  for pair in itertools.combinations(vallist,2):
    if(opposite(*pair)==True):
      print energy(xblock,yblock)
      print "We could create more points in this cell %d %d"%(xblock,yblock),
      print pair
      decisions = wrapperInterpolate(m,pair[0],pair[1])
      for decision in decisions:newpoints.append(generateSlot(m,decision,xblock,yblock))
  print "Number of new points generated: ", len(newpoints)
  for ij in newpoints:
    print ij.xblock,ij.yblock


    

  
def main():
  m='model'
  chessBoard = whereMain()
  x= int(8*random.random())
  y= int(8*random.random()) 
  #print x,y
  for i in range(1,9):
      for j in range(1,9):
          temp=[]
          for x in chessBoard:
              if x.xblock==i and x.yblock==j:
                  temp.append(x)
          if(len(temp)!=0):
            #print "tempList",
            #print temp[0].xblock,temp[0].yblock,len(temp)
            index=temp[0].xblock*100+temp[0].yblock
            dictionary[index] = temp
            assert(len(temp)==len(dictionary[index])),"something"
            #print dictionary[index][0].xblock
  #print (dictionary.keys())
  #print "Elements: %d"%len(dictionary[506])
  #print neighbourhood(5,6)
  #decisionMaker(m,5,6)
  wrapperextrapolate(m,405,607)


def _extrapolate():
  print extrapolate([2,2,2],[3,3,3],[1,1,1],fmin=0,fmax=0.1)

if __name__ == '__main__':
 # _interpolate()
  main()
  #_extrapolate()
  #_neighbourhood()
