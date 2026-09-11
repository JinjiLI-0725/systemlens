import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SystemLens — AI for thinking in systems",
  description: "See the structure behind complex problems.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
