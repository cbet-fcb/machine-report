export default function MyIcon(
  props: React.SVGProps<SVGSVGElement>
): React.JSX.Element {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 48 48"
      fill="none"
      stroke="currentColor"
      {...props}
    >
      <path
        d="M8.6,9.54v2.11H6.29A1.79,1.79,0,0,0,4.5,13.44v23.23a1.79,1.79,0,0,0,1.79,1.79H41.71a1.79,1.79,0,0,0,1.79-1.79V13.45a1.8,1.8,0,0,0-1.79-1.8H16.39V9.54ZM24,17.75a8.52,8.52,0,1,1-8.51,8.51A8.51,8.51,0,0,1,24,17.75Z"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
