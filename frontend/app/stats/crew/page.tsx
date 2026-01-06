"use client";

import { useState, useEffect } from "react";
import { DollarSign, Users, Send, Calculator, TrendingUp, AlertCircle } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const COLORS = {
  cyan: "#06b6d4",
  cyanDark: "#0891b2",
  green: "#22c55e",
  greenDark: "#16a34a",
  orange: "#f97316",
  red: "#ef4444",
  bgDark: "#0a0a0a",
  bgMedium: "#1a1a1a",
  bgLight: "#2a2a2a",
  textPrimary: "#e5e7eb",
  textSecondary: "#9ca3af",
  glowCyan: "rgba(6, 182, 212, 0.3)",
  glowGreen: "rgba(34, 197, 94, 0.3)",
};

interface CrewMember {
  id: number;
  username: string;
  share: number;
}

interface HistoryEvent {
  id: number;
  title: string;
  amount: number;
  event_date: string;
  crew_members_details: Array<{ id: number; username: string }>;
  tags: string[];
}

export default function CrewPayoutPage() {
  const [events, setEvents] = useState<HistoryEvent[]>([]);
  const [selectedEvents, setSelectedEvents] = useState<number[]>([]);
  const [crewShares, setCrewShares] = useState<CrewMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [sendingTo, setSendingTo] = useState<number | null>(null);

  useEffect(() => {
    loadProfitableEvents();
  }, []);

  const loadProfitableEvents = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${API_URL}/stats/history?tag=profit`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        // Filter events with amount > 0 and crew members
        const profitable = data.filter(
          (e: HistoryEvent) => e.amount > 0 && e.crew_members_details && e.crew_members_details.length > 1
        );
        setEvents(profitable);
      }
    } catch (err) {
      console.error("Failed to load events:", err);
    } finally {
      setLoading(false);
    }
  };

  const toggleEvent = (eventId: number) => {
    if (selectedEvents.includes(eventId)) {
      setSelectedEvents(selectedEvents.filter((id) => id !== eventId));
    } else {
      setSelectedEvents([...selectedEvents, eventId]);
    }
  };

  const calculateShares = () => {
    if (selectedEvents.length === 0) return;

    const selected = events.filter((e) => selectedEvents.includes(e.id));
    const totalProfit = selected.reduce((sum, e) => sum + e.amount, 0);

    // Get all unique crew members from selected events
    const crewMap = new Map<number, string>();
    selected.forEach((event) => {
      event.crew_members_details.forEach((member) => {
        crewMap.set(member.id, member.username);
      });
    });

    // Calculate equal shares
    const shareAmount = totalProfit / crewMap.size;

    const shares: CrewMember[] = Array.from(crewMap.entries()).map(([id, username]) => ({
      id,
      username,
      share: shareAmount,
    }));

    setCrewShares(shares);
  };

  const totalProfit = events
    .filter((e) => selectedEvents.includes(e.id))
    .reduce((sum, e) => sum + e.amount, 0);

  const serviceFee = totalProfit * 0.005; // 0.5% service fee like in-game
  const netAmount = totalProfit - serviceFee;

  if (loading) {
    return (
      <div
        style={{
          minHeight: "100vh",
          background: COLORS.bgDark,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: COLORS.textPrimary,
        }}
      >
        <div style={{ textAlign: "center" }}>
          <div
            style={{
              width: "60px",
              height: "60px",
              border: `4px solid ${COLORS.bgMedium}`,
              borderTopColor: COLORS.cyan,
              borderRadius: "50%",
              animation: "spin 1s linear infinite",
              margin: "0 auto 20px",
            }}
          />
          <div style={{ fontSize: "14px", letterSpacing: "3px", fontWeight: 600 }}>
            LOADING WALLET...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: "32px", maxWidth: "1600px", margin: "0 auto", minHeight: "100vh" }}>
      {/* HEADER */}
      <div style={{ marginBottom: "48px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "16px", marginBottom: "12px" }}>
          <DollarSign style={{ width: "32px", height: "32px", color: COLORS.green }} />
          <h1
            style={{
              fontSize: "48px",
              fontWeight: 700,
              color: "white",
              letterSpacing: "6px",
              textTransform: "uppercase",
              margin: 0,
              background: `linear-gradient(90deg, ${COLORS.green} 0%, ${COLORS.greenDark} 100%)`,
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            CREW PAYOUT
          </h1>
        </div>
        <div
          style={{
            color: COLORS.textSecondary,
            fontSize: "14px",
            letterSpacing: "2px",
            textTransform: "uppercase",
          }}
        >
          // MOBIGLASS WALLET - PROFIT DISTRIBUTION
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "32px" }}>
        {/* LEFT: SELECT EVENTS */}
        <div>
          <div
            style={{
              fontSize: "18px",
              fontWeight: 700,
              color: COLORS.textPrimary,
              marginBottom: "16px",
              letterSpacing: "2px",
              textTransform: "uppercase",
            }}
          >
            <Users style={{ width: "20px", height: "20px", display: "inline", marginRight: "8px" }} />
            SELECT PROFITABLE EVENTS
          </div>

          {events.length === 0 ? (
            <div
              style={{
                padding: "40px",
                background: COLORS.bgMedium,
                border: `1px solid ${COLORS.cyan}40`,
                borderRadius: "8px",
                textAlign: "center",
                color: COLORS.textSecondary,
              }}
            >
              <AlertCircle style={{ width: "40px", height: "40px", margin: "0 auto 16px", opacity: 0.5 }} />
              <div>No profitable crew events found</div>
              <div style={{ fontSize: "12px", marginTop: "8px" }}>
                Run missions with crew to see events here
              </div>
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              {events.map((event) => (
                <div
                  key={event.id}
                  onClick={() => toggleEvent(event.id)}
                  style={{
                    padding: "16px",
                    background: selectedEvents.includes(event.id)
                      ? `linear-gradient(135deg, ${COLORS.cyan}20 0%, ${COLORS.bgMedium} 100%)`
                      : COLORS.bgMedium,
                    border: `2px solid ${selectedEvents.includes(event.id) ? COLORS.cyan : `${COLORS.cyan}20`}`,
                    borderRadius: "8px",
                    cursor: "pointer",
                    transition: "all 0.3s ease",
                    boxShadow: selectedEvents.includes(event.id) ? `0 0 20px ${COLORS.glowCyan}` : "none",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
                    <div style={{ fontSize: "14px", fontWeight: 600, color: COLORS.textPrimary }}>
                      {event.title}
                    </div>
                    <div style={{ fontSize: "16px", fontWeight: 700, color: COLORS.green }}>
                      +{event.amount.toLocaleString()} aUEC
                    </div>
                  </div>
                  <div style={{ fontSize: "12px", color: COLORS.textSecondary }}>
                    {new Date(event.event_date).toLocaleDateString()} • Crew:{" "}
                    {event.crew_members_details.map((m) => m.username).join(", ")}
                  </div>
                </div>
              ))}
            </div>
          )}

          <button
            onClick={calculateShares}
            disabled={selectedEvents.length === 0}
            style={{
              width: "100%",
              padding: "16px",
              marginTop: "16px",
              background:
                selectedEvents.length === 0
                  ? COLORS.bgLight
                  : `linear-gradient(135deg, ${COLORS.cyan} 0%, ${COLORS.cyanDark} 100%)`,
              border: "none",
              borderRadius: "8px",
              color: selectedEvents.length === 0 ? COLORS.textSecondary : "white",
              fontSize: "14px",
              fontWeight: 700,
              letterSpacing: "2px",
              textTransform: "uppercase",
              cursor: selectedEvents.length === 0 ? "not-allowed" : "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "8px",
              boxShadow: selectedEvents.length === 0 ? "none" : `0 0 20px ${COLORS.glowCyan}`,
            }}
          >
            <Calculator style={{ width: "18px", height: "18px" }} />
            CALCULATE SHARES
          </button>
        </div>

        {/* RIGHT: PAYOUT SUMMARY */}
        <div>
          <div
            style={{
              fontSize: "18px",
              fontWeight: 700,
              color: COLORS.textPrimary,
              marginBottom: "16px",
              letterSpacing: "2px",
              textTransform: "uppercase",
            }}
          >
            <TrendingUp style={{ width: "20px", height: "20px", display: "inline", marginRight: "8px" }} />
            PAYOUT SUMMARY
          </div>

          {/* Total Calculation Card */}
          <div
            style={{
              padding: "24px",
              background: `linear-gradient(135deg, ${COLORS.bgMedium} 0%, ${COLORS.bgDark} 100%)`,
              border: `2px solid ${COLORS.cyan}60`,
              borderRadius: "12px",
              marginBottom: "24px",
              boxShadow: `0 0 30px ${COLORS.glowCyan}`,
            }}
          >
            <div style={{ marginBottom: "16px" }}>
              <div style={{ fontSize: "12px", color: COLORS.textSecondary, marginBottom: "4px" }}>
                TOTAL PROFIT
              </div>
              <div style={{ fontSize: "32px", fontWeight: 700, color: COLORS.green }}>
                {totalProfit.toLocaleString()} <span style={{ fontSize: "18px" }}>aUEC</span>
              </div>
            </div>

            <div
              style={{
                height: "1px",
                background: `linear-gradient(90deg, transparent, ${COLORS.cyan}40, transparent)`,
                margin: "16px 0",
              }}
            />

            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
              <div style={{ fontSize: "12px", color: COLORS.textSecondary }}>SERVICE FEE (0.5%)</div>
              <div style={{ fontSize: "14px", color: COLORS.orange }}>-{serviceFee.toFixed(0)} aUEC</div>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", marginTop: "16px" }}>
              <div style={{ fontSize: "14px", fontWeight: 700, color: COLORS.textPrimary }}>NET AMOUNT</div>
              <div style={{ fontSize: "20px", fontWeight: 700, color: COLORS.green }}>
                {netAmount.toFixed(0)} aUEC
              </div>
            </div>
          </div>

          {/* Crew Shares */}
          {crewShares.length > 0 && (
            <div
              style={{
                padding: "24px",
                background: COLORS.bgMedium,
                border: `1px solid ${COLORS.green}40`,
                borderRadius: "12px",
              }}
            >
              <div
                style={{
                  fontSize: "14px",
                  fontWeight: 700,
                  color: COLORS.textPrimary,
                  marginBottom: "16px",
                  letterSpacing: "1px",
                  textTransform: "uppercase",
                }}
              >
                SENDING TO
              </div>

              {crewShares.map((member) => (
                <div
                  key={member.id}
                  style={{
                    padding: "16px",
                    background: `linear-gradient(135deg, ${COLORS.green}10 0%, transparent 100%)`,
                    border: `1px solid ${COLORS.green}40`,
                    borderRadius: "8px",
                    marginBottom: "12px",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div>
                      <div style={{ fontSize: "16px", fontWeight: 700, color: COLORS.green }}>
                        {member.username}
                      </div>
                      <div style={{ fontSize: "11px", color: COLORS.textSecondary, marginTop: "2px" }}>
                        @{member.username.toLowerCase()}
                      </div>
                    </div>

                    <div style={{ textAlign: "right" }}>
                      <div style={{ fontSize: "18px", fontWeight: 700, color: COLORS.textPrimary }}>
                        {member.share.toFixed(0)}
                      </div>
                      <div style={{ fontSize: "11px", color: COLORS.textSecondary }}>aUEC</div>
                    </div>
                  </div>

                  <button
                    onClick={() => setSendingTo(member.id)}
                    style={{
                      width: "100%",
                      padding: "12px",
                      marginTop: "12px",
                      background: `linear-gradient(135deg, ${COLORS.green} 0%, ${COLORS.greenDark} 100%)`,
                      border: "none",
                      borderRadius: "6px",
                      color: "white",
                      fontSize: "12px",
                      fontWeight: 700,
                      letterSpacing: "1px",
                      textTransform: "uppercase",
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      gap: "8px",
                      boxShadow: `0 0 15px ${COLORS.glowGreen}`,
                    }}
                  >
                    <Send style={{ width: "14px", height: "14px" }} />
                    SEND
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <style jsx>{`
        @keyframes spin {
          to {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </div>
  );
}