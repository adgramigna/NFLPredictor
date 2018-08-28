import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import sys
from collections import Counter

def main():
    #pbp = pd.read_csv('pbp-2014.csv')
    pbp = pd.read_csv('pbp-2015.csv')  #downloaded from NFLsavant.com/about.php
    #pbp = pd.read_csv('pbp-2016.csv')
    
    #sorting to get a reasonable view
    pbp = pbp.sort_values(['GameId', 'Quarter', 'Minute', 'Second', 'YardLine'], ascending = [True,True,False,False,False])
    pbp = pbp.reset_index(drop=True)

    # pbp.to_csv('pbp2015_test.csv')

    print(pbp['PlayType'].unique())

    
    count = 1
    gameCount = -1 #initally, how many games are played in a season
    game_ids = [] #collecting ids of each unique game
    season_scores = np.zeros((256,2))
    team_records = np.zeros((32,2))
    game_stats = np.zeros((256,40))
    teams = {'ARI': 0, 'ATL': 1, 'BAL': 2, 'BUF': 3, 'CAR': 4, 'CHI': 5, 'CIN': 6, 'CLE': 7, 'DAL': 8, 'DEN': 9,\
    'DET': 10, 'GB': 11, 'HOU': 12, 'IND': 13, 'JAX': 14, 'JAC': 14, 'KC': 15, 'LA': 16, 'LAR': 16, 'STL': 16, \
    'MIA': 17, 'MIN': 18, 'NE': 19, 'NO': 20, 'NYJ': 21, 'NYG': 22, 'OAK': 23,'PHI': 24, 'PIT': 25, 'SD': 26, \
    'LAC': 26, 'SEA': 27, 'SF': 28, 'TB': 29, 'TEN': 30, 'WAS': 31} 
    for index in range(pbp.shape[0]):
        game_id,game_date,quarter,minute,second,oTeam,dTeam,down,yardsToGo,yardline0to100,gotFirstDown,des,season,yardsGained,formation,playType,isRush,\
        isPass,isIncomplete,isTouchdown,passType,isSack,isChallenge,isChallengeReversed,isMeasurement,isInterception,isFumble,isPenalty,isTwoPointConversion,\
        isTwoPointConversionSuccessful,rushDirection,isPenaltyAccepted,yardlineFixed,yardlineDirection,penTeam,isNoPlay,penType,penYards = getEssentialPlayByPlayFeatures(index,pbp)
        #setting up my initial variables of potiential useful features in play by play data

       
        #Fixing Error with descriptions, problems 3 and 4
        if oTeam == 'JAX' and season == 2015: 
            oTeam = 'JAC'
        if dTeam == 'JAX' and season == 2015:
            dTeam = 'JAC'
        if oTeam == 'LA' and season == 2015:
            oTeam = 'STL'
        if dTeam == 'LA' and season == 2015:
            dTeam = 'STL'

        if quarter == 1 and minute == 15 and second == 0 and playType == 'KICK OFF' and yardline0to100 == 35: #this must occur at the start of every game only once
            if gameCount != -1:
                prevGameStats = computePrevGameStats(last_game_id,team1,team2,season_scores,team_key,gameCount)
                print(prevGameStats)
                updateTeamRecords(team1,team2,season_scores,team_key,gameCount,team_records, teams)
                game_stats[gameCount][4] = game_stats[gameCount][0]+game_stats[gameCount][2]
                game_stats[gameCount][5] = game_stats[gameCount][1]+game_stats[gameCount][3] 
            last_game_id = game_id
            last_game_date = game_date
            gameCount = gameCount+1
            team1 = oTeam
            team2 = dTeam
            game_ids.append(game_id)
            team_key = {team1:0,team2:1}
        
        # if gameCount == 16:
        #     break

        if index == 24229:
            playType = 'FUMBLES'

        if index == 12528 and season == 2015: #fixing error with data, problem 2
            isTouchdown = 0

        if index == 36932 and season == 2015: #fixing error with data, problem 7
            isTouchdown = 0

        if index == 27450 and season == 2015: #Description was bad, so play is hard coded, aborted play 1 rush and 1 fum for R. FITZPATRICK
            game_stats[gameCount][10+team_key[oTeam]] += 1
            continue

        if index == 2310 and season == 2015: #Same, 1 rush and 3 yards for J. RANDLE
            game_stats[gameCount][10+team_key[oTeam]] += 1
            game_stats[gameCount][team_key[oTeam]]+= 3
            continue

        if index == 17455 and season == 2015: #Same, 1 rush and -1 yards for T. Brady
            game_stats[gameCount][10+team_key[oTeam]] += 1
            game_stats[gameCount][team_key[oTeam]]+= -1
            continue
        # if gameCount != 2:
        #     continue

        if type(des) != str: #If we don't have a description, nothing happen and skip this row
            continue

        if 'NULLIFIED' in des: #If the play was nullified, nothing matters because there was no play
            continue

        if 'REVERSED' in des:
            des = des.split('REVERSED')[1]
            if 'TOUCHDOWN' not in des:
                isTouchdown = 0
            if 'FUMBLES' not in des:
                isFumble = 0
            if 'INTERCEPTED' not in des:
                isInterception = 0
            # print(index, des)

        if isFumble and 'FUMBLES' not in des:
            isFumble = 0

        if playType == 'FUMBLES' and isFumble and 'ABORTED' not in des:
            playType = 'RUSH'

        if 'DELAY OF GAME' in des:
            isNoPlay = 1
            # if not isPenalty:
            #     print(index,des)

        if isInterception:
            retrunYards = yardsGained
            yardsGained = 0

        # if playType == 'PUNT' and 'PUNTS' not in des and 'BLOCKED' not in des and 'KICKS' not in des:
        #     playType = 'RUSH'

        isTOFromFumble = isTurnoverFromFumble(isFumble,des,oTeam,dTeam,season,isInterception)

        isSafety = 0
        isExtraPoint = 0
        isFieldGoal = 0
        is2PC = 0 
        isDef2PC = 0

        # print(gameCount)

        if 'SAFETY' in des and 'FOLLOWING THE SAFETY' not in des: #Safety can occur with isNoPlay==1 if Holding in end zone, using the other parts of thisHappened()
            ##If safety truly occurred, defense team gets 2 points
            isSafety = 1
            season_scores[gameCount][team_key[dTeam]] += 2
            # print(index,dTeam,des)

        if isPenaltyAccepted and penTeam == oTeam and penType != 'UNNECESSARY ROUGHNESS': #maybe?
            isNoPlay = 1

        if isNoPlay == 1: #Play didn't happen, ignore everything else
            continue

        if playType == 'FUMBLES':
            game_stats[gameCount][10+team_key[oTeam]] += 1

        if playType == 'FUMBLES' and not isTOFromFumble:
            if 'OUT OF BOUNDS' in des: #covers safeties too
                pass
            elif isTouchdown:
                yardsGained = 100 - yardline0to100
            else:
                if 'RAN OB AT' in des:
                    tdes = des.split('RAN OB AT ')
                else:
                    tdes = des.split(' TO ')
                howFar = tdes[1][:6].split()
                if howFar[0] == dTeam:
                    howFar[1]=100-int(howFar[1])
                if howFar[0][:2] != '50': #No gain
                    howFar = howFar[1]
                else:
                    howFar = howFar[0]
                howFar = int(howFar)
                yardsGainedTotal = howFar-yardline0to100
                yardsGained = max(0,yardsGainedTotal) #official rules of an aborted play, aborter credited with a rush for no gain
            game_stats[gameCount][0+team_key[oTeam]] += yardsGained
            #Increment Rush Attempts and yardsGained
        # if playType == 'FUMBLES' and isSafety and not isTurnoverOnDowns(down, yardsGained, yardsToGo, isInterception, isTOFromFumble,isSafety, 'PUNTS' in des):
        #     print(index, yardlineDirection, yardlineFixed, des, yardsGained, bool(isTurnoverOnDowns(down, yardsGained, yardsToGo, isInterception, isTOFromFumble, isSafety,'PUNTS' in des)))

        # if game_id == 2015101804 and isFumble == 1:
        #     print(index,des)

        if (isFumble and (playType == 'RUSH' or playType == 'QB KNEEL' or playType == 'SCRAMBLE')) or (playType == 'PUNT' and 'PUNTS' not in des and 'BLOCKED' not in des and 'KICKS' not in des):
            tdes = des.split('FOR ')
            howFar = tdes[1][:tdes[1].index(' ')]
            if howFar == 'NO': #No gain
                howFar = 0
            howFar = int(howFar)
            if 'AND RECOVERS' in des and len(tdes) > 2: #Rare scenario where runner recovers their own fumble and gains yardage
                if tdes[2][:tdes[2].index(' ')] != 'NO': #No gain
                    howFar += int(tdes[2][:tdes[2].index(' ')])
            yardsGained = howFar

            if isFumble:
                if 'TOUCHBACK' in des:
                    pass
                elif 'BALL OUT OF BOUNDS' in des: #covers safeties too
                    tdes = des.split('BALL OUT OF BOUNDS AT ')
                    howFar = tdes[1][:6].replace('.',' ').replace(',',' ').split()
                    if howFar[0] == dTeam:
                        howFar[1]=100-int(howFar[1])
                    if howFar[0][:2] != '50': #No gain
                        howFar = howFar[1]
                    else:
                        howFar = howFar[0]
                    howFar = int(howFar)
                    yardsGained = min(howFar-yardline0to100, yardsGained)
                else:
                    # if 'RAN OB AT' in des:
                    #     tdes = des.split('RAN OB AT ')
                    # else:
                    # print(index,des,playType)
                    tdes = des.split(' AT ')
                    howFar = tdes[1][:6].replace('.',' ').replace(',',' ').split()
                    if howFar[0] == dTeam:
                        howFar[1]=100-int(howFar[1])
                    if howFar[0][:2] != '50': #No gain
                        howFar = howFar[1]
                    else:
                        howFar = howFar[0]
                    howFar = int(howFar)
                    yardsGained = min(howFar-yardline0to100, yardsGained)

            game_stats[gameCount][0+team_key[oTeam]] += yardsGained

            if not isTOFromFumble:
                print(index, yardlineDirection, yardlineFixed, yardsGained, des, bool(isTOFromFumble), playType)
        
        if playType == 'SACK' and isFumble and 'OUT OF BOUNDS' in des:
            if isSafety:
                yardsGained = 0 - yardline0to100
            tdes = des.split('OUT OF BOUNDS AT ')
            game_stats[gameCount][6+team_key[dTeam]] += 1
            game_stats[gameCount][8+team_key[dTeam]] += yardsGained
            # print(index, yardlineDirection, yardlineFixed, yardsGainedTotal, yardsGained, des, bool(isTOFromFumble))
        
        if playType == 'RUSH' or playType == 'QB KNEEL' or playType == 'SCRAMBLE':
            game_stats[gameCount][0+team_key[oTeam]] += yardsGained
        if playType == 'PASS' or playType == 'SACK':
            game_stats[gameCount][2+team_key[oTeam]] += yardsGained
        

        # if playType == 'PASS':
        #     print(index, yardlineDirection, yardlineFixed, yardsGainedTotal, yardsGained, des, bool(isTOFromFumble))

        # if playType == 'SCRAMBLE' and isFumble:
        #     print(index, yardlineDirection, yardlineFixed, yardsGainedTotal, yardsGained, des, bool(isTOFromFumble), playType)
        # print(index)


        # continue 

        if isInterception==1 or 'PUNTS' in des or 'KICKS' in des: 
        #If we are punting or on an interception, the other team becomes the "offense" technically speaking
            temp = oTeam
            oTeam = dTeam
            dTeam = temp

        if 'BLOCKED' in des: #Blocked kick or punt, find out who recovered the block and adjust teams accordingly
            oTeam,dTeam = blockedRecoverer(des,oTeam,dTeam,down)

        if isFumble == 1:
            potentialFumbleTOs = numTurnoversFromFumble(des) #gets how many times there might have been a turnover from fumble
            tdes = des #So I can check each time with the most recent revocery
            for i in range(potentialFumbleTOs):
                if isTOFromFumble: #if there's a turnover from a fumble, needs to come after INT for edge case where intercepting team fumbles.
                    #print(index,des)           
                    temp = oTeam #swap offense and defense
                    oTeam = dTeam
                    dTeam = temp
                if potentialFumbleTOs > 1:
                    # print(index,tdes,oTeam,dTeam)
                    if 'RECOVERED' not in tdes:
                        break #can't be any more potential turnovers from fumbles if no one recovers
                    tdes = tdes[des.index('RECOVERED')+1:] #Now checking on the next time a fumble might be recovered

        # continue
        if isTouchdown==1: #If touchdown truly occurred, offense team gets 6 points
            season_scores[gameCount][team_key[oTeam]] += 6
            # print(index,oTeam,des)
        if 'EXTRA POINT IS GOOD' in des: #If XP truly occurred, offense team gets 1 point
            isExtraPoint = 1
            season_scores[gameCount][team_key[oTeam]] += 1
            # print(index,oTeam,des)
        if 'FIELD GOAL IS GOOD' in des: #If FG truly occurred, offense team gets 3 points
            isFieldGoal = 1
            season_scores[gameCount][team_key[oTeam]] += 3
            # print(index,oTeam,des)
        if isTwoPointConversionSuccessful == 1: #If 2PC truly occurred, offense team gets 2 points
            is2PC = 1
            season_scores[gameCount][team_key[oTeam]] += 2
            # print(index,oTeam,des)
        if 'DEFENSIVE TWO-POINT ATTEMPT' in des and 'SUCCEEDS' in des:
            isDef2PC = 1
            season_scores[gameCount][team_key[dTeam]] += 2
            # print(index,dTeam,des)

        # if 'DEFENSIVE TWO-POINT ATTEMPT' in des and thisHappened(des, 'DEFENSIVE TWO-POINT ATTEMPT'):
        #     # print(index, gameCount, des)

    prevGameStats = computePrevGameStats(last_game_id,team1,team2,season_scores,team_key,gameCount)
    print(prevGameStats)
    updateTeamRecords(team1,team2,season_scores,team_key,gameCount,team_records, teams)
    fixProblems(game_id,season_scores)
    # print(season_scores)
    print(count)


    checkMissingGames(gameCount, pbp, game_ids)

    for key in teams:
        wins = team_records[teams[key]][0]
        losses = team_records[teams[key]][1]
        print(key, '%i-%i' % (wins,losses))

    print(game_stats[2])


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
    down = df.get_value(index, 'Down') #3rd down conversion rate
    yardsToGo = df.get_value(index, 'ToGo')
    yardline0to100 = df.get_value(index, 'YardLine')
    gotFirstDown = df.get_value(index, 'SeriesFirstDown') #first downs
    des = df.get_value(index, 'Description')
    season = df.get_value(index, 'SeasonYear')
    yardsGained = df.get_value(index, 'Yards') #total yards, pass yards, rush yards
    formation = df.get_value(index, 'Formation')
    playType = df.get_value(index, 'PlayType')
    isRush = df.get_value(index, 'IsRush') #YPC
    isPass = df.get_value(index, 'IsPass') #YPA
    isIncomplete = df.get_value(index, 'IsIncomplete') #Completion rate
    isTouchdown = df.get_value(index, 'IsTouchdown')
    passType = df.get_value(index, 'PassType')
    isSack = df.get_value(index, 'IsSack') #sacks
    isChallenge = df.get_value(index, 'IsChallenge') #challenges, won challenges, rate
    isChallengeReversed = df.get_value(index, 'IsChallengeReversed')
    isMeasurement = df.get_value(index, 'IsMeasurement')
    isInterception = df.get_value(index, 'IsInterception') #turnover margin, fumbles, ints,
    isFumble = df.get_value(index, 'IsFumble')
    isPenalty = df.get_value(index, 'IsPenalty') #penalties
    isTwoPointConversion = df.get_value(index, 'IsTwoPointConversion')
    isTwoPointConversionSuccessful = df.get_value(index, 'IsTwoPointConversionSuccessful')
    rushDirection = df.get_value(index, 'RushDirection')
    isPenaltyAccepted = df.get_value(index, 'IsPenaltyAccepted') 
    yardlineFixed = df.get_value(index, 'YardLineFixed')
    yardlineDirection = df.get_value(index, 'YardLineDirection')
    penTeam = df.get_value(index, 'PenaltyTeam')
    isNoPlay = df.get_value(index, 'IsNoPlay')
    penType = df.get_value(index, 'PenaltyType')
    penYards = df.get_value(index, 'PenaltyYards') #penalty yards

    return game_id,game_date,quarter,minute,second,oTeam,dTeam,down,yardsToGo,yardline0to100,gotFirstDown,des,season,yardsGained,\
    formation,playType,isRush,isPass,isIncomplete,isTouchdown,passType,isSack,isChallenge,isChallengeReversed,isMeasurement,\
    isInterception,isFumble,isPenalty,isTwoPointConversion,isTwoPointConversionSuccessful,rushDirection,isPenaltyAccepted,yardlineFixed,\
    yardlineDirection,penTeam,isNoPlay,penType,penYards\

