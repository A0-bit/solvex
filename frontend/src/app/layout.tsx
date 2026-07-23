import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GarbageMS — Garbage Reporting System",
  description: "Report and manage garbage collection in your community.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
