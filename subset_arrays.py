"""
This module makes subset objects by different functions and Subset class.
"""
import sys
from eccodes import CODES_MISSING_LONG as miss
from eccodes import CODES_MISSING_DOUBLE as missD

class Subset:
    """
    This class makes keyname objects with key names that are used in climat
    data. All the values with same keyname are placed into the same object as an array.
    The values are modified in different functions according to codes manual.
        1. At first Subset class makes all the values, which are not dependent
        on any other objects to be missing. Only the number of subsets (NSUB) is given.
        2. The values are read form v_a, and value is placed in keyname object acording
        keyname's index position. Values that don't depend on any other are given first.
        As an exception, block number and sation number are given acording to WMO. Date
        values are picked from REPORDED MONTH and WIGOS valus are picked from WSI.
        3. The rest of all the needed values are given.
        4. Functions which gives the right values to bufr message, are placed below.
    """
    # 1.
    def __init__(self, key_array, value_array):
        k_a = key_array
        v_a = value_array
        self.NSUB = len(v_a[0])
        miss_list = []
        miss_char_list = []
        for i in range(0, self.NSUB):
            miss_list.append('-1e+100')
            miss_char_list.append('')
        self.TTAAII = miss_list
        self.ELANEM = str2float(miss_list, 1)
        self.ELBARO = str2float(miss_list, 2)
        self.ELSTAT = str2float(miss_list, 3)
        self.ELTERM = str2float(miss_list, 4)
        self.LAT = str2float(miss_list, 5)
        self.LON = str2float(miss_list, 6)
        self.STATION_NAME = miss_list
        self.STATION_TYPE = str2int(miss_list, 8)
        self.WMON = miss_list
        self.WSI_IDS = str2int(miss_list, 0)
        self.WSI_IDI = str2int(miss_list, 0)
        self.WSI_INR = str2int(miss_list, 0)
        self.WSI_LID = miss_char_list
        self.BLOCK_NUMBER = str2int(self.WMON, 64)
        self.STATION_NUMBER = str2int(self.WMON, 65)
        self.YYYY = str2int(miss_list, 63)
        self.R_YYYY = str2int(miss_list, 63)
        self.S20_YB = str2int(miss_list, 63)
        self.S20_YC = str2int(miss_list, 63)
        self.MM = str2int(miss_list, 27)
        self.R_MM = str2int(miss_list, 27)
        self.R_DD = str2int(miss_list, 21)
        self.HH24 = str2int(miss_list, 24)
        self.R_HH0 = str2int(miss_list, 24)
        self.R_HH6 = str2int(miss_list, 24)
        self.MI = str2int(miss_list, 26)
        self.R_MI = str2int(miss_list, 26)
        self.DD = str2int(miss_list, 21)
        self.S40_YX = str2int(miss_list, 21)
        self.S41_YN = str2int(miss_list, 21)
        self.S42_YAX = str2int(miss_list, 21)
        self.S43_YAN = str2int(miss_list, 21)
        self.S45_YFX = str2int(miss_list, 21)
        self.S44_YR = str2int(miss_list, 21)
        self.S11_P = str2float(miss_list, 34)
        self.S21_P = str2float(miss_list, 34)
        self.S12_P = str2float(miss_list, 34)
        self.S22_P = str2float(miss_list, 34)
        self.S15_E = str2float(miss_list, 34)
        self.S25_E = str2float(miss_list, 34)
        self.S16_R = str2float(miss_list, 40)
        self.S26_R = str2float(miss_list, 40)
        self.S16_RD = str2int(miss_list, 31)
        self.S16_NR = str2int(miss_list, 32)
        self.S26_NR = str2int(miss_list, 32)
        self.S44_RX = str2float(miss_list, 44)
        self.S17_S = str2float(miss_list, 43)
        self.S17_PS = str2float(miss_list, 43)
        self.S27_S = str2float(miss_list, 43)
        self.S13_T = str2float(miss_list, 50)
        self.S42_TAX = str2float(miss_list, 50)
        self.S43_TAN = str2float(miss_list, 50)
        self.S23_T = str2float(miss_list, 50)
        self.S14_TX = str2float(miss_list, 50)
        self.S14_TN = str2float(miss_list, 50)
        self.S24_TX = str2float(miss_list, 50)
        self.S24_TN = str2float(miss_list, 50)
        self.S13_ST = str2float(miss_list, 52)
        self.S23_ST = str2float(miss_list, 52)
        self.S18_MP = str2int(miss_list, 51)
        self.S18_MT = str2int(miss_list, 51)
        self.S19_ME = str2int(miss_list, 51)
        self.S18_MTX = str2int(miss_list, 51)
        self.S18_MTN = str2int(miss_list, 51)
        self.S19_MS = str2int(miss_list, 51)
        self.S19_MR = str2int(miss_list, 51)
        self.S28_YP = str2int(miss_list, 56)
        self.S28_YT = str2int(miss_list, 56)
        self.S28_YTX = str2int(miss_list, 56)
        self.S29_YE = str2int(miss_list, 56)
        self.S29_YR = str2int(miss_list, 56)
        self.S29_YS = str2int(miss_list, 56)
        self.S38_F10 = str2int(miss_list, 51)
        self.S38_F20 = str2int(miss_list, 51)
        self.S38_F30 = str2int(miss_list, 51)
        self.S32_TX0 = str2int(miss_list, 51)
        self.S30_T25 = str2int(miss_list, 51)
        self.S30_T30 = str2int(miss_list, 51)
        self.S31_T35 = str2int(miss_list, 51)
        self.S31_T40 = str2int(miss_list, 51)
        self.S32_TN0 = str2int(miss_list, 51)
        self.S36_S00 = str2int(miss_list, 51)
        self.S36_S01 = str2int(miss_list, 51)
        self.S37_S10 = str2int(miss_list, 51)
        self.S37_S50 = str2int(miss_list, 51)
        self.S39_V1 = str2int(miss_list, 51)
        self.S39_V2 = str2int(miss_list, 51)
        self.S39_V3 = str2int(miss_list, 51)
        self.S33_R01 = str2int(miss_list, 51)
        self.S33_R05 = str2int(miss_list, 51)
        self.S34_R10 = str2int(miss_list, 51)
        self.S34_R50 = str2int(miss_list, 51)
        self.S35_R100 = str2int(miss_list, 51)
        self.S35_R150 = str2int(miss_list, 51)
        self.S40_TXD = str2float(miss_list, 50)
        self.S41_TND = str2float(miss_list, 50)
        self.S45_IW = str2int(miss_list, 66)
        self.S45_FX =  str2float(miss_list, 67)

    # 2.
        for key in k_a:
            if key == 'TTAAII':
                self.TTAAII = v_a[k_a.index(key)]
            elif key == 'ELANEM':
                self.ELANEM = str2float(v_a[k_a.index(key)], 1)
            elif key == 'ELBARO':
                self.ELBARO = str2float(v_a[k_a.index(key)], 2)
            elif key == 'ELSTAT':
                self.ELSTAT = str2float(v_a[k_a.index(key)], 3)
            elif key == 'ELTERM':
                self.ELTERM = str2float(v_a[k_a.index(key)], 4)
            elif key == 'LAT':
                self.LAT = str2float(v_a[k_a.index(key)], 5)
            elif key == 'LON':
                self.LON = str2float(v_a[k_a.index(key)], 6)
            elif key == 'STATION_NAME':
                self.STATION_NAME = v_a[k_a.index(key)]
            elif key == 'STATION_TYPE':
                self.STATION_TYPE = str2int(v_a[k_a.index(key)], 8)
            elif key == 'WMON':
                self.WMON = v_a[k_a.index(key)]
                self.BLOCK_NUMBER = str2int(self.WMON, 64)
                self.STATION_NUMBER = str2int(self.WMON, 65)
            elif key == 'WSI':
                self.WSI_IDS = get_wigos(v_a[k_a.index(key)], 0)
                self.WSI_IDI = get_wigos(v_a[k_a.index(key)], 1)
                self.WSI_INR = get_wigos(v_a[k_a.index(key)], 2)
                self.WSI_LID = get_wigos(v_a[k_a.index(key)], 3)
            elif key == 'S40_YX':
                self.S40_YX = str2int(v_a[k_a.index(key)], 21)
            elif key == 'S41_YN':
                self.S41_YN = str2int(v_a[k_a.index(key)], 21)
            elif key == 'S42_YAX':
                self.S42_YAX = str2int(v_a[k_a.index(key)], 21)
            elif key == 'S43_YAN':
                self.S43_YAN = str2int(v_a[k_a.index(key)], 21)
            elif key == 'S45_YFX':
                self.S45_YFX = str2int(v_a[k_a.index(key)], 21)
            elif key == 'S44_YR':
                self.S44_YR = str2int(v_a[k_a.index(key)], 21)
            elif key == 'S11_P':
                self.S11_P = str2float(v_a[k_a.index(key)], 34)
            elif key == 'S21_P':
                self.S21_P = str2float(v_a[k_a.index(key)], 34)
            elif key == 'S12_P':
                self.S12_P = str2float(v_a[k_a.index(key)], 34)
            elif key == 'S22_P':
                self.S22_P = str2float(v_a[k_a.index(key)], 34)
            elif key == 'S15_E':
                self.S15_E = str2float(v_a[k_a.index(key)], 34)
            elif key == 'S25_E':
                self.S25_E = str2float(v_a[k_a.index(key)], 34)
            elif key == 'S16_R':
                self.S16_R = str2float(v_a[k_a.index(key)], 40)
            elif key == 'S26_R':
                self.S26_R = str2float(v_a[k_a.index(key)], 40)
            elif key == 'S16_RD':
                self.S16_RD = str2int(v_a[k_a.index(key)], 31)
            elif key == 'S16_NR':
                self.S16_NR = str2int(v_a[k_a.index(key)], 32)
            elif key == 'S26_NR':
                self.S26_NR = str2int(v_a[k_a.index(key)], 32)
            elif key == 'S44_RX':
                self.S44_RX = str2float(v_a[k_a.index(key)], 44)
            elif key == 'S13_T':
                self.S13_T = str2float(v_a[k_a.index(key)], 50)
            elif key == 'S42_TAX':
                self.S42_TAX = str2float(v_a[k_a.index(key)], 50)
            elif key == 'S43_TAN':
                self.S43_TAN = str2float(v_a[k_a.index(key)], 50)
            elif key == 'S23_T':
                self.S23_T = str2float(v_a[k_a.index(key)], 50)
            elif key == 'S13_ST':
                self.S13_ST = str2float(v_a[k_a.index(key)], 52)
            elif key == 'S23_ST':
                self.S23_ST = str2float(v_a[k_a.index(key)], 52)
            elif key == 'S14_TX':
                self.S14_TX = str2float(v_a[k_a.index(key)], 50)
            elif key == 'S24_TX':
                self.S24_TX = str2float(v_a[k_a.index(key)], 50)
            elif key == 'S14_TN':
                self.S14_TN = str2float(v_a[k_a.index(key)], 50)
            elif key == 'S24_TN':
                self.S24_TN = str2float(v_a[k_a.index(key)], 50)
            elif key == 'S18_MP':
                self.S18_MP = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S18_MT':
                self.S18_MT = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S19_ME':
                self.S19_ME = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S18_MTX':
                self.S18_MTX = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S18_MTN':
                self.S18_MTN = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S19_MS':
                self.S19_MS = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S19_MR':
                self.S19_MR = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S28_YP':
                self.S28_YP = str2int(v_a[k_a.index(key)], 56)
            elif key == 'S28_YT':
                self.S28_YT = str2int(v_a[k_a.index(key)], 56)
            elif key == 'S28_YTX':
                self.S28_YTX = str2int(v_a[k_a.index(key)], 56)
            elif key == 'S29_YE':
                self.S29_YE = str2int(v_a[k_a.index(key)], 56)
            elif key == 'S29_YR':
                self.S29_YR = str2int(v_a[k_a.index(key)], 56)
            elif key == 'S29_YS':
                self.S29_YS = str2int(v_a[k_a.index(key)], 56)
            elif key == 'S17_S':
                self.S17_S = str2float(v_a[k_a.index(key)], 43)
            elif key == 'S17_PS':
                self.S17_PS = str2float(v_a[k_a.index(key)], 43)
            elif key == 'S27_S':
                self.S27_S = str2float(v_a[k_a.index(key)], 43)
            elif key == 'S20_YB':
                self.S20_YB = get_times(v_a[k_a.index(key)], 1)
            elif key == 'S20_YC':
                self.S20_YC = get_times(v_a[k_a.index(key)], 1)
            elif key == 'REPORT_MONTH':
                self.REPORT_MONTH = v_a[k_a.index(key)]
                self.R_YYYY = get_times(self.REPORT_MONTH, 0)
                self.R_MM = get_times(self.REPORT_MONTH, 2)
                self.R_DD = get_times(self.REPORT_MONTH, 3)
                self.R_HH0 = get_number_list(self.NSUB, 0)
                self.R_HH6 = get_number_list(self.NSUB, 6)
                self.R_MI = get_number_list(self.NSUB, 0)
            elif key == 'S38_F10':
                self.S38_F10 = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S38_F20':
                self.S38_F20 = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S38_F30':
                self.S38_F30 = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S32_TX0':
                self.S32_TX0 = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S30_T25':
                self.S30_T25 = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S30_T30':
                self.S30_T30 = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S31_T35':
                self.S31_T35 = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S31_T40':
                self.S31_T40 = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S32_TN0':
                self.S32_TN0 = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S36_S00':
                self.S36_S00 = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S36_S01':
                self.S36_S01 = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S37_S10':
                self.S37_S10 = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S37_S50':
                self.S37_S50 = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S39_V1':
                self.S39_V1 = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S39_V2':
                self.S39_V2 = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S39_V3':
                self.S39_V3 = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S33_R01':
                self.S33_R01 = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S33_R05':
                self.S33_R05 = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S34_R10':
                self.S34_R10 = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S34_R50':
                self.S34_R50 = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S35_R100':
                self.S35_R100 = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S35_R150':
                self.S35_R150 = str2int(v_a[k_a.index(key)], 51)
            elif key == 'S40_TXD':
                self.S40_TXD = str2float(v_a[k_a.index(key)], 50)
            elif key == 'S41_TND':
                self.S41_TND = str2float(v_a[k_a.index(key)], 50)
            elif key == 'S45_IW':
                self.S45_IW = str2int(v_a[k_a.index(key)], 66)
            elif key == 'S45_FX':
                self.S45_FX = str2float(v_a[k_a.index(key)], 67)

    # 3.
        self.YYYY = make_list([self.R_YYYY, self.S20_YB, self.S20_YC, self.S20_YB,
            self.S20_YC], self.NSUB)
        self.MM = make_list([self.R_MM, self.R_MM, self.R_MM], self.NSUB)
        self.DD = make_day_list([self.R_DD, self.S40_YX, self.S41_YN, self.S42_YAX, self.S43_YAN,
            self.S45_YFX, self.R_DD, self.S44_YR, self.R_DD, self.R_DD], self.NSUB)
        self.HH24 = make_list([self.R_HH0, self.R_HH6, self.R_HH0, self.R_HH6], self.NSUB)
        self.MI = self.R_MI
        self.NM = days_in_month_list(self.R_YYYY, self.R_MM)
        self.UTC_DIFF = get_times(self.R_MM, 4)
        self.TP = make_list([self.UTC_DIFF, self.NM, self.NM, self.UTC_DIFF,
            get_number_list(self.NSUB, 1), get_number_list(self.NSUB, 1)], self.NSUB)
        self.TOT_MISS = make_list([self.S18_MP, self.S18_MT, self.S19_ME, self.S18_MTX,
            self.S18_MTN, self.S19_MS, self.S19_MR,
            self.S28_YP, self.S28_YT, self.S28_YTX,self.S29_YE, self.S29_YR, self.S29_YS,
            self.S28_YTX, self.S28_YTX], self.NSUB)
        self.TNRA = make_list([self.S38_F10, self.S38_F20, self.S38_F30, self.S32_TX0,
            self.S30_T25, self.S30_T30, self.S31_T35, self.S31_T40, self.S32_TN0,
            self.S36_S00, self.S36_S01, self.S37_S10, self.S37_S50,
            self.S39_V1, self.S39_V2, self.S39_V3, str2int(miss_list, 51), str2int(miss_list, 51),
            self.S33_R01, self.S33_R05, self.S34_R10, self.S34_R50, self.S35_R100, self.S35_R150],
            self.NSUB)
        self.P_ST = make_list([self.S11_P, self.S21_P], self.NSUB)
        self.P_SEA = make_list([self.S12_P, self.S22_P], self.NSUB)
        self.T = make_list([self.S13_T, self.S42_TAX, self.S43_TAN, self.S23_T], self.NSUB)
        self.TMAX = make_list([self.S14_TX, self.S24_TX], self.NSUB)
        self.TMIN = make_list([self.S14_TN, self.S24_TN], self.NSUB)
        self.TMEAN = make_list([self.S13_ST, self.S23_ST], self.NSUB)
        self.E = make_list([self.S15_E, self.S25_E], self.NSUB)
        self.SUND = make_list([self.S17_S, sunshine_pros(self.S17_S, self.S27_S), self.S27_S],
            self.NSUB)
        self.R_AC = make_list([self.S16_R, self.S26_R], self.NSUB)
        self.R_N = make_list([self.S16_NR, self.S26_NR], self.NSUB)
        self.N_MISS = make_const_list([1,2,4,7,8,6,5,1,2,3,4,5,6,7,8], self.NSUB)
        self.SENSOR = height_of_sensor(self.ELANEM, self.ELTERM)
        self.INSTRUMENT = instrument_type(self.NSUB)
        self.FS = first_order_statistics(self.NSUB)
        self.IND = observing_method_extreme_temperatures(self.NSUB)
        self.CND = make_const_list([0,1,2,3,4,5,6,7,8,16,17,18,19,20,21,22,23,24,10,11,12,13,14,15],
            self.NSUB)
        self.D_OC = day_of_occurance_qualifier(self.S40_YX, self.S41_YN, self.S42_YAX, self.S43_YAN,
            self.S45_YFX, miss_list, self.S44_YR)
