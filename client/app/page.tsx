"use client";

import React from "react";

import PageWrapper from "../components/PageWrapper";

import CameraIcon from "./assets/camera.svg";

import Image from "next/image";

export default function Home() {
  const cameraInputRef = React.useRef<HTMLInputElement | null>(null);

  const [uploadedImage, setUploadedImage] = React.useState<string | null>(null);

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setUploadedImage(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleCameraClick = () => {
    if (cameraInputRef.current) {
      cameraInputRef.current.click();
    }
  };

  return (
    <PageWrapper>
      <main className={` container ${uploadedImage && " !justify-start "} `}>
        <h1 className="text-2xl tracking-[8px]">Machine  Report</h1>
        <div
          className={` flex flex-col items-center justify-center gap-10 pb-10`}
        >
          <input
            type="file"
            accept="image/*"
            capture="environment"
            className="hidden"
            onChange={handleImageUpload}
            ref={cameraInputRef}
          />
          <span
            className="btn btn-xl h-max tooltip tooltip-open tooltip-right"
            data-tip="Upload"
          >
            <Image
              className="size-20"
              alt="Camera Upload"
              height={10}
              width={10}
              onClick={handleCameraClick}
              src={CameraIcon}
            ></Image>
          </span>
          {uploadedImage && (
            <div className="flex flex-col items-center justify-center ">
              <img
                className="max-w-[99vw] h-max"
                src={uploadedImage}
                alt="Uploaded"
              />
            </div>
          )}
          {uploadedImage && (
            <div className="flex flex-col items-center justify-center h-[45vh] w-[98vw] border">
              <img
                className="w-full h-full"
                src={uploadedImage}
                alt="Uploaded"
              />
            </div>
          )}
        </div>
      </main>
    </PageWrapper>
  );
}
