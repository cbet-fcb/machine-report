"use client";

import React from "react";

import CameraIcon from "./assets/camera.svg";

import ServerRequests from "./api/ServerRequests";

import ThemeControl from "../components/ThemeControl";
import ProgressLoading from "../components/ProgressLoading";
import OcrResults from "../components/OcrResults";

import Image from "next/image";

interface ProgressData {
  progress: number;
  msg: string;
  data?: {
    machine_report: ocrResult;
  };
}
interface OcrValue {
  value: string | number;
  unit?: string;
}

interface ocrResult {
  [key: string]: OcrValue | string | number | undefined;
}

// function sleep(ms: number): Promise<void> {
//   return new Promise((resolve) => setTimeout(resolve, ms));
// }

export default function Home(): React.JSX.Element {
  const server = new ServerRequests();

  const cameraInputRef = React.useRef<HTMLInputElement | null>(null);

  const [ocrData, setOcrData] = React.useState<ocrResult | null>(null);

  const [progressData, setProgressData] = React.useState<ProgressData>(
    {} as ProgressData
  );

  const [loading, setLoading] = React.useState(false);

  const [uploadedImage, setUploadedImage] = React.useState<string | null>(null);

  const [allowFeedback, setAllowFeedback] = React.useState(true);
  const [showFeedback, setShowFeedback] = React.useState(false);

  const [machineReportId, setMachineReportId] = React.useState<string | null>(
    null
  );

  const handleImageUpload = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setLoading(true);
        setUploadedImage(reader.result as string);
      };
      reader.readAsDataURL(file);

      server.streamProcessImage(file, (data) => {
        setProgressData(data);
        if (data?.error) {
          setLoading(false);
          setProgressData({
            progress: 0,
            msg: "Error: " + data.error,
          });
          setOcrData(null);
          console.log(data.error);
          alert("Error Image ");
        }
        if (data?.data && data?.progress === 100) {
          setOcrData(data.data);
          setLoading(false);
          setProgressData({
            progress: 0,
            msg: "...",
          });
          setAllowFeedback(data?.data?.["allow-feedback"] || false);
          setShowFeedback(data?.data?.["allow-feedback"] || false);
          setMachineReportId(data?.data?._id || null);
          console.log(data);
          alert("Image Process Success ");
        }
      });
      setLoading(false);
    }
  };

  const handleCameraClick = () => {
    if (cameraInputRef.current) {
      cameraInputRef.current.click();
    }
  };

  const handleFeedback = async (feedback: boolean) => {
    if (machineReportId) {
      const res = await server.feedback(machineReportId, feedback);
      if (res) {
        alert("Feedback Sent");
      } else {
        alert("Error Sending Feedback");
      }
      setAllowFeedback(false);
      setShowFeedback(false);
    }
  };

  return (
    <main className={` container !justify-start transition-all duration-300 `}>
      {/* theme control */}
      <ThemeControl />

      <h1 className="text-2xl tracking-[8px] mt-auto">Machine  Report</h1>

      {/* camera input component */}
      <div className={` flex flex-col items-center justify-center gap-10 `}>
        <input
          type="file"
          accept="image/*"
          capture="environment"
          className="hidden"
          onChange={handleImageUpload}
          ref={cameraInputRef}
        />
        <div
          className="w-[75vw] md:w-max max-w-[75vw] btn btn-xl h-max tooltip tooltip-open tooltip-bottom md:tooltip-right "
          onClick={handleCameraClick}
        >
          <div className="tooltip-content bg-base-100 border border-base-content rounded-sm">
            <div className=" font-light text-base-content">
              Upload Something
            </div>
          </div>
          <Image
            className={` size-20`}
            height={10}
            width={10}
            alt="Camera Upload"
            src={CameraIcon}
          />
        </div>
      </div>

      <div className="w-[95vw] flex flex-col md:flex-row items-center justify-center gap-10 py-10 mb-auto transition-all duration-300 ">
        {/* image preview modal */}
        {!showFeedback && (
          <OcrResults
            ocrData={ocrData}
            uploadedImage={uploadedImage}
            loading={loading}
            allowFeedback={allowFeedback}
            showFeedback={showFeedback}
            setShowFeedback={setShowFeedback}
          />
        )}

        {/* upload loading modal */}
        <ProgressLoading loading={loading} progressData={progressData} />

        {/* feedback modal */}
        {showFeedback && (
          <div
            className={`fixed inset-0 bg-black/80 z-50 flex flex-col h-screen w-full justify-center items-center transition-all duration-300`}
          >
            <div
              className={`${
                allowFeedback
                  ? "text-base-100 border border-base-100"
                  : "bg-base-100"
              } relative  w-[75vw] md:w-max max-w-[75vw] p-8 rounded-box flex flex-col gap-4`}
            >
              <button
                onClick={() => setShowFeedback(false)}
                className="absolute btn btn-xs btn-circle btn-outline top-1.5 right-1.5"
              >
                x
              </button>
              <p className="w-max text-center">
                Do the result matches the picture?
              </p>
              <div className="w-full flex justify-evenly">
                <button
                  className="btn btn-sm btn-outline"
                  onClick={() => {
                    handleFeedback(false);
                  }}
                >
                  No
                </button>
                <button
                  onClick={() => {
                    handleFeedback(true);
                  }}
                  className="btn btn-sm btn-primary"
                >
                  Yes
                </button>
              </div>
            </div>

            <div className="h-max w-[95vw] flex flex-col md:flex-row items-center justify-center gap-10 py-10 ">
              <OcrResults
                ocrData={ocrData}
                uploadedImage={uploadedImage}
                loading={loading}
                allowFeedback={allowFeedback}
                showFeedback={showFeedback}
                setShowFeedback={setShowFeedback}
              />
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
