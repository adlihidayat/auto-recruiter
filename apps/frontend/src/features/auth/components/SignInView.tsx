"use client";

import React, { useState } from "react";
import { FileCode2 } from "lucide-react";
import { useRouter } from "next/navigation";

export default function SignInView() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Navigate to dashboard on login
    router.push("/");
  };

  return (
    <div className="min-h-screen bg-[#F6F6F6] flex items-center justify-center p-4 md:p-8 font-sans">
      {/* Outer Card Container */}
      <div className="bg-white rounded-3xl border border-[#F1F1F1] p-5 md:p-4.5 shadow-2xs max-w-325 w-full grid grid-cols-1 lg:grid-cols-12 items-stretch">
        {/* Left Hero Panel */}
        <div className="lg:col-span-7 bg-[#F9F9F9] rounded-[24px] p-8 md:p-8 flex flex-col justify-between min-h-[700px]">
          {/* Top Brand & Menu Row */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5 text-black">
              <FileCode2 className="w-6 h-6" strokeWidth={2.5} />
              <span className="font-light text-2xl tracking-tight">
                auto-rec
              </span>
            </div>
            <div className="flex items-center gap-4 text-sm font-semibold text-[#272727]">
              <span className="cursor-pointer hover:underline">Username</span>
              <span className="cursor-pointer hover:underline">Username</span>
              <span className="cursor-pointer hover:underline">Username</span>
            </div>
          </div>

          {/* Bottom Banner Content */}
          <div className="pt-16 pb-4 ">
            <h1 className="text-4xl md:text-[54px] max-w-150 font-medium text-[#272727] tracking-tight leading-[1.12] mb-4">
              Login to access the app the app
            </h1>
            <p className="text-sm font-medium text-[#616161] leading-relaxed">
              We Pride Ourselves On Being The World&apos;s Leading Purveyor Of
              Highly Inventive (And Sometimes Explosive) Gadgets. We Are
              Actively Expanding Our Digital Infrastructure To Support Our
              Growing Catalog. We&apos;re Looking For An Innovative AI Engineer
              Who Can Bridge The Gap Between Complex Machine Learning Models And
              Intuitive Web Applications.
            </p>
          </div>
        </div>

        {/* Right Login Form Panel */}
        <div className="lg:col-span-5 flex flex-col justify-center pr-4 md:pr-16 ml-8 py-6">
          {/* Top Black Logo Icon */}
          <div className="w-10 h-10 rounded-xl bg-black text-white flex items-center justify-center mb-7">
            <FileCode2 className="w-5 h-5" strokeWidth={2} />
          </div>

          {/* Title */}
          <h2 className="text-2xl font-semibold text-[#272727] mb-7">
            Login to access the app
          </h2>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-sm font-semibold text-[#272727] mb-2.5 block">
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Your Name"
                className="w-full bg-[#F6F6F6] border-0 rounded-xl px-4 py-2.5 text-sm font-medium text-[#272727] placeholder:text-[#B8B8B8] focus:outline-none focus:ring-2 focus:ring-black/10 transition-shadow"
              />
            </div>

            <div>
              <label className="text-sm font-semibold text-[#272727] mb-2.5 block">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="password"
                className="w-full bg-[#F6F6F6] border-0 rounded-xl px-4 py-2.5 text-sm font-medium text-[#272727] placeholder:text-[#B8B8B8] focus:outline-none focus:ring-2 focus:ring-black/10 transition-shadow"
              />
            </div>

            <button
              type="submit"
              className="w-full bg-black hover:bg-[#272727] text-white text-sm font-semibold py-2.5 rounded-xl transition-colors cursor-pointer mt-4"
            >
              Login
            </button>
          </form>

          {/* Created with Footer */}
          <div className="mt-7">
            <span className="text-sm font-semibold text-[#272727] mb-3 block">
              Created with
            </span>
            <div className="flex gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-[#F6F6F6]" />
              <div className="w-9 h-9 rounded-xl bg-[#F6F6F6]" />
              <div className="w-9 h-9 rounded-xl bg-[#F6F6F6]" />
              <div className="w-9 h-9 rounded-xl bg-[#F6F6F6]" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
