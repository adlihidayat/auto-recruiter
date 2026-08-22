import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";
import PageSkeletonWrapper from "@/components/common/PageSkeletonWrapper";

const plusJakartaSans = Plus_Jakarta_Sans({
  variable: "--font-plus-jakarta-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AutoRecruiter - AI Interview Platform",
  description: "Autonomous AI-powered interview platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${plusJakartaSans.variable} font-sans h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <PageSkeletonWrapper>{children}</PageSkeletonWrapper>
      </body>
    </html>
  );
}
