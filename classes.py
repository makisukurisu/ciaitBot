import datetime
class Day():

    DayNames = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    def __init__(self, Day, Groups):
        ''' 
        Day - Date in ISO format\n
        Groups - array of Group objects
        '''
        self.Groups = Groups
        self.Day = Day
        self.DayOrdinal = datetime.date.fromisoformat(Day).toordinal()
    
    def findGroup(self, Name):
        Name = str(Name).upper()
        for x in self.Groups:
            if x.Name == Name:
                return x
    def findGroups(self, Name):
        Name = str(Name).upper()
        retArray = []
        for x in self.Groups:
            if str(x.Name).find(Name) >= 0:
                retArray.append(x)
        return retArray
    
    def getAll(self):
        return self.Groups
    def getDayInfo(self):
        return "{} - {} ({}), {} Групп".format(Day.DayNames[datetime.date.fromisoformat(self.Day).isoweekday()-1], self.Day, self.DayOrdinal, len(self.Groups))

class Group():

    def __init__(self, Name, Pairs):
        try:
            self.Name = str(Name).upper()
        except:
            raise("Name is not string")
        if type(Pairs) == type([]):
            if len(Pairs) == 4:
                for x in Pairs:
                    if type(x) == type(Pair()):
                        x.assignGroup(self)
                    else:
                        raise("Pair {} is not object Pair()".format(list(Pairs).index(x)+1))
                self.Pairs = Pairs
            else:
                raise("Pairs (array) are not len 4")
        else:
            raise("Pairs are not array of Pair()")
    def getPairs(self):
        return self.Pairs
    def __str__(self) -> str:
        return self.Name
    
class Pair():

    def __init__(self, name = None, teacher = None):
        self.Group = None #Yet to be assigned
        self.Name = name
        self.Teacher = teacher
    def assignGroup(self, group):
        self.Group = group
    def __str__(self) -> str:
        return "{} - {} ({})".format(self.Name, self.Teacher, str(self.Group))

# grp1 = Group("kp-181", [Pair("Д", "Ф"), Pair("Д", "Ф"), Pair("Ф", "С"), Pair("Ф", "С")])
# grp2 = Group("kp-182", [Pair("Ф", "С"), Pair("Ф", "С"), Pair("Д", "Ф"), Pair("Д", "Ф")])
# day1 = Day("2021-05-24", [grp1, grp2])

# def getAllTeacher(teacher):

#     retArray = []
#     for group in day1.Groups:
#         for pair in group.Pairs:
#             if pair.Teacher == teacher:
#                 retArray.append({"Group": str(group), "Pair": group.Pairs.index(pair)+1})
#     return retArray

# print(getAllTeacher("Ф"))