# 4.

def get_wigos(wigos_id, key_id):
    """
    This function splits WIGOS identifier (wigos_id)from "-" to get a wigos_array with:
        wigos_array[0] = WIGOS identifier series = WSI_IDS  (value between 0-14)
        wigos_array[1] = WIGOS issuer of identifier = WSI_IDI
            Value between 1 and 9 999 when no WMO number.
            Value between 10 000 and 99 999 otherwise.
        wigos_array[2] = WIGOS issue number = WSI_INR
        wigos_array[3] = WIGOS local identifier (character) = WSI_LID
            NSI number is used if WMO number is missing provided.
    https://wiki.fmi.fi/pages/viewpage.action?pageId=107195152
    """
    wigos_term = []
    for i in range(0, len(wigos_id)):
        if wigos_id[i] != '-1e+100':
            wigos_array = wigos_id[i].split('-')

            if len(wigos_array)!= 4:
                print('WIGOS identifier is wrongly written!\n')
                sys.exit(1)
            try:
                wigos_array[0] = int(wigos_array[0])
                wigos_array[1] = int(wigos_array[1])
                wigos_array[2] = int(wigos_array[2])
                if wigos_array[0] not in range(0, 15):
                    print('WIGOS identifier series number should be in range (0, 14).\n')
                    sys.exit(1)
                elif wigos_array[1] not in range(1, 100000):
                    print('WIGOS issuer of identifier number should be in range (1, 99 999).\n')
                    sys.exit(1)
                elif wigos_array[2] not in range(0, 100000):
                    print('WIGOS issue number should be in range (0, 99 999.\n')
                    sys.exit(1)
                elif len(wigos_array[3])> 16:
                    print('WIGOS local identifier should be 16 characters max.\n')
                    sys.exit(1)
                wigos_term.append(wigos_array[key_id])
            except ValueError:
                print('WIGOS identifier series, WIGOS issuer of identifier')
                print('and WIGOS issuer number should be positive integers.\n')
                sys.exit(1)
        else:
            wigos_array = [miss, miss, miss, '']
            wigos_term.append(wigos_array[key_id])

    return wigos_term

