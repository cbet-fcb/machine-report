"use client";

import React from "react";

import CameraIcon from "./assets/camera.svg";

import Image from "next/image";

import ServerRequests from "./api/ServerRequests";

export default function Home() {
  const server = new ServerRequests();

  const cameraInputRef = React.useRef<HTMLInputElement | null>(null);

  const [loading, setLoading] = React.useState(false);

  const [uploadedImage, setUploadedImage] = React.useState<string | null>(null);
  const [expanded, setExpanded] = React.useState(false);

  // const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
  //   setLoading(true);
  //   const file = event.target.files?.[0];
  //   if (file) {
  //     const reader = new FileReader();
  //     reader.onloadend = () => {
  //       setUploadedImage(reader.result as string);
  //     };
  //     reader.readAsDataURL(file);
  //   }
  //   setLoading(false);
  // };

  const handleImageUpload = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setLoading(true);
    const file = event.target.files?.[0];
    console.log(file)
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setUploadedImage(reader.result as string);
      };
      reader.readAsDataURL(file);

      server.streamProcessImage(file, (data) => {
        console.log("Progress:", data.progress);
      });
    }
    setLoading(false);
  };

  const handleCameraClick = () => {
    if (cameraInputRef.current) {
      cameraInputRef.current.click();
    }
  };

  // React.useEffect(() => {
  //   const eventSource = new EventSource("/api/events");

  //   eventSource.onmessage = (event) => {
  //     console.log(event.data);
  //   };

  //   eventSource.onerror = () => {
  //     eventSource.close();
  //   };

  //   return () => {
  //     eventSource.close();
  //   };
  // }, []);

  return (
    <main className={` container !justify-start transition-all duration-300 `}>
      <label className="swap swap-rotate">
        <input type="checkbox" className="theme-controller" value="capagain" />

        <svg
          className="swap-off h-10 w-10 fill-current"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
        >
          <path d="M5.64,17l-.71.71a1,1,0,0,0,0,1.41,1,1,0,0,0,1.41,0l.71-.71A1,1,0,0,0,5.64,17ZM5,12a1,1,0,0,0-1-1H3a1,1,0,0,0,0,2H4A1,1,0,0,0,5,12Zm7-7a1,1,0,0,0,1-1V3a1,1,0,0,0-2,0V4A1,1,0,0,0,12,5ZM5.64,7.05a1,1,0,0,0,.7.29,1,1,0,0,0,.71-.29,1,1,0,0,0,0-1.41l-.71-.71A1,1,0,0,0,4.93,6.34Zm12,.29a1,1,0,0,0,.7-.29l.71-.71a1,1,0,1,0-1.41-1.41L17,5.64a1,1,0,0,0,0,1.41A1,1,0,0,0,17.66,7.34ZM21,11H20a1,1,0,0,0,0,2h1a1,1,0,0,0,0-2Zm-9,8a1,1,0,0,0-1,1v1a1,1,0,0,0,2,0V20A1,1,0,0,0,12,19ZM18.36,17A1,1,0,0,0,17,18.36l.71.71a1,1,0,0,0,1.41,0,1,1,0,0,0,0-1.41ZM12,6.5A5.5,5.5,0,1,0,17.5,12,5.51,5.51,0,0,0,12,6.5Zm0,9A3.5,3.5,0,1,1,15.5,12,3.5,3.5,0,0,1,12,15.5Z" />
        </svg>

        {/* moon icon */}
        <svg
          className="swap-on h-10 w-10 fill-current"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
        >
          <path d="M21.64,13a1,1,0,0,0-1.05-.14,8.05,8.05,0,0,1-3.37.73A8.15,8.15,0,0,1,9.08,5.49a8.59,8.59,0,0,1,.25-2A1,1,0,0,0,8,2.36,10.14,10.14,0,1,0,22,14.05,1,1,0,0,0,21.64,13Zm-9.5,6.69A8.14,8.14,0,0,1,7.08,5.22v.27A10.15,10.15,0,0,0,17.22,15.63a9.79,9.79,0,0,0,2.1-.22A8.11,8.11,0,0,1,12.14,19.73Z" />
        </svg>
      </label>

      <h1 className="text-2xl tracking-[8px] mt-auto">Machine  Report</h1>

      {/* input component */}
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
          className="btn btn-xl h-max tooltip tooltip-open tooltip-bottom md:tooltip-right "
          // data-tip="Upload"
          onClick={handleCameraClick}
        >
          <div className="tooltip-content bg-base-100 border border-base-content rounded-sm">
            <div className=" font-light text-base-content">
              Upload Something
            </div>
          </div>
          <Image
            className={`${loading && "loading"} size-20`}
            alt="Camera Upload"
            height={10}
            width={10}
            src={CameraIcon}
          ></Image>
        </div>
      </div>

      <div className="w-[95vw] flex flex-col md:flex-row items-center justify-center gap-10 py-10 mb-auto">
        {uploadedImage && (
          <div className="h-full w-full md:w-[46%]">
            <div className="w-full rounded-box border overflow-clip">
              <div className="bg-base-200 w-full h-12 border-b flex items-center justify-center font-semibold">
                {" "}
                Results{" "}
              </div>
              <table className="table text-center ">
                <tbody>
                  <tr className="">
                    <th className="w-[90px] bg-base-200 border-r border-b">
                      1
                    </th>
                    <td className="border-b">2</td>
                  </tr>
                  <tr>
                    <th className=" bg-base-200 border-r">3</th>
                    <td>4</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}
        {uploadedImage && (
          <>
            <div
              className={`${
                expanded
                  ? " fixed inset-0 bg-black/50 z-50 justify-center"
                  : " static w-full md:w-[46%] justify-start "
              }  flex items-center transition-all duration-300`}
              onClick={() => setExpanded((prev) => !prev)}
            >
              <img
                src={uploadedImage}
                alt="Expanded"
                className=" w-[95vw] max-h-[95vh] rounded-lg transition-all duration-300"
              />
            </div>
          </>
        )}
      </div>
    </main>
  );
}
