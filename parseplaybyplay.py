import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import sys
from collections import Counter

def main():
    # pbp2013 = pd.read_csv('pbp-2013.csv')
    # print(pbp2013)
    #pbp2014 = pd.read_csv('pbp-2014.csv') #downloaded from NFLsavant.com/about.php
    pbp2014 = pd.read_csv('pbp-2015.csv')
    #print(pbp2014.loc[12]['GameId'])
    #pbp2014 = pd.read_csv('pbp-2016.csv')
    #sorting to get a reasonable view
    pbp2014 = pbp2014.sort_values(['GameId', 'Quarter', 'Minute', 'Second', 'YardLine'], ascending = [True,True,False,False,False])
    pbp2014 = pbp2014.reset_index(drop=True)
    #pbp2014.to_csv('pbp2015_test.csv')
    gameCount = -1 #initally, how many games are played in a seasons
    game_ids = [] #collecting ids of each unique game
    season_scores = np.zeros((256,2))
    ids_to_teams = {}
    count=0
    for index in range(pbp2014.shape[0]):
        game_id,game_date,quarter,minute,second,oTeam,dTeam,down,togo,yardline0to100,gotFirstDown,des,season,yardsGained,formation,playType,isRush,\
        isPass,isIncomplete,isTouchdown,passType,isSack,isChallenge,isChallengeReversed,isMeasurement,isInterception,isFumble,isPenalty,isTwoPointConversion,\
        isTwoPointConversionSuccessful,rushDirection,isPenaltyAccepted,yardlineFixed,yardlineDirection,penTeam,isNoPlay,penType,penYards = getEssentialPlayByPlayFeatures(index,pbp2014)
        #setting up my initial variables of potiential useful features in our play by play data

        must_loop=1
        if quarter == 1 and minute == 15 and second == 0 and playType == 'KICK OFF' and yardline0to100 == 35: #this must occur at the start of every game only once
            if gameCount != -1:
                prevGameStats = computePrevGameStats(last_game_id,team1,team2,season_scores,team_key,gameCount)
                print(prevGameStats)
            last_game_id = game_id
            last_game_date = game_date
            team1 = oTeam
            team2 = dTeam
            gameCount = gameCount+1
            game_ids.append(game_id)
            team_key = {team1:0,team2:1}
            ids_to_teams[game_id] = [oTeam,dTeam]
            #print(team_key.keys())
            #print(index,game_id, gameCount)
            #getting every unique game in a season
        # if gameCount == 16:
        #     break


        if type(des) != str: #If we don't have a description, nothing happen and skip this row
            continue

        if 'NULLIFIED' in des: #If the play was nullfied, nothing matters because there was no play
            continue

        if 'SAFETY' in des and thisHappened(des,'SAFETY'): #Safety can occur with isNoPlay==1 if Holding in end zone, using the other parts of thisHappened()
            ##If safety truly occurred, defense team gets 2 points
            isSafety = 1
            season_scores[gameCount][team_key[dTeam]] += 2
            #print(index,dTeam,des)

        if isNoPlay == 1: #Play didn't happen, ignore everything else
            continue 

        if (isInterception==1 and thisHappened(des,'INTERCEPTED')) or ('PUNTS' in des and thisHappened(des,'PUNTS')) or ('KICKS' in des and thisHappened(des,'KICKS')): 
        #If we are punting or on an interception, the other team becomes the "offense" technically speaking
            temp = oTeam
            oTeam = dTeam
            dTeam = temp

        if 'BLOCKED' in des and thisHappened(des,'BLOCKED'): #Blocked kick or punt, find out who recovered the block and adjust teams accordingly
            oTeam,dTeam = blockedRecoverer(des,oTeam,dTeam,down)

        # if isFumble == 1:
        #     if 'REVERSED' not in des:
        #         word_counts = Counter(des.split())
        #     else:
        #         word_counts= Counter(des.split('REVERSED')[1].split())
        #     if word_counts.get('FUMBLES') > 1:
        #         must_loop=word_counts.get('FUMBLES')
                #pass#print(index,word_counts.get('FUMBLES'), des, isTurnoverFromFumble(isFumble,des,dTeam),thisHappened(des,'FUMBLES'))

        if isTurnoverFromFumble(isFumble,des,oTeam,dTeam) and 'REVERSED' in des and isGoodReversed(des, 'FUMBLES'):
            pass#print(index,des)

        if isFumble ==1:
            potentialFumbleTOs = numTurnoversFromFumble(des) #gets how many times there might have been a turnover from fumble
            tdes = des
            for i in range(totalFumbles):
                if isTurnoverFromFumble(isFumble,tdes,oTeam,dTeam) and thisHappened(des,'FUMBLES'): #if there's a turnover from a fumble, needs to come after INT for edge case where intercepting team fumbles.
                    print(index,des)           
                    temp = oTeam #swap offense and defense
                    oTeam = dTeam
                    dTeam = temp
                if potentialFumbleTOs > 1:
                    tdes = des[des.index('RECOVERED')+1:] #Now checking on the next time a fumble might be recovered

        if isTouchdown==1 and thisHappened(des,'TOUCHDOWN'): #If touchdown truly occurred, offense team gets 6 points
            season_scores[gameCount][team_key[oTeam]] += 6
            #print(index,oTeam,des)
        if 'EXTRA POINT IS GOOD' in des and thisHappened(des,'EXTRA POINT IS GOOD'): #If XP truly occurred, offense team gets 1 point
            isExtraPoint = 1
            season_scores[gameCount][team_key[oTeam]] += 1
            #print(index,oTeam,des)
        if 'FIELD GOAL IS GOOD' in des and thisHappened(des,'FIELD GOAL IS GOOD'): #If FG truly occurred, offense team gets 3 points
            isFieldGoal = 1
            season_scores[gameCount][team_key[oTeam]] += 3
            #print(index,oTeam,des)
        if isTwoPointConversionSuccessful == 1 and thisHappened(des,'SUCCEEDS'): #If 2PC truly occurred, offense team gets 2 points
            is2PC = 1
            season_scores[gameCount][team_key[oTeam]] += 2
            #print(index,oTeam,des)

        
    fixProblems()
    print(season_scores)
    print(ids_to_teams)
    print('xp', count)

    checkMissingGames(gameCount, pbp2014, game_ids)