def get_times(time_list, n):
    """
    This function returns time list according to number n:
        n == 0: years from parameter REPORT_MONTH=YYYY-MM-DD
        n == 1: years from year list (yyyy)
        n == 2: months from parameter REPORT_MONTH=YYYY-MM-DD
        n == 3: days from parameter REPORT_MONTH=YYYY-MM-DD
        n == 4: utc - ltm according which month it is (mm)
    """
    times = []
    for i in range (0, len(time_list)):
        time = time_list[i]
        if n == 0:
            times.append(int(time[:4]))
        elif n == 1:
            times.append(int(time))
        elif n == 2:
            times.append(int(time[5:7]))
        elif n == 3:
            times.append(int(time[-2:]))
        elif n == 4:
            if int(time) < 4:
                times.append(-2)
            elif int(time) > 10:
                times.append(-2)
            else:
                times.append(-3)
        else:
            times.append(miss)

    return times

def get_number_list(ns, value):
    """
    This function returns list of values.
    List will have items as many as subsets (ns).
    """
    values = []
    for i in range (0, ns):
        values.append(int(value))
    return values

def is_leap_year(year):
    """
    This function checks if the year is a leap year
    """
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def days_in_month(year, month):
    """
    This function return number of days in month.
    If it's February, the leap year is checked.
    """
    days_in_months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    if month == 2 and is_leap_year(year):
        return 29
    else:
        return days_in_months[month - 1]