def findRelevantIndex(index, df):
    while df.get_value(index, 'YardLine') == 0:
        index+= 1
    return index

'''Used for troubleshooting, to see if I was correctly counting each game'''
def checkMissingGames(gameCount, pbp, game_ids):           
    print('gameCount ', gameCount)
    uniqueGames = len(pbp['GameId'].unique())
    print('uniqueGames', uniqueGames)
    print(len(set(game_ids)), len(game_ids), uniqueGames)
    print(list(set(pbp['GameId'].unique())-set(game_ids))) #looking for missing game ids
    print ([item for item, count in Counter(game_ids).items() if count > 1]) #looking for duplicate game ids

'''Checks if there is a turnover on downs.'''
def isTurnoverOnDowns(down, yardsGained, yardsToGo, isInterception, isTOFromFumble, isSafety, isActualPunt):
    return down == 4 and yardsGained < yardsToGo and not isInterception and not isTOFromFumble and not isSafety and not isActualPunt

'''isFumble accounts for fumbles recovered by the own team, this stat is more helpful to know'''
def isTurnoverFromFumble(fum,des,oTeam,dTeam,season,isInterception):
    if not fum:
        return False
    if 'TOUCHBACK' in des:
        return True 
    if isInterception:
        temp = oTeam #swap offense and defense
        oTeam = dTeam
        dTeam = temp
    tester = 'RECOVERED BY '+dTeam
    return tester in des

