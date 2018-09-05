import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
from sklearn import model_selection
from sklearn import svm
import sys


def main():
	pgs2015 = pd.read_csv('PerGameStatistics2015.csv')
	pgs2016 = pd.read_csv('PerGameStatistics2016.csv')
	pgs2017 = pd.read_csv('PerGameStatistics2017.csv')

	print(pgs2016.iloc[105],pgs2016.iloc[108])

	train_y_2015 = pgs2015.iloc[:,6]
	train_y_2015 = train_y_2015.values

	train_y_2016 = pgs2016.iloc[:,6]
	train_y_2016 = train_y_2016.drop([105,108]) #ties, can't possibly predict winner correctly 
	train_y_2016 = train_y_2016.values
	

	true_y = pgs2017.iloc[:,6]
	true_y = true_y.values

	train_X_2015 = pgs2015.iloc[:,8:]
	train_X_2015 = train_X_2015.values
	
	train_X_2016 = pgs2016.iloc[:,8:]
	train_X_2016 = train_X_2016.drop([105,108]) #ties, can't possibly predict winner correctly
	train_X_2016 = train_X_2016.values

	test_X = pgs2017.iloc[:,8:]
	test_X = test_X.values #One game missing from data.

	# sys.exit()

	train_X = np.concatenate((train_X_2015,train_X_2016))
	train_y = np.concatenate((train_y_2015,train_y_2016))

	# print(train_X, train_y)

	param_grid = [
		# {'C': np.linspace(.05,15,100), 'kernel': ['linear']}, 
		# {'C': np.linspace(.05,.15,100), 'gamma': [.1,.01,.001,.0001,1e-5,1e-6,1e-7,1e-8], 'kernel': ['rbf']},
		# {'C': [0.01,.02,.03,.04,.05,.06,.07,.08,.09,.10,.11,.12,.13,.14,.15,.16,.17,.18,.19,.20], 'kernel': ['linear']}, 
		# {'C': [0.01,.02,.03,.04,.05,.06,.07,.08,.09,.10,.11,.12,.13,.14,.15,.16,.17,.18,.19,.20], 'gamma': [.1,.01,.001,.0001,1e-5,1e-6,1e-7,1e-8], 'kernel': ['rbf']},
		{'C': np.linspace(.1304,.1306,101), 'kernel': ['linear']}, 
	]

	# clf = model_selection.GridSearchCV(svm.SVC(),param_grid)

	clf = svm.SVC(C=.1305 ,kernel = 'linear')
	clf.fit(train_X, train_y)
	# print(clf.best_params_)
	predicted = clf.predict(test_X)
	print(true_y,predicted)

	differences = true_y-predicted
	correct_rate = 1-(np.count_nonzero(differences)/differences.size)

	incorrect = []
	for index in range(len(differences)):
		if differences[index] != 0:
			incorrect.append(index)

	np_incorrect = np.asarray(incorrect)
	incorrectStats = []
	for index in np_incorrect:
		incorrectStats.append(pgs2017.iloc[index,:])

	incorrectStats = np.asarray(incorrectStats)
	incorrectGames = pd.DataFrame(incorrectStats, columns=pgs2017.columns)

	incorrectGames.to_csv('WrongPredictionsAllFeatures.csv')

	print('I predicted %.3f of the games correctly!' % correct_rate)

	pgs2015 = pgs2015.drop(['Team 1 Rushing Attempts', 'Team 2 Rushing Attempts', 'Team 1 Pass Completions', \
							'Team 2 Pass Completions', 'Team 1 Pass Attempts', 'Team 2 Pass Attempts',\
							'Team 1 Total Yards', 'Team 2 Total Yards', 'Team 1 Times Sacked', 'Team 2 Times Sacked',\
							'Team 1 3rd Down Conversions', 'Team 2 3rd Down Conversions', 'Team 1 3rd Down Attempts', \
							'Team 2 3rd Down Attempts','Team 1 Turnovers on Downs', 'Team 2 Turnovers on Downs', \
							'Team 1 Fumbles Lost', 'Team 2 Fumbles Lost', 'Team 1 Interceptions Thrown',\
  							'Team 2 Interceptions Thrown', 'Team 1 Penalties', 'Team 2 Penalties'], axis=1)
	pgs2016 = pgs2016.drop(['Team 1 Rushing Attempts', 'Team 2 Rushing Attempts', 'Team 1 Pass Completions', \
							'Team 2 Pass Completions', 'Team 1 Pass Attempts', 'Team 2 Pass Attempts',\
							'Team 1 Total Yards', 'Team 2 Total Yards', 'Team 1 Times Sacked', 'Team 2 Times Sacked',\
							'Team 1 3rd Down Conversions', 'Team 2 3rd Down Conversions', 'Team 1 3rd Down Attempts', \
							'Team 2 3rd Down Attempts','Team 1 Turnovers on Downs', 'Team 2 Turnovers on Downs', \
							'Team 1 Fumbles Lost', 'Team 2 Fumbles Lost', 'Team 1 Interceptions Thrown',\
  							'Team 2 Interceptions Thrown', 'Team 1 Penalties', 'Team 2 Penalties'], axis=1)
	pgs2017 = pgs2017.drop(['Team 1 Rushing Attempts', 'Team 2 Rushing Attempts', 'Team 1 Pass Completions', \
							'Team 2 Pass Completions', 'Team 1 Pass Attempts', 'Team 2 Pass Attempts',\
							'Team 1 Total Yards', 'Team 2 Total Yards', 'Team 1 Times Sacked', 'Team 2 Times Sacked',\
							'Team 1 3rd Down Conversions', 'Team 2 3rd Down Conversions', 'Team 1 3rd Down Attempts', \
							'Team 2 3rd Down Attempts','Team 1 Turnovers on Downs', 'Team 2 Turnovers on Downs', \
							'Team 1 Fumbles Lost', 'Team 2 Fumbles Lost', 'Team 1 Interceptions Thrown',\
  							'Team 2 Interceptions Thrown', 'Team 1 Penalties', 'Team 2 Penalties'], axis=1)

	# # print(pgs2015, pgs2015.shape)


	# # 0: rushes
 # #    2: rush yards
 # #    4: YPC
 # #    6: Pass Completions
 # #    8: Pass Attempts
 # #    10: Comp %
 #        #12: Y/A
 #        #14: Passing Yards
 #        #16: Total Yards
 #        #18: Sacks
 #        #20: Sack Yardage
 #        #22: 3rd Down Conversion
 #        #24: 3rd Down Attempts
 #        #26: 3rd Down Conversion Rate
 #        #28: Turnover On Downs
 #        #30: TO's from fumble
 #        #32: Interceptions
 #        #34: Total TO's
 #        #36: Penalties
 #        #38: Penalty Yards
 #        ###NOT FINISHED WITH BOTTOM
 #        #40: Red Zone Conversion
 #        #42: Red Zone Attempts
 #        #44: Red Zone Conversion Rate

	train_X_2015 = pgs2015.iloc[:,8:]
	train_X_2015 = train_X_2015.values

	train_X_2016 = pgs2016.iloc[:,8:]
	train_X_2016 = train_X_2016.drop([105,108])
	train_X_2016 = train_X_2016.values

	test_X = pgs2017.iloc[:,8:]
	test_X = test_X.values #One game missing from data.

	train_X = np.concatenate((train_X_2015,train_X_2016))

	# param_grid = [
	# 	# {'C': np.linspace(.05,15,100), 'kernel': ['linear']}, 
	# 	# {'C': np.linspace(.05,.15,100), 'gamma': [.1,.01,.001,.0001,1e-5,1e-6,1e-7,1e-8], 'kernel': ['rbf']},
	# 	# {'C': [0.01,.02,.03,.04,.05,.06,.07,.08,.09,.10,.11,.12,.13,.14,.15,.16,.17,.18,.19,.20], 'kernel': ['linear']}, 
	# 	# {'C': [0.01,.02,.03,.04,.05,.06,.07,.08,.09,.10,.11,.12,.13,.14,.15,.16,.17,.18,.19,.20], 'gamma': [.1,.01,.001,.0001,1e-5,1e-6,1e-7,1e-8], 'kernel': ['rbf']},
	# 	{'C': np.linspace(.127,.128,101), 'kernel': ['linear']}, 
	# ]

	# clf = model_selection.GridSearchCV(svm.SVC(),param_grid)

	clf = svm.SVC(C=.12719 ,kernel = 'linear')
	clf.fit(train_X, train_y)
	print(clf.best_params_)
	predicted = clf.predict(test_X)
	print(true_y,predicted)


	differences = true_y-predicted
	correct_rate = 1-(np.count_nonzero(differences)/differences.size)

	print('I predicted %.3f of the games correctly!' % correct_rate)

	incorrect = []
	for index in range(len(differences)):
		if differences[index] != 0:
			incorrect.append(index)

	np_incorrect = np.asarray(incorrect)
	incorrectStats = []
	for index in np_incorrect:
		incorrectStats.append(pgs2017.iloc[index,:])

	incorrectStats = np.asarray(incorrectStats)
	incorrectGames = pd.DataFrame(incorrectStats, columns=pgs2017.columns)

	incorrectGames.to_csv('WrongPredictionsSelectedFeatures.csv')

if __name__ == '__main__':
	main()
    #sys.exit(main())