#! /usr/bin/env python3


import argparse
import csv
from modules import PlotGraph

def main():
    parser=argparse.ArgumentParser(
        description='Create a dist_vs_int graph from a CSV file'
    )
    parser.add_argument(
        'infile',type=str,
        help='Input CSV file'
    )
    parser.add_argument(
        'name',type=str,default=None,nargs='?',
        help='Name of graph'
    )

    args=parser.parse_args()
    infile=args.infile
    name=args.name or infile

    print('Creating graph %s from %s' % (name,infile))

    dictdata=[]
    with open(infile,'r') as f:
        reader=csv.DictReader(f,fieldnames=('dist','intensity'))
        for row in reader:
            dictdata.append(row)

    plot=PlotGraph(
        event=getEventData(name),
        data=getGraphData(dictdata),
        graphtype='dist_vs_intensity',
        title=name
    )
    plot.save(name+'.png')

class Simple:
    pass

def getEventData(name):
    event=Simple()

    return event

def getGraphData(dictdata):

    data=Simple()
    data.id='none'
    data.min_x=50
    data.max_x=5000

    scatterdata={
        'data':[],
        'legend':'Raw input data',
        'class':'scatterplot',
    }
    for row in dictdata:
        pt={
            'x':float(row['dist']),
            'y':float(row['intensity'])
        }
        scatterdata['data'].append(pt)
    data.scatterdata=scatterdata
    
    return data
    
    
if __name__=='__main__':
    main()

