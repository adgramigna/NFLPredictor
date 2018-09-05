import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import sys
from collections import Counter

def main():
    for gameSeason in range(2015,2018):
        if gameSeason == 2015:
            pbp = pd.read_csv('pbp-2015.csv')  #downloaded from NFLsavant.com/about.php
        elif gameSeason == 2016:
            pbp = pd.read_csv('pbp-2016.csv')
        elif gameSeason == 2017:
            pbp = pd.read_csv('pbp-2017.csv')
    
    #sorting to get a reasonable view
        pbp = pbp.sort_values(['GameId', 'Quarter', 'Minute', 'Second', 'Down', 'YardLine'], ascending = [True,True,False,False,True,False])
        pbp = pbp.reset_index(drop=True)
        

        # pbp.to_csv('pbp2017_test.csv')

        # sys.exit()

        gameCount = -1 #initally, how many games are played in a season
        game_ids = [] #collecting ids of each unique game
        team_records = np.zeros((32,2))
        prev_game_stats = []
        if gameSeason == 2017:
            game_stats = np.zeros((255,40))
            gameStatsIndex = range(0,255)
            season_scores = np.zeros((255,2))
             #MAJOR PROBLEM #If 2017 season, dataset is missing the IND vs BUF game from this past year
             #Removing game to account for it. Could add manually, but this game was a blizzard and an outlier anyway
        else: #Normal Season 
            game_stats = np.zeros((256,40))
            gameStatsIndex = range(0,256)
            season_scores = np.zeros((256,2))
        gameStatsCols = ['game_id', 'gameCount', 'Team 1', 'Team 2', 'Team 1 Score', 'Team 2 Score', 'Team 1 Win', \
      'Team 2 Win', 'Team 1 Rushing Attempts', 'Team 2 Rushing Attempts', 'Team 1 Rushing Yards', 'Team 2 Rushing Yards',\
      'Team 1 YPC', 'Team 2 YPC', 'Team 1 Pass Completions', 'Team 2 Pass Completions', 'Team 1 Pass Attempts', \
      'Team 2 Pass Attempts', 'Team 1 Completion Percentage', 'Team 2 Completion Percentage', 'Team 1 YPA', 'Team 2 YPA',\
      'Team 1 Passing Yards', 'Team 2 Passing Yards', 'Team 1 Total Yards', 'Team 2 Total Yards', 'Team 1 Times Sacked',\
      'Team 2 Times Sacked', 'Team 1 Sack Yardage', 'Team 2 Sack Yardage', 'Team 1 3rd Down Conversions', \
      'Team 2 3rd Down Conversions', 'Team 1 3rd Down Attempts', 'Team 2 3rd Down Attempts',\
      'Team 1 3rd Down Conversion Rate', 'Team 2 3rd Down Conversion Rate', 'Team 1 Turnovers on Downs',\
      'Team 2 Turnovers on Downs', 'Team 1 Fumbles Lost', 'Team 2 Fumbles Lost', 'Team 1 Interceptions Thrown',\
      'Team 2 Interceptions Thrown', 'Team 1 Total Turnovers', 'Team 2 Total Turnovers', 'Team 1 Penalties',\
      'Team 2 Penalties', 'Team 1 Penalty Yardage', 'Team 2 Penalty Yardage']
        teams = {'ARI': 0, 'ATL': 1, 'BAL': 2, 'BUF': 3, 'CAR': 4, 'CHI': 5, 'CIN': 6, 'CLE': 7, 'DAL': 8, 'DEN': 9,\
        'DET': 10, 'GB': 11, 'HOU': 12, 'IND': 13, 'JAX': 14, 'JAC': 14, 'KC': 15, 'LA': 16, 'STL': 16, \
        'MIA': 17, 'MIN': 18, 'NE': 19, 'NO': 20, 'NYJ': 21, 'NYG': 22, 'OAK': 23,'PHI': 24, 'PIT': 25, 'SD': 26, \
        'LAC': 26, 'SEA': 27, 'SF': 28, 'TB': 29, 'TEN': 30, 'WAS': 31} 



        for index in range(pbp.shape[0]):
            game_id,game_date,quarter,minute,second,oTeam,dTeam,down,yardsToGo,yardline0to100,gotFirstDown,des,season,yardsGained,formation,playType,isRush,\
            isPass,isIncomplete,isTouchdown,passType,isSack,isChallenge,isChallengeReversed,isMeasurement,isInterception,isFumble,isPenalty,isTwoPointConversion,\
            isTwoPointConversionSuccessful,rushDirection,isPenaltyAccepted,yardlineFixed,yardlineDirection,penTeam,isNoPlay,penType,penYards = getEssentialPlayByPlayFeatures(index,pbp)
            #setting up my initial variables of potiential useful features in play by play data


            # Fixing Error with descriptions, problems 3 and 4
            # if season == 2017 and game_id == 2017121000:
            #     print(index,des,playType, dTeam)

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
                    fixProblems(game_id, gameCount, season, season_scores, team_key)
                    prevGameStats = computePrevGameStats(game_id,team1,team2,season_scores,team_key,gameCount)
                    prev_game_stats.append(prevGameStats)
                    updateTeamRecords(team1,team2,season_scores,team_key,gameCount,team_records, teams)
                    # print(prevGameStats)
                    if gameCount == 62 or gameCount == 112 or gameCount == 179:
                        print(prevGameStats)
                    
                    game_stats[gameCount][14] += game_stats[gameCount][20]
                    game_stats[gameCount][15] += game_stats[gameCount][21]
                    game_stats[gameCount][16] = game_stats[gameCount][2]+game_stats[gameCount][14] #total yards
                    game_stats[gameCount][17] = game_stats[gameCount][3]+game_stats[gameCount][15]
                    game_stats[gameCount][4] = round(game_stats[gameCount][2]/game_stats[gameCount][0],1) #ypc
                    game_stats[gameCount][5] = round(game_stats[gameCount][3]/game_stats[gameCount][1],1)
                    game_stats[gameCount][10] = round(game_stats[gameCount][6]/game_stats[gameCount][8],3)*100 #Comp %
                    game_stats[gameCount][11] = round(game_stats[gameCount][7]/game_stats[gameCount][9],3)*100
                    game_stats[gameCount][12] = round(game_stats[gameCount][14]/game_stats[gameCount][8],1) #ypa
                    game_stats[gameCount][13] = round(game_stats[gameCount][15]/game_stats[gameCount][9],1)
                    game_stats[gameCount][26] = round(game_stats[gameCount][22]/game_stats[gameCount][24],3)*100 #3rd down Conv rate
                    game_stats[gameCount][27] = round(game_stats[gameCount][23]/game_stats[gameCount][25],3)*100
                    game_stats[gameCount][34] = game_stats[gameCount][30]+game_stats[gameCount][32] #Total TO's
                    game_stats[gameCount][35] = game_stats[gameCount][31]+game_stats[gameCount][33]

                # if season == 2017 and oTeam == 'IND':
                #     print(dTeam)
                # if season == 2017 and dTeam == 'IND':
                #     print(oTeam)
                last_game_id = game_id
                last_game_date = game_date
                gameCount = gameCount+1
                team1 = oTeam
                team2 = dTeam
                game_ids.append(game_id)
                team_key = {team1:0,team2:1}
            
            # if gameCount == 16:
            #     break

            if index == 44732 and season == 2015: #Description said pass so they though it was a pass
                playType = 'EXTRA POINT'
                # print(index, des)

            if index == 12528 and season == 2015: #fixing error with data, problem 2
                isTouchdown = 0
                # print(index, des)

            if index == 36932 and season == 2015: #fixing error with data, problem 7
                isTouchdown = 0
                # print(index, des)

            if index == 22472 and season == 2015: #Officals Huddled but did not call a penalty, dumb description
                isPenaltyAccepted = 0
                isPenalty = 0 
                # print(index, des)

            if index == 32857 and season == 2015: #Kickoff after a penalty, this play is not a penalty
                isPenaltyAccepted = 0
                isPenalty = 0
                # print(index, des)
                continue #Another error 'PENALTY ON' in des, decided to just skip


            if index == 39519 and season == 2015: #Penalty on previous play
                isPenaltyAccepted = 0
                isPenalty = 0
                # print(index, des)
                continue #Another error 'PENALTY ON' in des, decided to just skip

            if index == 40437 and season == 2015: #Flag Thrown no penalty
                isPenaltyAccepted = 0
                isPenalty = 0
                # print(index, des)

            if index == 2320 and season == 2016: #Don't ask
                season_scores[gameCount][team_key['DET']] += 2
                continue

            if index == 6166 and season == 2016: #Attempted TO messing up sack yards
                des = des.split('ATTEMPTED')[0]
                # print(index, des)

            if index == 11828 and season == 2016: #Kessler 'pass' backwards out of back of endzone safety
                playType = 'FUMBLES'
                # print(index,des)

            if index == 14938 and season == 2016:
                playType = 'EXCEPTION'
                # print(index, des)

            if index == 19926 and season == 2016: #Enforced from messsing up description 1 penalty 6 yards
                game_stats[gameCount][36+team_key['BUF']] += 1
                game_stats[gameCount][38+team_key['BUF']] += 6
                # print(index, des)
                continue

            if index == 43281 and season == 2016: #Made as exception, but it isn't
                playType = 'TWO-POINT CONVERSION'


            if type(des) != str: #If we don't have a description, nothing happen and skip this row
                continue

             # (' PASS ' in des or ' SPIKED ' in des) game_stats[gameCount][6+team_key['BUF']],game_stats[gameCount][8+team_key['BUF']]


            if ' REVERSED' in des:
                des = des.split(' REVERSED')[1]
                if ' TOUCHDOWN' not in des:
                    isTouchdown = 0
                if ' FUMBLES' not in des:
                    isFumble = 0
                if ' INTERCEPTED' not in des:
                    isInterception = 0

            if ' NO PLAY' in des:
                des = des[:des.index(' NO PLAY')]

            if isFumble and ' FUMBLES' not in des:
                isFumble = 0

            if 'MUFFS' in des:
                isFumble = 1

            if (playType == 'FUMBLES' and isFumble and 'ABORTED' not in des) or (playType == 'EXCEPTION' and ' FOR ' in des and ('YARDS' in des or 'NO GAIN' in des)):
                playType = 'RUSH'

            if 'DELAY OF GAME' in des or ' FALSE START' in des:
                isNoPlay = 1
                # if not isPenalty:
                #     print(index,des)

            if ' INTERCEPTED' in des:
                returnYards = yardsGained
                yardsGained = 0

            if 'ENFORCED' in des and ' TO BE ENFORCED' not in des and not isPenaltyAccepted:
                isPenaltyAccepted = 1

            if down == 4 and ' INTERCEPTED' in des:
                print(index,des)

            # if playType == 'PUNT' and 'PUNTS' not in des and 'BLOCKED' not in des and 'KICKS' not in des:
            #     playType = 'RUSH'

            # if gameCount == 155 and isPotentialRush(playType) and oTeam == 'STL':
            #     print(index, yardlineDirection, yardlineFixed, yardsGained, des, playType, isNoPlay, game_stats[gameCount][team_key['STL']],game_stats[gameCount][2+team_key['STL']],game_stats[gameCount][14+team_key['STL']])

            isTOFromFumble = isTurnoverFromFumble(isFumble,des,oTeam,dTeam)   

            isSafety = 0
            isExtraPoint = 0
            isFieldGoal = 0
            is2PC = 0 
            isDef2PC = 0
            inRedZone = 0

            ##RED ZONE, Not done
            # if yardline0to100 >= 80:
            #     if inRedZone == 0:
            #         game_stats[gameCount][42+team_key[oTeam]] += 1
            #     inRedZone = 1

            # print(gameCount)

            if 'SAFETY' in des and 'FOLLOWING THE SAFETY' not in des and isNoPlay: #Safety can occur with isNoPlay==1 if Holding in end zone, using the other parts of thisHappened()
                ##If safety truly occurred, defense team gets 2 points
                isSafety = 1
                season_scores[gameCount][team_key[dTeam]] += 2

           
            if 'PENALTY ON ' in des and ' ENFORCED' in des and ' OFFSETTING' not in des and ' TO BE ENFORCED' not in des: #Penalty Accepted, No stats reocrded for offsetting penalties
                tdes = des.split('PENALTY ON ')
                tdes2 = des.split('ENFORCED ')
                for i in range(len(tdes2)-1):
                    # print(index,des,tdes2,tdes2[i+1],tdes2[i+1][0],tdes2[i+1][-1])
                    if tdes2[i+1].split()[0] == 'AT' or tdes2[i+1].split()[0] == 'BETWEEN':
                        tdes3 = tdes2[i].split()
                        penYards = int(tdes3[len(tdes3)-2])
                        tdes4 = tdes2[i].split('PENALTY ON ')
                        penTeam = tdes4[-1].replace('.','-').replace(',','-').split('-')[0]
                # print(index,des,penTeam)

                        game_stats[gameCount][36+team_key[penTeam]] += 1
                        game_stats[gameCount][38+team_key[penTeam]] += penYards

            # if 'ENFORCED IN END ZONE' in des:
            #     print(penTeam, penYards, penType, index, des, down)

            if isNoPlay == 1: #Play didn't happen, ignore everything else
                continue

            if (' KICKS' in des or ' PUNTS' in des or 'BLOCKED' in des) and penType == 'ILLEGAL FORWARD PASS': #technicality with illegal forward pass penalty triggering an incompletion
                continue

            isAwkPenPlay = isAwkwardPenaltyPlay(isPenaltyAccepted, penType, isNoPlay, penTeam, oTeam)

            if playType == 'FUMBLES':
                game_stats[gameCount][team_key[oTeam]] += 1

            if playType == 'FUMBLES' and not isTOFromFumble and 'AND RECOVERS' in des: #meaning the yardage will be 0 unless same player recovers and gains yardage
                if isTouchdown:
                    yardsGained = 100 - yardline0to100
                else:
                    if ' TO ' in des:
                        hfYardLine = getHowFarYardLine(des, ' TO ', 1, oTeam, dTeam)
                    else:
                        hfYardLine = getHowFarYardLine(des, ' AT ', 1, oTeam, dTeam)
                    howFar = hfYardLine-yardline0to100
                    yardsGained = max(0,howFar) #official rules of an aborted play, aborter credited with a rush for no gain
                game_stats[gameCount][2+team_key[oTeam]] += yardsGained
        
            # if playType == 'FUMBLES' and gameCount == 155:
            #     print(index, yardlineDirection, yardlineFixed, des, yardsGained)

            elif (' FUMBLES ' in des and (playType == 'RUSH' or playType == 'QB KNEEL' or playType == 'SCRAMBLE')) or (playType == 'PUNT' and ' PUNTS ' not in des and ' BLOCKED ' not in des and ' KICKS ' not in des and 'ABORTED' not in des):
                
                tdes = des.split(' FOR ')
                howFar = getHowFarYards(des, ' FOR ', 1)
                if 'AND RECOVERS' in des and len(tdes) > 2: #Rare scenario where runner recovers their own fumble and gains yardage
                    if tdes[2][:tdes[2].index(' ')] != 'NO': #No gain
                        howFar += int(tdes[2][:tdes[2].index(' ')])
                yardsGained = howFar

                if isFumble and 'TOUCHBACK' not in des:
                    hfYardLine = getHowFarYardLine(des, ' AT ',1, oTeam, dTeam)
                    howFar = hfYardLine-yardline0to100
                    yardsGained = min(howFar, yardsGained)

                if isAwkPenPlay:
                    # print(index,des)
                    hfYardLine = getHowFarYardLine(des, 'ENFORCED AT ', 1, oTeam, dTeam)
                    yardsGained = hfYardLine-yardline0to100
               
                game_stats[gameCount][team_key[oTeam]] += 1
                game_stats[gameCount][2+team_key[oTeam]] += yardsGained

                # if 'SMITH' in des and oTeam == 'KC':
                #     print(index, yardlineDirection, yardlineFixed, yardsGained, des, bool(isTOFromFumble), playType)
            elif ' FUMBLES' not in des and (playType == 'RUSH' or playType == 'QB KNEEL' or playType == 'SCRAMBLE'):
                yardsGained = getHowFarYards(des, ' FOR ', 1)
                if isAwkPenPlay:
                    # print(index,des)
                    hfYardLine = getHowFarYardLine(des, 'ENFORCED AT ', 1, oTeam, dTeam)
                    yardsGained = hfYardLine-yardline0to100

                lateralYards = checkLateral(index, des, season)
                yardsGained += lateralYards

                game_stats[gameCount][team_key[oTeam]] += 1
                game_stats[gameCount][2+team_key[oTeam]] += yardsGained

            elif ' SACKED' in des and playType != 'TWO-POINT CONVERSION':
                if isSafety:
                    yardsGained = 0 - yardline0to100
                    # print(game_id, index, yardlineDirection, yardlineFixed, yardsGained, des, bool(isTOFromFumble))
                elif 'OUT OF BOUNDS' in des or 'ABORTED' in des: #covers safeties too
                    yardsGained = getHowFarYards(des, ' FOR ', 1)
                elif isFumble and not isTOFromFumble:
                    if ' TO ' not in des:
                        hfYardLine = getHowFarYardLine(des, ' AT ', 2, oTeam, dTeam)
                        if down == 4:
                            hfYardLineTest = getHowFarYardLine(des, ' AT ', 1, oTeam, dTeam)
                            hfYardLine = min(hfYardLine,hfYardLineTest)
                    else:
                        hfYardLine = getHowFarYardLine(des, ' TO ', 1, oTeam, dTeam)
                    howFar = hfYardLine-yardline0to100
                    yardsGained = min(0,howFar)
                    # print(game_id, index, yardlineDirection, yardlineFixed, yardsGained, des, bool(isTOFromFumble))
                elif isTOFromFumble:
                    hfYardLine = getHowFarYardLine(des, ' AT ', 2, oTeam, dTeam)
                    howFar = hfYardLine-yardline0to100
                    yardsGained = min(0,howFar)
                else:
                    yardsGained = getHowFarYards(des, ' FOR ', 1)

                # if gameCount == 6:
                #     print(game_id, index, yardlineDirection, yardlineFixed, yardsGained, des, bool(isTOFromFumble))
                
                game_stats[gameCount][18+team_key[oTeam]] += 1
                game_stats[gameCount][20+team_key[oTeam]] += yardsGained
            
            elif playType == 'CLOCK STOP':
                game_stats[gameCount][8+team_key[oTeam]] += 1
            
            elif ' PASS ' in des and playType != 'TWO-POINT CONVERSION' and playType != 'EXTRA POINT' and playType != 'FUMBLES':
                tdes = des[des.index(' PASS '):]
                game_stats[gameCount][8+team_key[oTeam]] += 1
                if ' PASS INCOMPLETE' in tdes or ' INTERCEPTED' in tdes:
                    yardsGained = 0
                else:
                    game_stats[gameCount][6+team_key[oTeam]] += 1
                    yardsGained = getHowFarYards(des, ' FOR ', 1)
                    # if gameCount == 1 and oTeam == 'CHI':
                    #     print(index, des, yardsGained, game_stats[gameCount][14+team_key[oTeam]])
                    if ' FUMBLES' in tdes and ' TOUCHBACK' not in tdes: #if touchback, clearly yardsGained is less
                        hfYardLine = getHowFarYardLine(des, ' AT ', 1, oTeam, dTeam)
                        howFar = hfYardLine-yardline0to100
                        if 'AND RECOVERS' in tdes:
                            yardsGained = howFar
                            # print(index, des, yardsGained)
                        else:
                            yardsGained = min(yardsGained, howFar)
                    else:
                        lateralYards = checkLateral(index, des, season)
                        yardsGained += lateralYards
                if isAwkPenPlay:
                    # print(index,des)
                    hfYardLine = getHowFarYardLine(tdes, 'ENFORCED AT ', 1, oTeam,dTeam)
                    yardsGained = hfYardLine-yardline0to100

                # if gameCount == 1 and oTeam == 'CHI':
                #         print(index, des, yardsGained, game_stats[gameCount][14+team_key[oTeam]])
                
                game_stats[gameCount][14+team_key[oTeam]] += yardsGained
            
            isTOOnDowns = isTurnoverOnDowns(down, yardsGained, yardsToGo, isInterception, isTOFromFumble, isSafety, ' PUNTS ' in des, playType)
            
            if isTOOnDowns:
                game_stats[gameCount][28+team_key[oTeam]] += 1
            # if 'MUFFS' in des:
            #     print(index,des,isTOFromFumble)
                # print(game_id,index, down, yardsGained, yardsToGo,des)

            #3rd Down Conversion
            if is3rdDownAttempt(down, playType, isNoPlay, isAwkPenPlay):
                game_stats[gameCount][24+team_key[oTeam]] += 1
                if isDownConversion(yardsGained,yardsToGo,isTOFromFumble):
                    game_stats[gameCount][22+team_key[oTeam]] += 1

            if is4thDownAttempt(down, playType, isNoPlay, isAwkPenPlay):


            ##FIRST DOWNS- Not Working
            # if isDownConversion(yardsGained,yardsToGo) or (isPenaltyAccepted and penTeam == dTeam):
            #     if gameCount == 0:
            #         print(index,des)
            #     game_stats[gameCount][28+team_key[oTeam]] += 1

            # continue 

            # if ' LATERAL TO ' in des and 'INTERCEPTED' not in des and (isPotentialPass(playType) or isPotentialRush(playType)):
            #     print(game_id, index, des, playType, yardsGained)

            ##SCORING

            if ' INTERCEPTED ' in des or ' PUNTS ' in des or ' KICKS ' in des: 
            #If we are punting or on an interception, the other team becomes the "offense" technically speaking
                if ' INTERCEPTED ' in des and playType != 'TWO-POINT CONVERSION':
                    game_stats[gameCount][32+team_key[oTeam]] += 1
                temp = oTeam
                oTeam = dTeam
                dTeam = temp

            if 'BLOCKED' in des: #Blocked kick or punt, find out who recovered the block and adjust teams accordingly
                oTeam,dTeam = blockedRecoverer(des,oTeam,dTeam,down)

            if isFumble == 1:
                if ' OUT OF BOUNDS ' in des and 'TOUCHBACK' in des and playType != 'TWO-POINT CONVERSION':
                    game_stats[gameCount][30+team_key[oTeam]] += 1 
                if ' RECOVERED BY ' in des:
                    tdes = des.split(' RECOVERED BY ') #So I can check each time with the most recent revocery
                    for i in range(len(tdes)-1):
                        recoverTeam = tdes[i+1].split('-')[0]
                        if recoverTeam == dTeam:
                            if playType != 'TWO-POINT CONVERSION':  
                                game_stats[gameCount][30+team_key[oTeam]] += 1 
                            temp = oTeam #swap offense and defense
                            oTeam = dTeam
                            dTeam = temp

            # continue

            if 'NULLIFIED' in des and 'ENFORCED IN END ZONE,' not in des:
                # print(index,des, 'ENFORCED IN END ZONE' in des)
                continue

            if 'SAFETY' in des and 'FOLLOWING THE SAFETY' not in des: #Safety can occur with isNoPlay==1 if Holding in end zone, using the other parts of thisHappened()
                ##If safety truly occurred, defense team gets 2 points
                isSafety = 1
                season_scores[gameCount][team_key[dTeam]] += 2

            if isTouchdown==1: #If touchdown truly occurred, offense team gets 6 points
                season_scores[gameCount][team_key[oTeam]] += 6
                # if inRedZone == 1:
                #     game_stats[gameCount][40+team_key[oTeam]]
                
            if 'EXTRA POINT IS GOOD' in des: #If XP truly occurred, offense team gets 1 point
                isExtraPoint = 1
                season_scores[gameCount][team_key[oTeam]] += 1
                
            if 'FIELD GOAL IS GOOD' in des: #If FG truly occurred, offense team gets 3 points
                isFieldGoal = 1
                season_scores[gameCount][team_key[oTeam]] += 3
                
            if isTwoPointConversionSuccessful == 1: #If 2PC truly occurred, offense team gets 2 points
                is2PC = 1
                season_scores[gameCount][team_key[oTeam]] += 2
                
            if 'DEFENSIVE TWO-POINT ATTEMPT' in des and 'SUCCEEDS' in des:
                isDef2PC = 1
                season_scores[gameCount][team_key[oTeam]] += 2

            # if gameCount == 16 and isScore(isTouchdown, isSafety, isExtraPoint, isFieldGoal, is2PC, isDef2PC):
            #     print(index,des, season_scores[gameCount][0], season_scores[gameCount][1])


        prevGameStats = computePrevGameStats(last_game_id,team1,team2,season_scores,team_key,gameCount) 
        prev_game_stats.append(prevGameStats)
        updateTeamRecords(team1,team2,season_scores,team_key,gameCount,team_records, teams)

        checkMissingGames(gameCount, pbp, game_ids)

        for key in teams:
            wins = team_records[teams[key]][0]
            losses = team_records[teams[key]][1]
            print(key, '%i-%i' % (wins,losses))
        
        #0: rushes
        #2: rush yards
        #4: YPC
        #6: Pass Completions
        #8: Pass Attempts
        #10: Comp %
        #12: Y/A
        #14: Passing Yards
        #16: Total Yards
        #18: Sacks
        #20: Sack Yardage
        #22: 3rd Down Conversion
        #24: 3rd Down Attempts
        #26: 3rd Down Conversion Rate
        #28: Turnover On Downs
        #30: TO's from fumble
        #32: Interceptions
        #34: Total TO's
        #36: Penalties
        #38: Penalty Yards
        ###NOT FINISHED WITH BOTTOM
        #40: Red Zone Conversion
        #42: Red Zone Attempts
        #44: Red Zone Conversion Rate
        
        numpy_prev_game_stats = np.asarray(prev_game_stats)
        truePerGameStats = np.concatenate((numpy_prev_game_stats,game_stats),axis=1)

        print(truePerGameStats[:16])

        perGamedf = pd.DataFrame(truePerGameStats, index = gameStatsIndex, columns=gameStatsCols)
        
        if gameSeason == 2015:
            perGamedf.to_csv('PerGameStatistics2015.csv', index = False)
        elif gameSeason == 2016:
            perGamedf.to_csv('PerGameStatistics2016.csv', index = False)
        elif gameSeason == 2017:
            perGamedf.to_csv('PerGameStatistics2017.csv', index = False)

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

