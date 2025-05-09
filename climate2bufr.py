#!/usr/bin/env python3

"""
climate2bufr.py is the main program which converts climate data to bufr message (edition 4).
Run program by command: python3 climate2bufr.py name_of_the_climate_file.dat
"""
import sys
import traceback
from eccodes import *
import subset_arrays as subA
import separate_keys_and_values

VERBOSE = 1

def print_error_message(error_code, text):
    """
    This function prints out error message and stops program.
        If error_code = 0: Error is with naming the bufr file according to the first row of
        climate data file.
        If error_code = 1: Error is with the data structure in climate file.
        Function gets argument text, which adds information to the error text.
    """
    print('\nError in climate data:\n')
    if error_code == 0:
        print('Error with naming the bufr file.')
        print('The first row of climate data shoud be: ')
        print('FILENAME: /path/to/file/TTAAII_year-month-day_hour:minute_something.dat')
        print(text)
    elif error_code == 1:
        print('Row in climate data with n data values should be: ')
        print('keyname1=value1;keyname2=value2;keyname3=value3;...;keynamen=valuen*')
        print(text)
    sys.exit(1)

def check_name(data):
    """
    This function check if the first row in climate data (data) is written correctly.
    """
    try:
        test = data[0]
    except IndexError:
        print_error_message(0, 'climate file is empty!\n')

    if 'FILENAME: ' not in data[0]:
        print_error_message(0, '"Filename:  " is missing!\n')
    elif '.dat' not in data[0]:
        print_error_message(0, '".dat" is missing!\n')
    elif '_' not in data[0]:
        print_error_message(0, '"_" are missing!\n')

    test = data[0].split('/')
    test = test[len(test) - 1].split('_')
    if len(test) < 4:
        print_error_message(0, 'Amount of "_" is less than 3!\n')
    elif '-' not in test[1]:
        print_error_message(0, '"-" or "_" in wrong place!\n')
    elif ':' not in test[2]:
        print_error_message(0, '":" not in right place!\n')

    day = test[1].split('-')
    time = test[2].split(':')

    if len(day) != 3:
        print_error_message(0, '"year-month-day" is wrong!\n')
    elif len(time) !=2:
        print_error_message(0, '"hour:minute" is wrong!\n')
    try:
        int(day[0])
        int(day[1])
        int(day[2])
        int(time[0])
        int(time[1])
    except ValueError:
        print_error_message(0, 'year, month, day, hour and minute should be integers!\n')

    return data

def check_data(data):
    """
    This function checks if the data section in climate file is written correctly.
    Argument data is the data in climate file.
    """
    try:
        data[1]
    except IndexError:
        print_error_message(1, 'climate file seems not to have any data.\n')

    for i in range(1, len(data)):
        if ';' not in data[i] or '=' not in data[i] or '*' not in data[i]:
            message = 'climate file has bad data in row ' + str(i) + '.\n'
            print_error_message(1, message)
    for i in range(1, len(data)):
        if ';=' in data[i] or '=;' in data[i]:
            message = 'climate file has bad data in row ' + str(i) + '.\n'
            print_error_message(1, message)
        elif ';*' in data[i] or '*;' in data[i]:
            message = 'climate file has bad data in row ' + str(i) + '.\n'
            print_error_message(1, message)
        elif '=*' in data[i] or '*=' in data[i]:
            message = 'climate file has bad data in row ' + str(i) + '.\n'
            print_error_message(1, message)

    return data

def read_filename(row):
    """
    Separates the 1st row (row) of data to get the parts needed to name the output file.
        1. Splits the first row from ":" -> [some text, file path]
        2. Splits the path -> [path, to, the, file] and selects the last part (file).
        3. Splits filename from, "_" and selects the right parts to name the file.
        4. The second value (year-month-day) is split from "-" and the day is selected.
        5. The 3rd value (hour:minute) is also split from ":".
    """
    # 1.
    first_row = row.split(': ')

    # 2.
    filepath = first_row[1].split('/')
    for i in range (0, len(filepath)):
        if i == len(filepath) - 1:
            filename = filepath[i]

    # 3.
    parts = filename.split('_')

    # 4.
    output = []
    for i in range (0, len(parts)):
        if i in (0, 2):
            output.append(parts[i])
        elif i == 1:
            day = parts[i].split('-')
            output.append(day[2])

    # 5.
    time = output[2].split(':')
    output[2] = time[0]
    output.append(time[1])
    return output

def read_climate(rows):
    """
    Separates climate data to key and value arrays:
        1. Splits rows from ";", -> [ [key=value], [key=value], ...]
        2. Splits: [key=value] in each row to [key, value] and the last value from "*".
    """
    # 1.
    split_rows = []
    for row in rows:
        split_rows.append(row.split(';'))

    number_of_rows =  len(split_rows)

    # 2.
    rows_with_key_value_pairs = []
    for i in range(0, number_of_rows):
        key_value_array = []
        row = split_rows[i]
        number_of_arguments = len(row)
        for j in range(0, number_of_arguments):
            key_value_pair = row[j]
            split_key_value = key_value_pair.split('=')
            if j == number_of_arguments - 1:
                last_value = split_key_value[1]
                only_value = last_value.split('*')
                split_key_value[1] = only_value[0]
            key_value_array.append(split_key_value)
        rows_with_key_value_pairs.append(key_value_array)
    return rows_with_key_value_pairs

def message_encoding(input_file):
    """
    Main sends input file here.
    1. Reads lines from input_file and checks (check_name) if file's first row
    contains right parts for naming the output file. After that it checks (check_data)
    if the climate data in input_file contains right parts for fetching the data.
    2. Sends the first row of input file to read_filename to get the name for the
    output file. After that it checks if output has a right amount of values for naming
    the file.
    3. Calls read_climate to get keys and values from input file.
    4. Separates keys and values to their own arrays and makes subset array objects.
    Keys and values are separated by separate_keys_and_values module.
    Subset object has all the values from different subsets in the same array
    according to key-name.
    5. separate_keys_and_values module's longest_row function is used to choose the key
    row from keys_in_each_row, which has the biggest amount of key names.
    6. The bufr message sceleton is made from a sample (edition 4).
    7. Sends the bufr sceleton and subset_array to bufr_encode to fill the bufr message.
    8. Output filename is named by the parts from the first row of the data (output) and
    the name of the centre.
    9. Output file is opened, bufr message is written to it and output filename is
    returned to main function.
    """

    # 1.
    rows_in_input_file = input_file.readlines()
    rows_in_input_file = check_name(rows_in_input_file)
    rows_in_input_file = check_data(rows_in_input_file)

    # 2.
    output = read_filename(rows_in_input_file[0])
    if len(output) != 4:
        print_error_message(0, '\n')
    # 3.
    data_in = read_climate(rows_in_input_file[1:])

    # 4.
    keys_in_each_row = []
    sub_array = []

    for i in range(0,len(data_in[0])):
        sub_array.append([])

    for i in range(0, len(data_in)):
        keys_in_each_row.append(separate_keys_and_values.get_keys(data_in[i]))
        values = separate_keys_and_values.get_values(data_in[i])

        for j in range(0,len(values)):
            sub_array[j].append(values[j])

    # 5.
    longest = separate_keys_and_values.longest_row(keys_in_each_row)
    subset_array = subA.Subset(keys_in_each_row[longest], sub_array)

    # 6.
    bufr = codes_bufr_new_from_samples('BUFR4')

    # 7.
    try:
        bufr = bufr_encode(bufr, subset_array)
    except CodesInternalError as err:
        if VERBOSE:
            traceback.print_exc(file=sys.stderr)
        else:
            sys.stderr.write(err.msg + '\n')
        codes_release(bufr)
        sys.exit(1)

    # 8.
    centre = codes_get_string(bufr, 'bufrHeaderCentre')
    output_filename = output[0] + '_' + str(centre.upper()) + '_' + output[1] + output[2]
    output_filename = output_filename + output[3] + '.bufr'

    # 9.
    with open(output_filename, 'wb') as fout:
        codes_write(bufr, fout)
        fout.close()

    codes_release(bufr)
    return output_filename