'''Sees how many Potential Turnovers there are from a fumble to determine how many times to loop isTurnoverFromFumble'''
def numTurnoversFromFumble(des):
    turnovers = 0
    word_counts = Counter(des.replace('.',' ').replace(',',' ').split())
    # print(word_counts)
    if 'TOUCHBACK' in des:
        turnovers+=1
    if word_counts.get('RECOVERED')!=None:
        turnovers+=word_counts.get('RECOVERED')
    return turnovers
        

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

'''Making a list of stats for the previous game to be added to a dataframe to make a collection of game by game stats''' 
def computePrevGameStats(game_id,team1,team2,season_scores,team_key,gameCount):
    team1Score = int(season_scores[gameCount][team_key[team1]])
    team2Score = int(season_scores[gameCount][team_key[team2]])
    team1Win = int(team1Score > team2Score)
    team2Win = int(team2Score > team1Score)
    return [game_id,gameCount,team1,team2,team1Score,team2Score,team1Win,team2Win]

def updateTeamRecords(team1,team2,season_scores,team_key,gameCount,team_records,teams):
    team1Score = int(season_scores[gameCount][team_key[team1]])
    team2Score = int(season_scores[gameCount][team_key[team2]])
    if team1Score > team2Score:
        team_records[teams[team1]][0] += 1
        team_records[teams[team2]][1] += 1
    else:
        team_records[teams[team1]][1] += 1
        team_records[teams[team2]][0] += 1