def getHowFarYards(des, whatToSplitOn, whatPiece):
    tdes = des.split(whatToSplitOn)
    howFar = tdes[whatPiece].replace('.',' ').replace(',',' ').split()
    if howFar[0] == 'NO' and howFar[1] == 'GAIN': #No gain
        howFar = 0
    else:
        howFar = howFar[0] #The yards
    try:
        howFar = int(howFar) #If it works, good, else, I'm in the wrong spot, go further down the description
    except:
        return getHowFarYards(des, whatToSplitOn, whatPiece+1)
    return howFar

def getHowFarYardLine(des, whatToSplitOn, whatPiece, oTeam, dTeam):
    tdes = des.split(whatToSplitOn)
    hfYardLine = tdes[whatPiece][:6].replace('.',' ').replace(',',' ').split() #at worst BUF 28, for example, six chars
    if hfYardLine[0] == dTeam: #adjusting for opponents yard line
        hfYardLine[1]=100-int(hfYardLine[1]) 
    if hfYardLine[0][:2] != '50': #Midfield, no team name
        if hfYardLine[0] != oTeam and hfYardLine[0] != dTeam:
            return getHowFarYardLine(des, whatToSplitOn, whatPiece+1, oTeam, dTeam)
        hfYardLine = hfYardLine[1]
    else:
        hfYardLine = hfYardLine[0]
    hfYardLine = int(hfYardLine)
    return hfYardLine


