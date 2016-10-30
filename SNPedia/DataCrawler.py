
from bs4 import BeautifulSoup

import urllib.request
import pprint
import json
import pandas as pd
import argparse
import os


from GenomeImporter import PersonalData


class SNPCrawl:
    def __init__(self, rsids=[], filepath=None, snppath=None):
        if filepath and os.path.isfile(filepath):
            self.importDict(filepath)
            self.rsidList = []
        else:
            self.rsidDict = {}
            self.rsidList = []

        if snppath and os.path.isfile(snppath):
            self.importSNPs(snppath)
        else:
            self.snpdict = {}

        for rsid in rsids:
            print(rsid)

            self.grabTable(rsid)
            print("")
        pp = pprint.PrettyPrinter(indent=1)
        pp.pprint(self.rsidDict)

        self.export()
        self.createList()

    def grabTable(self, rsid):
        try:
            url = "https://www.snpedia.com/index.php/" + rsid
            if rsid not in self.rsidDict.keys():
                self.rsidDict[rsid] = {
                    "Description": "",
                    "Variations": []
                }
                response = urllib.request.urlopen(url)
                html = response.read()
                bs = BeautifulSoup(html, "html.parser")
                table = bs.find("table", {"class": "sortable smwtable"})
                description = bs.find('table', {'style': 'border: 1px; background-color: #FFFFC0; border-style: solid; margin:1em; width:90%;'})

                if description:
                    d1 = self.tableToList(description)
                    self.rsidDict[rsid]["Description"] = d1[0][0]
                    print(d1[0][0])
                if table:
                    d2 = self.tableToList(table)
                    self.rsidDict[rsid]["Variations"] = d2[1:]
                    print(d2[1:])
        except urllib.error.HTTPError:
            print(url + " was not found or contained no valid information")

    def tableToList(self, table):
        rows = table.find_all('tr')
        data = []
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele])
        return data

    def createList(self):
        make = lambda rsname, description, variations: \
            {"Name": rsname,
             "Description": description,
             "Genotype": self.snpdict[rsname.lower()] \
             if rsname.lower() in self.snpdict.keys() else "(-;-)", \
             "Variations": str.join("<br>", variations)}

        formatCell = lambda rsid, variation : \
            "<b>" + str.join(" ", variation) + "</b>" \
                if rsid in self.snpdict.keys() and \
                   self.snpdict[rsid.lower()] == variation[0] \
                else str.join(" ", variation)

        for rsid in self.rsidDict.keys():
            curdict = self.rsidDict[rsid]
            variations = [formatCell(rsid, variation) for variation in curdict["Variations"]]
            self.rsidList.append(make(rsid, curdict["Description"], variations))

        #print(self.rsidList[:5])

    def importDict(self, filepath):
        with open(filepath, 'r') as jsonfile:
            self.rsidDict = json.load(jsonfile)

    def importSNPs(self, snppath):
        with open(snppath, 'r') as jsonfile:
            self.snpdict = json.load(jsonfile)

    def export(self):
        data = pd.DataFrame(self.rsidDict)
        data = data.fillna("-")
        data = data.transpose()
        datapath = os.path.join(os.path.curdir, "data", 'rsidDict.csv')
        data.to_csv(datapath)
        filepath = os.path.join(os.path.curdir, "data", 'rsidDict.json')
        with open(filepath,"w") as jsonfile:
            json.dump(self.rsidDict, jsonfile)


parser = argparse.ArgumentParser()


parser.add_argument('-f', '--filepath', help='Filepath for 23andMe data to be used for import', required=False)
parser.add_argument('-l', '--load', help='Filepath for json dump to be used for import', required=False)

args = vars(parser.parse_args())

rsid = ["rs1815739", "Rs53576", "rs4680", "rs1800497", "rs429358", "rs9939609", "rs4988235", "rs6806903" , "rs4244285"]

if args["filepath"]:
    personal = PersonalData(args["filepath"])
    rsid += personal.snps[:550]
if args['load']:
    clCrawl = SNPCrawl(rsids=rsid, filepath=args["load"])

else:
    if __name__ == "__main__":
        clCrawl = SNPCrawl(rsids=rsid)