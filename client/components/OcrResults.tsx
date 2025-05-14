import React from "react";

import Image from "./Image";

import FormSubmit from "./FormSubmit";

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
        <div className="flex flex-col md:flex-row justify-evenly relative py-10 px-5 gap-5 overflow-y-auto border border-base-300 rounded-box">
          {allowFeedback && !showFeedback && (
            <button
              onClick={() => setShowFeedback(true)}
              className={`
                 hover:w-[70px] after:content-['?'] hover:after:content-['Feedback'] 
                transition-all duration-300 absolute btn btn-primary btn-xs btn-circle top-2 right-5 origin-left
                `}
            ></button>
          )}

          <div className="w-full md:w-1/2 h-[50vh] flex items-center">
            <Image
            src={uploadedImage}
            className={`${
              loading && "animate-pulse"
            }  max-h-full max-w-full overflow-clip bg-base-200 rounded-box `}
          />
          </div>

          <FormSubmit data={ocrData}/>
        </div>
      )}

      {/* {ocrData?._id && uploadedImage && !loading && (
        <div className="relative w-[75vw] lg:w-[60vw] py-10 px-5 columns-1 md:columns-2 overflow-y-auto border border-base-300 rounded-box">
          {allowFeedback && !showFeedback && (
            <button
              onClick={() => setShowFeedback(true)}
              className={`
                 hover:w-[70px] after:content-['?'] hover:after:content-['Feedback'] 
                transition-all duration-300 absolute btn btn-primary btn-xs btn-circle top-2 right-5 origin-left
                `}
            ></button>
          )}

          <Image
            src={uploadedImage}
            className={`${
              loading && "animate-pulse"
            } overflow-clip bg-base-200 rounded-box`}
          />

          {Object.keys(ocrData || {}).map((key) => (
            <div
              key={key}
              className={`${
                loading && "animate-pulse"
              } bg-base-200 last:border-b-0 border-b border-base-300 md:truncate text-pretty my-2 p-3 rounded-box `}
            >
              {key}:{" "}
              {typeof ocrData?.[key] === "object" && ocrData[key]?.value ? (
                <span className="font-semibold">
                  {Number(ocrData[key]?.value).toLocaleString()}
                </span>
              ) : (
                <span className="font-semibold">
                  {String(ocrData?.[key]).toLocaleString()}
                </span>
              )}
            </div>
          ))}
        </div>
      )} */}

      {/* {ocrData?._id && uploadedImage && !loading && (
        <div className=" flex items-center justify-center w-[75vw] md:w-max max-w-[75vw] ">
          <div className=" relative shadow-lg rounded-box overflow-clip w-full ">
            {allowFeedback && !showFeedback && (
              <button
                onClick={() => setShowFeedback(true)}
                className={`after:content-['?'] hover:after:content-['Feedback'] hover:w-[70px] transition-all duration-300 absolute btn btn-xs btn-circle top-2 right-2`}
              ></button>
            )}
            <div className="bg-neutral text-neutral-content pt-10 pb-7 px-2 text-center text-4xl ">
              {typeof ocrData?.["pcs/min"] === "object" &&
              ocrData["pcs/min"]?.value ? (
                <>
                  {Number(ocrData["pcs/min"]?.value).toLocaleString()}
                  <div className=" text-xs mt-0.5 ">
                    {String(ocrData["pcs/min"]?.unit)}
                  </div>
                </>
              ) : (
                String(ocrData?.["pcs/min"]).toLocaleString()
              )}
            </div>
            <div className="text-sm text-center px-10  py-2 bg-base-100 ">
              {String(ocrData?.["machine-number"])}
            </div>
          </div>
        </div>
      )}
      {uploadedImage && !loading && <Image uploadedImage={uploadedImage} />} */}
    </>
  );
};

export default OcrResults;