'''E.g Holding enforced later in the run, leading to a 1st&7 or something'''
def isAwkwardPenaltyPlay(isPenaltyAccepted, penType, isNoPlay, penTeam, oTeam):
    return isPenaltyAccepted and isPotentialKeyOffensivePenalty(penType) and not isNoPlay and penTeam == oTeam

'''Used for troubleshooting, to see if I was correctly counting each game'''
def checkMissingGames(gameCount, pbp, game_ids):           
    print('gameCount ', gameCount)
    uniqueGames = len(pbp['GameId'].unique())
    print('uniqueGames', uniqueGames)
    print(len(set(game_ids)), len(game_ids), uniqueGames)
    print(list(set(pbp['GameId'].unique())-set(game_ids))) #looking for missing game ids
    print ([item for item, count in Counter(game_ids).items() if count > 1]) #looking for duplicate game ids

def checkLateral(index, des, season):
    lateralYards = 0
    if index == 34456 and season == 2015: #Bad description problem, james white lateral.
        return lateralYards
    if index == 18414 and season == 2017: #Bad description problem, Russell wilson lateral (probably like a pitch).
        return lateralYards
    if index == 27231 and season == 2017: #Bad description problem, Brees threw backwards pass/lateral.
        return lateralYards
    if index == 31017 and season == 2015: #bad description, pass back used instead of lateral
        return -7
    if ' LATERAL TO ' in des:
        tdes = des.split(' LATERAL TO ')
        for i in range(1,len(tdes)):
            lateralYards += getHowFarYards(tdes[i], ' FOR ', 1)
    return lateralYards

