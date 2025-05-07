import React from "react";

import Image from "./Image";

interface OcrResultsProps {
  ocrData: ocrResult | null;
  uploadedImage: string | null;
  loading: boolean;
  allowFeedback: boolean;
  showFeedback: boolean;
  setShowFeedback: React.Dispatch<React.SetStateAction<boolean>>;
}

interface OcrValue {
  value: string | number;
  unit?: string;
}

interface ocrResult {
  [key: string]: OcrValue | string | number | undefined;
}

const OcrResults: React.FC<OcrResultsProps> = ({
  ocrData,
  uploadedImage,
  loading,
  allowFeedback,
  showFeedback,
  setShowFeedback,
}) => {
  return (
    <>
      {ocrData?._id && uploadedImage && !loading && (
        <div className=" flex items-center justify-center w-[75vw] md:w-max max-w-[75vw] ">
          <div className=" relative shadow-lg rounded-box overflow-clip w-full ">
            {allowFeedback && !showFeedback && (
              <button
                onClick={() => setShowFeedback(true)}
                className={`after:content-['?'] hover:after:content-['Feedback'] hover:w-[70px] transition-all duration-300 absolute btn btn-xs btn-circle top-2 right-2`}
              ></button>
            )}
            <div className="bg-neutral text-neutral-content pt-10 pb-7 text-center text-4xl ">
              {typeof ocrData?.["pcs/min"] === "object" &&
              ocrData["pcs/min"]?.value ? (
                <>
                  {String(ocrData["pcs/min"]?.value)} 
                  {String(ocrData["pcs/min"]?.unit)}
                </>
              ) : (
                String(ocrData?.["pcs/min"])
              )}
              <div className=" text-xs mt-0.5 ">pcs / min</div>
            </div>
            <div className="text-sm text-center px-10 py-2 bg-base-100 ">
              {String(ocrData?.["machine-number"])}
            </div>
          </div>
        </div>
      )}
      {uploadedImage && !loading && <Image uploadedImage={uploadedImage} />}
    </>
  );
};

export default OcrResults;
