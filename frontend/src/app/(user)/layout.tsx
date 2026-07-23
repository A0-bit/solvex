"use client";

import Navbar from "@/components/layout/Navbar";
import BottomNav from "@/components/layout/BottomNav";
import { useAuthStore } from "@/store/authStore";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function UserLayout({ children }: { children: React.ReactNode }) {
  const { user, accessToken } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (!accessToken || !user) {
      router.replace("/login");
    } else if (user.role !== "user") {
      router.replace("/supervisor/dashboard");
    }
  }, [accessToken, user, router]);

  if (!accessToken || !user || user.role !== "user") return null;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="mx-auto max-w-2xl px-4 pb-24 pt-6">{children}</main>
      <BottomNav />
    </div>
  );
}
