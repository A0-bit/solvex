"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import type { ComponentType } from "react";
import type { Role } from "@/types/user";
import { useAuthStore } from "@/store/authStore";

/**
 * Higher-order component that restricts route access to users with specific roles.
 * Unauthenticated users and users with the wrong role are redirected to /login.
 */
export function withRole<P extends object>(allowedRoles: Role[]) {
  return function (WrappedComponent: ComponentType<P>) {
    return function ProtectedRoute(props: P) {
      const router = useRouter();
      const { user, accessToken } = useAuthStore();

      useEffect(() => {
        if (!accessToken || !user) {
          router.replace("/login");
          return;
        }
        if (!allowedRoles.includes(user.role)) {
          // Redirect to the user's own dashboard
          if (user.role === "user") {
            router.replace("/dashboard");
          } else if (user.role === "supervisor") {
            router.replace("/supervisor/dashboard");
          } else {
            router.replace("/login");
          }
        }
      }, [accessToken, user, router]);

      if (!accessToken || !user || !allowedRoles.includes(user.role)) {
        return (
          <div className="flex min-h-screen items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-500 border-t-transparent" />
          </div>
        );
      }

      return <WrappedComponent {...props} />;
    };
  };
}