def days_in_month_list(y_list, m_list):
    """
    This function return number of days in month list.
    """
    nm_list = []
    for i in range (0, len(m_list)):
        nm_list.append(days_in_month(int(y_list[i]), int(m_list[i])))
    return nm_list

def sunshine_pros(s_month_list, s_30v_list):
    """
    The percentage of the normal that value represents shall be reported using
    Total sunshine (0 14 033). Any missing element shall be reported as a missing value.
    Notes:
        (1) If the percentage of the normal is 1% or less but greater than 0, Total sunshine
            0 14 033 shall be set to 1.
        (2) If the normal is zero hours, Total sunshine 0 14 033 shall be set to 510.
        (3) If the normal is not defined, Total sunshine 0 14 033 shall be set to missing.
    """
    s_pros_list = []
    for s in range(0, len(s_month_list)):
        if float(s_30v_list[s]) == missD or float(s_month_list[s]) == missD:
            s_pros_list.append(missD)
        else:
            if float(s_30v_list[s]) == 0.0:
                s_pros_list.append(510)
            else:
                s_pros = 100* float(s_month_list[s]) / float(s_30v_list[s])
                if 0.0 <= s_pros and s_pros <= 1.0:
                    s_pros_list.append(1)
                else:
                    s_pros_list.append(int(s_pros))

    return s_pros_list