def is3rdDownAttempt(down, playType, isNoPlay, isAwkPenPlay):
    return not isNoPlay and down == 3 and playType != 'FIELD GOAL' and not isAwkPenPlay

def isDownConversion(yardsGained, yardsToGo, isTOFromFumble):
    return yardsGained >= yardsToGo and yardsToGo > 0 and not isTOFromFumble

def isPotentialKeyOffensivePenalty(penType):
    return penType == 'OFFENSIVE HOLDING' or penType == 'TRIPPING' or penType == 'ILLEGAL BLOCK ABOVE THE WAIST'

def isPotentialRush(playType):
    return playType == 'RUSH' or playType == 'QB KNEEL' or playType == 'FUMBLES' or playType == 'SCRAMBLE'

def isPotentialPass(playType):
    return playType == 'PASS' or playType == 'CLOCK STOP'

def isScore(isTouchdown, isSafety, isExtraPoint, isFieldGoal, is2PC, isDef2PC):
    return isTouchdown or isSafety or isExtraPoint or isFieldGoal or is2PC or isDef2PC

def isTurnover(isTOOnDowns, isTOFromFumble, isInterception):
    return isTOOnDowns or isTOFromFumble or isInterception

'''Checks if there is a turnover on downs.'''
def isTurnoverOnDowns(down, yardsGained, yardsToGo, isInterception, isTOFromFumble, isSafety, isActualPunt, playType):
    return down == 4 and yardsGained < yardsToGo and not isInterception and not isTOFromFumble and not isSafety and not isActualPunt and playType != 'FIELD GOAL'

