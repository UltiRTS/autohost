#!/usr/bin/env python3
# coding=utf-8
import re
import math
from collections import Counter
import sklearn as sk
from sklearn.neural_network import MLPClassifier







def updateBalanceScheme():
	NN = MLPClassifier(solver='lbfgs',max_iter=9999, alpha=1e-5,activation='logistic',random_state=1,learning_rate="adaptive")
	NN.fit(X, y)   #y contains the battle result(0 or 1), X contains: map name, sorted team 1 player name list, sorted team 2 player list, weekday-time
	print(NN.loss_)

def findLeastScrewedTeam(playerList):
	leastConfidence=10
	finalCombination=['teamAplayerName','teamBPlayerName']
	for combination in possibleTeams:
		ret=getTeamPrediction(combination[0],combination[1])
		if leastConfidence> ret['confidence']:   #make sure to always use the combination that the nn thinks the least likely to happen
			leastConfidence=ret['confidence']
			finalCombination[0]=combination[0]
			finalCombination[1]=combination[1]

	return finalCombination

def getTeamPrediction(allyTeamList,enemyTeamList):
	allyTeamList.sort()
	enemyTeamList.sort()
	ateamSentence=" ".join(allyTeamList)
	enemyTeamList=" ".join(enemyTeamList)

	allySum=get_result(ateamSentence, 'ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZ')
	enemySum=get_result(enemyTeamList, 'ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZ')




	return {'result':NN.predict(input),'confidence':predict_proba(input)}   #returns the prediction and how likely the prediction is true





def _get_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


def _text_to_vector(text):
    word = re.compile(r'\w+')
    words = word.findall(text)
    return Counter(words)


def get_result(content_a, content_b):
    text1 = content_a
    text2 = content_b

    vector1 = _text_to_vector(text1)
    vector2 = _text_to_vector(text2)

    cosine_result = _get_cosine(vector1, vector2)
    return cosine_result


