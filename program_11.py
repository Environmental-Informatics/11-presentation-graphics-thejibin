#!/bin/env python
#  by Jibin Joseph
#
# This script serves as the solution set for assignment-11 on presentation
# graphics fro ABE65100 Environmental Informatics.  See the assignment documention 
# and repository at:
# https://github.com/Environmental-Informatics/assignment-11.git for more
# details about the assignment.

## Import Packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

def ReadData( fileName ):
    """This function takes a filename as input, and returns a dataframe with
    raw data read from that file in a Pandas DataFrame.  The DataFrame index
    should be the year, month and day of the observation.  DataFrame headers
    should be "agency_cd", "site_no", "Date", "Discharge", "Quality". The 
    "Date" column should be used as the DataFrame index. The pandas read_csv
    function will automatically replace missing values with np.NaN, but needs
    help identifying other flags used by the USGS to indicate no data is 
    availabiel.  Function returns the completed DataFrame, and a dictionary 
    designed to contain all missing value counts that is initialized with
    days missing between the first and last date of the file."""
    
    # define column names
    colNames = ['agency_cd', 'site_no', 'Date', 'Discharge', 'Quality']

    # open and read the file
    DataDF = pd.read_csv(fileName, header=1, names=colNames,  
                         delimiter=r"\s+",parse_dates=[2], comment='#',
                         na_values=['Eqp'])
    DataDF = DataDF.set_index('Date')
    
    # quantify the number of missing values
    MissingValues = DataDF["Discharge"].isna().sum()
    
    ## Remove invalid streamflow data
    DataDF.Discharge[(DataDF['Discharge']<0)]=np.nan
    
    return( DataDF, MissingValues )

def ReadMetrics( fileName ):
    """This function takes a filename as input, and returns a dataframe with
    the metrics from the assignment on descriptive statistics and 
    environmental metrics.  Works for both annual and monthly metrics. 
    Date column should be used as the index for the new dataframe.  Function 
    returns the completed DataFrame."""
    DataDF=pd.read_csv(fileName,header=0,delimiter=',',parse_dates=[0])
    DataDF = DataDF.set_index('Date')
    #print(DataDF.head())
    return( DataDF )

def ClipData( DataDF, startDate, endDate ):
    """This function clips the given time series dataframe to a given range 
    of dates. Function returns the clipped dataframe and and the number of 
    missing values."""
    
    ## Clip the data to the data range
    DataDF=DataDF.loc[startDate:endDate]
    ## Find the number of missing values
    MissingValues=DataDF['Discharge'].isna().sum()
    
    return( DataDF, MissingValues )

# the following condition checks whether we are running as a script, in which 
# case run the test code, otherwise functions are being imported so do not.
# put the main routines from your code after this conditional check.

