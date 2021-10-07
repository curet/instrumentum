from itertools import combinations 
from itertools import chain

from sklearn.model_selection import cross_val_score
from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier

import pandas as pd
import numpy as np


def _default_scoring(X_train, y_train):
    
    model = DecisionTreeClassifier()
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
    return cross_val_score(model, X_train, y_train, scoring='accuracy', cv=cv).mean()
      
    
def _get_combs(set_size, combs):

    l_combs = [combinations(list(range(0, set_size)), x) for x in range(0, combs + 1)]

    return chain.from_iterable(l_combs)


# TODO: en vez de drop real y las condiciones, tener una variable que vaya agregando los globales que se eliminan
def backward_stepwise(X_train, y_train, n_combs=1, rounding=4, remove_always=False, _scorer = None):

    scorer = _default_scoring
    
    if(_scorer is not None):
        if(not hasattr(_scorer, '__call__')):
            raise ValueError("Value provided for scorer is not a callable function")
        
        scorer = _scorer
        
    print("Number of combinations: ", n_combs)
    print("Training shape: ", X_train.shape)
    print("Label distribution: \n", y_train.value_counts())
    
    X_train = X_train.copy()

    result_global = round(scorer(X_train, y_train), rounding)
  
    print("\nInitial scoring with all columns: ", result_global)
    while True:

        columns_to_remove   = [None]
        best_result_local   = 0

        combs = list(_get_combs(len(X_train.columns),n_combs))
        combs.pop(0) # remove the empty set
        
        print("Combinations to test: {}".format(len(combs)))
        for comb in combs:
            l_comb = list(comb)
            
            result_local = round(scorer(X_train.drop(X_train.columns[l_comb],axis=1), y_train), rounding)
                
            if result_local > best_result_local:
                best_result_local = result_local
                columns_to_remove = l_comb


        # equal is important below, so all being equal, keep moving and removing columns
        if (best_result_local >= result_global or remove_always) and (len(X_train.columns)>1):
            print("Best score: {}, previous {}, columns removed: {}".format(best_result_local, result_global, list(X_train.columns[columns_to_remove])))
            print("Best columns so far: {}".format(list(X_train.drop(X_train.columns[columns_to_remove],axis=1).columns)))
            result_global = best_result_local

            X_train.drop(X_train.columns[columns_to_remove],axis=1, inplace=True)
              
        else:
            print("\nBest score: {}, columns final: {}".format(result_global, list(X_train.columns)))
            break


def forward_stepwise(X_train, y_train, n_combs=1, rounding=4, add_always=False, _scorer = None):

    scorer = _default_scoring
    
    if(_scorer is not None):
        if(not hasattr(_scorer, '__call__')):
            raise ValueError("Value provided for scorer is not a callable function")
        
        scorer = _scorer
    
    
    print("Number of combinations: ", n_combs)
    print("Training shape: ", X_train.shape)
    print("Label distribution: \n", y_train.value_counts())
    
    X_train = X_train.copy()

    main = {'score':0, 'cols':[]}

    
    while True:

        local = {'score':0, 'cols':[]}
        
        cols_remainig = [x for x in X_train.columns if x not in main['cols']]  

        combs = list(_get_combs(len(cols_remainig),n_combs))
        combs.pop(0) # remove the empty set
        
        print("\nCombinations to test: {}".format(len(combs)))
        
        # Find the best result testing the current combinations
        for list(comb) in combs:
            cols_to_test = main['cols'] + list(X_train[cols_remainig].columns[comb])
            score = round(scorer(X_train[cols_to_test], y_train), rounding)
                
            if score > local['score']:
                local['score'], local['cols'] = score, cols_to_test 

        if (local['score'] > main['score'] or add_always) and (len(main['cols']) < len(X_train.columns)):
            
            print("New score: {}, previous {}".format(local['score'], main['score']))
            print("Columns so far: {}".format(local['cols'] ))
           
            main = local.copy()
            
        else:
            print("\nFinal score: {}, columns final: {}".format(main['score'], main['cols']))
            break