def bufr_encode(ibufr, subs):
    """
    Encodes a bufr message (ibufr) by subset_array object (subs).
    Subser_array object is used to get all the values in each subset.
    """
    codes_set(ibufr, 'edition', 4)
    codes_set(ibufr, 'masterTableNumber', 0)
    codes_set(ibufr, 'bufrHeaderCentre', 86)
    codes_set(ibufr, 'bufrHeaderSubCentre', 0)
    codes_set(ibufr, 'updateSequenceNumber', 1)
    codes_set(ibufr, 'dataCategory', 0)
    codes_set(ibufr, 'internationalDataSubCategory', 0)
    codes_set(ibufr, 'dataSubCategory', 1)
    codes_set(ibufr, 'masterTablesVersionNumber', 35) # 14)
    codes_set(ibufr, 'localTablesVersionNumber', 0)
    codes_set(ibufr, 'observedData', 1)
    codes_set(ibufr, 'numberOfSubsets', subs.NSUB)
    codes_set(ibufr, 'compressedData', 0)
    codes_set(ibufr, 'typicalYear', max(set(subs.YYYY), key = subs.YYYY.count))
    codes_set(ibufr, 'typicalMonth', max(set(subs.MM), key = subs.MM.count))
    codes_set(ibufr, 'typicalDay', max(set(subs.DD), key = subs.DD.count))
    codes_set(ibufr, 'typicalHour', max(set(subs.HH24), key = subs.HH24.count))
    codes_set(ibufr, 'typicalMinute', max(set(subs.MI), key = subs.MI.count))
    codes_set(ibufr, 'typicalSecond', 0)
    # codes_set_array(ibufr, 'inputDelayedDescriptorReplicationFactor', subs.DEL)
    # codes_set(ibufr, 'unexpandedDescriptors', 307073)
    codes_set_array(ibufr, 'unexpandedDescriptors', [301150, 307073])

    # WIGOS identyfier:
    # 301150:
        # 001125: WIGOS identifier series
        # 001126: WIGOS issuer of identifier
        # 001127: WIGOS issue number
        # 001128: WIGOS local identifier (character)

    codes_set_array(ibufr, 'wigosIdentifierSeries', subs.WSI_IDS)
    codes_set_array(ibufr, 'wigosIssuerOfIdentifier', subs.WSI_IDI)
    codes_set_array(ibufr, 'wigosIssueNumber', subs.WSI_INR)

    for i in range(0, len(subs.WSI_LID)):
        key = '#'+str(i+1)+'#wigosLocalIdentifierCharacter'
        codes_set(ibufr, key, subs.WSI_LID[i])
        # codes_set_string_array, codes_get_string_array do not work

    # 307073 (Representation of CLIMAT data of the actual month and for monthly normals): 307071, 307072
    # 307071 Monthly values of a land station: (data of CLIMAT Sections 0, 1, 3 and 4)
        # 301090: 301004, 301011, 301012, 301021, 7030, 7031
            # 301004: 1001, 1002, 1015, 2001:
                #    block number, station number, station name, station type
    # Tasta loppuun ????
    codes_set_array(ibufr, 'blockNumber', subs.BLOCK_NUMBER)
    codes_set_array(ibufr, 'stationNumber', subs.STATION_NUMBER)
    # codes_set_array is not for string values: codes_set_string_array, codes_get_string_array
    for i in range(0, len(subs.STATION_NAME)):
        key = '#'+str(i+1)+'#stationOrSiteName'
        codes_set(ibufr, key, subs.STATION_NAME[i])

    codes_set_array(ibufr, 'stationType', subs.STATION_TYPE)

            # 301011: 4001, 4002, 4003: year, moth, day
            # 301012: 4004, 4005: hour, minute
                # Date <3 01 011> and time <3 01 012> shall be reported, i.e. year (0 04 001),
                # month (0 04 002), day (0 04 003) and hour (0 04 004), minute (0 04 005) of
                # beginning of the month for which the monthly values are reported. Day (0 04 003)
                # shall be set to 1 and both hour (0 04 004) and minute (0 04 005) shall be set to 0.
    # codes_set_array(ibufr, 'year', subs.YYYY) # REPORT_MONTH=2024-11-01
    # codes_set_array(ibufr, 'month', subs.MM)
    # scodes_set_array(ibufr, 'day', subs.DD) # aseta 1
    # codes_set_array(ibufr, 'hour', subs.HH24) # aseta 0
    codes_set_array(ibufr, 'minute', subs.MI) # Aseta 0

            # 301021: 5001, 6001: latitude, longitude
            # 7030: height of station ground above mean sea level
            # 7031: height of barometer above mean sea level
    codes_set_array(ibufr, 'latitude', subs.LAT)
    codes_set_array(ibufr, 'longitude', subs.LON)
    codes_set_array(ibufr, 'heightOfStationGroundAboveMeanSeaLevel', subs.ELSTAT)
    codes_set_array(ibufr, 'heightOfBarometerAboveMeanSeaLevel', subs.ELBARO)

    # 4074 Short time period or displacement (see Note 3) = UTC – LT
        #1#timePeriod
    # codes_set(ibufr, 'timePeriod', subs.TP) # -2
    # 4023 Time period or displacement Number of days in the month.
        #2#timePeriod
    # codes_set(ibufr, 'timePeriod', subs.TP) # NM

    # Monthly mean values of pressure, temperature, extreme temperatures and vapour pressure:
        # 8023 First-order statistics = 4 Mean value
            #1#firstOrderStatistics
                # This datum shall be set to 4 (mean value) to indicate that the following entries
                # represent mean values of the elements (pressure, pressure reduced to mean sea
                # level or geopotential height, temperature, extreme temperatures and vapour
                # pressure) averaged over the one-month period.
    # codes_set(ibufr, 'firstOrderStatistics', subs.FS) # 4

        # 10004 Pressure
            #1#nonCoordinatePressure
    # codes_set_array(ibufr, 'nonCoordinatePressure', subs.P_ST) #  S11_P
        # 10051 Pressure reduced to mean sea level
            #1#pressureReducedToMeanSeaLevel
    # codes_set_array(ibufr, 'pressureReducedToMeanSeaLevel', subs.P_SEA) # S12_P
                # Monthly data (with the exception of precipitation data) are recommended to be
                # reported for one-month period, corresponding to the local time (LT) month
                # [Handbook on CLIMAT and CLIMAT TEMP Reporting (WMO/TD-No.1188)]. In
                # that case, short time displacement (0 04 074) shall specify the difference
                # between UTC and LT (set to non-positive values in the eastern hemisphere, nonnegative values in the western hemisphere).
                # Time period (0 04 023) represents the number of days in the month for which the
                # data are reported, and shall be expressed as a positive value in days.
                # Note: A BUFR (or CREX) message shall contain reports for one specific month only. 

        # 7004 Pressure Standard level | Set to missing for lowland stations # miss
            #1#pressure
        # 10009 Geopotential height Standard level | Set to missing for lowland stations # miss
            #1#nonCoordinateGeopotentialHeight

        # 7032 Height of sensor above local ground (or deck of marine platform) (see Note 4)
            #1#heightOfSensorAboveLocalGroundOrDeckOfMarinePlatform
                # Height of sensor above local ground (0 07 032) for temperature and humidity
                # measurement shall be reported in metres (with precision in hundredths of a
                # metre).
                # This datum represents the actual height of temperature and humidity sensors
                # above ground at the point where the sensors are located
        # codes_set_array(ibufr, 'heightOfSensorAboveLocalGroundOrDeckOfMarinePlatform', subs.SENSOR) # ELTERM

        # 12101 Temperature/air temperature
            #1#airTemperature
        # codes_set_array(ibufr, 'airTemperature', subs.T) # S13_T
            # Monthly mean value of temperature shall be reported using 0 12 101
            # (Temperature/air temperature) in kelvin (with precision in hundredths of a kelvin)
            # Temperature data shall be reported with precision in hundredths
            # of a degree even if they are available with the accuracy in tenths of a degree.
            # Notes:
            # (2) Temperature t (in degrees Celsius) shall be converted into temperature T (in kelvin)
            # using equation: T = t + 273.15. 

        # 2051 Indicator to specify observing method for extreme temperatures
            #1#indicatorToSpecifyObservingMethodForExtremeTemperatures
                # This datum shall be set to 1 (maximum/minimum thermometers) or to 2
                # (automated instruments) or to 3 (thermograph) to indicate observing method for
                # extreme temperatures.
        # codes_set(ibufr, 'indicatorToSpecifyObservingMethodForExtremeTemperatures', subs.IND) # 1..3 laitetaan miss=15

        # 4051 Principal time of daily reading of maximum temperature
            #1#principalTimeOfDailyReadingOfMaximumTemperature
        # 12118 Maximum temperature at height specified, past 24 hours
            #1#maximumTemperatureAtHeightSpecifiedPast24Hours
            # codes_set(ibufr, 'principalTimeOfDailyReadingOfMaximumTemperature',?)
        # codes_set(ibufr, 'maximumTemperatureAtHeightSpecifiedPast24Hours', subs.TMAX) # S14_TX
                # The monthly mean value of maximum temperature shall be reported using 0 12 118
                # (Maximum temperature at height specified, past 24 hours). The height is specified by
                # the preceding entry 0 07 032. Principal time of daily reading of maximum
                # temperature (0 04 051) indicates the end of the 24-hour period to which the daily
                # maximum temperature refers

        # 4052 Principal time of daily reading of minimum temperature
            #1#principalTimeOfDailyReadingOfMinimumTemperature
        # 12119 Minimum temperature at height specified, past 24 hours
            #1#minimumTemperatureAtHeightSpecifiedPast24Hours
            # codes_set(ibufr, 'principalTimeOfDailyReadingOfMinimumTemperature',?)
        # codes_set(ibufr, 'minimumTemperatureAtHeightSpecifiedPast24Hours', subs.TMIN) # S14_TN
                # Samat ohjeet ku maksissa
            
        # 13004 Vapour pressure
            #1#vapourPressure
            # codes_set(ibufr, 'vapourPressure', subs.E) # 15_E
                # pascals (with precision in tens of pascals)

        # 8023 First-order statistics Set to missing
            #2#firstOrderStatistics
                # This datum shall be set to missing to indicate that the following entries do not
                # represent the monthly mean values.
            # codes_set(ibufr, 'firstOrderStatistics', subs.FS) # miss

        # 12151 Standard deviation of daily mean temperature
            #1#dailyMeanTemperatureStandardDeviation
            # codes_set(ibufr, 'dailyMeanTemperatureStandardDeviation', subs.TMEAN) # S13_ST
                # Standard deviation of daily mean temperature (0 12 151) shall be reported in
                # kelvin (with precision in hundredths of a kelvin);

        # 7032 Height of sensor above local ground (or deck of marine platform) Set to missing
            #2#heightOfSensorAboveLocalGroundOrDeckOfMarinePlatform # miss

        # 102005 Replicate 2 descriptors 5 times
        # 8050 Qualifier for number of missing values in calculation of statistic = 1 Pressure, = 2 Temperature, = 4 Vapour pressure, = 7 Maximum temperature, = 8 Minimum temperature
            #1..5#qualifierForNumberOfMissingValuesInCalculationOfStatistic
        # lista = [1, 2, 4, 7, 8]
        # codes_set_array(ibufr, 'qualifierForNumberOfMissingValuesInCalculationOfStatistic', subs.N_MISS)

        # 8020 Total number of missing entities (with respect to accumulation or average) Days
            #1..5#totalNumberOfMissingEntitiesWithRespectToAccumulationOrAverage
        #   [S18_MP, S18_MT, S19_ME, S18_MTX, S18_MTN]
        # codes_set(ibufr, 'totalNumberOfMissingEntitiesWithRespectToAccumulationOrAverage', subs.TOT_MISS)

                # Number of days in the month for which values are missing shall be reported using
                # Total number of missing entities (0 08 020) being preceded by Qualifier for
                # number of missing values in calculation of statistic (0 08 050) in each of the
                # required five replications (1 02 005).
                # Qualifier for number of missing values in calculation of statistic (0 08 050) is:
                # – Set to 1 (pressure) in the first replication;
                # – Set to 2 (temperature) in the second replication;
                # – Set to 4 (vapour pressure) in the third replication;
                # – Set to 7 (maximum temperature) in the fourth replication;
                # – Set to 8 (minimum temperature) in the fifth replication.
                # The number of days in the month for which values of the parameter are missing,
                # shall be reported using 0 08 020 in the corresponding replication.

    # Sunshine duration
        # 14032 Total sunshine
            #1#totalSunshine
        # 14033 Total sunshine
            #2#totalSunshine
        #codes_set(ibufr, 'totalSunshine', S17_S)
        #codes_set(ibufr, 'totalSunshine', S17_PS)
        # codes_set_array(ibufr, 'totalSunshine', subs.SUND)
                # The monthly values of total duration of sunshine shall be reported in hours using
                # Total sunshine (0 14 032) and the percentage of the normal that that value
                # represents shall be reported using Total sunshine (0 14 033). Any missing
                # element shall be reported as a missing value.
                # Notes:
                # (1) If the percentage of the normal is 1% or less but greater than 0, Total sunshine
                # 0 14 033 shall be set to 1.
                # (2) If the normal is zero hours, Total sunshine 0 14 033 shall be set to 510.
                # (3) If the normal is not defined, Total sunshine 0 14 033 shall be set to missing.
        # 8050 Qualifier for number of missing values in calculation of statistic = 6 Sunshine duration
            #6#qualifierForNumberOfMissingValuesInCalculationOfStatistic
            # lista = 6
        # codes_set(ibufr, 'qualifierForNumberOfMissingValuesInCalculationOfStatistic', subs.N_MISS)

        # 8020 Total number of missing entities (with respect to accumulation or average) Days
            #6#totalNumberOfMissingEntitiesWithRespectToAccumulationOrAverage
        # codes_set(ibufr, 'totalNumberOfMissingEntitiesWithRespectToAccumulationOrAverage', subs.TOT_MISS) #S19_MS
                # Number of days in the month for which sunshine data are missing shall be
                # reported using Total number of missing entities (0 08 020) being preceded by
                # Qualifier for number of missing values in calculation of statistic (0 08 050) set to 6
                # (sunshine duration).

    # Number of days of occurrence
        # 102018 Replicate 2 descriptors 18 times
        # 8052 Condition for which number of days of occurrence follows
            #1..18#conditionForWhichNumberOfDaysOfOccurrenceFollows
            # lista = [0,1,2,3,4,5,6,7,8,16,17,18,19,20,21,22,23,24]
        # codes_set_array(ibufr, 'conditionForWhichNumberOfDaysOfOccurrenceFollows', subs.CND)

        # 8022 Total number (with respect to accumulation or average) Days
            #1..18#totalNumberWithRespectToAccumulationOrAverage
            # lista = [S38_F10, S38_F20, S38_F30, S32_TX0,
            #  S30_T25, S30_T30, S31_T35, S31_T40, S32_TN0,
            #  S36_S00, S36_S01, S37_S10, S37_S50
            #  S39_V1, S39_V2, S39_V3, miss, miss]
        # codes_set_array(ibufr, 'totalNumberWithRespectToAccumulationOrAverage', subs.TNRA)
                # Number of days in the month with parameters beyond certain thresholds and with
                # thunderstorm and hail shall be reported using Total number (0 08 022) being
                # preceded by Condition for which number of days of occurrence follows (0 08 052)
                # in each of the required eighteen replications (1 02 018).
                # Condition for which number of days of occurrence follows (0 08 052) is:
                # – Set to 0 (mean wind speed over 10-minute period ≥ 10 m s–1);
                # – Set to 1 (mean wind speed over 10-minute period ≥ 20 m s–1);
                # – Set to 2 (mean wind speed over 10-minute period ≥ 30 m s–1);
                # – Set to 3 (maximum temperature < 273.15 K);                      T = t + 273.15. 
                # – Set to 4 (maximum temperature ≥ 298.15 K);
                # – Set to 5 (maximum temperature ≥ 303.15 K);
                # – Set to 6 (maximum temperature ≥ 308.15 K);
                # – Set to 7 (maximum temperature ≥ 313.15 K);
                # – Set to 8 (minimum temperature < 273.15 K);
                # – Set to 16 (snow depth > 0.00 m);
                # – Set to 17 (snow depth > 0.01 m);
                # – Set to 18 (snow depth > 0.10 m);
                # – Set to 19 (snow depth > 0.50 m);
                # – Set to 20 (horizontal visibility < 50 m);
                # – Set to 21 (horizontal visibility < 100 m);
                # – Set to 22 (horizontal visibility < 1 000 m);
                # – Set to 23 (occurrence of hail);
                # – Set to 24 (occurrence of thunderstorm) in the last replication.
                # The number of days in the month with parameters beyond the specified
                # thresholds and with thunderstorm and hail shall be reported using 0 08 022 in the
                # corresponding replication.
                # Note: Number of days in the month with horizontal visibility beyond the specified
                # thresholds is the number of days with visibility less than 50, 100 and 1 000 m,
                # respectively, irrespective of the duration of the period during which horizontal visibility
                # below the specified thresholds was observed or recorded.

    #####################################################################
    # Occurrence of extreme values of temperature and wind speed
    #######################################################################

        # 7032 Height of sensor above local ground (or deck of marine platform) (see Note 4)
            #3#heightOfSensorAboveLocalGroundOrDeckOfMarinePlatform
                # Height of sensor above local ground (0 07 032) for temperature measurement
                # shall be reported in metres (with precision in hundredths of a metre).
                # This datum represents the actual height of temperature sensor above ground at
                # the point where the sensor is located.
        # codes_set_array(ibufr, 'heightOfSensorAboveLocalGroundOrDeckOfMarinePlatform', subs.SENSOR) #  ELTERM
        # 8053 Day of occurrence qualifier = 0 On 1 day only, = 1 On 2 or more days
            #1#dayOfOccurrenceQualifier
            # codes_set(ibufr, 'dayOfOccurrenceQualifier', 0tai1) # 3 = miss

        # 4003 Day
            #2#day
        # codes_set(ibufr, 'day', subs.DD) # S40_YX
        # 12152 Highest daily mean temperature  #1#highestDailyMeanTemperature
                # The day on which the highest daily mean temperature occurred shall be reported
                # using Day (0 04 003). If the highest daily mean temperature occurred on only one
                # day, the preceding entry 0 08 053 (Day of occurrence qualifier) shall be set to 0.
                # If the highest daily mean temperature occurred on more than one day, the first
                # day shall be reported for 0 04 003 and the preceding entry 0 08 053 shall be set
                # to 1.
    codes_set_array(ibufr, 'highestDailyMeanTemperature', subs.S40_TXD)
        # 8053 Day of occurrence qualifier = 0 On 1 day only, = 1 On 2 or more days
            #2#dayOfOccurrenceQualifier

    ########################################################################################################3

        # 4003 Day
            #3#day
        # codes_set(ibufr, 'day', subs.DD) # S41_YN
                # The day on which the lowest daily mean temperature occurred shall be reported
                # using Day (0 04 003). If the lowest daily mean temperature occurred on only one
                # day, the preceding entry 0 08 053 (Day of occurrence qualifier) shall be set to 0.
                # If the lowest daily mean temperature occurred on more than one day, the first day
                # shall be reported for 0 04 003 and the preceding entry 0 08 053 shall be set to 1. 
        # 12153 Lowest daily mean temperature
            #1#lowestDailyMeanTemperature
    codes_set_array(ibufr, 'lowestDailyMeanTemperature', subs.S41_TND)
        # 8053 Day of occurrence qualifier = 0 On 1 day only, = 1 On 2 or more days  
            #3#dayOfOccurrenceQualifier

    #####################################################################################

        # 4003 Day
            #4#day
        # codes_set(ibufr, 'day', subs.DD) # S42_YAX
                # The day on which the highest air temperature occurred shall be reported using
                # Day (0 04 003). If the highest air temperature occurred on only one day, the
                # preceding entry 0 08 053 (Day of occurrence qualifier) shall be set to 0. If the
                # highest air temperature occurred on more than one day, the first day shall be
                # reported for 0 04 003 and the preceding entry 0 08 053 shall be set to 1. [71.6.1]
                # The highest air temperature of the month shall be reported using 0 12 101
                # (Temperature/air temperature), preceded by first-order statistics (0 08 023) set to
                # 2 (maximum value). The temperature shall be reported in kelvin (with precision in
                # hundredths of a kelvin);
        # 8023 First-order statistics = 2 Maximum value
            #3#firstOrderStatistics
        # codes_set(ibufr, 'firstOrderStatistics', subs.FS) # 2
        
        # 12101 Temperature/air temperature
            #2#airTemperature
        # codes_set(ibufr, 'airTemperature', subs.T) # S42_TAX
        # 8053 Day of occurrence qualifier = 0 On 1 day only, = 1 On 2 or more days
            #4#dayOfOccurrenceQualifier

    #####################################################################################################

        # 4003 Day
            #5#day
        # codes_set(ibufr, 'day', subs.DD) # S43_YAN 
                # The day on which the lowest air temperature occurred shall be reported using
                # Day (0 04 003). If the lowest air temperature occurred on only one day, the
                # preceding entry 0 08 053 (Day of occurrence qualifier) shall be set to 0. If the
                # lowest air temperature occurred on more than one day, the first day shall be
                # reported for 0 04 003 and the preceding entry 0 08 053 shall be set to 1. [71.6.1]
                # The lowest air temperature of the month shall be reported using 0 12 101
                # (Temperature/air temperature), preceded by first-order statistics (0 08 023) set to
                # 3 (minimum value). The temperature shall be reported in kelvin (with precision in
                # hundredths of a kelvin)
        # 8023 First-order statistics = 3 Minimum value
            #4#firstOrderStatistics
        # codes_set(ibufr, 'firstOrderStatistics', subs.FS) # 3
        # 12101 Temperature/air temperature
            #3#airTemperature
        # codes_set(ibufr, 'airTemperature', subs.T) # S43_TAN

    ##########################################################################################

        # 8023 First-order statistics Set to missing 
            #5#firstOrderStatistics
            # codes_set(ibufr, 'firstOrderStatistics', subs.FS) # miss
    #############################################################################################

        # 7032 Height of sensor above local ground (or deck of marine platform) (see Note 4)
            #4#heightOfSensorAboveLocalGroundOrDeckOfMarinePlatform
                # Height of sensor above local ground (0 07 032) for wind measurement shall be
                # reported in metres (with precision in hundredths of a metre).
                # This datum represents the actual height of wind sensors above ground at the
                # point where the sensors are located.
        # codes_set_array(ibufr, 'heightOfSensorAboveLocalGroundOrDeckOfMarinePlatform', subs.SENSOR) # ELANEM
        # 2002 Type of instrumentation for wind measurement
            #1#instrumentationForWindMeasurement
                # This datum shall be used to specify whether the wind speed was measured by
                # certified instruments (bit No. 1 set to 1) or estimated on the basis of the Beaufort
                # wind scale (bit No. 1 set to 0), and to indicate the original units for wind speed
                # measurement. Bit No. 2 set to 1 indicates that wind speed was originally
                # measured in knots and bit No. 3 set to 1 indicates that wind speed was originally
                # measured in kilometres per hour. Setting both bits No. 2 and No. 3 to 0 indicates
                # that wind speed was originally measured in metres per second.
    codes_set_array(ibufr, 'instrumentationForWindMeasurement', subs.S45_IW)
        # 8053 Day of occurrence qualifier = 0 On 1 day only, = 1 On 2 or more days
            #5#dayOfOccurrenceQualifier

    #################################################################################################


        # 4003 Day
            #6#day
        # codes_set(ibufr, 'day', sub.DD) # S45_YFX
        # 11046 Maximum instantaneous wind speed 
            #1#maximumInstantaneousWindSpeed
    codes_set_array(ibufr, 'maximumInstantaneousWindSpeed', subs.S45_FX)
        # 8053 Day of occurrence qualifier Set to missing (cancel)
            #6#dayOfOccurrenceQualifier
                # The day on which the highest instantaneous wind speed occurred shall be
                # reported using Day (0 04 003). If the highest instantaneous wind speed occurred
                # on only one day, the preceding entry 0 08 053 (Day of occurrence qualifier) shall
                # be set to 0. If the highest instantaneous wind speed occurred on more than one
                # day, the first day shall be reported for 0 04 003 and the preceding entry 0 08 053
                # shall be set to 1. [71.6.1]
                # The highest instantaneous wind speed of the month shall be reported using
                # 0 11 046 (Maximum instantaneous wind speed) in metres per second (with
                # precision in tenths of a metre per second).

    ##############################################################################################

    # Precipitation
        # 4003 Day (see Note 5) = 1
            #7#day
        # codes_set(ibufr, 'day', subs.DD) # 1
        # 4004 Hour (see Note 5) = 6
            #2#hour
        # codes_set(ibufr, 'hour', subs.HH24) # 6
                # Day (0 04 003) and hour (0 04 004) of the beginning of the one-month period for
                # monthly precipitation data are reported. Day (0 04 003) shall be set to 1 and hour
                # (0 04 004) shall be set to 6.
                # Notes:
                # (1) In case of precipitation measurements, a month begins at 0600 hours UTC on the
                # first day of the month and ends at 0600 hours UTC on the first day of the following
                # month

        # 4023 Time period or displacement (see Note 5) Number of days in the month
            #3#timePeriod
        # codes_set(ibufr, 'timePeriod', self.TP) # NM
                # Time period (0 04 023) represents the number of days in the month for which the
                # monthly mean data are reported, and shall be expressed as a positive value in
                # days.
                # Note: A BUFR (or CREX) message shall contain reports for one specific month only

        # 7032 Height of sensor above local ground (or deck of marine platform) (see Note 4)
            #5#heightOfSensorAboveLocalGroundOrDeckOfMarinePlatform # miss
                # Height of sensor above local ground (0 07 032) for precipitation measurement
                # shall be reported in metres (with precision in hundredths of a metre).
                # This datum represents the actual height of the rain gauge rim above ground at
                # the point where the rain gauge is located.

        # 13060 Total accumulated precipitation
            #1#totalAccumulatedPrecipitation
        # codes_set(ibufr, 'totalAccumulatedPrecipitation', subs.R_AC) # S16_R
                # Total accumulated precipitation (0 13 060) which has fallen during the month
                # shall be reported in kilograms per square metre (with precision in tenths of a
                # kilogram per square metre).
                # Note: Trace shall be reported as “–0.1 kg m–2”.

        # 13051 Frequency group, precipitation
            #1#frequencyGroupPrecipitation
    codes_set_array(ibufr, 'frequencyGroupPrecipitation', subs.S16_RD) # S16_RD
                # Frequency group in which the total amount of precipitation of the month falls shall
                # be reported using Code table 0 13 051 (Frequency group; precipitation).
                # Note: If for a particular month the total amount of precipitation is zero, the code figure
                # for 0 13 051 shall be given by the highest number of quintile which has 0.0 as lower limit
                # (e.g. in months with no rainfall in the 30-year period, 0 13 051 shall be set to 5).
                    # 0 Smaller than any value in the 30-year period
                    # 1 In the first quintile
                    # 2 In the second quintile
                    # 3 In the third quintile
                    # 4 In the fourth quintile
                    # 5 In the fifth quintile
                    # 6 Greater than any value in the 30-year period
                    # 7–14 Reserved
                    # 15 Missing value

        # 4053 Number of days with precipitation equal to or more than 1 mm 
            #1#numberOfDaysWithPrecipitationEqualToOrMoreThan1Mm
                # Number of days in the month with precipitation equal to or greater than
                # 1 kilogram per square metre shall be reported using 0 04 053 (Number of days in
                # the month with precipitation equal to or greater than 1 mm).
        # codes_set(ibufr, 'numberOfDaysWithPrecipitationEqualToOrMoreThan1Mm', subs.R_N) # S16_NR

        # 8050 Qualifier for number of missing values in calculation of statistic = 5 Precipitation
            #7#qualifierForNumberOfMissingValuesInCalculationOfStatistic
        #     lista = 5
        # codes_set(ibufr, 'qualifierForNumberOfMissingValuesInCalculationOfStatistic', subs.N_MISS)
        # 8020 Total number of missing entities (with respect to accumulation  or average) Days
            #7#totalNumberOfMissingEntitiesWithRespectToAccumulationOrAverage
        # codes_set(ibufr, 'totalNumberOfMissingEntitiesWithRespectToAccumulationOrAverage', subs.TOT_MISS) # S19_MR
                # Number of days in the month for which precipitation is missing shall be reported
                # using Total number of missing entities (0 08 020) being preceded by Qualifier for
                # number of missing values in calculation of statistic (0 08 050) set to 5
                # (precipitation).
        
    # ###############################################################################################################

    # Number of days of occurrence
        # 102006 Replicate 2 descriptors 6 times
        # 8052 Condition for which number of days of occurrence follows
            #19..24#conditionForWhichNumberOfDaysOfOccurrenceFollows
        # lista = [10, 11, 12, 13, 14, 15]
    # muka vaara koko .. ??? codes_set_array(ibufr, 'conditionForWhichNumberOfDaysOfOccurrenceFollows', subs.CND)

        # 8022 Total number (with respect to accumulation or average) Days
            #19..24#totalNumberWithRespectToAccumulationOrAverage
        # lista = [S33_R01, S33_R05, S34_R10, S34_R50, S35_R100, S35_R150]
    codes_set_array(ibufr, 'totalNumberWithRespectToAccumulationOrAverage', subs.TNRA)

                # Number of days in the month with precipitation beyond certain thresholds shall be
                # reported using Total number (0 08 022) being preceded by Condition for which
                # number of days of occurrence follows (0 08 052) in each of the required six
                # replications (1 02 006).
                # Condition for which number of days of occurrence follows (0 08 052) is:
                # – Set to 10 (precipitation ≥ 1.0 kg m–2) in the first replication;  
                # – Set to 11 (precipitation ≥ 5.0 kg m–2);             1kg vetta tilavuus on:                    
                # – Set to 12 (precipitation ≥ 10.0 kg m–2);            1 L = 1 dm³ = 0,001 m³                                 
                # – Set to 13 (precipitation ≥ 50.0 kg m–2);            1 kg / m² = 0,001 m³ / m² = 0,001 m = 1 mm
                # – Set to 14 (precipitation ≥ 100.0 kg m–2);
                # – Set to 15 (precipitation ≥ 150.0 kg m–2) in the last replication.
                # The number of days in the month with precipitation beyond the specified
                # thresholds shall be reported using 0 08 022 in the corresponding replication.

    # Occurrence of extreme precipitation
        # 8053 Day of occurrence qualifier = 0 On 1 day only, = 1 On 2 or more days 
            #7#dayOfOccurrenceQualifier
        # 4003 Day
            #8#day
        # codes_set(ibufr, 'day', subs.DD) # S44_YR
        # 13052 Highest daily amount of precipitation
            #1#highestDailyAmountOfPrecipitation
    codes_set_array(ibufr, 'highestDailyAmountOfPrecipitation', subs.S44_RX)
                # The day on which the highest daily amount of precipitation occurred shall be
                # reported using Day (0 04 003). If the highest daily amount of precipitation
                # occurred on only one day, the preceding entry 0 08 053 (Day of occurrence
                # qualifier) shall be set to 0. If the highest daily amount of precipitation occurred on
                # more than one day, the first day shall be reported for 0 04 003 and the preceding
                # entry 0 08 053 shall be set to 1. [71.6.1]
                # Highest daily amount of precipitation (0 13 052) shall be reported in kilograms per
                # square metre (with precision in tenths of a kilogram per square metre).
                # Note: Trace shall be reported as “–0.1 kg m–2”. 

        # 7032 Height of sensor above local ground (or deck of marine platform) Set to missing (cancel)
            #6#heightOfSensorAboveLocalGroundOrDeckOfMarinePlatform # miss


    # 307072 Monthly normals for a land station: (data of CLIMAT Section 2)
        # 4001 Year Beginning of the reference period
            #2#year
            # codes_set(ibufr, 'year', subs.YYYY) # oletan, kysy S20_YB
        # 4001 Year Ending of the reference period
            #3#year
            # codes_set(ibufr, 'year', subs.YYYY) # oletan, kysy S20_YC
                # Reference period for calculation of the normal values of the elements shall be
                # reported using two consecutive entries 0 04 001 (Year). The first 0 04 001 shall
                # express the year of beginning of the reference period and the second 0 04 001
                # shall express the year of ending of the reference period.
                # Note: The normal data reported shall be deduced from observations made over a
                # specific period defined by the Technical Regulations (WMO-No. 49)
        # 4002 Month
            #2#month
            # codes_set(ibufr, 'month', subs.MM) # kai_se_mika_muuallakin?
        # 4003 Day (see Note 3) = 1
            #9#day
            # codes_set(ibufr, 'day', subs.DD) # 1
        # 4004 Hour (see Note 3) = 0
            #3#hour
            # codes_set(ibufr, 'hour', subs.HH24) # 0
        # 4074 Short time period or displacement (see Note 3) = UTC – LT
            #4#timePeriodc
            # codes_set(ibufr, 'timePeriod', subs.TP) # -2
        # 4022 Time period or displacement = 1
            #5#timePeriod
            # codes_set(ibufr, 'timePeriod', subs.TP) # 1
                # The one-month period for which the normal values are reported shall be specified
                # by month (0 04 002), day (0 04 003) being set to 1, hour (0 04 004) being set to 0,
                # short time displacement (0 04 074) being set to (UTC – LT) and time period
                # (0 04 022) being set to 1, i.e. 1 month.
                # Short time displacement (0 04 074) shall be set to non-positive values in the
                # eastern hemisphere, non-negative values in the western hemisphere. 


        # 8023 First-order statistics = 4 Mean value
            #6#firstOrderStatistics
            # codes_set(ibufr, 'firstOrderStatistics', subs.FS) # 4
                # This datum shall be set to 4 (mean value) to indicate that the following entries
                # represent mean values of the elements (pressure, pressure reduced to mean sea
                # level or geopotential height, temperature, extreme temperatures, vapour pressure,
                # standard deviation of daily mean temperature and sunshine duration) averaged
                # over the reference period specified in Regulation

        # 10004 Pressure
            #2#nonCoordinatePressure
    codes_set_array(ibufr, 'nonCoordinatePressure', subs.P_ST) # S21_P
                # Normal value of pressure shall be reported using 0 10 004 (Pressure) in pascals
                # (with precision in tens of pascals).

        # 10051 Pressure reduced to mean sea level
            #2#pressureReducedToMeanSeaLevel
    codes_set_array(ibufr, 'pressureReducedToMeanSeaLevel', subs.P_SEA) # S22_P
                # Samat ohjeet kun edellä olevalla

        # 7004 Pressure Standard level # miss
            #2#pressure
        # 10009 Geopotential height Standard level # miss
            #2#nonCoordinateGeopotentialHeight
                # Normal value of geopotential height of a standard level shall be reported using
                # 0 10 009 (Geopotential height) in geopotential metres from high-level stations
                # which cannot give pressure at mean sea level to a satisfactory degree of
                # accuracy. The standard isobaric level is specified by the preceding entry
                # Pressure (0 07 004). 

        # 7032 Height of sensor above local ground (or deck of marine platform) (see Note 4)
            #7#heightOfSensorAboveLocalGroundOrDeckOfMarinePlatform
        # codes_set_array(ibufr, 'heightOfSensorAboveLocalGroundOrDeckOfMarinePlatform', subs.SENSOR) #  ELTERM
        # 12101 Temperature/air temperature
            #4#airTemperature
    codes_set_array(ibufr, 'airTemperature', subs.T) # S23_T
                # Kuten aiemmin

        # 2051 Indicator to specify observing method for extreme temperatures = 2
            #2#indicatorToSpecifyObservingMethodForExtremeTemperatures
    codes_set_array(ibufr, 'indicatorToSpecifyObservingMethodForExtremeTemperatures', subs.IND) # 2
        # 4051 Principal time of daily reading of maximum temperature
            #2#principalTimeOfDailyReadingOfMaximumTemperature
        # 12118 Maximum temperature at height specified, past 24 hours
            #2#maximumTemperatureAtHeightSpecifiedPast24Hours
    codes_set_array(ibufr, 'maximumTemperatureAtHeightSpecifiedPast24Hours', subs.TMAX) # S24_TX
        # 4052 Principal time of daily reading of minimum temperature
            #2#principalTimeOfDailyReadingOfMinimumTemperature
        # 12119 Minimum temperature at height specified, past 24 hours
            #2#minimumTemperatureAtHeightSpecifiedPast24Hours
                # Kaikki kuten aiemmin
    codes_set_array(ibufr, 'minimumTemperatureAtHeightSpecifiedPast24Hours', subs.TMIN) # S24_TN
        # 13004 Vapour pressure
            #2#vapourPressure
                # Normal value of vapour pressure shall be reported using 0 13 004 (Vapour
                # pressure) in pascals (with precision in tens of pascals).
    codes_set_array(ibufr, 'vapourPressure', subs.E) # S25_E

        # 12151 Standard deviation of daily mean temperature
            #2#dailyMeanTemperatureStandardDeviation
                # Normal value of standard deviation of daily mean temperature shall be reported
                # using 0 12 151 in kelvin
    # Täs outo, ei pidä kelvineistä ??? codes_set_array(ibufr, 'dailyMeanTemperatureStandardDeviation', subs.TMEAN) #  S23_ST

        # 7032 Height of sensor above local ground (or deck of marine platform) Set to missing
            #8#heightOfSensorAboveLocalGroundOrDeckOfMarinePlatform # miss
        # 14032 Total sunshine
            #3#totalSunshine
                # Normal of monthly sunshine duration shall be reported in hours using 0 14 032
                # (Total sunshine)
                # The monthly values of total duration of sunshine shall be reported in hours using
                # Total sunshine (0 14 032) and the percentage of the normal that that value
                # represents shall be reported using Total sunshine (0 14 033). Any missing
                # element shall be reported as a missing value.
                # Notes:
                # (1) If the percentage of the normal is 1% or less but greater than 0, Total sunshine
                # 0 14 033 shall be set to 1.
                # (2) If the normal is zero hours, Total sunshine 0 14 033 shall be set to 510.
                # (3) If the normal is not defined, Total sunshine 0 14 033 shall be set to missing.
    codes_set_array(ibufr, 'totalSunshine', subs.SUND) # S27_S

        # 8023 First-order statistics Set to missing
            #7#firstOrderStatistics
            # codes_set(ibufr, 'firstOrderStatistics', subs.FS) # miss
        # 4001 Year Beginning of the reference period
            #4#year
            # codes_set(ibufr, 'year', subs.YYYY) # S20_YB oletan, kysy
        # 4001 Year Ending of the reference period
            #5#year
    codes_set_array(ibufr, 'year', subs.YYYY) # S20_YC oletan, kysy
                # Reference period for calculation of the normal values of precipitation shall be
                # reported using two consecutive entries 0 04 001 (Year). The first 0 04 001 shall
                # express the year of beginning of the reference period and the second 0 04 001
                # shall express the year of ending of the reference period.

        # 4002 Month
            #3#month
    codes_set_array(ibufr, 'month', subs.MM) # sama kaikissa kolmessa, oletan, kysy
        # 4003 Day (see Note 5) = 1
            #10#day
    codes_set_array(ibufr, 'day', subs.DD) # 1
        # 4004 Hour (see Note 5) = 6
            #4#hour
    codes_set_array(ibufr, 'hour', subs.HH24) # 6
        # 4022 Time period or displacement = 1
            #6#timePeriod
                # The one-month period for which the normals of precipitation are reported shall be
                # specified by month (0 04 002), day (0 04 003) being set to 1, hour (0 04 004)
                # being set to 6 and time period (0 04 022) being set to 1, i.e. 1 month.
    codes_set_array(ibufr, 'timePeriod', subs.TP) # 1
        # 7032 Height of sensor above local ground (or deck of marine platform) (see Note 4)
            #9#heightOfSensorAboveLocalGroundOrDeckOfMarinePlatform
    codes_set_array(ibufr, 'heightOfSensorAboveLocalGroundOrDeckOfMarinePlatform', subs.SENSOR) # miss
        # 8023 First-order statistics = 4 Mean value
            #8#firstOrderStatistics
                # This datum shall be set to 4 (mean value) to indicate that the following entries
                # represent mean values of precipitation data, averaged over the reference period
                # specified in Regulation
            # codes_set(ibufr, 'firstOrderStatistics', subs.FS) # 4 

        # 13060 Total accumulated precipitation
            #2#totalAccumulatedPrecipitati
    codes_set_array(ibufr, 'totalAccumulatedPrecipitation', subs.R_AC) # S26_R
                # Normal value of monthly amount of precipitation shall be reported in kilograms
                # per square metre (with precision in tenths of a kilogram per square metre) using
                # 0 13 060 (Total accumulated precipitation).
                # Note: Trace shall be reported as “–0.1 kg m–2”. 
                # 1 kg /m^2 ~ 1 L / m^2 = 1dm^3 / m^2 = 0,001 m^3 / m^2 = 0,001 m = 1 mm

        # 4053 Number of days with precipitation equal to or more than 1 mm
            #2#numberOfDaysWithPrecipitationEqualToOrMoreThan1Mm
    codes_set_array(ibufr, 'numberOfDaysWithPrecipitationEqualToOrMoreThan1Mm', subs.R_N) # S26_NR
                # Normal value of number of days in the month with precipitation equal to or
                # greater than 1 kilogram per square metre shall be reported using 0 04 053
                # (Number of days in the month with precipitation equal to or greater than 1 mm).

        # 8023 First-order statistics Set to missing
            #9#firstOrderStatistics
    codes_set_array(ibufr, 'firstOrderStatistics', subs.FS) # miss
        # 102008 Replicate 2 descriptors 8 times
        # 8050 Qualifier for number of missing values in calculation of statistic (see Note 6) = 1 Pressure, = 2 Temperature, = 3 Extreme temperature, = 4 Vapour pressure, = 5 Precipitation, = 6 Sunshine duration,  = 7 Maximum temperature, = 8 Minimum temperature
            #8..15#qualifierForNumberOfMissingValuesInCalculationOfStatistic
            # codes_set(ibufr, 'qualifierForNumberOfMissingValuesInCalculationOfStatisti', 1)
            # codes_set(ibufr, 'qualifierForNumberOfMissingValuesInCalculationOfStatisti', 2)
            # codes_set(ibufr, 'qualifierForNumberOfMissingValuesInCalculationOfStatisti', 3)
            # codes_set(ibufr, 'qualifierForNumberOfMissingValuesInCalculationOfStatisti', 4)
            # codes_set(ibufr, 'qualifierForNumberOfMissingValuesInCalculationOfStatisti', 5)
            # codes_set(ibufr, 'qualifierForNumberOfMissingValuesInCalculationOfStatisti', 6)
            # codes_set(ibufr, 'qualifierForNumberOfMissingValuesInCalculationOfStatisti', 7)
            # codes_set(ibufr, 'qualifierForNumberOfMissingValuesInCalculationOfStatisti', 8)
            # lista=[1,2,3,4,5,6,7,8]
    # tas joku ??? codes_set_array(ibufr, 'qualifierForNumberOfMissingValuesInCalculationOfStatisti', subs.N_MISS)
        # 8020 Total number of missing entities (with respect to accumulation or average) (see Note 6) Years
            #8..15#totalNumberOfMissingEntitiesWithRespectToAccumulationOrAverage
            # codes_set(ibufr, 'totalNumberOfMissingEntitiesWithRespectToAccumulationOrAverage', S28_YP) # kuukausi -> vuosi
            # codes_set(ibufr, 'totalNumberOfMissingEntitiesWithRespectToAccumulationOrAverage', S28_YT) # kuukausi -> vuosi
            # codes_set(ibufr, 'totalNumberOfMissingEntitiesWithRespectToAccumulationOrAverage', S28_YTX) # kuukausi -> vuosi
            # codes_set(ibufr, 'totalNumberOfMissingEntitiesWithRespectToAccumulationOrAverage', S29_YE) # kuukausi -> vuosi
            # codes_set(ibufr, 'totalNumberOfMissingEntitiesWithRespectToAccumulationOrAverage', S29_YR) # kuukausi -> vuosi
            # codes_set(ibufr, 'totalNumberOfMissingEntitiesWithRespectToAccumulationOrAverage', S29_YS) # kuukausi -> vuosi
            # codes_set(ibufr, 'totalNumberOfMissingEntitiesWithRespectToAccumulationOrAverage', S28_YTX) # kuukausi -> vuosi
            # codes_set(ibufr, 'totalNumberOfMissingEntitiesWithRespectToAccumulationOrAverage', S28_YTX) # kuukausi -> vuosi
    codes_set_array(ibufr, 'totalNumberOfMissingEntitiesWithRespectToAccumulationOrAverage', subs.TOT_MISS) 
                # Number of missing years within the reference period shall be reported using Total
                # number of missing entities (0 08 020) being preceded by Qualifier for number of
                # missing values in calculation of statistic (0 08 050) in each of the required eight
                # replications (1 02 008).
                # Qualifier for number of missing values in calculation of statistic (0 08 050) is:
                # – Set to 1 (pressure) in the first replication;
                # – Set to 2 (temperature);
                # – Set to 3 (extreme temperatures);
                # – Set to 4 (vapour pressure);
                # – Set to 5 (precipitation);
                # – Set to 6 (sunshine duration);
                # – Set to 7 (maximum temperature);
                # – Set to 8 (minimum temperature) in the last replication.
                # The number of missing years within the reference period for calculation of the
                # normal values of the element shall be reported using 0 08 020 in the
                # corresponding replication.
                # Note: The number of missing years within the reference period from the calculation
                # of normal for mean extreme air temperature should be given, if available, for both the
                # calculation of normal maximum temperature and for the calculation of normal minimum
                # temperature in addition to the number of missing years for the extreme air temperatures
                # reported under 0 08 020 preceded by 0 08 050 in which Figure 3 is used.

    codes_set(ibufr, 'pack', 1)  # Required to encode the keys back in the data section
    return ibufr

def main():
    """
    Main function gets input file from command line and sends it to message_encode
    function which writes the bufr into the output file named by input file information.
    """
    if len(sys.argv) < 2:
        print('Usage: ', sys.argv[0], ' climate_filename', file=sys.stderr)
        sys.exit(1)
    climate_filename = sys.argv[1]

    try:
        with open(climate_filename, 'r', encoding="utf8") as climate_file:
            print('climate data from file: ', climate_filename)
            try:
                bufr_filename = message_encoding(climate_file)
            except CodesInternalError as err:
                if VERBOSE:
                    traceback.print_exc(file=sys.stderr)
                else:
                    sys.stderr.write(err.msg + '\n')
                return 1
            except Exception as err:
                if VERBOSE:
                    traceback.print_exc(file=sys.stderr)
                else:
                    print(err)
                return 1
            finally:
                climate_file.close()
    except FileNotFoundError as err:
        if VERBOSE:
            traceback.print_exc(file=sys.stderr)
        else:
            sys.stderr.write(err.msg + '\n')
        return 1

    print('bufr data in file: ', bufr_filename)
    return None

if __name__ == '__main__':
    sys.exit(main())
