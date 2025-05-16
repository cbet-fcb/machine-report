from pymongo import MongoClient
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from AppConfig import AppConfig
import time
import os
# from pubSub import PubSub

class TTLIndexMaker:
    # Format:
    # {
    #   "CollectionName": {"field_name": "processedAt", "expiration_in_seconds": 604800}
    # }
    def __init__(self, collection_name: str = None, field_name: str = None, expiration: int = 3600):
        self.ttl_indexes = {}
        self.MINUTE = 60 
        self.HOUR = 60 * self.MINUTE
        self.DAY = 24 * self.HOUR
        self.WEEK = 7 * self.DAY
        self.MONTH = 4 * self.WEEK

        if collection_name and field_name:
            self.add(collection_name, field_name, expiration)

    def add(self, collection_name: str, field_name: str, expiration: int = 3600):
        self.ttl_indexes[collection_name] = {
            "field_name": field_name,
            "expiration_in_seconds": expiration
        }

    def make_ttl_index(self) -> dict:
        """
        Returns:
            dict: {
                "CollectionName": {
                    "field_name": field_name,
                    "expiration_in_seconds": expiration
                }
            }
        """
        return self.ttl_indexes

    def get_field_for_collection(self, collection_name: str) -> str:
        """
        Optional: Gets the TTL field for a given collection
        """
        return self.ttl_indexes.get(collection_name, {}).get("field_name", None)


