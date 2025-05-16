from objects import *
import time
import json
import os
import dotenv

dotenv.load_dotenv()

from mongoDb import TTLIndexMaker
ttl = TTLIndexMaker() # Time to live index maker for mongoDB

ttl.add(collection_name='Image', field_name='processed_at', expiration=ttl.WEEK)
ttl.add(collection_name='Monitoring', field_name='process_begins_at', expiration=ttl.WEEK)

db = mongoDb(ttl_index_dict=ttl.make_ttl_index())

class MonitoringActions:
    def __init__(self):
        pass

    def __check_if_env_is_in_local(self) -> bool:
        from AppConfig import AppConfig
        ac = AppConfig()
        return ac.getisLocalDevEnvironment() or ac.getisLocalEnvironment()

    def feedback(self,
                 id: str, 
                 does_match: bool, 
                 machine_report_monitoring_cname: str = 'Monitoring',
                 test_flag = False
        ):
        if test_flag and self.__check_if_env_is_in_local():
            db.delete(query={}, collection_name=machine_report_monitoring_cname)
        
        machine_report_data = db.read(query={'_id': id}, collection_name=machine_report_monitoring_cname)
        
        SYSTEM_MESSAGE = 'The system'
        
        if not machine_report_data:
            return f"{SYSTEM_MESSAGE} could not find the data. Please try again"
        elif does_match:
            db.delete(query={**machine_report_data}, collection_name=machine_report_monitoring_cname)
            message = ''
            message = f'{SYSTEM_MESSAGE} has evaluated your feedback. Thank you for your feedback.' 

            return message
        
        db.update(
            query={'_id': id},
            new_values={'does_match': does_match},
            collection_name=machine_report_monitoring_cname,
        )
        return f'{SYSTEM_MESSAGE} will follow up on that. If this happens once again to you, please provide feedback immediately. Thank you for your feedback.'

