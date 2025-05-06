from objects import *
import time
import json

db = mongoDb()


class ReportActions:
    def __init__(self):
        pass
    
    def __delete(self, query: dict = {}, collection_name='Machine Report'):
        res = db.delete(query=query, collection_name=collection_name)
        pass

    def __createMachineReport(self, query: dict, collection_name: str) -> None:
        try:
            res = db.create(data=query, collection_name=collection_name)
            if not res:
                raise RuntimeError("Failed to insert machine report into database.")
            print("Machine report created with ID:", res.get("_id"))
        except Exception as e:
            print(f"Error during machine report creation: {e}")

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
        

    def processImageToMachineReport(self, image: str) -> Dict[str, Dict]:
        try:
            targets = [
                TargetMaker.make_target('bpm', 'pcs/min(bpm)'),
                TargetMaker.make_target('pcs/min', 'pcs/min(orig)')
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
            TargetMaker.make_target('bpm', 'pcs/min(bpm)'),
            TargetMaker.make_target('pcs/min', 'pcs/min(orig)')
        ],
        version: Version = Version(0, 0, 1),
        collection_name: str = 'Machine Report'
    ):

        self.__delete()
        machine_report_builder = MachineReportBuilder(
            input=MachineReportInputWrapper(image_path=image),
            list_of_targets=list_of_targets,
            version=version
        )
        print('Processing image...')
        res = {}
        res['process_begins_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        yield f"data: {{\"progress\": 10, \"msg\": \"Starting image to text...\"}}\n\n"

        try:
            first_stage = machine_report_builder.image_to_unprocessed_text(image)
            res['unprocessed_text'] = first_stage
            yield f"data: {{\"progress\": 70, \"msg\": \"OCR complete. Normalizing text...\"}}\n\n"

            second_stage = machine_report_builder.unprocessed_to_processed_text(first_stage)
            res['processed_text'] = second_stage
            yield f"data: {{\"progress\": 85, \"msg\": \"Text normalized. Building report...\"}}\n\n"

            third_stage = machine_report_builder.processed_text_to_machine_report(
                machine_report_builder.machine_report_handler.targets,
                second_stage
            )

            yield f"data: {{\"progress\": 90, \"msg\": \"Finalizing machine report...\"}}\n\n"
            
            # if not third_stage and 0 or 'id_info' not in third_stage:
            #     raise ValueError('Cannot generate machine report within the processed text')

            res['machine_report'] = third_stage
            res['process_ends_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            res['version'] = str(machine_report_builder.version)

            self.__createMachineReport(res, collection_name)

            yield f"data: {{\"progress\": 100, \"msg\": \"Done\", \"data\": {res} }}\n\n"
        except Exception as e:
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"



class ServerRequests(ReportActions):
    def __init__(self):
        super().__init__()
        pass
    
if __name__ == "__main__":
    sr = ServerRequests()

    image = 'test/test41.jpg'

    text = '400 pcs/min ... ... ... ... mchine . 4..'

    res = sr.processTextToMachineReport(text)
    res = sr.processImageToMachineReport(image)
    print(res)
    pass