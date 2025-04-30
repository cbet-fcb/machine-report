from objects import *
import time

class ServerRequests:
    def __init__(self):
        pass
    
    # def testModel(self, a, b, c, d, e, f) -> None:
    #     TestModel(a=a,b=b,c=c,d=d,e=e,f=f).print_all()
    #     pass


    def processImageToMachineReport(self, image: str) -> Dict[str, Dict]:
        from imageToText import ImageToTextHandler
        itth = ImageToTextHandler()
        processed_image_to_nlp_dict = itth.run_image_to_text_handler(path=image)

        mr = MachineReport(
            targets=[
                TargetMaker.make_target('bpm', 'bpm-pcs/min'),
                TargetMaker.make_target('pcs/min'),
            ],
            nlp_output=processed_image_to_nlp_dict
        )

        return mr.generate_machine_report()

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