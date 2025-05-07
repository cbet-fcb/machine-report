import React from "react";

interface ProgressLoadingProps {
  loading: boolean;
  progressData: ProgressData;
}

interface ProgressData {
  progress: number;
  msg: string;
}

const ProgressLoading: React.FC<ProgressLoadingProps> = ({
  loading,
  progressData,
}) => {
  return (
    <>
      {loading && (
        <div
          className={`${
            loading
              ? " fixed inset-0 bg-black/80 z-50 justify-center"
              : " static w-full md:w-[46%] justify-start "
          }  flex flex-col items-center gap-2 `}
        >
          <progress
            className="progress progress-info h-4 w-56"
            value={progressData?.progress || 0}
            max="100"
          ></progress>
          <h3 className="text-white tracking-widest ">{progressData?.msg}</h3>
        </div>
      )}
    </>
  );
};

export default ProgressLoading;
