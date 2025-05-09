import React from "react";

interface ImageProps {
  src: string | null;
  className?: string;
}

const Image: React.FC<ImageProps> = ({
  src,
  className = " w-full md:w-[46%] max-h-[50vh] ",
}) => {
  const [expanded, setExpanded] = React.useState(false);
  return (
    <div
      className={`${
        expanded ? " fixed inset-0 bg-black/80 z-50 " : ` ${className} static `
      } justify-center flex items-center transition-all duration-300 `}
    >
      <img
        src={src || ""}
        alt="Expanded"
        onClick={() => setExpanded((prev) => !prev)}
        className={`${
          !expanded && " h-full w-full "
        } select-none border max-w-[90%] max-h-[90%] cursor-pointer hover:border-black border-transparent `}
      />
    </div>
  );
};

export default Image;
