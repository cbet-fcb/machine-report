import React from "react";

interface ImageProps {
  uploadedImage: string | null;
}

const Image: React.FC<ImageProps> = ({ uploadedImage }) => {
  const [expanded, setExpanded] = React.useState(false);
  return (
    <div
      className={`${
        expanded
          ? " fixed inset-0 bg-black/80 z-50 "
          : " static w-full md:w-[46%] max-h-[50vh] "
      } justify-center flex items-center transition-all duration-300`}
    >
      <img
        src={uploadedImage || ""}
        alt="Expanded"
        onClick={() => setExpanded((prev) => !prev)}
        className={` select-none border max-w-[90%] max-h-[90%] rounded-lg cursor-pointer hover:border-black border-transparent `}
      />
    </div>
  );
};

export default Image;
