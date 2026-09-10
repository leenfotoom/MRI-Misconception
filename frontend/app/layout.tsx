import type { Metadata } from "next";
import { IBM_Plex_Sans_Arabic, Manrope } from "next/font/google";
import "./globals.css";

const manrope = Manrope({
  subsets: ["latin"],
  variable: "--font-manrope",
  display: "swap",
});

const arabic = IBM_Plex_Sans_Arabic({
  subsets: ["arabic"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-arabic",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Misconception MRI | Cognitive Diagnostics Platform",
  description:
    "Closed-loop STEM learning that diagnoses misconceptions, delivers targeted interventions, verifies reasoning, and builds major-aware study plans.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${manrope.variable} ${arabic.variable}`}>{children}</body>
    </html>
  );
}