# '''If REVERSED comes after the word in question, then the play never actually happened because the call was reversed, but otherwise the call was reversed into the play, which means it did happen'''
# def isGoodReversed(des, word):
#     des = des.replace('.',' ').replace(',',' ').split('REVERSED')
#     return word in des[1]

# '''The play did indeed occur and the result stood into the next play'''
# def thisHappened(des,word):
#     return 'REVERSED' not in des or isGoodReversed(des,word)

'''Fixing problems with missing data in the csv, hardcoded'''
def fixProblems(game_id,season_scores):
    problem_count=0
    problem_count+=1
    season_scores[62][1] +=1
    print('Problem: '+str(problem_count)+ ' Fixed. New Score- DET: '+str(int(season_scores[62][1]))+' SEA: '+str(int(season_scores[62][0])))
    problem_count+=1
    print('Problem: '+str(problem_count)+ ' Fixed in code, removed isTouchdown from index 12528. New score correct in code.')
    problem_count+=1
    print('Problem: '+str(problem_count)+ ' Fixed in code, changed dTeam from JAX to JAC for 2015. New score correct in code.')
    problem_count+=1
    print('Problem: '+str(problem_count)+ ' Fixed in code, changed dTeam from LA to JAC for STL. New score correct in code.')
    problem_count+=1
    season_scores[112][0] +=1
    print('Problem: '+str(problem_count)+ ' Fixed. New Score- NYG: '+str(int(season_scores[112][0]))+' NO: '+str(int(season_scores[112][1])))
    problem_count+=1
    season_scores[179][1] +=2
    print('Problem: '+str(problem_count)+ ' Fixed. New Score- BAL: '+str(int(season_scores[179][0]))+' MIA: '+str(int(season_scores[179][1])))
    problem_count+=1
    print('Problem: '+str(problem_count)+ ' Fixed in code, removed isTouchdown from index 36932. New score correct in code.')
            

'''PROBLEMS
2015
1. M.PRATER one XP not accounted for in table DET vs SEA, score 13-9, should be 13-10. id: 2015100500
2. J.FLACCO Given touchdown twice because of mismarked isTouchdown on index 12528. Score 33-36, should be 33-30. id: 2015101105
3. JAX Showing up as JAC for dTeam in 2015, changes to JAX in 2016
4. LA Showing up as STL for dTeam in 2015, changes to LA in 2016
5. J.BROWN one XP not accounted for in table NYG vs NO, score 48-52, should be 49-52. id: 2015110106
6. J. AJAYI 2PC not counted for MIA vs BAL, score 13-13, should be 13-15 Dolphins. id: 2015120602
7. SF Given touchdown twice because of mismarked isTouchdown on index 36932. Score 16-24, should be 10-24. id: 2015121310
8-12. RUSH plays mislabeled as FUMBLES (i.e. Aborted snap) indicies: 43494, 38361, 32882, 28345, 21522 
'''

if __name__ == '__main__':
	main()
    #sys.exit(main())