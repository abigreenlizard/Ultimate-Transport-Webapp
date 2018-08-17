from rest_api.models import Modelstops

import os
import pickle
import pandas as pd
import numpy as np
import math
import sklearn
from rest_api.models import Composite 
from functools import reduce

class NNModel:

    current_file_path = __file__
    current_file_dir = os.path.dirname(__file__)

    def __init__(self, route, direction, startStop, finishStop, stops, rain):
        self.route = route
        self.direction = direction
        self.startStop = startStop
        self.finishStop = finishStop
        self.stops = stops
        self.dayArray = ['Friday', 'Monday', 'Saturday', 'Sunday','Thursday', 'Tuesday', 'Wednesday']
        self.rainOptions = ['Precipitation_Moderate','Precipitation_None', 'Precipitation_Slight']
        self.timeIntervals = ['day_Friday', 'day_Monday', 'day_Saturday','day_Sunday', 'day_Thursday','day_Tuesday', 'day_Wednesday','time_interval_midnight-1am', 'time_interval_1-2am','time_interval_2-3am', 'time_interval_3-4am', 'time_interval_4-5am','time_interval_5-6am', 'time_interval_6-7am','time_interval_7-8am','time_interval_8-9am', 'time_interval_9-10am', 'time_interval_10-11am','time_interval_11-12midday', 'time_interval_12-1pm','time_interval_1-2pm', 'time_interval_2-3pm', 'time_interval_3-4pm','time_interval_4-5pm', 'time_interval_5-6pm','time_interval_6-7pm','time_interval_7-8pm', 'time_interval_8-9pm', 'time_interval_9-10pm','time_interval_10-11pm']
        
    def parseRequest(self, route, direction):
        parseDir = lambda x: '1' if x == 'I' else '2'
        key = "bus{}_d{}.pkl".format(route, parseDir(direction))
        model_path = os.path.join(NNModel.current_file_dir, "objects/picklefiles/{}".format(key))
        print(key)
        return model_path

    # def createStopArray(self, route, direction, startStop, finishStop, numStopsInJourney, numStopsInRoute, df = None ):
    def createStopDf(self):
        
        stopsInJourney = [i for i in self.stops if 
            (i['sequence_number'] >= self.startStop['sequence_number'])
            or (i['sequence_number'] <= self.finishStop['sequence_number'])]
        # stopsInJourney = []
        # for i in self.stops:
        #     if i['sequence_number'] >= self.startStop['sequence_number'] or i['sequence_number'] <= self.finishStop['sequence_number']:
        #         stopsInJourney.append(i)
        # print("JOURNEY", stopsInJourney)
        stopsInJourney = sorted(stopsInJourney, key = lambda x: x['sequence_number'])
        self.stopsInJourney = stopsInJourney

        # columnsList = [i for i in range(len(self.stops) * 2)]
        convertDir = lambda x: 2 if x == 'I' else 1
        stopsColsList = sorted(Modelstops.objects
                .filter(route=self.route)
                .filter(direction=convertDir(self.direction))
                .values()[0]['stopids']
                .split(' ')
                , key=lambda x: int(x)
            )
        
        print(stopsColsList)
        # for i in stopsColsList:
        #     print(i)

                
        # startColsList = ["start_stoppointid_{}".format(i['stop_id']) for i in self.stops]
        # endColsList = ['end_point_{}'.format(i['stop_id']) for i in self.stops]
        # startColsList.extend(endColsList)
        startColsList = ["start_stoppointid_{}".format(i) for i in stopsColsList]
        endColsList = ["end_point_{}".format(i) for i in stopsColsList]
        startColsList.extend(endColsList)
        df = pd.DataFrame(columns=startColsList)
        print("df created")
        print(df.head())
        errorCount = 0
        stopsColsList = [int(i) for i in stopsColsList]
        count = 0
        finalStops = []

        for i in range(len(self.stopsInJourney) - 1):
            item = self.stopsInJourney[i]
            nextItem = self.stopsInJourney[i + 1]
            # print(item)
        
            startStopId = next((stop['stop_id'] for (index, stop) in enumerate(self.stops) if stop["sequence_number"] == item['sequence_number']), None)
            finishStopId = next((stop['stop_id'] for (index, stop) in enumerate(self.stops) if stop["sequence_number"] == nextItem['sequence_number']), None)
            # print("GOT STOP INDEXES")
            # print(startStopId, finishStopId)
            # print(type(startStopId), type(finishStopId))
            try:
                startIndex = stopsColsList.index(int(startStopId))
                currentStop = next((stop for (index, stop) in enumerate(self.stops) if stop["stop_id"] == startStopId), None)
                finalStops.append(currentStop)
            except ValueError as e:
                print(e)
                errorCount += 1
            try:
                finishIndex = stopsColsList.index(int(finishStopId))
            except ValueError as e:
                print(e)
                errorCount += 1
                continue
            # print("ERRORS", errorCount)
            # print(startIndex, finishIndex)
            # print(type(startIndex), type(finishIndex))

            count += 1
            row = [0 for i in range(len(stopsColsList) * 2)]
            # row = [0 for i in range(len(stopsColsList) * 2)]
            row[startIndex] = 1
            # print(row)
            row[len(stopsColsList) + finishIndex] = 1
            # print(row)
            df.loc[i] = row

        print("ERRORS", errorCount)
        self.stopsDf = df
        self.numStops = count
        print(count)
        print(df.shape)
        print("STOPS DATA")
        print(df)
        df = df.reset_index()
        print(df)
        # finalStops = sorted(finalStops, key = lambda x: x['sequence_number'])
        self.finalStops = finalStops
        print(finalStops)
        return df

    def createTimeDf(self, hour, day):
        # 7 days + 23 hour ranges
        print(hour)
        columnsList = [i for i in range(30)]
        df = pd.DataFrame(columns=columnsList)
        timeRow = [0 for i in range(23)]
        dayRow = [0 for i in range(7)]
        dayIndex = self.dayArray.index(day)
        dayRow[dayIndex] = 1
        timeRow[hour - 1] = 1
        dayRow.extend(i for i in timeRow)
        self.timeRow = dayRow
        return dayRow
      
    def createRainArray (self, rain):
        rain_arr = [0 for i in range(len(self.rainOptions))]
        rain_arr[self.rainOptions.index(rain)]=1
        return rain_arr

    def calculateDistances(self):
        distances = []
        radius_earth = 6371
        print("stops length", len(self.stopsInJourney))
        for i in range(len(self.finalStops) - 1):
            item = self.finalStops[i]
            nextItem = self.finalStops[i + 1]
            theta1 = np.deg2rad(float(item['stop_lon']))
            theta2 = np.deg2rad(float(nextItem['stop_lon']))
            phi1 = np.deg2rad(90 - float(item['stop_lat']))
            phi2 = np.deg2rad(90 - float(nextItem['stop_lat']))
            if item['stop_lon'] =='0.0' or nextItem['stop_lon'] =='0.0':
                distance= 0 
            else:
                distance = math.acos(math.sin(phi1) * math.sin(phi2) * math.cos(
                theta1 - theta2) + math.cos(phi1) * math.cos(phi2)) * radius_earth
            # print(distance)
            distances.append(distance)
        print(distances)
        distances.append(0)
        return distances
            

    def makePrediction(self, model_path, df):
        '''Returns a prediction for journey time
        
        Try/catch block to adjust dataframe size if new stops were added'''
        nn_model = pickle.load(open(model_path, "rb"))
        try:
            result = nn_model.predict(df)
            print(result)
            sum = reduce(lambda x, acc: x+acc, result)
            print(sum / 60)
        except ValueError as e:
            dimesnsions = [int(s) for s in str(e).split() if s.isdigit()]
            print("DIMENSIONS", dimesnsions)
            our_df_size, model_df_size  = dimesnsions[0] , dimesnsions[1]
            print('our_df_size\t', our_df_size, 'model_df_size\t', model_df_size)
            if our_df_size > model_df_size:
                num_cols_to_remove = our_df_size - model_df_size
                df = df.iloc[:, :-(num_cols_to_remove)]
            else:
                num_cols_to_add =  model_df_size - our_df_size 
                num_rows_our_df = df.shape[0]
                cols_zeros =pd.DataFrame(np.zeros((num_rows_our_df, num_cols_to_add )))
                df = pd.concat([df,cols_zeros], axis=1)
                
                
            result = nn_model.predict(df)
            sum = reduce(lambda x, acc: x+acc, result)
            time = abs( sum/60)
            print (time)
            return time
                
                
        # startCols = createStopArray()
        # finishCols = createStopArray()

        # totalSeconds = result[0] * numStops
        # seconds = int(round((totalSeconds % 60), 0))
        # minutes = int(totalSeconds // 60)
        # result = '{} minutes, {} seconds'.format(abs(minutes), abs(seconds))
        # print(result)
        # return [result]
        # multiply this num by the number of points bewteen start and destination - then divide by 60 for the time
        