def first_order_statistics(ns):
    """
    This function retusn list of first order statistics
    according to code table 0 08 023
    """
    fs_list = []
    for i in range (0, ns):
        fs_list.append(4)
        fs_list.append(63)
        fs_list.append(2)
        fs_list.append(3)
        fs_list.append(63)
        fs_list.append(4)
        fs_list.append(63)
        fs_list.append(4)
        fs_list.append(63)
    return fs_list

def observing_method_extreme_temperatures(ns):
    """
    This function retusn list of indicator to specify observing
    method for extreme temperatures
    according to code table 0 02 051
        0 Reserved
        1 Maximum/minimum thermometers
        2 Automated instruments
        3 Thermograph
        4–14 Reserved
        15 Missing value
    """
    ind_list = []
    for i in range (0, ns):
        ind_list.append(15)
        ind_list.append(2)
    return ind_list



def height_of_sensor(elanem_list, elterm_list):
    """
    This function makes a list of all the sensor heights
    in CLIMATE sequence 3 07 073.
    """
    float_list = []
    for i in range(0, len(elanem_list)):
        float_list.append(elterm_list[i])
        float_list.append(missD)
        float_list.append(elterm_list[i])
        float_list.append(elanem_list[i])
        float_list.append(missD)
        float_list.append(missD)
        float_list.append(elterm_list[i])
        float_list.append(missD)
        float_list.append(missD)
    return float_list


