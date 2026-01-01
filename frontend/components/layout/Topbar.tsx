"use client";

import { Menu, Wifi, Settings, User, Bell, Search, LogOut, Home } from "lucide-react";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

type TopbarProps = {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
};

export function Topbar({ sidebarOpen, toggleSidebar }: TopbarProps) {
  const router = useRouter();
  const [currentTime, setCurrentTime] = useState<Date | null>(null);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [user, setUser] = useState<any>(null);

  // Charger l'utilisateur depuis localStorage
  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  // Timer
  useEffect(() => {
    setCurrentTime(new Date());
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const handleUserClick = () => {
    if (!user) {
      // Pas connecté → rediriger vers login
      router.push("/login");
    } else {
      // Connecté → toggle menu
      setUserMenuOpen(!userMenuOpen);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
    setUserMenuOpen(false);
    router.push("/login");
  };

  return (
    <header
      style={{
        height: "72px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 32px",
        background: "linear-gradient(90deg, #0a0e1a 0%, #050810 100%)",
        borderBottom: "1px solid rgba(6, 182, 212, 0.1)",
        position: "relative",
      }}
    >
      {/* Ligne lumineuse en bas */}
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
          height: "1px",
          background:
            "linear-gradient(90deg, transparent 0%, #06b6d4 50%, transparent 100%)",
          opacity: 0.3,
        }}
      />

      {/* LEFT SIDE */}
      <div style={{ display: "flex", alignItems: "center", gap: "24px" }}>
        {/* Menu Toggle */}
        <button
          onClick={toggleSidebar}
          style={{
            width: "40px",
            height: "40px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: "rgba(6, 182, 212, 0.05)",
            border: "1px solid rgba(6, 182, 212, 0.2)",
            borderRadius: "8px",
            color: "#06b6d4",
            cursor: "pointer",
            transition: "all 0.2s ease",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = "rgba(6, 182, 212, 0.1)";
            e.currentTarget.style.borderColor = "rgba(6, 182, 212, 0.4)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = "rgba(6, 182, 212, 0.05)";
            e.currentTarget.style.borderColor = "rgba(6, 182, 212, 0.2)";
          }}
        >
          <Menu style={{ width: "20px", height: "20px" }} />
        </button>

        {/* Title */}
        <div>
          <h1
            style={{
              fontSize: "18px",
              fontWeight: 700,
              color: "white",
              letterSpacing: "2px",
              textTransform: "uppercase",
              margin: 0,
            }}
          >
            Star Citizen – Economy Tool
          </h1>
          <div
            style={{
              fontSize: "11px",
              color: "#52525b",
              letterSpacing: "1px",
              marginTop: "2px",
            }}
          >
            Resource Management System
          </div>
        </div>
      </div>

      {/* RIGHT SIDE */}
      <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
        {/* Search */}
        <button
          style={{
            width: "40px",
            height: "40px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: "transparent",
            border: "1px solid rgba(82, 82, 91, 0.3)",
            borderRadius: "8px",
            color: "#71717a",
            cursor: "pointer",
            transition: "all 0.2s ease",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = "rgba(6, 182, 212, 0.3)";
            e.currentTarget.style.color = "#06b6d4";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = "rgba(82, 82, 91, 0.3)";
            e.currentTarget.style.color = "#71717a";
          }}
        >
          <Search style={{ width: "18px", height: "18px" }} />
        </button>

        {/* Notifications */}
        <button
          style={{
            width: "40px",
            height: "40px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: "transparent",
            border: "1px solid rgba(82, 82, 91, 0.3)",
            borderRadius: "8px",
            color: "#71717a",
            cursor: "pointer",
            transition: "all 0.2s ease",
            position: "relative",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = "rgba(6, 182, 212, 0.3)";
            e.currentTarget.style.color = "#06b6d4";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = "rgba(82, 82, 91, 0.3)";
            e.currentTarget.style.color = "#71717a";
          }}
        >
          <Bell style={{ width: "18px", height: "18px" }} />
          <div
            style={{
              position: "absolute",
              top: "8px",
              right: "8px",
              width: "6px",
              height: "6px",
              background: "#ef4444",
              borderRadius: "50%",
              boxShadow: "0 0 8px #ef4444",
            }}
          />
        </button>

        {/* Divider */}
        <div
          style={{
            width: "1px",
            height: "24px",
            background: "rgba(82, 82, 91, 0.3)",
          }}
        />

        {/* Time Display */}
        {currentTime && (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "flex-end",
            }}
          >
            <div
              style={{
                fontSize: "14px",
                fontWeight: 600,
                color: "#06b6d4",
                fontFamily: "monospace",
                letterSpacing: "1px",
              }}
            >
              {currentTime.toLocaleTimeString("fr-FR", {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
              })}
            </div>
            <div
              style={{
                fontSize: "10px",
                color: "#52525b",
                fontFamily: "monospace",
              }}
            >
              {currentTime.toLocaleDateString("fr-FR")}
            </div>
          </div>
        )}

        {/* API Status */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            padding: "8px 16px",
            background: "rgba(16, 185, 129, 0.1)",
            border: "1px solid rgba(16, 185, 129, 0.3)",
            borderRadius: "20px",
          }}
        >
          <Wifi style={{ width: "14px", height: "14px", color: "#10b981" }} />
          <span
            style={{
              fontSize: "11px",
              color: "#10b981",
              fontWeight: 600,
              letterSpacing: "0.5px",
            }}
          >
            ONLINE
          </span>
        </div>

        {/* Settings */}
        <button
          style={{
            width: "40px",
            height: "40px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: "transparent",
            border: "1px solid rgba(82, 82, 91, 0.3)",
            borderRadius: "8px",
            color: "#71717a",
            cursor: "pointer",
            transition: "all 0.2s ease",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = "rgba(6, 182, 212, 0.3)";
            e.currentTarget.style.color = "#06b6d4";
            e.currentTarget.style.transform = "rotate(90deg)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = "rgba(82, 82, 91, 0.3)";
            e.currentTarget.style.color = "#71717a";
            e.currentTarget.style.transform = "rotate(0deg)";
          }}
        >
          <Settings style={{ width: "18px", height: "18px" }} />
        </button>

        {/* User Profile with Dropdown */}
        <div style={{ position: "relative" }}>
          <button
            onClick={handleUserClick}
            style={{
              width: "40px",
              height: "40px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              background: user 
                ? "linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)"
                : "linear-gradient(135deg, #71717a 0%, #52525b 100%)",
              borderRadius: "8px",
              cursor: "pointer",
              boxShadow: user 
                ? "0 0 20px rgba(6, 182, 212, 0.3)"
                : "0 0 10px rgba(113, 113, 122, 0.2)",
              border: "none",
              transition: "all 0.2s ease",
            }}
          >
            <User style={{ width: "20px", height: "20px", color: "white" }} />
          </button>

          {/* Dropdown Menu */}
          {userMenuOpen && user && (
            <div
              style={{
                position: "absolute",
                top: "calc(100% + 8px)",
                right: 0,
                width: "220px",
                background: "linear-gradient(135deg, #0a0e1a 0%, #050810 100%)",
                border: "1px solid rgba(6, 182, 212, 0.3)",
                borderRadius: "8px",
                boxShadow: "0 8px 24px rgba(0, 0, 0, 0.5)",
                zIndex: 1000,
                overflow: "hidden",
              }}
            >
              {/* User Info */}
              <div
                style={{
                  padding: "16px",
                  borderBottom: "1px solid rgba(6, 182, 212, 0.2)",
                }}
              >
                <div
                  style={{
                    fontSize: "14px",
                    fontWeight: 700,
                    color: "#06b6d4",
                    marginBottom: "4px",
                  }}
                >
                  {user.username}
                </div>
                <div
                  style={{
                    fontSize: "11px",
                    color: "#52525b",
                    textTransform: "uppercase",
                    letterSpacing: "1px",
                  }}
                >
                  {user.role}
                </div>
              </div>

              {/* Menu Items */}
              <button
                onClick={() => {
                  setUserMenuOpen(false);
                  router.push("/");
                }}
                style={{
                  width: "100%",
                  padding: "12px 16px",
                  display: "flex",
                  alignItems: "center",
                  gap: "12px",
                  background: "transparent",
                  border: "none",
                  color: "#94a3b8",
                  fontSize: "13px",
                  cursor: "pointer",
                  transition: "all 0.2s ease",
                  textAlign: "left",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = "rgba(6, 182, 212, 0.1)";
                  e.currentTarget.style.color = "#06b6d4";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = "transparent";
                  e.currentTarget.style.color = "#94a3b8";
                }}
              >
                <Home style={{ width: "16px", height: "16px" }} />
                Dashboard
              </button>

              <button
                onClick={handleLogout}
                style={{
                  width: "100%",
                  padding: "12px 16px",
                  display: "flex",
                  alignItems: "center",
                  gap: "12px",
                  background: "transparent",
                  border: "none",
                  color: "#ef4444",
                  fontSize: "13px",
                  cursor: "pointer",
                  transition: "all 0.2s ease",
                  textAlign: "left",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = "rgba(239, 68, 68, 0.1)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = "transparent";
                }}
              >
                <LogOut style={{ width: "16px", height: "16px" }} />
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}