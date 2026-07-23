"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuthStore } from "@/store/authStore";

export default function LandingPage() {
  const router = useRouter();
  const { user, accessToken } = useAuthStore();

  // If already logged in, skip this page
  useEffect(() => {
    if (accessToken && user) {
      if (user.role === "user") router.replace("/dashboard");
      else if (user.role === "supervisor") router.replace("/supervisor/dashboard");
    }
  }, [accessToken, user, router]);

  // Still checking auth state — show nothing to avoid flash
  if (accessToken && user) return null;

  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-br from-green-50 via-white to-emerald-50">
      {/* Navbar */}
      <header className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-2 font-bold text-green-700 text-lg">
          <svg className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          GarbageMS
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/login"
            className="rounded-lg px-4 py-2 text-sm font-medium text-green-700 hover:bg-green-50 transition"
          >
            Log in
          </Link>
          <Link
            href="/register"
            className="rounded-lg bg-green-600 px-4 py-2 text-sm font-semibold text-white hover:bg-green-700 transition shadow-sm"
          >
            Sign up
          </Link>
        </div>
      </header>

      {/* Hero */}
      <main className="flex flex-1 flex-col items-center justify-center px-6 text-center">
        {/* Icon badge */}
        <div className="mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-green-100 shadow-inner">
          <svg className="h-10 w-10 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </div>

        <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl">
          Keep your city <span className="text-green-600">clean</span>
        </h1>
        <p className="mt-4 max-w-md text-base text-gray-500 sm:text-lg">
          Report garbage, track cleanups, and help supervisors manage waste collection — all in one place.
        </p>

        {/* CTA buttons */}
        <div className="mt-8 flex flex-col gap-3 sm:flex-row">
          <Link
            href="/register"
            className="rounded-xl bg-green-600 px-8 py-3 text-base font-semibold text-white shadow-md hover:bg-green-700 transition"
          >
            Get started — it&apos;s free
          </Link>
          <Link
            href="/login"
            className="rounded-xl border border-gray-300 bg-white px-8 py-3 text-base font-semibold text-gray-700 hover:bg-gray-50 transition"
          >
            Log in to your account
          </Link>
        </div>

        {/* Feature pills */}
        <div className="mt-12 flex flex-wrap justify-center gap-3">
          {[
            { icon: "📍", label: "GPS-pinned reports" },
            { icon: "📸", label: "Before & after photos" },
            { icon: "🗺️", label: "Area map view" },
            { icon: "🔔", label: "Status notifications" },
          ].map((f) => (
            <span
              key={f.label}
              className="inline-flex items-center gap-1.5 rounded-full border border-gray-200 bg-white px-4 py-1.5 text-sm font-medium text-gray-600 shadow-sm"
            >
              <span>{f.icon}</span>
              {f.label}
            </span>
          ))}
        </div>
      </main>

      {/* How it works */}
      <section className="mx-auto w-full max-w-3xl px-6 py-16">
        <h2 className="mb-8 text-center text-2xl font-bold text-gray-900">How it works</h2>
        <div className="grid gap-6 sm:grid-cols-3">
          {[
            {
              step: "1",
              title: "Snap & report",
              desc: "Take a photo of the garbage, pin the location, and submit in seconds.",
              color: "bg-yellow-100 text-yellow-700",
            },
            {
              step: "2",
              title: "Supervisor assigns",
              desc: "A local supervisor reviews the report and assigns the nearest cleaner.",
              color: "bg-blue-100 text-blue-700",
            },
            {
              step: "3",
              title: "Resolved ✓",
              desc: "The cleaner cleans up, uploads an after photo, and you get notified.",
              color: "bg-green-100 text-green-700",
            },
          ].map((item) => (
            <div key={item.step} className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
              <span className={`inline-flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold ${item.color}`}>
                {item.step}
              </span>
              <h3 className="mt-3 font-semibold text-gray-900">{item.title}</h3>
              <p className="mt-1 text-sm text-gray-500">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer CTA */}
      <section className="border-t border-gray-200 bg-white py-12 text-center">
        <h2 className="text-xl font-bold text-gray-900">Ready to make a difference?</h2>
        <p className="mt-2 text-sm text-gray-500">Join your community. Report garbage today.</p>
        <div className="mt-6 flex justify-center gap-4">
          <Link
            href="/register"
            className="rounded-xl bg-green-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-green-700 transition"
          >
            Create free account
          </Link>
          <Link
            href="/login"
            className="rounded-xl border border-gray-300 px-6 py-2.5 text-sm font-semibold text-gray-700 hover:bg-gray-50 transition"
          >
            Log in
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-6 text-center text-xs text-gray-400">
        © {new Date().getFullYear()} GarbageMS. Built to keep communities clean.
      </footer>
    </div>
  );
}
