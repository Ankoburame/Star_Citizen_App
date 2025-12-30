"use client";

import { Menu, Wifi, Settings, User, Bell, Search } from "lucide-react";
import { useState } from "react";

type TopbarProps = {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
};

export function Topbar({ sidebarOpen, toggleSidebar }: TopbarProps) {
  const [currentTime, setCurrentTime] = useState(new Date());

  // Update time every second
  useState(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  });

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
        {/* Search (future feature) */}
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

        {/* Notifications (future) */}
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
          {/* Notification badge (exemple) */}
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

        {/* API Status Indicator */}
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

        {/* User Profile */}
        <div
          style={{
            width: "40px",
            height: "40px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: "linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)",
            borderRadius: "8px",
            cursor: "pointer",
            boxShadow: "0 0 20px rgba(6, 182, 212, 0.3)",
          }}
        >
          <User style={{ width: "20px", height: "20px", color: "white" }} />
        </div>
      </div>
    </header>
  );
}