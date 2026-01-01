"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { User, Lock, LogIn } from "lucide-react";

const COLORS = {
  orange: "#d97706",
  red: "#dc2626",
  yellow: "#eab308",
  greenOlive: "#84a98c",
  bgDark: "#0f172a",
  bgMedium: "#1e293b",
  bgLight: "#334155",
  textPrimary: "#e2e8f0",
  textSecondary: "#94a3b8",
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
console.log("🔍 API_URL:", API_URL);

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Login failed");
      }

      const data = await response.json();
      
      // Stocker le token et les infos user
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));

      // Déclencher événement de login ✅
      window.dispatchEvent(new Event("user-login"));

      // Rediriger vers le dashboard
      router.push("/");
      
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: `linear-gradient(135deg, #030712 0%, #000000 100%)`,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: "20px"
    }}>
      <div style={{
        width: "100%",
        maxWidth: "400px",
        background: `linear-gradient(135deg, ${COLORS.bgMedium} 0%, ${COLORS.bgDark} 100%)`,
        border: `1px solid ${COLORS.orange}60`,
        borderRadius: "4px",
        padding: "40px",
        clipPath: "polygon(0 0, calc(100% - 12px) 0, 100% 12px, 100% 100%, 12px 100%, 0 calc(100% - 12px))",
        boxShadow: `0 0 30px ${COLORS.orange}30`
      }}>
        {/* Header */}
        <div style={{
          textAlign: "center",
          marginBottom: "40px"
        }}>
          <div style={{
            fontSize: "11px",
            color: COLORS.red,
            letterSpacing: "2px",
            textTransform: "uppercase",
            fontWeight: 700,
            marginBottom: "12px",
            fontFamily: "monospace"
          }}>
            // AUTHENTICATION SYSTEM
          </div>
          <h1 style={{
            fontSize: "32px",
            fontWeight: 700,
            color: COLORS.textPrimary,
            letterSpacing: "2px",
            textTransform: "uppercase",
            margin: 0,
            fontFamily: "monospace",
            textShadow: `0 0 15px ${COLORS.orange}40`
          }}>
            STAR CITIZEN
          </h1>
          <div style={{
            fontSize: "14px",
            color: COLORS.textSecondary,
            marginTop: "8px",
            fontFamily: "monospace"
          }}>
            ECONOMY TOOL
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div style={{
            padding: "12px",
            background: `${COLORS.red}20`,
            border: `1px solid ${COLORS.red}`,
            borderRadius: "2px",
            color: COLORS.red,
            fontSize: "12px",
            marginBottom: "24px",
            fontFamily: "monospace"
          }}>
            ⚠️ {error}
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleLogin}>
          {/* Username */}
          <div style={{ marginBottom: "24px" }}>
            <label style={{
              display: "block",
              fontSize: "10px",
              color: COLORS.textSecondary,
              letterSpacing: "1px",
              textTransform: "uppercase",
              marginBottom: "8px",
              fontFamily: "monospace"
            }}>
              USERNAME
            </label>
            <div style={{ position: "relative" }}>
              <User style={{
                position: "absolute",
                left: "12px",
                top: "50%",
                transform: "translateY(-50%)",
                width: "16px",
                height: "16px",
                color: COLORS.textSecondary
              }} />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                style={{
                  width: "100%",
                  padding: "12px 12px 12px 40px",
                  background: COLORS.bgDark,
                  border: `1px solid ${COLORS.bgLight}`,
                  borderRadius: "2px",
                  color: COLORS.textPrimary,
                  fontSize: "14px",
                  fontFamily: "monospace",
                  outline: "none",
                  boxSizing: "border-box",
                }}
                onFocus={(e) => e.target.style.borderColor = COLORS.orange}
                onBlur={(e) => e.target.style.borderColor = COLORS.bgLight}
              />
            </div>
          </div>

          {/* Password */}
          <div style={{ marginBottom: "32px" }}>
            <label style={{
              display: "block",
              fontSize: "10px",
              color: COLORS.textSecondary,
              letterSpacing: "1px",
              textTransform: "uppercase",
              marginBottom: "8px",
              fontFamily: "monospace"
            }}>
              PASSWORD
            </label>
            <div style={{ position: "relative" }}>
              <Lock style={{
                position: "absolute",
                left: "12px",
                top: "50%",
                transform: "translateY(-50%)",
                width: "16px",
                height: "16px",
                color: COLORS.textSecondary
              }} />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                style={{
                  width: "100%",
                  padding: "12px 12px 12px 40px",
                  background: COLORS.bgDark,
                  border: `1px solid ${COLORS.bgLight}`,
                  borderRadius: "2px",
                  color: COLORS.textPrimary,
                  fontSize: "14px",
                  fontFamily: "monospace",
                  outline: "none",
                  boxSizing: "border-box",
                }}
                onFocus={(e) => e.target.style.borderColor = COLORS.orange}
                onBlur={(e) => e.target.style.borderColor = COLORS.bgLight}
              />
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            style={{
              width: "100%",
              padding: "14px",
              background: loading 
                ? COLORS.bgLight 
                : `linear-gradient(135deg, ${COLORS.yellow} 0%, ${COLORS.orange} 100%)`,
              border: `1px solid ${loading ? COLORS.bgLight : COLORS.yellow}`,
              borderRadius: "2px",
              color: COLORS.bgDark,
              fontSize: "13px",
              fontWeight: 700,
              letterSpacing: "2px",
              textTransform: "uppercase",
              cursor: loading ? "not-allowed" : "pointer",
              fontFamily: "monospace",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "10px",
              boxShadow: loading ? "none" : `0 0 20px ${COLORS.yellow}40`,
              transition: "all 0.2s ease"
            }}
          >
            <LogIn style={{ width: "16px", height: "16px" }} />
            {loading ? "AUTHENTICATING..." : "ACCESS SYSTEM"}
          </button>
        </form>
      </div>
    </div>
  );
}