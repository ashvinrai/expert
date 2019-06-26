from tabulate import tabulate
from git import *
from statistics import *
from os import listdir
from os.path import isfile, join
import numpy as np
import time
import datetime

class Expert():
    out = []
    directory = None
    repo = None
    authorHash = dict()
    commitHash = dict()
    sizeHash = dict()
    commitSizes = []
    directoryAverage = 0
    directorySTD = 1
    compare = False

    def __init__(self, directory):
        self.directory = directory
        self.repo = Repo(path=directory)


    def traverseDirectory(self, processFile, filepath=""):
        for f in listdir(filepath):
            joined = join(filepath, f)
            if isfile(joined):
                processFile(joined)
            else:
                self.traverseDirectory(processFile, joined)


    def getRepoScore(self, filepath):
        filepath = filepath.replace(self.directory, "")
        for commit, lines in self.repo.blame('HEAD', filepath):
            self.commitSizes.append(len(lines))
            commitsPerFileChecked = len(self.commitSizes)
            if (commitsPerFileChecked % 250 == 0):
                print(f"Getting commit sizes for: {commitsPerFileChecked} files per commit")


    def getCommits(self, filepath):
        self.authorHash = dict()
        self.commitHash = dict()
        self.sizeHash = dict()

        for commit in self.repo.iter_commits(paths=filepath):
            self.commitHash[commit.__str__()] = commit.author.email
            self.sizeHash[commit.__str__()] = 0
            if commit.author.email not in self.authorHash:
                self.authorHash[commit.author.email] = dict(commits=[commit], numberOfCommits=1, lines=[], commentedLines=0, todoComments=0, mostRecent=commit.committed_datetime)
            else:
                self.authorHash[commit.author.email]["commits"].append(commit)
                self.authorHash[commit.author.email]["numberOfCommits"] = self.authorHash[commit.author.email]["numberOfCommits"] + 1
                self.authorHash[commit.author.email]["mostRecent"] = max(commit.committed_datetime, self.authorHash[commit.author.email]["mostRecent"])



    def blameFiles(self, filepath):
        path = self.directory + filepath
        self.traverseDirectory(self.blameFile, path)


    def blameFile(self, filepath):
        filepath = filepath.replace(self.directory, "")
        for commit, lines in self.repo.blame('HEAD', filepath):
            if commit.__str__() in self.commitHash:
                author = self.commitHash[commit.__str__()]
                self.sizeHash[commit.__str__()] = len(lines)
                self.authorHash[author]["lines"].extend(lines)
                for line in lines:
                    if line.startswith("//"):
                        self.authorHash[author]["commentedLines"] = self.authorHash[author]["commentedLines"] + 1
                        if "TODO" in line:
                            self.authorHash[author]["todoComments"] = self.authorHash[author]["todoComments"] + 1


    def generateScore(self):
        output = []
        for key in self.authorHash.keys():
            author = self.authorHash[key]
            commitSizes = []
            for commit in author["commits"]:
                commitSizes.append(self.sizeHash[commit.__str__()])

            output.append(dict(
                author=key, 
                numberOfCommits=author["numberOfCommits"], 
                numberOfLines=len(author["lines"]),
                commentedLines=author["commentedLines"],
                medianSize=median(sorted(commitSizes)),
                todoComments=author["todoComments"],
                mostRecentCommit=author["mostRecent"]
            ))

        self.score(output)

        sortedOut = sorted(output, key=lambda k: k["score"], reverse=True)

        self.out = sortedOut

        return sortedOut
        

    def print(self, verbose=False):
        if verbose:
            print(tabulate(self.out[:3], headers="keys", tablefmt='orgtbl'))
        else:
            for entry in self.out[:3]:
                author = entry["author"]
                score = entry["score"]
                print(f"{author}: {score}")


    def scoreDirectory(self, path, verbose=False, compare=None):
        if compare:
            self.compare = True
            self.traverseDirectory(self.getRepoScore, self.directory + compare)
            directoryAverage = mean(self.commitSizes)
            directorySTD = np.std(self.commitSizes)
            self.directoryAverage = directoryAverage
            self.directorySTD = directorySTD
            print(f"Applying directory score: {directoryAverage} with standard deviation {directorySTD}")


        self.getCommits(path)
        self.blameFiles(path)
        self.generateScore()
        self.print(verbose)


    def score(self, output):
        epochArray = [entry["mostRecentCommit"].timestamp() for entry in output] + [datetime.datetime.today().timestamp()]
        stdTime = np.std(epochArray)
        meanTime = mean(epochArray)

        numCommitsArray = [entry["numberOfCommits"] for entry in output]
        stdCommits = np.std(numCommitsArray)
        meanCommits = mean(numCommitsArray)

        for entry in output:
            timeSTD = (entry["mostRecentCommit"].timestamp() - meanTime) / stdTime
            commitSTD = (entry["numberOfCommits"] - meanCommits) / stdCommits
            lineSTD = (entry["numberOfLines"] - self.directoryAverage) / self.directorySTD

            numCodeLines = entry["numberOfLines"] - entry["commentedLines"]
            weightedLineScore = numCodeLines + .2*(entry["commentedLines"] - entry["todoComments"])

            if self.compare:
                if lineSTD < 0:
                    weightedLineScore = weightedLineScore / (abs(lineSTD) + 1)
                else:
                    weightedLineScore = weightedLineScore * (abs(lineSTD) + 1)

            if timeSTD < 0:
                weightedLineScore = weightedLineScore / (abs(timeSTD) + 1)
            else:
                weightedLineScore = weightedLineScore * (abs(timeSTD) + 1)

            if commitSTD < 0:
                weightedLineScore = weightedLineScore / (abs(commitSTD) + 1)
            else:
                weightedLineScore = weightedLineScore * (abs(commitSTD) + 1)

            entry["unweightedScore"] = weightedLineScore

        scoreSum = sum([entry["unweightedScore"] for entry in output])
        for entry in output:
            entry["score"] = round(entry["unweightedScore"] / scoreSum, 2)
