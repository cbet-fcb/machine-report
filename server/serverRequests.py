from objects import *
import time

db = mongoDb()


class ReportActions:
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

    def processImageToMachineReport(self, image: str) -> Dict[str, Dict]:
        try:
            targets = [
                TargetMaker.make_target('bpm', 'pcs/min(bpm)')
                TargetMaker.make_target('pcs/min', 'pcs/min(orig)')
            ]

            input = MachineReportInputWrapper(image_path=image)
            builder = MachineReportBuilder(input, list_of_targets=targets)
            res = builder.build()
            return res
        except FileNotFoundError:
            raise ValueError(f"Image file not found: {image}")
        except ImportError as e:
            raise ImportError(f"Missing required module: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to process image '{image}': {e}")
    pass

class ServerRequests(ReportActions):
    def __init__(self):
        super().__init__()
        pass
    
if __name__ == "__main__":
    sr = ServerRequests()

    start = time.perf_counter()

    image_path = f'test/test71.jpg'
    print(f"Processing {image_path}:")
    
    import ocr
    from textProcessor import Normalizer, TextProcessor 
    import nlp
    ### --------------------------------- OCR
    new_ocr = ocr.OCR(path=image_path)
    unproc_text = new_ocr.run_ocr()
    print("Unprocessed text: ", unproc_text)

    ### --------------------------------- OCR
    new_normalizer = Normalizer()
    normalized_text = new_normalizer.convert_ocr_result_alphabets_to_small_letter(unproc_text)

    ### --------------------------------- NLP
    new_nlp = nlp.NLP()
    handled_text = new_nlp.handle_text(normalized_text)
    print("Handled text: ", handled_text)
    
    ### --------------------------------- NLP
    new_tp = TextProcessor()
    proc_text = new_tp.process_text(handled_text)
    print("Processed text: ", proc_text)

    res = sr.processImageToMachineReport(image_path)
    print("res: ", res)

    # for i in range(41, 71):  # 72 is exclusive, so this covers 41 to 71
    #     if i != 69:
    #         image_path = f'../../Automation/test/test{i}.jpg'
    #         print(f"Processing {image_path}")
    #         res = sr.processImageToMachineReport(image_path)
    #         print(f"Result for test{i}.jpg: ", str(res))

    end = time.perf_counter()
    print(f"Processed all in {(end - start)*1000:.2f} ms")