'''isFumble accounts for fumbles recovered by the own team, this stat is more helpful to know'''
def isTurnoverFromFumble(fum,des,oTeam,dTeam):
    if not fum:
        return False
    if 'TOUCHBACK' in des:
        return True 
    if ' INTERCEPTED ' in des or ' PUNTS' in des or ' KICKS' in des:
        temp = oTeam
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
    elif 'DEFENSIVE TWO-POINT ATTEMPT' in des:
        return dTeam,oTeam
    else:
        return oTeam,dTeam

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
    elif team2Score > team1Score:
        team_records[teams[team1]][1] += 1
        team_records[teams[team2]][0] += 1
    else:
        # ties, not accounted for currently
        print(gameCount)

'''Fixing problems with missing data in the csv, hardcoded'''
def fixProblems(game_id, gameCount, season,season_scores, team_key):
    problem_count=0
    problem_count+=1
    # print(team_key)
    if gameCount == 62 and season == 2015:
        season_scores[62][team_key['DET']] +=1
    elif gameCount == 112 and season == 2015:
         season_scores[112][team_key['NYG']] += 1
    elif gameCount == 179 and season == 2015:
        season_scores[179][team_key['MIA']] += 2
    # print('Problem: '+str(problem_count)+ ' Fixed. New Score- DET: '+str(int(season_scores[62][1]))+' SEA: '+str(int(season_scores[62][0])))
    problem_count+=1
    # print('Problem: '+str(problem_count)+ ' Fixed in code, removed isTouchdown from index 12528. New score correct in code.')
    problem_count+=1
    # print('Problem: '+str(problem_count)+ ' Fixed in code, changed dTeam from JAX to JAC for 2015. New score correct in code.')
    problem_count+=1
    # print('Problem: '+str(problem_count)+ ' Fixed in code, changed dTeam from LA to JAC for STL. New score correct in code.')
    problem_count+=1
   
    # print('Problem: '+str(problem_count)+ ' Fixed. New Score- NYG: '+str(int(season_scores[112][0]))+' NO: '+str(int(season_scores[112][1])))
    problem_count+=1
    
    # print('Problem: '+str(problem_count)+ ' Fixed. New Score- BAL: '+str(int(season_scores[179][0]))+' MIA: '+str(int(season_scores[179][1])))
    problem_count+=1
    # print('Problem: '+str(problem_count)+ ' Fixed in code, removed isTouchdown from index 36932. New score correct in code.')
            

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