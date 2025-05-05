from objects import *
import time
import json

db = mongoDb()


class ReportActions(MachineReportBuilder):
    def __init__(self):
        self.__cachedMetadata = dict()
    
    def __clearCached(self):
        self.__cachedMetadata.clear()
        pass

    def __addMetadataToBeCached(self, key: str, data: any):
        self.__cachedMetadata[key] = data
        pass

    def __dataToDict(self, key: str, data: any) -> dict:
        return {**self.__cachedMetadata, key: data}
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

    def streamProcessImage(self, image: str):
        print('Processing image...')
        res = {}
        res['process_begins_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        yield f"data: {{\"progress\": 10, \"msg\": \"Starting image to text...\"}}\n\n"

        try:
            first_stage = self.image_to_unprocessed_text(image)
            if not first_stage:
                raise ValueError('No text detected')
            res['unprocessed_text'] = first_stage
            yield f"data: {{\"progress\": 70, \"msg\": \"OCR complete. Normalizing text...\"}}\n\n"

            second_stage = self.unprocessed_to_processed_text(first_stage)
            res['processed_text'] = second_stage

            yield f"data: {{\"progress\": 85, \"msg\": \"Text normalized. Building report...\"}}\n\n"

            time.sleep(1)  # simulate delay before final stage
            yield f"data: {{\"progress\": 90, \"msg\": \"Finalizing machine report...\"}}\n\n"

            targets = [
                TargetMaker.make_target('bpm', 'pcs/min(bpm)'),
                TargetMaker.make_target('pcs/min', 'pcs/min(orig)')
            ]
            third_stage = self.processed_text_to_machine_report(targets, second_stage)
            if not third_stage:
                raise ValueError('Cannot find anything within the processed text')
            res['machine_report'] = third_stage

            res['process_ends_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            res['version'] = Version(0, 0, 1).__str__()

            self.__addMetadataToBeCached('result', {**res})
            self.__createMachineReport({**res}, 'Machine Report')

            yield f"data: {{\"progress\": 100, \"msg\": \"Done\", \"data\": {self.__dataToDict('source', 'image_path')} }}\n\n"
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