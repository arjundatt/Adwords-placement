import sys
import collections
import itertools
import random
import copy
import math
from hopcroftkarp import HopcroftKarp

random.seed(0)
if len(sys.argv) != 2:
    print "python adwords.py <greedy|balance|msvv>"
    exit(1)
algorithm = sys.argv[1]

path_to_data = "bidder_dataset.csv"
path_to_queries = "queries.txt"

def main():
    bidders,budget,queries = load_data()
    revenue = 0.0
    comp_ratio = 0.0
    OPT = optimalMatching(bidders)
    
    if algorithm == "greedy":
        revenue = greedyAlgo(copy.deepcopy(bidders),copy.deepcopy(budget),queries)
        sum_rev = 0.0
        for i in range(0,99):
            random.shuffle(queries)
            r = greedyAlgo(copy.deepcopy(bidders),copy.deepcopy(budget), queries)
            sum_rev += r
        ALG = sum_rev/100
        comp_ratio =  ALG/OPT

    elif algorithm == "balance":
        revenue = balanceAlgo(copy.deepcopy(bidders),copy.deepcopy(budget),queries)
        sum_rev = 0.0
        for i in range(0,99):
            random.shuffle(queries)
            r = balanceAlgo(copy.deepcopy(bidders),copy.deepcopy(budget), queries)
            sum_rev += r
        ALG = sum_rev/100
        comp_ratio =  ALG/OPT
    elif algorithm == "msvv":
        revenue = msvvAlgo(copy.deepcopy(bidders),copy.deepcopy(budget),queries)
        sum_rev = 0.0
        for i in range(0,99):
            random.shuffle(queries)
            r = msvvAlgo(copy.deepcopy(bidders),copy.deepcopy(budget), queries)
            sum_rev += r
        ALG = sum_rev/100
        comp_ratio =  ALG/OPT
    else:
        print "invalid parameters"
    print "revenue = "+str(revenue)
    print "competitive ratio = "+str(comp_ratio/100)

#Loads all the data and creates bidders, budget and queries dictionaries
def load_data():
    f = open(path_to_data,"r")
    print "reading"
    bidders = {}
    budget = {}
    for i,line in enumerate(f):
        if i==0:
            continue
        entry = line.split(',')
        if(entry[1] in bidders):
            prev = bidders[entry[1]]
        else:
            prev = []
        prev.append((int(entry[0]),float(entry[2])))
        bidders[entry[1]] = prev
        
        if entry[3]!='' and entry[3]!='\n':
            budget[int(entry[0])]=float(entry[3].strip())
    f.close()
    
    f_query = open(path_to_queries,"r")
    queries = []
    for line in f_query:
        queries.append(line.strip())
    
    return bidders,budget,queries

#applies greedy algorithm on one sequence of queries and returns revenue
def greedyAlgo(bidders,budget,queries):
    revenue = 0.0
    for q in queries:
        if q in bidders:
            currBids = bidders[q]
            currBids = sorted(currBids,key=lambda x: x[1], reverse = True)
            for bid in currBids:
                if budget[bid[0]] >= bid[1]:
                    budget[bid[0]] = budget[bid[0]]-bid[1]
                    revenue += bid[1]
                    break
    return revenue

#applies balance algorithm on one sequence of queries and returns revenue
def balanceAlgo(bidders,budget,queries):
    revenue = 0.0
    for q in queries:
        if q in bidders:
            currBids = bidders[q]
            currBids = sorted(currBids, key= lambda x: x[0])
            maxBud = -1.0
            maxBidder = -1
            winningBid = -1.0
            for bid in currBids:
                if budget[bid[0]] >= bid[1] and maxBud<budget[bid[0]]:
                    maxBud = budget[bid[0]]
                    maxBidder = bid[0]
                    winningBid = bid[1]
            if maxBud!=-1.0:
                budget[maxBidder] = maxBud - winningBid
                revenue += winningBid
    return revenue

#applies msvv algorithm on one sequence of queries and returns revenue
def msvvAlgo(bidders,budget,queries):
    revenue = 0.0
    initBudget = {}
    initBudget = copy.deepcopy(budget)
    
    def chiX(xu):
        return 1.0-math.exp(xu-1.0)
    
    for q in queries:
        if q in bidders:
            currBids = bidders[q]
            currBids = sorted(currBids, key= lambda x: x[0])
            maxVal = -1.0
            maxBidder = -1
            winningBid = -1.0
            for bid in currBids:
                val = (bid[1]*chiX(1-(budget[bid[0]]/initBudget[bid[0]])))
                if budget[bid[0]] >= bid[1] and maxVal<val:
                    maxVal = val
                    maxBidder = bid[0]
                    winningBid = bid[1]
            if maxVal!=-1.0:
                budget[maxBidder] = budget[maxBidder] - winningBid
                revenue += winningBid
    return revenue

#computes cardinality of optimal matching
def optimalMatching(bidders):
    graph = {}
    for q in bidders:
        for advertiser in bidders[q]:
            l = []
            if((advertiser[0],advertiser[1]) in graph):
                l = graph[(advertiser[0],advertiser[1])]
            l.append(q)
            graph[(advertiser[0],advertiser[1])] = l
    optimal = HopcroftKarp(graph).maximum_matching()
#    print len(optimal)
#    revenue = 0.0
#    for entity in optimal:
#        key = ''
#        if(type(entity) is tuple):
#            print entity[1]
#            revenue += entity[1]
#        else:
#            print tuple(optimal[entity])[1]
#            revenue += tuple(optimal[entity])[1]
#    print revenue
    return len(optimal)
    

if __name__=="__main__":
    main()
