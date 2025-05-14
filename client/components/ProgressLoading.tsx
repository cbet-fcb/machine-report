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
  const [showCancel, setShowCancel] = React.useState(false);

  function sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  React.useEffect(() => {
    setShowCancel(false);
    if (loading) {
      sleep(8000).then(() => {
        setShowCancel(true);
      });
    }
  }, [loading]);

  return (
    <>
      {loading && (
        <div
          className={`${
            loading
              ? " fixed inset-0 bg-black/80 z-50 justify-center"
              : " static w-full justify-start "
          }  flex flex-col items-center gap-2 `}
        >
          <progress
            className="progress progress-info h-4 w-[80%]"
            value={progressData?.progress || undefined}
            max="100"
          ></progress>
          <h3 className="text-white tracking-widest ">{progressData?.msg}</h3>

          {!!showCancel && (
            <span
              onClick={() => {
                window.location.reload();
              }}
              className="btn btn-outline btn-error"
            >
              Close
            </span>
          )}
        </div>
      )}
    </>
  );
};

export default ProgressLoading;
