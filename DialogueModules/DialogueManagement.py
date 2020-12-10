"""
authors: Zirong Chen, Haotian Xue
DM for Dialogue System

11/25/2020
"""
import os
from utils import randomizeAction, bcolors


class DialogueManager(object):
    def __init__(self):
        self.utterance = None
        self.namespace = [file[:-4] for file in os.listdir('IntentDetails/')]
        self.orderSequence = ['bread', 'cheese', 'vegetable', 'sauce', 'extra']
        self.currentDir = 'TempRes/'
        self.warning = False

    def load(self, utterance):
        self.utterance = utterance

    def getNamespace(self):
        return self.namespace

    def tell(self):
        """
        This function is used for the recognition of user utterance, or say intention detection
        :return: flag(str, matched intent), keyword(str, matched keyword under intent), warning(boolean, whether new word occurs)
        """
        flag = "UKN"
        keyword = None
        self.warning = False

        initial_utterance = self.utterance.lower()
        # utterance = initial_utterance.split(" ")
        # Here is where the bug is!
        utterance = initial_utterance

        reference = {}
        for name in self.namespace:
            fname = 'IntentDetails/{}.txt'.format(name)
            with open(fname, 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    reference[name] = line.split(", ")

        for intent in reference.keys():
            for option in reference[intent]:
                if option != "" and option != " " and option in utterance:
                    # We need to handle invalid options since we do not split user inputs any more.
                    keyword = option
                    flag = intent

        # Human-in-the-loop error handling
        # TODO: relations between new intentions need to be fixed
        if flag == 'UKN':
            self.warning = True
            namestring = ""
            for name in self.namespace:
                namestring = namestring + name + ", "

            print(f"{bcolors.FAIL}-- Warning, This system currently can not interpret your input --{bcolors.ENDC}")
            print(f"{bcolors.HEADER}-- It needs your idea on your input intent for further learning --{bcolors.ENDC}")
            print(f"{bcolors.WARNING}-- However, your conversation will be continued --{bcolors.ENDC}")

            intent = input(
                "Fail to map this sentence: \" {} \" to existing intents: {} what is your intention? \n".format(
                    initial_utterance, namestring))
            keyword = input(
                "In addtion to intention, what is the keyword in your input? Remember to keep it unique! \n"
            )
            fname = 'IntentDetails/{}.txt'.format(intent)

            with open(fname, 'a+', encoding='utf-8') as f:
                f.write(initial_utterance + ", ")
                flag = intent

            if intent not in self.namespace:
                self.namespace.append(intent)

        return flag, keyword, self.warning

    def getAction(self, lastIntent):
        """
        Default Dialogue path: Greet+Bread -> Cheese -> Vegetable -> Sauce -> Extra -> Farewell
        :return: system action(str), the last intent given by the system
        """
        flag, keyword, _ = self.tell()

        if flag == 'decline' and lastIntent != 'extra':
            fname = 'TempRes/{}.txt'.format(lastIntent)
            keyword = 'nothing'
            with open(fname, 'a+', encoding='utf-8') as f:
                f.write("Nothing")

            next_intent = self.orderSequence[self.orderSequence.index(lastIntent) + 1]

            return randomizeAction('DialogueTemplates/addition_{}_{}.txt'.format(next_intent, lastIntent)).format(
                keyword, lastIntent), next_intent

        if flag == 'decline' and lastIntent == 'extra':
            fname = 'TempRes/{}.txt'.format(lastIntent)
            keyword = 'nothing'
            with open(fname, 'a+', encoding='utf-8') as f:
                f.write("Nothing")

            return randomizeAction('DialogueTemplates/conclusion_extra.txt').format(keyword, 'extra'), 'conclusion'

        # greet -> greet + bread
        if flag == 'greet':
            return randomizeAction('DialogueTemplates/greet.txt'), 'bread'

        if flag == 'bread':
            fname = 'TempRes/{}.txt'.format(flag)
            with open(fname, 'a+', encoding='utf-8') as f:
                f.write(keyword)

            return randomizeAction('DialogueTemplates/addition_cheese_bread.txt').format(keyword, flag), 'cheese'

        if flag == 'cheese':
            fname = 'TempRes/{}.txt'.format(flag)
            with open(fname, 'a+', encoding='utf-8') as f:
                f.write(keyword)

            return randomizeAction('DialogueTemplates/addition_vegetable_cheese.txt').format(keyword, flag), 'vegetable'

        if flag == 'vegetable':
            fname = 'TempRes/{}.txt'.format(flag)
            with open(fname, 'a+', encoding='utf-8') as f:
                f.write(keyword)

            return randomizeAction('DialogueTemplates/addition_sauce_vegetable.txt').format(keyword, flag), 'sauce'

        if flag == 'sauce':
            fname = 'TempRes/{}.txt'.format(flag)
            with open(fname, 'a+', encoding='utf-8') as f:
                f.write(keyword)

            return randomizeAction('DialogueTemplates/addition_extra_sauce.txt').format(keyword, flag), 'extra'

        if flag == 'extra':
            fname = 'TempRes/{}.txt'.format(flag)
            with open(fname, 'a+', encoding='utf-8') as f:
                f.write(keyword)

            return randomizeAction('DialogueTemplates/conclusion_extra.txt').format(keyword, flag), 'conclusion'

    def getConclusion(self):
        """
        generate conclusion from current directory
        :return: conclusion sentence
        """
        res = {}
        for file in os.listdir(self.currentDir):
            fname = self.currentDir + file
            with open(fname, 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    res[file[:-4]] = line

        return randomizeAction('DialogueTemplates/summary.txt').format(res['bread'], res['cheese'], res['vegetable'],
                                                                       res['sauce'], res['extra'])