'''Function that gets the vaue of each feature at a specific index. All features below are neccessary to compute
some sort of feature that I will be using in my training data.'''
def getEssentialPlayByPlayFeatures(index, df):
    game_id = df.get_value(index, 'GameId')
    game_date = df.get_value(index, 'GameDate')
    quarter = df.get_value(index, 'Quarter')
    minute = df.get_value(index, 'Minute')
    second = df.get_value(index, 'Second')
    oTeam = df.get_value(index, 'OffenseTeam')
    dTeam = df.get_value(index, 'DefenseTeam')
    down = df.get_value(index, 'Down')
    togo = df.get_value(index, 'ToGo')
    yardline0to100 = df.get_value(index, 'YardLine')
    gotFirstDown = df.get_value(index, 'SeriesFirstDown')
    des = df.get_value(index, 'Description')
    season = df.get_value(index, 'SeasonYear')
    yardsGained = df.get_value(index, 'Yards')
    formation = df.get_value(index, 'Formation')
    playType = df.get_value(index, 'PlayType')
    isRush = df.get_value(index, 'IsRush')
    isPass = df.get_value(index, 'IsPass')
    isIncomplete = df.get_value(index, 'IsIncomplete')
    isTouchdown = df.get_value(index, 'IsTouchdown')
    passType = df.get_value(index, 'PassType')
    isSack = df.get_value(index, 'IsSack')
    isChallenge = df.get_value(index, 'IsChallenge')
    isChallengeReversed = df.get_value(index, 'IsChallengeReversed')
    isMeasurement = df.get_value(index, 'IsMeasurement')
    isInterception = df.get_value(index, 'IsInterception')
    isFumble = df.get_value(index, 'IsFumble')
    isPenalty = df.get_value(index, 'IsPenalty')
    isTwoPointConversion = df.get_value(index, 'IsTwoPointConversion')
    isTwoPointConversionSuccessful = df.get_value(index, 'IsTwoPointConversionSuccessful')
    rushDirection = df.get_value(index, 'RushDirection')
    isPenaltyAccepted = df.get_value(index, 'IsPenaltyAccepted')
    yardlineFixed = df.get_value(index, 'YardLineFixed')
    yardlineDirection = df.get_value(index, 'YardLineDirection')
    penTeam = df.get_value(index, 'PenaltyTeam')
    isNoPlay = df.get_value(index, 'IsNoPlay')
    penType = df.get_value(index, 'PenaltyType')
    penYards = df.get_value(index, 'PenaltyYards')

    return game_id,game_date,quarter,minute,second,oTeam,dTeam,down,togo,yardline0to100,gotFirstDown,des,season,yardsGained,\
    formation,playType,isRush,isPass,isIncomplete,isTouchdown,passType,isSack,isChallenge,isChallengeReversed,isMeasurement,\
    isInterception,isFumble,isPenalty,isTwoPointConversion,isTwoPointConversionSuccessful,rushDirection,isPenaltyAccepted,yardlineFixed,\
    yardlineDirection,penTeam,isNoPlay,penType,penYards\
    
