/**
 * What: Login / Sign In View component.
 * Why: Renders login interface with password visibility toggle.
 * Boundaries: Rendered on /login route.
 */

"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Lock, Mail, ArrowRight, Eye, EyeOff } from "lucide-react";
import { loginAction } from "../actions";
import Image from "next/image";

export default function SignInView() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) {
      setErrorMessage("Please enter both email/username and password.");
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    const result = await loginAction(username, password);

    if (result.success) {
      router.push("/");
      router.refresh();
    } else {
      setErrorMessage(result.error || "Invalid username or password");
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F6F6F6] flex flex-col items-center justify-center p-4 md:p-8 font-sans">
      {/* Main Split Container Card */}
      <div className="bg-white border border-gray-200 rounded-3xl p-6 md:py-6 md:pl-6 md:pr-10 max-w-5xl w-full flex gap-8 items-stretch">
        {/* left Column: Hero Graphic Preview Section */}
        <div className="w-full flex-1 rounded-3xl p-6 relative overflow-hidden flex flex-col justify-end items-center min-h-[380px]">
          <Image
            src={"/signin-bg.webp"}
            alt=""
            fill
            priority
            className=" absolute z-0 top-0 left-0"
          />

          <div className="z-10 flex flex-col items-center space-y-2 pb-5">
            <Image
              src={"/logo-no-bg.svg"}
              alt="logo"
              width={25}
              height={25}
              className="mb-3"
            />
            <span className="text-sm font-semibold mb-2">Auto Recruiter</span>
            <span className="text-xs font-medium text-gray-600">
              Access your AI recruiting campaigns{" "}
            </span>
          </div>
        </div>

        {/* right Column: Form Section */}
        <div className="py-18 max-w-110">
          <div>
            <h1 className="text-xl font-semibold text-gray-900 mt-6 mb-1">
              Log in to Account
            </h1>
            <p className="text-sm text-gray-600 font-medium mb-10">
              Welcome back! Access your AI recruiting campaigns & live voice
              workspace.
            </p>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Email / Username */}
              <div>
                <label className="text-sm font-semibold text-[#191919] mb-1.5 block">
                  Email or Username
                </label>
                <div className="relative flex items-center">
                  <div className="absolute left-3.5 text-[#646464] pointer-events-none">
                    <Mail className="w-4 h-4" />
                  </div>
                  <input
                    type="text"
                    required
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="alex@acedesign.io"
                    className="w-full bg-[#F6F6F6] border border-gray-200 rounded-md pl-10 pr-4 py-2 text-sm font-medium text-[#191919] placeholder:text-[#B8B8B8] focus:outline-none focus:ring-2 focus:ring-black/10 transition-shadow"
                  />
                </div>
              </div>

              {/* Password Input with Show/Hide Toggle */}
              <div className="mb-10">
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-sm font-semibold text-[#191919] block">
                    Password
                  </label>
                </div>
                <div className="relative flex items-center">
                  <div className="absolute left-3.5 text-[#646464] pointer-events-none">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    type={showPassword ? "text" : "password"}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full bg-[#F6F6F6] border border-gray-200 rounded-md pl-10 pr-10 py-2 text-sm font-medium text-[#191919] placeholder:text-[#B8B8B8] focus:outline-none focus:ring-2 focus:ring-black/10 transition-shadow"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 text-[#646464] hover:text-[#191919] p-1 cursor-pointer transition-colors"
                    title={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>

              {errorMessage && (
                <div className="p-3 rounded-xl bg-red-50 text-red-600 text-xs font-semibold border border-red-100">
                  {errorMessage}
                </div>
              )}

              {/* Link */}
              <div className="text-center md:text-left text-xs font-medium text-gray-600">
                Don&apos;t have a workspace yet?{" "}
                <Link
                  href="/create-account"
                  className="font-bold text-gray-900 underline hover:opacity-60"
                >
                  Create account
                </Link>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-[#191919] hover:bg-black text-white text-sm font-semibold py-2 rounded-lg transition-colors cursor-pointer flex items-center justify-center gap-2 mt-4 disabled:opacity-50"
              >
                <span>{isLoading ? "Signing in..." : "Log in"}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