class mongoDb:
    def __init__(self, ttl_index_dict: dict = {}):
        
        
        if AppConfig().getEnvironment() == 'cloudprod':
            raise ValueError("Have not supported cloud production environment")
            # uri = os.getenv('MONGO_URI_ACCOUNTING')
            
            # if uri is None:
            #     raise Exception(
            #         'MONGO_URI_ACCOUNTING environment variable is not set')

            # self.client = MongoClient(uri,
            #                           server_api=ServerApi('1'),
            #                           tz_aware=True)
            # databaseName = ''
        if AppConfig().getEnvironment() == 'clouddev':
            raise ValueError("Have not supported cloud development environment")
            # uri = ""
            # self.client = MongoClient(uri,
            #                           server_api=ServerApi('1'),
            #                           tz_aware=True)
            # databaseName = ''

        # testEnvironment is used for automated testing while the actual is used for production / development
        if AppConfig().getEnvironment() == 'localdev':
            self.client = MongoClient('localhost', 27017, tz_aware=True)
            databaseName = 'testMachineReport'
        if AppConfig().getEnvironment() == 'localTest':
            self.client = MongoClient('localhost', 27017, tz_aware=True)
            databaseName = 'testMachineReport'
        if AppConfig().getEnvironment() == 'localprod':
            self.client = MongoClient('localhost', 27017, tz_aware=True)
            databaseName = 'testMachineReport'

        self.db = self.client[databaseName]

        for collection_name, config in ttl_index_dict.items():
            field_name = config.get("field_name", "processed_at")
            expire_seconds = config.get("expiration_in_seconds", 3600)
            self.createTTLIndex(collection_name, field_name, expire_seconds)

    def ping(self):
        try:
            start_time = time.time()  # get current time
            self.client.admin.command('ping')
            end_time = time.time()  # get current time after ping

            elapsed_time = end_time - start_time  # calculate elapsed time
            elapsed_time_ms = elapsed_time * 1000  # convert to milliseconds

            print(
                "Pinged your deployment. You successfully connected to MongoDB! Response time: %f ms"
                % elapsed_time_ms)
            return elapsed_time_ms
        except Exception as e:
            print(e)

    def create(self, data, collection_name, session=None):
        # Insert a document into the collection and return the created data.
        print("Creating data in collection: " + collection_name +
              " with data: " + str(data))
        start_time = time.time()  # get current time
        result = self.db[collection_name].insert_one(data, session=session)
        end_time = time.time()  # get current time after ping

        elapsed_time = end_time - start_time  # calculate elapsed time
        elapsed_time_ms = elapsed_time * 1000  # convert to milliseconds

        print(collection_name + " Response time: %f ms" % elapsed_time_ms)
        return self.db[collection_name].find_one({"_id": result.inserted_id},
                                                 session=session)

    def read(self, query, collection_name, projection={}, session=None,findOne=False, count=False):
        # Read documents from the collection.
        start_time = time.time()  # get current time

        if findOne:
            data = self.db[collection_name].find_one(query, projection, session=session)
        else:
            data = list(self.db[collection_name].find(query,
                                                    projection,
                                                    session=session))
        end_time = time.time()  # get current time after ping

        elapsed_time = end_time - start_time  # calculate elapsed time
        elapsed_time_ms = elapsed_time * 1000  # convert to milliseconds

        print(collection_name + ' ' + str(query) +
              " Response time: %f ms" % elapsed_time_ms)
        return data

    def readWithPagination(self,
                        query,
                        collection_name,
                        page,
                        limit,
                        projection={},
                        sort=None,
                        reverse=False,
                        session=None):
        
        if sort is None:
            sort = {'keyToSort': None, 'sortOrder': None}

        if limit is None or limit < 1:
            if page > 1:
                raise ValueError("Page must be 1 if limit is None or less than 1")

        start_time = time.time()
        totalDocuments = self.db[collection_name].count_documents(query)

        if limit is None:
            limit = totalDocuments

        cursor = self.db[collection_name].find(query, projection, session=session)

        if reverse:
            cursor = cursor.sort([('$natural', -1)])

        if isinstance(sort, dict) and sort.get('keyToSort') and sort.get('sortOrder') is not None:
            cursor = cursor.sort(sort['keyToSort'], sort['sortOrder'])

        skip = (page - 1) * limit
        cursor = cursor.skip(skip).limit(limit)
        data = list(cursor)

        totalPages = (totalDocuments + limit - 1) // limit if totalDocuments > 0 else 0

        elapsed_time_ms = (time.time() - start_time) * 1000
        print(f"{collection_name} {query} Response time: {elapsed_time_ms:.2f} ms")

        return {
            'data': data,
            'page': page,
            'limit': limit,
            'totalDocuments': totalDocuments,
            'totalPages': totalPages
        }

    def createTTLIndex(self, collection_name, field_name='createdAt', expire_seconds=3600):
        """
        Create a TTL index on the specified field in the collection.
        If a conflicting index exists, drop it first.
        """
        try:
            coll = self.db[collection_name]
            existing_indexes = coll.index_information()

            # Look for existing TTL index
            for index_name, index_info in existing_indexes.items():
                if index_info.get('key') == [(field_name, 1)]:
                    if index_info.get('expireAfterSeconds') != expire_seconds:
                        print(f"[TTL] Dropping outdated TTL index '{index_name}' on {collection_name}...")
                        coll.drop_index(index_name)
                    break

            # (Re)create index
            result = coll.create_index(
                [(field_name, 1)],
                expireAfterSeconds=expire_seconds,
                name=f"{field_name}_1"
            )
            print(f"[TTL] Index created: {collection_name}.{field_name} with expiration {expire_seconds}s")
            return result

        except Exception as e:
            raise RuntimeError(f"[TTL] Failed on {collection_name}.{field_name}: {e}")
            
    def update(self,
               query,
               new_values,
               collection_name,
               checkVersion=False,
               incrementVersion=True,
               session=None):
        # Update documents in the collection.
        print('Updating data in collection: ' + collection_name +
              ' with query: ' + str(query) + ' and new values: ' +
              str(new_values))

        if checkVersion:
            latestData = self.db[collection_name].find_one(
                {
                    '_id': query['_id'],
                    '_version': query['_version']
                },
                session=session)
            if latestData is None:
                raise Exception(
                    'Your data is outdated. Please refresh the page and try again.'
                )
        else:
            latestData = self.db[collection_name].find_one(
                {'_id': query['_id']}, session=session)

        newVersion = latestData['_version'] + 1
        oldVersion = newVersion - 1
        new_values['_version'] = newVersion

        # we update the query with the new version
        if checkVersion == True:
            query['_version'] = oldVersion
        else:
            if '_version' in query:
                query.pop('_version')

        def find_instance(d, o, path=""):
            if isinstance(d, dict):
                for key, value in d.items():
                    current_path = f"{path}.{key}" if path else key  # Construct the current path

                    if isinstance(value, dict):
                        # Recursively check nested dictionaries
                        found, instance_path = find_instance(
                            value, o, current_path)
                        if found:
                            print('object detected', instance_path)
                    elif isinstance(value, list):
                        # Recursively check nested lists
                        for i, item in enumerate(value):
                            found, instance_path = find_instance(
                                item, o, f"{current_path}[{i}]")
                            if found:
                                print('object detected', instance_path)
                    elif isinstance(value, o):
                        # Return True and the path if a value is an instance of the specified class
                        print('object detected', current_path)

            elif isinstance(d, list):
                for i, item in enumerate(d):
                    found, instance_path = find_instance(
                        item, o, f"{path}[{i}]")
                    if found:
                        print('object detected', instance_path)

            # Return False and an empty string if no instance of the class is found
            return False, ""

        # from objects import Unit
        # find_instance(new_values, Unit)

        if incrementVersion == False:
            new_values.pop('_version')

        result = self.db[collection_name].update_many(query, {
            '$set': new_values,
        },
                                                      session=session)

        if incrementVersion == True:
            if result.modified_count == 0:
                raise ValueError("No documents were modified.")

        if checkVersion == True:
            query.pop('_version')

        updatedData = self.read(query, collection_name, session=session)
        return updatedData

    def delete(self, query, collection_name, session=None):
        # Delete documents from the collection.
        print('Deleting data in collection: ' + collection_name +
              ' with query: ' + str(query))

        if query == {} and AppConfig().getIsProductionEnvironment():
            raise Exception(
                'You cannot delete all documents in the collection in production environment'
            )

        deleted_result = self.db[collection_name].delete_many(query,
                                                              session=session)

        if deleted_result.deleted_count > 0:
            return deleted_result.deleted_count
        else:
            return 'No document to delete'

    def getAllCollections(self):
        # Get all collections in the database.
        return self.db.list_collection_names()

    def deleteAllDataInDatabaseForDevEnvironment(self):
        # Delete all documents from the collection. Only works in the dev environment

        if not AppConfig().getIsDevEnvironment():
            raise Exception(
                'This function is only available in the localdev environment')

        allCollections = self.getAllCollections()
        for x in allCollections:
            self.db[x].delete_many({})

    def createTransaction(self, updateFunction, pubSubMessage=None):
        if AppConfig().getIsCloudEnvironment():
            with self.client.start_session() as session:
                with session.start_transaction():
                    try:
                        res = updateFunction(session)
                        # Commit the transaction

                        if pubSubMessage is not None:
                            topic = pubSubMessage['topic']
                            message = pubSubMessage['message']
                            PubSub().publishMessage(topic, message)

                        session.commit_transaction()
                        print("Transaction committed successfully.")
                        return res
                    except Exception as e:
                        print("Transaction aborted due to an error:", e)
                        # Abort the transaction
                        session.abort_transaction()
        else:
            res = updateFunction(None)
            return res

    def getAllCollectionNames(self):
        # Get all collections in the database.
        return self.db.list_collection_names()


if __name__ == '__main__':
    mongoDb().ping()
    pass