'''Used for troubleshooting, to see if I was correctly counting each game'''
def checkMissingGames(gameCount, pbp2014, game_ids):           
    print('gameCount ', gameCount)
    uniqueGames = len(pbp2014['GameId'].unique())
    print('uniqueGames', uniqueGames)
    print(len(set(game_ids)), len(game_ids), uniqueGames)
    print(list(set(pbp2014['GameId'].unique())-set(game_ids))) #looking for missing game ids
    print ([item for item, count in Counter(game_ids).items() if count > 1]) #looking for duplicate game ids

'''isFumble accounts for fumbles recovered by the own team, this stat is more helpful to know'''
def isTurnoverFromFumble(fum,des,oTeam,dTeam): 
    if fum ==0:
        return False
    if 'REVERSED' in des:
        des = des.replace('.',' ').replace(',',' ').split('REVERSED')[1]
    if 'TOUCHBACK' in des:
        return True 
    tester = 'RECOVERED BY '+dTeam
    return tester in des

'''Sees how many Potential Turnovers there are from a fumble to determine how many times to loopx isTurnoverFromFumble'''
def numTurnoversFromFumble(des):
    if 'REVERSED' not in des:
        word_counts = Counter(des.replace('.',' ').replace(',',' ').split())
    else:
        word_counts = Counter(des.split('REVERSED')[1].replace('.',' ').replace(',',' ').split())
    if word_counts.get('RECOVERED')==None:
        return 0
    else:
        return word_counts.get('RECOVERED')

'''Looks for the person who recovered the block'''
def blockedRecoverer(des,oTeam,dTeam,down): 
    tester = 'RECOVERED BY '+oTeam
    tester2 = 'RECOVERED BY '+dTeam
    if tester in des and tester2 in des:
        if des.index(tester2) > des.index(tester):
            return dTeam,oTeam
        else:
            return oTeam,dTeam
    elif tester in des:
        return oTeam,dTeam
    elif tester2 in des:
        return dTeam,oTeam
    elif down != 4:
        return oTeam,dTeam
    else:
        return dTeam,oTeam

'''Any chance of a score'''
def isScore(isTouchdown,isFieldGoal,isSafety,isNoPlay,des):
    return 'NULLIFIED' not in des and (isSafety == 1 or (isNoPlay == 0 and (isTouchdown==1 or isFieldGoal == 1))) 

'''Making a list of stats for the previous game to be added to a dataframe to make a collection of game by game stats''' 
def computePrevGameStats(game_id,team1,team2,season_scores,team_key,gameCount):
    team1Score = int(season_scores[gameCount][team_key[team1]])
    team2Score = int(season_scores[gameCount][team_key[team2]])
    team1Win = int(team1Score > team2Score)
    team2Win = int(team2Score > team1Score)
    return [game_id,team1,team2,team1Score,team2Score,team1Win,team2Win]

'''If REVERSED comes after the word in question, then the play never actually happened because the call was reversed, but otherwise the call was reversed into the play, which means it did happen'''
def isGoodReversed(des, word):
    des = des.replace('.',' ').replace(',',' ').split('REVERSED')
    return word in des[1]
    # return des.replace('.',' ').replace(',',' ').split().index(word) > des.replace('.',' ').replace(',',' ').split().index('REVERSED')


'''The play did indeed occur and the result stood into the next play'''
def thisHappened(des,word):
    return 'REVERSED' not in des or isGoodReversed(des,word)

def fixProblems():
    pass

'''PROBLEMS
1. M.PRATER one XP not accounted for in table DET vs SEA, score 13-9, should be 13-10. id: 2015100500
'''

if __name__ == '__main__':
	main()
    #sys.exit(main())