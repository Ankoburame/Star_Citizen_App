"use client";

import { useState, useEffect } from "react";
import { DollarSign, Users, Send, Calculator, TrendingUp, AlertCircle, Check, Zap } from "lucide-react";

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

interface ProfitableEvent {
  id: number;
  title: string;
  amount: number;
  event_date: string;
  crew_count: number;
  tags: string[];
}

interface CrewShare {
  user_id: number;
  username: string;
  share_amount: number;
  event_count: number;
}

interface PayoutCalculation {
  total_profit: number;
  service_fee: number;
  net_amount: number;
  crew_shares: CrewShare[];
}

export default function CrewPayoutPage() {
  const [events, setEvents] = useState<ProfitableEvent[]>([]);
  const [selectedEvents, setSelectedEvents] = useState<number[]>([]);
  const [calculation, setCalculation] = useState<PayoutCalculation | null>(null);
  const [loading, setLoading] = useState(true);
  const [calculating, setCalculating] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [sentTo, setSentTo] = useState<Set<number>>(new Set());

  useEffect(() => {
    loadProfitableEvents();
  }, []);

  const loadProfitableEvents = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${API_URL}/stats/history/payout/events`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setEvents(data.events || []);
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
    setCalculation(null);
  };

  const calculateShares = async () => {
    if (selectedEvents.length === 0) return;

    setCalculating(true);
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${API_URL}/stats/history/payout/calculate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ event_ids: selectedEvents }),
      });

      if (response.ok) {
        const data = await response.json();
        setCalculation(data);
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
      }
    } catch (err) {
      console.error("Failed to calculate:", err);
      alert("Failed to calculate shares");
    } finally {
      setCalculating(false);
    }
  };

  const sendPayout = async (recipientId: number, amount: number, username: string) => {
    if (executing) return;
    
    if (!confirm(`Send ${amount.toFixed(0)} aUEC to ${username}?`)) return;

    setExecuting(true);
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${API_URL}/stats/history/payout/execute`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          event_ids: selectedEvents,
          transactions: [
            {
              recipient_id: recipientId,
              amount: amount,
              note: `Crew payout for ${selectedEvents.length} events`,
            },
          ],
        }),
      });

      if (response.ok) {
        setSentTo(new Set([...sentTo, recipientId]));
        alert(`✅ Sent ${amount.toFixed(0)} aUEC to ${username}!`);
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
      }
    } catch (err) {
      console.error("Failed to send:", err);
      alert("Failed to send payout");
    } finally {
      setExecuting(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="hologram-loader">
          <div className="loader-ring"></div>
          <div className="loader-ring"></div>
          <div className="loader-ring"></div>
          <Zap className="loader-icon" />
        </div>
        <div className="loading-text">INITIALIZING WALLET INTERFACE</div>
        <div className="loading-subtext">// ACCESSING FINANCIAL SYSTEMS</div>
      </div>
    );
  }

  return (
    <div className="crew-payout-container">
      {/* Animated Background */}
      <div className="background-grid"></div>
      <div className="particles-container">
        {[...Array(20)].map((_, i) => (
          <div key={i} className="particle" style={{ 
            left: `${Math.random() * 100}%`,
            animationDelay: `${Math.random() * 5}s`,
            animationDuration: `${15 + Math.random() * 10}s`
          }}></div>
        ))}
      </div>

      <div className="content-wrapper">
        {/* HEADER */}
        <div className="header-section">
          <div className="header-title-row">
            <div className="icon-container">
              <DollarSign className="header-icon" />
              <div className="icon-glow"></div>
            </div>
            <h1 className="main-title">
              <span className="title-text">CREW PAYOUT</span>
              <div className="title-underline"></div>
            </h1>
          </div>
          <div className="header-subtitle">
            <div className="subtitle-line"></div>
            <span>MOBIGLASS WALLET - PROFIT DISTRIBUTION</span>
            <div className="subtitle-line"></div>
          </div>
          <div className="scan-line"></div>
        </div>

        <div className="grid-container">
          {/* LEFT: SELECT EVENTS */}
          <div className="panel-wrapper">
            <div className="panel-header">
              <Users className="panel-icon" />
              <span>SELECT PROFITABLE EVENTS</span>
              <div className="header-glow"></div>
            </div>

            {events.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon-container">
                  <AlertCircle className="empty-icon" />
                  <div className="pulse-ring"></div>
                </div>
                <div className="empty-text">No profitable crew events found</div>
                <div className="empty-subtext">Run missions with crew to see events here</div>
              </div>
            ) : (
              <div className="events-list">
                {events.map((event, index) => (
                  <div
                    key={event.id}
                    onClick={() => toggleEvent(event.id)}
                    className={`event-card ${selectedEvents.includes(event.id) ? 'selected' : ''}`}
                    style={{ animationDelay: `${index * 0.05}s` }}
                  >
                    <div className="card-glow"></div>
                    <div className="card-content">
                      <div className="event-header">
                        <div className="event-title">{event.title}</div>
                        <div className="event-amount">
                          <DollarSign className="amount-icon" />
                          <span>+{event.amount.toLocaleString()}</span>
                          <span className="currency">aUEC</span>
                        </div>
                      </div>
                      <div className="event-meta">
                        <span>{new Date(event.event_date).toLocaleDateString()}</span>
                        <span className="separator">•</span>
                        <Users className="meta-icon" />
                        <span>Crew: {event.crew_count}</span>
                      </div>
                    </div>
                    <div className="shimmer"></div>
                  </div>
                ))}
              </div>
            )}

            <button
              onClick={calculateShares}
              disabled={selectedEvents.length === 0 || calculating}
              className={`calculate-button ${selectedEvents.length === 0 || calculating ? 'disabled' : ''}`}
            >
              <div className="button-bg"></div>
              <Calculator className="button-icon" />
              <span>{calculating ? "CALCULATING..." : "CALCULATE SHARES"}</span>
              {!calculating && selectedEvents.length > 0 && (
                <>
                  <div className="button-glow"></div>
                  <div className="button-particles">
                    {[...Array(6)].map((_, i) => (
                      <div key={i} className="button-particle"></div>
                    ))}
                  </div>
                </>
              )}
            </button>
          </div>

          {/* RIGHT: PAYOUT SUMMARY */}
          <div className="panel-wrapper">
            <div className="panel-header">
              <TrendingUp className="panel-icon" />
              <span>PAYOUT SUMMARY</span>
              <div className="header-glow"></div>
            </div>

            {calculation ? (
              <>
                {/* Total Calculation */}
                <div className="calculation-card">
                  <div className="calc-overlay"></div>
                  <div className="total-section">
                    <div className="total-label">TOTAL PROFIT</div>
                    <div className="total-amount">
                      <span className="amount-value">{calculation.total_profit.toLocaleString()}</span>
                      <span className="amount-currency">aUEC</span>
                    </div>
                    <div className="amount-shimmer"></div>
                  </div>

                  <div className="divider">
                    <div className="divider-line"></div>
                  </div>

                  <div className="fee-row">
                    <span className="fee-label">SERVICE FEE (0.5%)</span>
                    <span className="fee-amount">-{calculation.service_fee.toFixed(0)} aUEC</span>
                  </div>

                  <div className="net-row">
                    <span className="net-label">NET AMOUNT</span>
                    <span className="net-amount">{calculation.net_amount.toFixed(0)} aUEC</span>
                  </div>
                </div>

                {/* Crew Shares */}
                <div className="shares-container">
                  <div className="shares-header">
                    <span>SENDING TO</span>
                    <div className="shares-count">{calculation.crew_shares.length}</div>
                  </div>

                  {calculation.crew_shares.map((member, index) => (
                    <div 
                      key={member.user_id} 
                      className="member-card"
                      style={{ animationDelay: `${index * 0.1}s` }}
                    >
                      <div className="member-glow"></div>
                      <div className="member-info">
                        <div className="member-details">
                          <div className="member-name">{member.username}</div>
                          <div className="member-handle">@{member.username.toLowerCase()}</div>
                        </div>
                        <div className="member-amount">
                          <span className="share-value">{member.share_amount.toFixed(0)}</span>
                          <span className="share-currency">aUEC</span>
                        </div>
                      </div>

                      <button
                        onClick={() => sendPayout(member.user_id, member.share_amount, member.username)}
                        disabled={executing || sentTo.has(member.user_id)}
                        className={`send-button ${sentTo.has(member.user_id) ? 'sent' : ''}`}
                      >
                        {sentTo.has(member.user_id) ? (
                          <>
                            <Check className="button-icon" />
                            <span>SENT</span>
                          </>
                        ) : (
                          <>
                            <Send className="button-icon" />
                            <span>{executing ? "SENDING..." : "SEND"}</span>
                            {!executing && <div className="send-glow"></div>}
                          </>
                        )}
                      </button>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="empty-state">
                <div className="empty-icon-container">
                  <Calculator className="empty-icon" />
                  <div className="pulse-ring"></div>
                </div>
                <div className="empty-text">Select events and calculate shares</div>
                <div className="empty-subtext">to see payout distribution</div>
              </div>
            )}
          </div>
        </div>
      </div>

      <style jsx>{`
        .crew-payout-container {
          min-height: 100vh;
          background: #0a0a0a;
          padding: 32px;
          position: relative;
          overflow: hidden;
        }

        /* Animated Background */
        .background-grid {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-image: 
            linear-gradient(rgba(6, 182, 212, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(6, 182, 212, 0.03) 1px, transparent 1px);
          background-size: 50px 50px;
          animation: gridMove 20s linear infinite;
          pointer-events: none;
        }

        @keyframes gridMove {
          0% { transform: translate(0, 0); }
          100% { transform: translate(50px, 50px); }
        }

        .particles-container {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          pointer-events: none;
          overflow: hidden;
        }

        .particle {
          position: absolute;
          width: 2px;
          height: 2px;
          background: #06b6d4;
          border-radius: 50%;
          animation: particleFloat linear infinite;
          box-shadow: 0 0 4px #06b6d4;
        }

        @keyframes particleFloat {
          0% {
            transform: translateY(100vh) translateX(0);
            opacity: 0;
          }
          10% {
            opacity: 1;
          }
          90% {
            opacity: 1;
          }
          100% {
            transform: translateY(-100px) translateX(100px);
            opacity: 0;
          }
        }

        .content-wrapper {
          max-width: 1600px;
          margin: 0 auto;
          position: relative;
          z-index: 1;
        }

        /* Header */
        .header-section {
          margin-bottom: 48px;
          position: relative;
        }

        .header-title-row {
          display: flex;
          align-items: center;
          gap: 24px;
          margin-bottom: 16px;
        }

        .icon-container {
          position: relative;
          width: 60px;
          height: 60px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .header-icon {
          width: 32px;
          height: 32px;
          color: #22c55e;
          position: relative;
          z-index: 2;
          filter: drop-shadow(0 0 8px #22c55e);
        }

        .icon-glow {
          position: absolute;
          inset: 0;
          background: radial-gradient(circle, rgba(34, 197, 94, 0.3) 0%, transparent 70%);
          animation: pulse 2s ease-in-out infinite;
        }

        .main-title {
          position: relative;
          margin: 0;
        }

        .title-text {
          font-size: 56px;
          font-weight: 700;
          letter-spacing: 8px;
          background: linear-gradient(90deg, #22c55e 0%, #16a34a 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          display: inline-block;
          animation: titleGlow 3s ease-in-out infinite;
          text-shadow: 0 0 30px rgba(34, 197, 94, 0.5);
        }

        @keyframes titleGlow {
          0%, 100% { filter: brightness(1); }
          50% { filter: brightness(1.3); }
        }

        .title-underline {
          height: 3px;
          background: linear-gradient(90deg, #22c55e, transparent);
          margin-top: 8px;
          animation: underlineExpand 2s ease-out;
        }

        @keyframes underlineExpand {
          from { width: 0; }
          to { width: 100%; }
        }

        .header-subtitle {
          display: flex;
          align-items: center;
          gap: 16px;
          color: #9ca3af;
          font-size: 13px;
          letter-spacing: 3px;
          text-transform: uppercase;
          font-weight: 600;
        }

        .subtitle-line {
          flex: 1;
          height: 1px;
          background: linear-gradient(90deg, transparent, #06b6d4, transparent);
        }

        .scan-line {
          position: absolute;
          bottom: -10px;
          left: 0;
          right: 0;
          height: 2px;
          background: linear-gradient(90deg, transparent, #06b6d4, transparent);
          animation: scanMove 3s linear infinite;
        }

        @keyframes scanMove {
          0% { transform: translateX(-100%); opacity: 0; }
          50% { opacity: 1; }
          100% { transform: translateX(100%); opacity: 0; }
        }

        /* Grid Layout */
        .grid-container {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 32px;
        }

        /* Panels */
        .panel-wrapper {
          background: linear-gradient(135deg, rgba(26, 26, 26, 0.9) 0%, rgba(10, 10, 10, 0.9) 100%);
          border: 1px solid rgba(6, 182, 212, 0.2);
          border-radius: 16px;
          padding: 24px;
          position: relative;
          backdrop-filter: blur(10px);
          overflow: hidden;
        }

        .panel-wrapper::before {
          content: '';
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(6, 182, 212, 0.1), transparent);
          animation: shimmerSweep 3s infinite;
        }

        @keyframes shimmerSweep {
          to { left: 100%; }
        }

        .panel-header {
          display: flex;
          align-items: center;
          gap: 12px;
          font-size: 16px;
          font-weight: 700;
          color: #e5e7eb;
          letter-spacing: 2px;
          text-transform: uppercase;
          margin-bottom: 24px;
          position: relative;
          padding-bottom: 16px;
        }

        .panel-header::after {
          content: '';
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          height: 1px;
          background: linear-gradient(90deg, #06b6d4, transparent);
        }

        .panel-icon {
          width: 20px;
          height: 20px;
          color: #06b6d4;
          filter: drop-shadow(0 0 6px #06b6d4);
        }

        .header-glow {
          flex: 1;
          height: 1px;
          background: linear-gradient(90deg, rgba(6, 182, 212, 0.5), transparent);
        }

        /* Events List */
        .events-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
          max-height: 600px;
          overflow-y: auto;
          padding-right: 8px;
          margin-bottom: 16px;
        }

        .events-list::-webkit-scrollbar {
          width: 6px;
        }

        .events-list::-webkit-scrollbar-track {
          background: rgba(6, 182, 212, 0.05);
          border-radius: 3px;
        }

        .events-list::-webkit-scrollbar-thumb {
          background: rgba(6, 182, 212, 0.3);
          border-radius: 3px;
        }

        .event-card {
          position: relative;
          padding: 16px;
          background: rgba(26, 26, 26, 0.6);
          border: 2px solid rgba(6, 182, 212, 0.2);
          border-radius: 12px;
          cursor: pointer;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          animation: fadeInUp 0.4s ease-out both;
          overflow: hidden;
        }

        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .event-card:hover {
          border-color: rgba(6, 182, 212, 0.6);
          transform: translateY(-4px) scale(1.02);
          box-shadow: 0 8px 32px rgba(6, 182, 212, 0.2);
        }

        .event-card.selected {
          background: linear-gradient(135deg, rgba(6, 182, 212, 0.15) 0%, rgba(26, 26, 26, 0.8) 100%);
          border-color: #06b6d4;
          box-shadow: 0 0 30px rgba(6, 182, 212, 0.3), inset 0 0 20px rgba(6, 182, 212, 0.1);
        }

        .card-glow {
          position: absolute;
          top: -50%;
          left: -50%;
          width: 200%;
          height: 200%;
          background: radial-gradient(circle, rgba(6, 182, 212, 0.1) 0%, transparent 70%);
          opacity: 0;
          transition: opacity 0.3s;
        }

        .event-card.selected .card-glow {
          opacity: 1;
          animation: rotate 4s linear infinite;
        }

        @keyframes rotate {
          to { transform: rotate(360deg); }
        }

        .card-content {
          position: relative;
          z-index: 2;
        }

        .event-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 12px;
        }

        .event-title {
          font-size: 15px;
          font-weight: 600;
          color: #e5e7eb;
          letter-spacing: 0.5px;
        }

        .event-amount {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 18px;
          font-weight: 700;
          color: #22c55e;
          text-shadow: 0 0 10px rgba(34, 197, 94, 0.5);
        }

        .amount-icon {
          width: 16px;
          height: 16px;
        }

        .currency {
          font-size: 12px;
          opacity: 0.8;
        }

        .event-meta {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 12px;
          color: #9ca3af;
        }

        .separator {
          opacity: 0.5;
        }

        .meta-icon {
          width: 14px;
          height: 14px;
        }

        .shimmer {
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        }

        .event-card:hover .shimmer {
          animation: shimmer 1.5s;
        }

        @keyframes shimmer {
          to { left: 100%; }
        }

        /* Calculate Button */
        .calculate-button {
          width: 100%;
          padding: 18px;
          background: transparent;
          border: 2px solid #06b6d4;
          border-radius: 12px;
          color: white;
          font-size: 14px;
          font-weight: 700;
          letter-spacing: 2px;
          text-transform: uppercase;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 12px;
          position: relative;
          overflow: hidden;
          transition: all 0.3s;
        }

        .calculate-button:not(.disabled):hover {
          transform: scale(1.05);
          box-shadow: 0 0 40px rgba(6, 182, 212, 0.4);
        }

        .button-bg {
          position: absolute;
          inset: 0;
          background: linear-gradient(135deg, rgba(6, 182, 212, 0.2) 0%, rgba(8, 145, 178, 0.2) 100%);
          opacity: 0;
          transition: opacity 0.3s;
        }

        .calculate-button:not(.disabled):hover .button-bg {
          opacity: 1;
        }

        .button-icon {
          width: 18px;
          height: 18px;
          position: relative;
          z-index: 2;
        }

        .button-glow {
          position: absolute;
          inset: -2px;
          background: linear-gradient(45deg, #06b6d4, #0891b2, #06b6d4);
          border-radius: 12px;
          opacity: 0.5;
          filter: blur(10px);
          animation: buttonPulse 2s ease-in-out infinite;
        }

        @keyframes buttonPulse {
          0%, 100% { opacity: 0.5; }
          50% { opacity: 0.8; }
        }

        .button-particles {
          position: absolute;
          inset: 0;
        }

        .button-particle {
          position: absolute;
          width: 4px;
          height: 4px;
          background: #06b6d4;
          border-radius: 50%;
          animation: particleBurst 2s ease-out infinite;
        }

        .button-particle:nth-child(1) { top: 50%; left: 0; animation-delay: 0s; }
        .button-particle:nth-child(2) { top: 20%; left: 50%; animation-delay: 0.3s; }
        .button-particle:nth-child(3) { top: 50%; right: 0; animation-delay: 0.6s; }
        .button-particle:nth-child(4) { bottom: 20%; left: 50%; animation-delay: 0.9s; }
        .button-particle:nth-child(5) { top: 30%; left: 20%; animation-delay: 1.2s; }
        .button-particle:nth-child(6) { bottom: 30%; right: 20%; animation-delay: 1.5s; }

        @keyframes particleBurst {
          0% {
            transform: scale(0);
            opacity: 1;
          }
          100% {
            transform: scale(3);
            opacity: 0;
          }
        }

        .calculate-button.disabled {
          opacity: 0.5;
          cursor: not-allowed;
          border-color: rgba(6, 182, 212, 0.3);
        }

        /* Calculation Card */
        .calculation-card {
          background: linear-gradient(135deg, rgba(26, 26, 26, 0.8) 0%, rgba(10, 10, 10, 0.8) 100%);
          border: 2px solid rgba(6, 182, 212, 0.4);
          border-radius: 16px;
          padding: 28px;
          margin-bottom: 24px;
          position: relative;
          overflow: hidden;
          box-shadow: 0 0 40px rgba(6, 182, 212, 0.2);
        }

        .calc-overlay {
          position: absolute;
          inset: 0;
          background: radial-gradient(circle at top right, rgba(6, 182, 212, 0.1) 0%, transparent 70%);
          animation: overlayPulse 4s ease-in-out infinite;
        }

        @keyframes overlayPulse {
          0%, 100% { opacity: 0.5; }
          50% { opacity: 1; }
        }

        .total-section {
          position: relative;
          z-index: 2;
          margin-bottom: 24px;
        }

        .total-label {
          font-size: 11px;
          color: #9ca3af;
          letter-spacing: 2px;
          margin-bottom: 8px;
          text-transform: uppercase;
        }

        .total-amount {
          display: flex;
          align-items: baseline;
          gap: 8px;
          position: relative;
        }

        .amount-value {
          font-size: 42px;
          font-weight: 700;
          color: #22c55e;
          text-shadow: 0 0 20px rgba(34, 197, 94, 0.5);
          animation: amountGlow 2s ease-in-out infinite;
        }

        @keyframes amountGlow {
          0%, 100% { filter: brightness(1); }
          50% { filter: brightness(1.2); }
        }

        .amount-currency {
          font-size: 20px;
          color: #9ca3af;
        }

        .amount-shimmer {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          height: 2px;
          background: linear-gradient(90deg, transparent, #22c55e, transparent);
          animation: shimmerFlow 2s linear infinite;
        }

        @keyframes shimmerFlow {
          to { transform: translateX(100%); }
        }

        .divider {
          position: relative;
          height: 1px;
          margin: 24px 0;
        }

        .divider-line {
          height: 100%;
          background: linear-gradient(90deg, transparent, #06b6d4, transparent);
          animation: dividerPulse 3s ease-in-out infinite;
        }

        @keyframes dividerPulse {
          0%, 100% { opacity: 0.3; }
          50% { opacity: 1; }
        }

        .fee-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 0;
          position: relative;
          z-index: 2;
        }

        .fee-label {
          font-size: 12px;
          color: #9ca3af;
          letter-spacing: 1px;
        }

        .fee-amount {
          font-size: 15px;
          font-weight: 600;
          color: #f97316;
        }

        .net-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding-top: 16px;
          border-top: 1px solid rgba(6, 182, 212, 0.2);
          position: relative;
          z-index: 2;
        }

        .net-label {
          font-size: 14px;
          font-weight: 700;
          color: #e5e7eb;
          letter-spacing: 1px;
        }

        .net-amount {
          font-size: 24px;
          font-weight: 700;
          color: #22c55e;
          text-shadow: 0 0 15px rgba(34, 197, 94, 0.5);
        }

        /* Shares Container */
        .shares-container {
          background: rgba(26, 26, 26, 0.6);
          border: 1px solid rgba(34, 197, 94, 0.3);
          border-radius: 16px;
          padding: 24px;
          position: relative;
          overflow: hidden;
        }

        .shares-container::before {
          content: '';
          position: absolute;
          top: -50%;
          left: -50%;
          width: 200%;
          height: 200%;
          background: radial-gradient(circle, rgba(34, 197, 94, 0.05) 0%, transparent 70%);
          animation: rotate 8s linear infinite;
        }

        .shares-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
          position: relative;
          z-index: 2;
        }

        .shares-header span {
          font-size: 13px;
          font-weight: 700;
          color: #e5e7eb;
          letter-spacing: 2px;
          text-transform: uppercase;
        }

        .shares-count {
          width: 28px;
          height: 28px;
          background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 12px;
          font-weight: 700;
          color: white;
          box-shadow: 0 0 15px rgba(34, 197, 94, 0.5);
        }

        /* Member Cards */
        .member-card {
          position: relative;
          background: linear-gradient(135deg, rgba(34, 197, 94, 0.08) 0%, transparent 100%);
          border: 1px solid rgba(34, 197, 94, 0.3);
          border-radius: 12px;
          padding: 18px;
          margin-bottom: 12px;
          overflow: hidden;
          animation: slideIn 0.5s ease-out both;
        }

        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateX(-20px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }

        .member-glow {
          position: absolute;
          inset: 0;
          background: radial-gradient(circle at center, rgba(34, 197, 94, 0.1) 0%, transparent 70%);
          opacity: 0;
          transition: opacity 0.3s;
        }

        .member-card:hover .member-glow {
          opacity: 1;
        }

        .member-info {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 14px;
          position: relative;
          z-index: 2;
        }

        .member-details {
          flex: 1;
        }

        .member-name {
          font-size: 17px;
          font-weight: 700;
          color: #22c55e;
          margin-bottom: 4px;
          text-shadow: 0 0 10px rgba(34, 197, 94, 0.3);
        }

        .member-handle {
          font-size: 11px;
          color: #9ca3af;
          letter-spacing: 0.5px;
        }

        .member-amount {
          text-align: right;
        }

        .share-value {
          font-size: 20px;
          font-weight: 700;
          color: #e5e7eb;
          display: block;
        }

        .share-currency {
          font-size: 11px;
          color: #9ca3af;
        }

        /* Send Button */
        .send-button {
          width: 100%;
          padding: 14px;
          background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
          border: none;
          border-radius: 8px;
          color: white;
          font-size: 12px;
          font-weight: 700;
          letter-spacing: 1.5px;
          text-transform: uppercase;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          position: relative;
          overflow: hidden;
          transition: all 0.3s;
          z-index: 2;
        }

        .send-button:not(.sent):hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 25px rgba(34, 197, 94, 0.4);
        }

        .send-glow {
          position: absolute;
          inset: -2px;
          background: linear-gradient(45deg, #22c55e, #16a34a, #22c55e);
          border-radius: 8px;
          opacity: 0.6;
          filter: blur(8px);
          animation: buttonPulse 2s ease-in-out infinite;
        }

        .send-button.sent {
          background: rgba(42, 42, 42, 0.6);
          color: #9ca3af;
          cursor: not-allowed;
        }

        /* Empty State */
        .empty-state {
          padding: 80px 40px;
          text-align: center;
          color: #9ca3af;
          position: relative;
        }

        .empty-icon-container {
          width: 80px;
          height: 80px;
          margin: 0 auto 24px;
          position: relative;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .empty-icon {
          width: 48px;
          height: 48px;
          opacity: 0.4;
          position: relative;
          z-index: 2;
        }

        .pulse-ring {
          position: absolute;
          inset: 0;
          border: 2px solid #06b6d4;
          border-radius: 50%;
          animation: pulsate 2s ease-out infinite;
        }

        @keyframes pulsate {
          0% {
            transform: scale(0.8);
            opacity: 1;
          }
          100% {
            transform: scale(1.5);
            opacity: 0;
          }
        }

        .empty-text {
          font-size: 15px;
          margin-bottom: 8px;
          font-weight: 500;
        }

        .empty-subtext {
          font-size: 13px;
          opacity: 0.7;
        }

        /* Loading State */
        .loading-container {
          min-height: 100vh;
          background: #0a0a0a;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          color: #e5e7eb;
        }

        .hologram-loader {
          width: 120px;
          height: 120px;
          position: relative;
          margin-bottom: 32px;
        }

        .loader-ring {
          position: absolute;
          inset: 0;
          border: 3px solid transparent;
          border-top-color: #06b6d4;
          border-radius: 50%;
          animation: spin 1.5s linear infinite;
        }

        .loader-ring:nth-child(2) {
          border-top-color: #22c55e;
          animation-duration: 2s;
          animation-direction: reverse;
        }

        .loader-ring:nth-child(3) {
          border-top-color: #f97316;
          animation-duration: 2.5s;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .loader-icon {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          width: 40px;
          height: 40px;
          color: #06b6d4;
          animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
          0%, 100% {
            opacity: 1;
            transform: translate(-50%, -50%) scale(1);
          }
          50% {
            opacity: 0.7;
            transform: translate(-50%, -50%) scale(1.1);
          }
        }

        .loading-text {
          font-size: 16px;
          font-weight: 700;
          letter-spacing: 4px;
          margin-bottom: 12px;
          animation: textPulse 1.5s ease-in-out infinite;
        }

        @keyframes textPulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }

        .loading-subtext {
          font-size: 12px;
          color: #9ca3af;
          letter-spacing: 2px;
        }

        /* Responsive */
        @media (max-width: 1200px) {
          .grid-container {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
}