class ReportActions:
    def __init__(self, MAX_DOCUMENTS_TO_BE_STORED: int = 50):
        self.TEST_SUITE = os.getenv("TEST_SUITE_REPORT_ACTIONS", "False") == "True"
        self.ENABLE_FEEDBACK = os.getenv("TSRA_ENABLE_FEEDBACK", "False") == "True"
        self.DELETE_ALL_DATA = os.getenv("TSRA_DELETE_ALL_DATA", "False") == "True"
        self.DISABLE_SCHEDULER = os.getenv("TSRA_DISABLE_SCHEDULER", "False") == "True"
        self.DISABLE_CHECKING_OF_KEYS = os.getenv("TSRA_DISABLE_CHECKING_OF_KEYS", "False") == "True"

        self.MAX_DOCUMENTS_TO_BE_STORED = MAX_DOCUMENTS_TO_BE_STORED
        self.created_documents = 0
        pass
    
    def __delete(self, query: dict = {}, collection_name='Machine Report'):
        res = db.delete(query=query, collection_name=collection_name)
        pass

    def __createMachineReport(self, 
                              image_id: str ,
                              image_path: str, 
                              query: dict, 
                              collection_name: str, 
                              success: bool = False, 
                              default_monitoring_collection_name: str = "Monitoring", 
                              image_cname: str = 'Image'
                              ) -> str:
        # get machine-number
        if not success: 
            if self.created_documents >= self.MAX_DOCUMENTS_TO_BE_STORED and collection_name == default_monitoring_collection_name:
                return f'Limit of {self.MAX_DOCUMENTS_TO_BE_STORED} reached, Skipping report.'
        else:
            machine_number = query.get('machine-number')

            if not machine_number:
                raise ValueError('Machine number not found. If error persists, please add a feedback.')

        try:
            import os
            from bson import Binary
            import mimetypes

            if not image_path or not image_id:
                raise ValueError('Could not find image, the machine report will be discarded. If error persists, please add a feedback.')

            with open(image_path, "rb") as f:
                image_data = f.read()

            content_type = mimetypes.guess_type(image_path)[0] or "application/octet-stream"

            query['image_id'] = image_id
            query['content_type'] = content_type

            image_doc = {
                '_id': image_id,
                'data': Binary(image_data)
            }

            mes_image = db.create(data=image_doc, collection_name=image_cname)
            if not mes_image:
                raise RuntimeError('Failed to insert image into database. If error persists, please add a feedback.')

            res = db.create(data=query, collection_name=collection_name)
            if not res:
                raise RuntimeError("Failed to insert machine report into database. If error persists, please add a feedback.")
            
            mes = f"Machine report created with ID: {res.get('_id')}."
            if collection_name == default_monitoring_collection_name:
                self.created_documents += 1
                mes += f"({self.created_documents} out of {self.MAX_DOCUMENTS_TO_BE_STORED} remaining before skipping report)"
            
            return mes
        except Exception as e:
            return f"Error during machine report creation: {e}"
        
    def __is_duplicate_report(self, progression_report: dict, minutes: int = 30, limit: int = None) -> bool:
        if not limit:
            limit = int(os.getenv("TOTAL_MACHINE", "0")) + 1
        
        if not self.TEST_SUITE or not self.DISABLE_SCHEDULER:
            machine_report = progression_report.get('machine_report')
            if not machine_report:
                raise ValueError('Expected machine report to be present, but got None. If error persists, please add a feedback.')
            
            machine_numbers = machine_report.get('machine_number', [])

            raw_timestamp = progression_report.get('process_begins_at')

            if not machine_numbers or not raw_timestamp:
                return False 

            if isinstance(raw_timestamp, str):
                process_time = datetime.datetime.strptime(raw_timestamp, "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc)
            else:
                process_time = raw_timestamp


            # Normalize time to 30-min interval
            interval = datetime.timedelta(minutes=minutes)
            snapped_start = TimerUtils.normalize_to_interval(process_time, interval)
            snapped_end = snapped_start + interval

            # Build query
            query = {
                "machine-number": {"$in": machine_numbers},
            }

            # Query MongoDB for matches
            result = db.readWithPagination(
                query=query,
                collection_name="Machine Report",
                page=1,
                limit=limit,
                projection={},
                sort={},
                reverse=True
            )

            for doc in result.get('data', []):
                db_ts = datetime.datetime.fromisoformat(doc['processed_at'])
                if snapped_start <= db_ts < snapped_end:
                    return True

        return False


    def __check_if_env_is_in_local(self) -> bool:
        from AppConfig import AppConfig
        ac = AppConfig()
        return ac.getisLocalDevEnvironment() or ac.getisLocalEnvironment()

    @deprecated('use streamProcessImage instead')
    def __processDataToMachineReport(self, data: str, type: str, list_of_targets: any) -> list[dict]:
        acceptable_types = ['image', 'text']

        input = None
        if type == acceptable_types[0]:
            input = MachineReportInputWrapper(image_path=data)
        elif type == acceptable_types[1]:
            input = MachineReportInputWrapper(raw_text=data)
        else:
            raise ValueError(f'Expected types to be in {acceptable_types} but got {type}. If error persists, please add a feedback.')
        
        builder = MachineReportBuilder(input, list_of_targets)
        return builder.build()
        
    @deprecated('use streamProcessImage instead')
    def processImageToMachineReport(self, image: str) -> Dict[str, Dict]:
        try:
            targets = [
                TargetMaker.make_target('bpm', 'pcs/min(bpm)'),
                TargetMaker.make_target('pcs/min', 'pcs/min(orig)'),
                TargetMaker.make_target('p', 'pcs/min(p-abbr)')
            ]

            res = self.__processDataToMachineReport(image, 'image', targets)

            self.__createMachineReport({**(res[0])}, 'Machine Report')
            return res
        except FileNotFoundError:
            raise ValueError(f"Image file not found: {image}")
        except ImportError as e:
            raise ImportError(f"Missing required module: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to process image '{image}': {e}")
    pass

    @deprecated('use streamProcessImage instead')
    def processTextToMachineReport(self, text: str) -> Dict[str, Dict]:
        try:
            targets = [
                TargetMaker.make_target('bpm', 'pcs/min(bpm)'),
                TargetMaker.make_target('pcs/min', 'pcs/min(orig)')
            ]

            res = self.__processDataToMachineReport(text, 'text', targets)
            self.__createMachineReport({**(res[0])}, 'Machine Report')
            return res
        except FileNotFoundError:
            raise ValueError(f"Empty text: {text}")
        except ImportError as e:
            raise ImportError(f"Missing required module: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to process text '{truncate_string(text, max_length=10)}: {e}")

    def streamProcessImage(
        self,
        image: str,
        list_of_targets: list[tuple[str, str]] = [
            TargetMaker.make_target('p', 'pcs/min'),
            TargetMaker.make_target('bpm', 'pcs/min'),
            TargetMaker.make_target('pcs/min', 'pcs/min'),
        ],
        version: Version = Version(0, 0, 1),
        collection_name: str = 'Machine Report',
        monitoring_cname: str = 'Monitoring',
    ):
        is_local_dev_env = self.__check_if_env_is_in_local()
        if self.TEST_SUITE and self.DELETE_ALL_DATA and is_local_dev_env:
            yield f"data: {{\"devmode\": \"enabled\", \"msg\": \"Deleting all data\"}}\n\n"
            self.deleteAllDataInTest(collection_name='Machine Report', monitoring_name='Monitoring')
        elif not is_local_dev_env and self.TEST_SUITE:
            raise ValueError('Environment must be in local if test suite and delete all data is enabled')
        
        machine_report_builder = MachineReportBuilder(
            input=MachineReportInputWrapper(image_path=image),
            list_of_targets=list_of_targets,
            version=version
        )

        print('Processing image...')
        res = self.__initialize_process_data('process_begins_at')
        res['image'] = image
        image_id = machine_report_builder.get_image_id()

        yield f"data: {{\"progress\": 10, \"msg\": \"Starting image to text...\"}}\n\n"

        try:
            #******************************
            # Stage 1: OCR Processing   ***
            #******************************
            
            
            first_stage = machine_report_builder.image_to_unprocessed_text(image)
            yield f"data: {{\"progress\": 60, \"msg\": \"OCR complete. Normalizing text...\"}}\n\n"
            if self.TEST_SUITE:
                yield f"data: {json.dumps({'stage': 'ocr processing', 'data': first_stage})}\n\n"

            #******************************
            # Stage 1.1: Normalization  ***
            #******************************
            
            
            
            clean_leading_zero = machine_report_builder.normalizer.fix_leading_O_in_text(first_stage, list_of_targets)
            clean_malforming_floats = machine_report_builder.normalizer.normalize_floats_in_text(clean_leading_zero)
            res['unprocessed_text'] = clean_malforming_floats
            yield f"data: {{\"progress\": 70, \"msg\": \"Cleaning up potential errors\"}}\n\n"
            if self.TEST_SUITE:
                yield f"data: {json.dumps({'stage': 'normalizing text', 'data': clean_malforming_floats})}\n\n" 



            #******************************
            # Stage 2: NLP              ***
            #******************************



            second_stage = machine_report_builder.unprocessed_to_processed_text(clean_malforming_floats)
            yield f"data: {{\"progress\": 80, \"msg\": \"Separation of text has been successful\"}}\n\n"
            res['processed_text'] = second_stage
            if self.TEST_SUITE:
                yield f"data: {json.dumps({'stage': 'natural language processing', 'data': second_stage})}\n\n" 



            #******************************
            # Stage 2.1: Normalization  ***
            #******************************            



            # NOT IMPLEMENTED YET
            # clean_up_duplicate_decimal_points_in_float = machine_report_builder.normalizer.remove_duplicate_decimal_points_in_float(second_stage['tokens'])
            # second_stage['tokens'] = clean_up_duplicate_decimal_points_in_float
            # res['processed_text'] = second_stage
            # if self.TEST_SUITE:
            #     yield f"data: {json.dumps({'stage': 'natural language processing', 'data': second_stage})}\n\n"



            #******************************
            # Stage 3: Machine Report   ***
            #******************************



            third_stage = machine_report_builder.processed_text_to_machine_report(
                machine_report_builder.machine_report_handler.targets,
                second_stage
            )
            if self.TEST_SUITE:
                yield f"data: {json.dumps({'stage': 'generating machine report', 'data': third_stage})}\n\n"

            if not third_stage:
                raise ValueError('Cannot generate machine report')
            yield f"data: {{\"progress\": 90, \"msg\": \"Finalizing machine report...\"}}\n\n"
            
            res['machine_report'] = third_stage
            res = {**res, **self.__initialize_process_data('process_ends_at')}
            res['version'] = machine_report_builder.version.__str__()
            
            if self.TEST_SUITE and self.DISABLE_CHECKING_OF_KEYS:
                yield f"data: {{\"devmode\": \"enabled\", \"msg\": \"Disabling checking of keys\"}}\n\n"
            else:
                missing_keys = self.__check_missing_keys(list_of_targets, third_stage)
                if missing_keys:
                    self.__createMachineReport(
                        image_path=image,
                        image_id=image_id, 
                        query={"missing_keys": missing_keys, **res}, 
                        collection_name=monitoring_cname, 
                        default_monitoring_collection_name=monitoring_cname
                    )
                    raise ValueError(f'Missing required keys: {", ".join(missing_keys)}')
            


            #******************************
            # Feature: Feedback         ***
            #******************************



            # If test flag is set to true then no failure rate then if created documents and max documents stored
            failure_rate = 0 if self.TEST_SUITE and self.ENABLE_FEEDBACK else (
                95 if self.created_documents < self.MAX_DOCUMENTS_TO_BE_STORED else 100
            )

            enable_feedback = probability_generator(failure_rate=failure_rate)
            if self.TEST_SUITE:
                yield f"data: {{\"devmode\": \"enabled\", \"msg\": \"Feedback enabled\"}}\n\n"
            
            res['allow-feedback'] = enable_feedback
            if self.ENABLE_FEEDBACK and self.TEST_SUITE:
                self.__createMachineReport(
                    image_path=image, 
                    image_id=image_id,
                    query=res, 
                    collection_name=monitoring_cname, 
                    default_monitoring_collection_name=monitoring_cname
                )



            #******************************
            # Last Stage: Final         ***
            #******************************



            final = self.__generate_final_report(enable_feedback, third_stage, list_of_targets, version.__str__())
            minutes = 30
            if self.__is_duplicate_report(res, minutes):
                PHT = datetime.timezone(datetime.timedelta(hours=8))
                machine_number = final.get('machine-number')
                current_time = datetime.datetime.now(PHT)  # Current time in PHT
                next_available_time = TimerUtils.normalize_to_interval(datetime.datetime.now(datetime.timezone.utc), datetime.timedelta(minutes=minutes)) + datetime.timedelta(minutes=minutes)
                
                # Format both times to 12-hour clock with AM/PM
                formatted_current_time = current_time.strftime('%I:%M:%S %p')
                formatted_next_available_time = next_available_time.strftime('%I:%M:%S %p')
                
                raise ValueError(
                    f'{machine_number} has already been created. It is currently {formatted_current_time}, please wait until {formatted_next_available_time} to proceed.'
                )


            final['processed_at'] = str(res['process_begins_at'])
            mes = self.__createMachineReport(
                image_path=image,
                query=final, 
                image_id=image_id,
                collection_name=collection_name, 
                default_monitoring_collection_name=monitoring_cname
            )

            payload = {
                "progress": 100,
                "msg": "Done",
                "data": final,
                "db_status": mes
            }

            #FINAL DATA
            yield f"data: {json.dumps(payload, default=convert_objectid)}\n\n"



            #******************************
            # END                       ***
            #******************************
        except Exception as e:
            yield f'data: {{\"error\": \"{str(e)}\"}}\n\n'


    # Helper Methods for Cleanliness
    def __initialize_process_data(self, key: str):
        return {
            key: datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
        }

    def __check_missing_keys(self, 
                            list_of_targets, third_stage, 
                            third_stage_machine_number_key: str = 'machine_number', 
                            missing_key_to_machine_number_key_as_replacement: str = ''):
        missing_keys = []

        for unit, alias in list_of_targets:
            if alias not in third_stage:
                missing_keys.append(f"{unit} as {alias}" if unit != alias else f"{unit}")

        if third_stage_machine_number_key not in third_stage or third_stage.get(third_stage_machine_number_key) == 'None':
            if missing_key_to_machine_number_key_as_replacement == '':
                hyphenated_key = third_stage_machine_number_key.replace('_', '-')
            else:
                hyphenated_key = missing_key_to_machine_number_key_as_replacement
            missing_keys.append(hyphenated_key) 

        return missing_keys

    def __generate_final_report(
            self, 
            enable_feedback: bool, 
            third_stage: any,
            list_of_targets: list[tuple[str, str]], 
            version: Version, 
        ):
        final = {}

        for unit, alias in list_of_targets:
            final[alias] = third_stage.get(alias)

        final['allow-feedback'] = enable_feedback
        final['version'] = version
        final['machine-number'] = third_stage.get('machine_number')

        return final
    
    def deleteAllDataInTest(self, collection_name: str, monitoring_name: str):
        if self.TEST_SUITE and self.DELETE_ALL_DATA:
            if self.__check_if_env_is_in_local():
                self.__delete(collection_name='Image')
                self.__delete(collection_name=collection_name)
                self.__delete(collection_name=monitoring_name)
                return True
            else:
                raise ValueError("Environment must be in local if test suite is enabled.")
        return False



class ServerRequests(ReportActions, MonitoringActions):
    def __init__(self):
        super().__init__()
        pass
    
if __name__ == "__main__":
    sr = ServerRequests()

    res = sr.streamProcessImage('server/test/mrtest.jpg')