if __name__ == '__main__':

    # define full river names as a dictionary so that abbreviations are not used in figures
    riverName = { "Wildcat": "Wildcat Creek",
                  "Tippe": "Tippecanoe River" }
    
    ## Define the metrics to be imported
    metrics={"Annual":"Annual_Metrics.csv",
             "Monthly":"Monthly_Metrics.csv"}
    
    fileName = { "Wildcat": "WildcatCreek_Discharge_03335000_19540601-20200315.txt",
                 "Tippe": "TippecanoeRiver_Discharge_03331500_19431001-20200315.txt" }
    
    ## Define plot colors
    color={"Wildcat":'red',
           "Tippe":'green'}
    marker={"Wildcat":'*',
           "Tippe":'o'}
    
    # define blank dictionaries (these will use the same keys as fileName)
    DataDF = {}
    MissingValues = {}
    
    for file in fileName.keys():
        
        #print( "\n", "="*50, "\n  Working on {} \n".format(file), "="*50, "\n" )
        
        DataDF[file], MissingValues[file] = ReadData(fileName[file])
        #print( "-"*50, "\n\nRaw data for {}...\n\n".format(file), DataDF[file].describe(), "\n\nMissing values: {}\n\n".format(MissingValues[file]))
        
        # clip to consistent period
        DataDF[file], MissingValues[file] = ClipData( DataDF[file], '2014-10-01', '2019-09-30' )
        #print( "-"*50, "\n\nSelected period data for {}...\n\n".format(file), DataDF[file].describe(), "\n\nMissing values: {}\n\n".format(MissingValues[file]))
        
        plt.figure(1)
        plt.plot(DataDF[file]['Discharge'],label=riverName[file],color=color[file])
        
        
        ReadDataDF={}
        for type_met in metrics.keys():
            ReadDataDF[type_met]=ReadMetrics(metrics[type_met])
            
            
            if type_met=='Annual':
                #ReadDataDF[type_met][ReadDataDF[type_met]['Station']==file].index
                plt.figure(2)
                plt.plot(ReadDataDF[type_met][ReadDataDF[type_met]['Station']==file].index,
                         ReadDataDF[type_met]['Coeff Var'].loc[ReadDataDF[type_met]
                ['Station']==file],label=riverName[file],color=color[file],
                linestyle='None',marker=marker[file])
                
                #ReadDataDF[type_met][ReadDataDF[type_met]['Station']==file].index
                plt.figure(3)
                plt.plot(ReadDataDF[type_met]['Tqmean'][ReadDataDF[type_met]
                ['Station']==file],label=riverName[file],color=color[file],
                marker=marker[file])
    
                plt.figure(4)
                plt.plot(ReadDataDF[type_met][ReadDataDF[type_met]['Station']
                ==file].index,ReadDataDF[type_met]['R-B Index'][ReadDataDF[type_met]
                ['Station']==file].values,label=riverName[file],color=color[file],
                marker=marker[file])
                
                ## Return Period Calculations
                ReadDataDF[type_met] = ReadDataDF[type_met].drop(columns=
                          ['site_no','Mean Flow','Tqmean','Median Flow',
                           'Coeff Var','Skew','R-B Index','7Q','3xMedian'])
                peak = ReadDataDF[type_met][ReadDataDF[type_met]['Station']==file]
                                             
                ## Sort in descending
                flow = peak.sort_values('Peak Flow', ascending=False)
                ## Calculate the rank and reversing the rank to give the largest discharge rank of 1
                ranks1 = stats.rankdata(flow['Peak Flow'], method='average')
                ranks2 = ranks1[::-1]
                ## Calculate exceedence probability using Weibull plotting position
                weibull = [100*(ranks2[i]/(len(flow)+1)) for i in range(len(flow))]
                ## Plot the exceedance probability
                plt.figure(6)
                plt.scatter(weibull, flow['Peak Flow'],label=riverName[file],
                            color=color[file], marker=marker[file])
                
            if type_met=='Monthly':
                ## Create monthly dataframe
                monthly = ReadDataDF[type_met][ReadDataDF[type_met]['Station']==file]
                ## Annual monthly average values
                cols=['Mean Flow']
                m=[3,4,5,6,7,8,9,10,11,0,1,2]
                index=0
                MonthlyAverages=pd.DataFrame(0,index=range(1,13),columns=cols)
                
                for i in range(12):
                    MonthlyAverages.iloc[index,0]=monthly['Mean Flow'][m[index]::12].mean()
                    index+=1
                ## Plot Annual Average Monthly values
                plt.figure(5)
                plt.scatter(MonthlyAverages.index.values, 
                         MonthlyAverages['Mean Flow'].values, 
                         label=riverName[file], color=color[file])
    ## Adding title,legend,label
    plt.figure(1)
    plt.title('Daily Flow for last 5 years')
    plt.legend()
    plt.xlabel('Date')
    plt.ylabel('Discharge (cfs)')
    plt.tight_layout()
    plt.savefig('Daily_Flow.png',dpi=96)
    plt.close(1)
    
    ## Adding title,legend,label
    plt.figure(2)
    plt.title('Annual Coefficient of Variation')
    plt.legend()
    plt.xlabel('Date (years)')
    plt.ylabel('Coefficient of Variation')
    plt.tight_layout()
    plt.savefig('Annual_COV.png',dpi=96)
    plt.close(2)
    
    ## Adding title,legend,label
    plt.figure(3)
    plt.title('Annual Tqmean')
    plt.legend()
    plt.xlabel('Date (years)')
    plt.ylabel('TQmean')
    plt.tight_layout()
    plt.savefig('Annual_TQmean.png',dpi=96)
    plt.close(3)
    
    ## Adding title,legend,label
    plt.figure(4)
    plt.title('Annual RB Index')
    plt.legend()
    plt.xlabel('Date (years)')
    plt.ylabel('RB Index')
    plt.tight_layout()
    plt.savefig('Annual_RBindex.png',dpi=96)
    plt.close(4)
    
    ## Adding title,legend,label
    plt.figure(5)
    plt.title('Average Annual Monthly Flow')
    plt.legend()
    plt.ylabel('Discharge (cfs)')
    plt.xlabel('Month')
    plt.tight_layout()
    plt.savefig('Average_Annual_Monthly_Flow.png', dpi = 96)
    plt.close(5)
    
    ## Adding title,legend,label
    plt.figure(6)
    plt.title('Plot of Return Period')
    plt.legend()
    plt.ylabel('Peak Discharge (cfs)')
    plt.xlabel('Exceedance Probability (%)')
    plt.tight_layout()
    plt.savefig('Annual_Return_Period.png', dpi = 96)
    plt.close(6)
                
    
        
    
    
 