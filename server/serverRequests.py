from objects import *
import time
import json

db = mongoDb()

class MonitoringActions:
    def __init__(self):
        pass

    def feedback(self,
                 id: str, 
                 does_match: bool, 
                 collection_name: str='Feedback', 
                 machine_report_monitoring_cname: str = 'Monitoring',
                 test_flag = True
        ):
        if test_flag:
            db.delete(query={}, collection_name=collection_name)
        machine_report_data = db.read(query={'_id': convert_objectid(id)}, collection_name=machine_report_monitoring_cname)
        
        SYSTEM_MESSAGE = 'The system'
        
        if not machine_report_data:
            return f"{SYSTEM_MESSAGE} could not find the data. Thank you for your feedback"
        elif not machine_report_data['allow-feedback'] or does_match:
            db.delete(query={**machine_report_data}, collection_name=machine_report_monitoring_cname)
            message = ''
            if does_match:
                message = f'{SYSTEM_MESSAGE} has evaluated your feedback'
                if not machine_report_data['allow-feedback']:
                    message = message + f'and it seems that it does not allow feedback as of right now.'
            else:
                message = f'{SYSTEM_MESSAGE} sees that it does not allow feedback as of right now.'
            message = message + 'Thank you for your feedback. '

            return message
        
        return f'{SYSTEM_MESSAGE} will follow up on that. If this happens once again to you, please Thank you for your feedback.'

        

class ReportActions:
    def __init__(self, MAX_DOCUMENTS_TO_BE_STORED = 50):
        self.MAX_DOCUMENTS_TO_BE_STORED = MAX_DOCUMENTS_TO_BE_STORED
        self.created_documents = 0
        pass
    
    def __delete(self, query: dict = {}, collection_name='Machine Report'):
        res = db.delete(query=query, collection_name=collection_name)
        pass

    def __createMachineReport(self, query: dict, collection_name: str) -> None:
        if self.created_documents >= self.MAX_DOCUMENTS_TO_BE_STORED:
            print(f'Limit hit at {self.MAX_DOCUMENTS_TO_BE_STORED}, discarding incoming query for further processing')
            return
        
        try:
            res = db.create(data=query, collection_name=collection_name)
            if not res:
                raise RuntimeError("Failed to insert machine report into database.")
            
            self.created_documents += 1

            print("Machine report created with ID:", res.get("_id"))
        except Exception as e:
            print(f"Error during machine report creation: {e}")

    @deprecated('use streamProcessImage instead')
    def __processDataToMachineReport(self, data: str, type: str, list_of_targets: any) -> list[dict]:
        acceptable_types = ['image', 'text']

        input = None
        if type == acceptable_types[0]:
            input = MachineReportInputWrapper(image_path=data)
        elif type == acceptable_types[1]:
            input = MachineReportInputWrapper(raw_text=data)
        else:
            raise ValueError(f'Expected types to be in {acceptable_types} but got {type}')
        
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
        test_flag: bool = True
    ):
        if test_flag:
            self.__delete()
            self.__delete(collection_name=monitoring_cname)
        
        machine_report_builder = MachineReportBuilder(
            input=MachineReportInputWrapper(image_path=image),
            list_of_targets=list_of_targets,
            version=version
        )

        print('Processing image...')
        res = self._initialize_process_data()

        yield f"data: {{\"progress\": 10, \"msg\": \"Starting image to text...\"}}\n\n"

        try:
            #******************************
            # Stage 1: OCR Processing   ***
            #******************************
            first_stage = machine_report_builder.image_to_unprocessed_text(image)
            yield f"data: {{\"progress\": 60, \"msg\": \"OCR complete. Normalizing text...\"}}\n\n"

            #******************************
            # Stage 1.1: Normalization  ***
            #******************************
            change_leading_zero = machine_report_builder.normalizer.fix_leading_O_in_text(first_stage, list_of_targets)
            yield f"data: {{\"progress\": 70, \"msg\": \"Cleaning up potential errors\"}}\n\n"

            res['unprocessed_text'] = change_leading_zero

            #******************************
            # Stage 2: NLP              ***
            #******************************
            second_stage = machine_report_builder.unprocessed_to_processed_text(change_leading_zero)
            yield f"data: {{\"progress\": 80, \"msg\": \"Separation of text has been successful\"}}\n\n"

            res['processed_text'] = second_stage

            #******************************
            # Stage 3: Machine Report   ***
            #******************************
            third_stage = machine_report_builder.processed_text_to_machine_report(
                machine_report_builder.machine_report_handler.targets,
                second_stage
            )
            if not third_stage:
                raise ValueError('Cannot generate machine report')

            yield f"data: {{\"progress\": 90, \"msg\": \"Finalizing machine report...\"}}\n\n"
            if not test_flag:
                missing_keys = self._check_missing_keys(list_of_targets, third_stage)
                if missing_keys:
                    self.__createMachineReport(query={"missing_keys": missing_keys, **res}, collection_name=collection_name)
                    raise ValueError(f'Missing required keys: {", ".join(missing_keys)}')
            else:
                yield f"data: {{\"devmode\": \"enabled\", \"msg\": \"Disabling checking of keys\"}}\n\n"

            res['machine-report'] = third_stage
            res['process_ends_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            res['version'] = machine_report_builder.version.__str__()

            #******************************
            # Feature: Feedback         ***
            #******************************
            # If test flag is set to true then no failure rate 
            failure_rate = 0 if test_flag else (
                95 and self.MAX_DOCUMENTS_TO_BE_STORED > self.created_documents
            )
            enable_feedback = probability_generator(failure_rate=failure_rate)
            if enable_feedback and test_flag:
                yield f"data: {{\"devmode\": \"enabled\", \"msg\": \"Feedback enabled\"}}\n\n"
            
            res['allow-feedback'] = enable_feedback
            if enable_feedback:
                self.__createMachineReport(res, monitoring_cname)

            
            #******************************
            # Last Stage: Final         ***
            #******************************
            final = self._generate_final_report(enable_feedback, third_stage, list_of_targets, version.__str__())
            self.__createMachineReport(final, collection_name)

            payload = {
                "progress": 100,
                "msg": "Done",
                "data": final
            }

            yield f"data: {json.dumps(payload, default=convert_objectid)}\n\n"

        except Exception as e:
            yield f'data: {{\"error\": \"{str(e)}\"}}\n\n'


    # Helper Methods for Cleanliness
    def _initialize_process_data(self):
        return {
            'process_begins_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def _check_missing_keys(self, list_of_targets, third_stage):
        missing_keys = []
        for unit, alias in list_of_targets:
            if alias not in third_stage:
                missing_keys.append(f"{unit} or {alias}")
        
        if third_stage.get('machine_number') == 'None':
            missing_keys.append("machine-number") 

        return missing_keys

    def _generate_final_report(
            self, 
            enable_feedback: bool, 
            third_stage: any,
            list_of_targets: list[tuple[str, str]], 
            version: Version, 
        ):
        final = {}
        final['machine-number'] = third_stage.get('machine_number')

        for unit, alias in list_of_targets:
            final[alias] = third_stage.get(alias)

        final['allow-feedback'] = enable_feedback
        final['version'] = version
        
        return final



class ServerRequests(ReportActions, MonitoringActions):
    def __init__(self):
        super().__init__()
        pass
    
if __name__ == "__main__":
    sr = ServerRequests()

    res = sr.streamProcessImage('server/test/mrtest.jpg')