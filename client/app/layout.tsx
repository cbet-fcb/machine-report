import type { Metadata } from "next";
import { ViewTransitions } from "next-view-transitions";
import { Poppins } from "next/font/google";
import "./globals.css";

import PageWrapper from "../components/PageWrapper";

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["100", "200", "300", "400", "500", "600", "700", "800", "900"],
});

export const metadata: Metadata = {
  title: "Machine Report",
  description: "machine report ocr",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ViewTransitions>
      <html lang="en">
        <body className={`${poppins.className}`}>
          <PageWrapper>{children}</PageWrapper>
        </body>
      </html>
    </ViewTransitions>
  );
}