def instrument_type(ns):
    """
    This function gives the total list of instrument types.
    The size of list depends on ns = NSUB = number of subsets.
    """
    float_list = []
    i = 0
    while i < ns:
        float_list.append(8.0)
        i = i + 1
    return float_list

def day_of_occurance_qualifier(d1_list, d2_list, d3_list, d4_list, d5_list, d6_list, d7_list):
    """
    This functions return a list of day of occrurance qualifiers.
    If the extreme daily value occurred on only one day, the day of occurrence qualifier
    shall be set to 0. If the extreme daily value occurred on more than one day, the first
    day shall be reported for 0 04 003 and the day of occurrence qualifier shall be set to 1.
    If the extreme daily value is missing, the day of occurrence qualifier shall be set to 3.
    The input in this function is list of the days when the extreme daily value occured.
    If the value occured more than once the value of day is increased with 50.
    """
    q_list = []
    d_list_of_lists = [d1_list, d2_list, d3_list, d4_list, d5_list, d6_list, d7_list]
    for sub in range(0, len(d1_list)):
        for d_list in d_list_of_lists:
            if d_list[sub] == '-1e+100':
                q_list.append(3)
            elif int(d_list[sub]) >= 1 and int(d_list[sub]) <= 31:
                q_list.append(0)
            elif int(d_list[sub]) > 31 and int(d_list[sub]) <= 81:
                q_list.append(1)
            else:
                q_list.append(3)
    return q_list

