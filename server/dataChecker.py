from mongoDb import mongoDb
from objects import *
# from settings import Setting

### This file checks if the data in the database is valid ###

class InvalidData():

    def __init__(self, data):
        self.data = data['data']
        self.collection = data['collection']
        self.error = data['error']


class DataChecker:

    def __init__(self):
        self.db = mongoDb()
        allCollections = self.db.getAllCollectionNames()
        self.allData = {}
        for collection in allCollections:
            self.allData[collection] = self.db.read({}, collection)

        self.collectionObjectMap = {
        # add all collections here
        }

        allCollectionsInObjectMap = [x for x in self.collectionObjectMap]
        for x in allCollections:
            if x not in allCollectionsInObjectMap:
                raise ValueError('Please add key : ' + str(x) +
                                 ' and object to collection object map')

    # run this to get all data and checks if data is valid
    def checkInvalidData(self):
        for collection, data_list in self.allData.items():
            for count, data in enumerate(data_list):
                print(collection + ' - ' + str(count + 1) + ' / ' +
                      str(len(data_list)))
                print(collection, data['_id'])

                self.collectionObjectMap[collection](data)


if __name__ == '__main__':
    checker = DataChecker()
    checker.checkInvalidData()

    # data = db.read({'_id': 'RfrGD87L8AHKrw4Nj6HkeQXpZ8qLvd9m'},
    #                'SalesOrders',
    #                findOne=True)
    # SalesOrder(data)
    