def precipitation(str_value):
    """
    Function retuns value for precipitation with one decimal point.
    """
    return round(float(str_value), 1)

def make_missing(k_id):
    """
    This function gives right missing values according to value's id (k_id)
    """
    value = miss
    if 22 <= k_id <= 23:
        value = 31
    elif k_id == 31:
        value = 15
    elif 54 <= k_id <= 55:
        value = 31
    elif k_id == 62:
        value = 511
    return value

def not_missing(str_value, k_id):
    """
    Function gives right values according to given value (str_value) and its id (k_id).
    """
    value = int(str_value)
    if k_id == 29:
        value = int(value*12.5 + 0.5)
    elif k_id == 53 and value > 81900:
        value = 81900
    elif k_id == 64:
        value = int(str_value[:2])
    elif k_id == 65:
        value = int(str_value[-3:])
    return value

def str2int(str_list, k_id):
    """
    This function makes a string list (str_list) to a integer list (int_list).
        k_id represents the id of different values. Values are converted from string to
        integer depending on k_id. Before this function, missing values = '/' are changed
        to be '-1e+100', which in eccodes is the missing value of float type value.
        It is changed to be missing value of integer type value.
    """
    int_list = []
    for i in range (0, len(str_list)):
        if str_list[i] == '-1e+100':
            int_list.append(make_missing(k_id))
        else:
            int_list.append(not_missing(str_list[i], k_id))
    return int_list

def str2float(str_list, k_id):
    """
    This function makes a string list (str_list) to a float list (float_list).
        k_id represents the id of different values. Values are converted from string to
        float depending on k_id. Before this function, missing values = '/' are changed
        to be '-1e+100' which in eccodes is the missing value of float type value.
    """
    float_list = []
    for i in range (0, len(str_list)):
        if str_list[i] == '-1e+100' and k_id != 42:
            float_list.append(float(str_list[i]))
        elif k_id == 4 and 1.5 <= float(str_list[i]) < 3.0:
            float_list.append(2.00)
        elif k_id == 34:
            float_list.append(float(str_list[i]) * 100)
        elif k_id == 40:
            float_list.append(precipitation(str_list[i]))
        elif k_id == 41:
            float_list.append(float(str_list[i]) * 0.010)
        elif k_id == 42:
            if str_list[i] == miss or str_list[i] == '-1e+100':
                float_list.append(miss)
            else:
                float_list.append(float(str_list[i]) * 60.0)
        elif k_id == 50:
            float_list.append(float(str_list[i]) + 273.15)
        else:
            float_list.append(float(str_list[i]))
    return float_list

def make_day_list(list_of_lists, n_sub):
    """
    This function gets list of lists as input
    and it combines the lists to a result list
    by taking the first element of every list,
    then the second, and so on..
    If a single list is provided, it will be treated as a list of lists with one list.
    This function also check if the day is in range [1,31] or [51,81]. If the later, the
    result day is decreased by 50.
    """
    # Check if list_of_lists is a list of integers or other non-list elements
    if list_of_lists and not any(isinstance(item, list) for item in list_of_lists):
        # Wrap the single list in another list to make it a list of lists
        list_of_lists = [list_of_lists]
    result_list = []

    for sub in range (0, n_sub):
        for l in list_of_lists:
            if l[sub] == '-1e+100':
                result_list.append(miss)
            elif int(l[sub]) >= 51 and int(l[sub]) <= 81:
                result_list.append(int(l[sub]) - 50)
            else:
                result_list.append(int(l[sub]))
    return result_list

def make_list(list_of_lists, n_sub):
    """
    This function gets list of lists as input
    and it combines the lists to a result list
    by taking the first element of every list,
    then the second, and so on..
    If a single list is provided, it will be treated as a list of lists with one list.
    """
    # Check if list_of_lists is a list of integers or other non-list elements
    if list_of_lists and not any(isinstance(item, list) for item in list_of_lists):
        # Wrap the single list in another list to make it a list of lists
        list_of_lists = [list_of_lists]
    result_list = []

    for sub in range (0, n_sub):
        for l in list_of_lists:
            result_list.append(l[sub])
    return result_list

def make_const_list(constant_list, n_sub):
    """
    This function makes same constant list for each subset.
    """
    result_list = []
    for i in range(0, n_sub):
        for j in range(0, len(constant_list)):
            result_list.append(constant_list[j])
    return result_list
