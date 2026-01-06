"use client";

import { useState, useEffect } from "react";
import { Clock, Tag, DollarSign, MapPin, Users, Edit2, Check, X } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const COLORS = {
  cyan: "#06b6d4",
  orange: "#f97316",
  red: "#ef4444",
  green: "#22c55e",
  purple: "#a855f7",
  blue: "#3b82f6",
  yellow: "#eab308",
  bgDark: "#0a0a0a",
  bgMedium: "#1a1a1a",
  textPrimary: "#e5e7eb",
  textSecondary: "#9ca3af",
};

const PREDEFINED_TAGS = [
  { name: "mining", color: COLORS.cyan, icon: "⛏️" },
  { name: "refining", color: COLORS.purple, icon: "⚙️" },
  { name: "trading", color: COLORS.green, icon: "📦" },
  { name: "salvage", color: COLORS.orange, icon: "🔧" },
  { name: "combat", color: COLORS.red, icon: "⚔️" },
  { name: "profit", color: COLORS.green, icon: "💰" },
  { name: "loss", color: COLORS.red, icon: "💸" },
  { name: "cost", color: COLORS.orange, icon: "💵" },
  { name: "crew", color: COLORS.blue, icon: "👥" },
];

interface HistoryEvent {
  id: number;
  title: string;
  description: string;
  event_type: string;
  tags: string[];
  amount: number;
  location: string;
  event_date: string;
  crew_members_details: Array<{ id: number; username: string }>;
}

export default function HistoryPage() {
  const [events, setEvents] = useState<HistoryEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterTag, setFilterTag] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editTags, setEditTags] = useState<string[]>([]);

  useEffect(() => {
    loadEvents();
  }, [filterTag]);

  const loadEvents = async () => {
    try {
      const token = localStorage.getItem("token");
      let url = `${API_URL}/stats/history`;
      if (filterTag) url += `?tag=${filterTag}`;

      const response = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setEvents(data);
      }
    } catch (err) {
      console.error("Failed to load events:", err);
    } finally {
      setLoading(false);
    }
  };

  const startEditTags = (event: HistoryEvent) => {
    setEditingId(event.id);
    setEditTags([...event.tags]);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditTags([]);
  };

  const saveTags = async (eventId: number) => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${API_URL}/stats/history/${eventId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ tags: editTags }),
      });

      if (response.ok) {
        loadEvents();
        setEditingId(null);
        setEditTags([]);
      }
    } catch (err) {
      console.error("Failed to update tags:", err);
    }
  };

  const toggleTag = (tagName: string) => {
    if (editTags.includes(tagName)) {
      setEditTags(editTags.filter((t) => t !== tagName));
    } else {
      setEditTags([...editTags, tagName]);
    }
  };

  const getTagColor = (tag: string) => {
    const predefined = PREDEFINED_TAGS.find((t) => t.name === tag);
    return predefined?.color || COLORS.textSecondary;
  };

  const getTagIcon = (tag: string) => {
    const predefined = PREDEFINED_TAGS.find((t) => t.name === tag);
    return predefined?.icon || "🏷️";
  };

  const filteredEvents = events.filter(
    (e) =>
      e.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      e.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
            LOADING HISTORY...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: "32px", maxWidth: "1400px", margin: "0 auto", minHeight: "100vh" }}>
      {/* HEADER */}
      <div style={{ marginBottom: "48px" }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "16px",
            marginBottom: "12px",
          }}
        >
          <Clock style={{ width: "32px", height: "32px", color: COLORS.cyan }} />
          <h1
            style={{
              fontSize: "48px",
              fontWeight: 700,
              color: "white",
              letterSpacing: "6px",
              textTransform: "uppercase",
              margin: 0,
              background: `linear-gradient(90deg, ${COLORS.cyan} 0%, #0891b2 100%)`,
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            HISTORY
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
          // AUTO-GENERATED ACTIVITY LOG - TAG EDITING ONLY
        </div>
      </div>

      {/* FILTERS */}
      <div style={{ marginBottom: "32px" }}>
        {/* Search */}
        <input
          type="text"
          placeholder="Search events..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            width: "100%",
            padding: "12px 16px",
            background: COLORS.bgMedium,
            border: `1px solid ${COLORS.cyan}40`,
            borderRadius: "4px",
            color: COLORS.textPrimary,
            fontSize: "14px",
            marginBottom: "16px",
            outline: "none",
          }}
        />

        {/* Tag Filters */}
        <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
          <button
            onClick={() => setFilterTag(null)}
            style={{
              padding: "8px 16px",
              background: !filterTag ? COLORS.cyan : "transparent",
              border: `1px solid ${COLORS.cyan}`,
              borderRadius: "4px",
              color: !filterTag ? COLORS.bgDark : COLORS.cyan,
              fontSize: "12px",
              fontWeight: 600,
              cursor: "pointer",
              textTransform: "uppercase",
              letterSpacing: "1px",
            }}
          >
            ALL
          </button>
          {PREDEFINED_TAGS.map((tag) => (
            <button
              key={tag.name}
              onClick={() => setFilterTag(tag.name)}
              style={{
                padding: "8px 16px",
                background: filterTag === tag.name ? tag.color : "transparent",
                border: `1px solid ${tag.color}`,
                borderRadius: "4px",
                color: filterTag === tag.name ? COLORS.bgDark : tag.color,
                fontSize: "12px",
                fontWeight: 600,
                cursor: "pointer",
                textTransform: "uppercase",
                letterSpacing: "1px",
                display: "flex",
                alignItems: "center",
                gap: "4px",
              }}
            >
              {tag.icon} {tag.name}
            </button>
          ))}
        </div>
      </div>

      {/* TIMELINE */}
      <div style={{ position: "relative", paddingLeft: "40px" }}>
        {/* Timeline Line */}
        <div
          style={{
            position: "absolute",
            left: "12px",
            top: 0,
            bottom: 0,
            width: "2px",
            background: `linear-gradient(180deg, ${COLORS.cyan} 0%, transparent 100%)`,
          }}
        />

        {/* Events */}
        {filteredEvents.length === 0 ? (
          <div
            style={{
              padding: "40px",
              textAlign: "center",
              color: COLORS.textSecondary,
              fontSize: "14px",
            }}
          >
            No events found
          </div>
        ) : (
          filteredEvents.map((event, index) => (
            <div
              key={event.id}
              style={{
                marginBottom: "24px",
                position: "relative",
                animation: "fadeInUp 0.4s ease-out",
                animationDelay: `${index * 0.05}s`,
                animationFillMode: "both",
              }}
            >
              {/* Timeline Dot */}
              <div
                style={{
                  position: "absolute",
                  left: "-34px",
                  top: "16px",
                  width: "12px",
                  height: "12px",
                  borderRadius: "50%",
                  background: COLORS.cyan,
                  boxShadow: `0 0 12px ${COLORS.cyan}`,
                }}
              />

              {/* Event Card */}
              <div
                style={{
                  background: `linear-gradient(135deg, ${COLORS.bgMedium} 0%, ${COLORS.bgDark} 100%)`,
                  border: `1px solid ${COLORS.cyan}40`,
                  borderRadius: "8px",
                  padding: "20px",
                  transition: "all 0.3s ease",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = COLORS.cyan;
                  e.currentTarget.style.transform = "translateY(-2px)";
                  e.currentTarget.style.boxShadow = `0 4px 20px ${COLORS.cyan}20`;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = `${COLORS.cyan}40`;
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.boxShadow = "none";
                }}
              >
                {/* Header */}
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "12px" }}>
                  <div>
                    <h3
                      style={{
                        fontSize: "18px",
                        fontWeight: 700,
                        color: COLORS.textPrimary,
                        margin: "0 0 4px 0",
                        letterSpacing: "1px",
                      }}
                    >
                      {event.title}
                    </h3>
                    <div style={{ fontSize: "12px", color: COLORS.textSecondary }}>
                      {new Date(event.event_date).toLocaleString()}
                    </div>
                  </div>

                  {/* Amount */}
                  {event.amount !== 0 && (
                    <div
                      style={{
                        fontSize: "20px",
                        fontWeight: 700,
                        color: event.amount > 0 ? COLORS.green : COLORS.red,
                        display: "flex",
                        alignItems: "center",
                        gap: "4px",
                      }}
                    >
                      <DollarSign style={{ width: "20px", height: "20px" }} />
                      {event.amount > 0 ? "+" : ""}
                      {event.amount.toLocaleString()}
                    </div>
                  )}
                </div>

                {/* Description */}
                {event.description && (
                  <p style={{ fontSize: "14px", color: COLORS.textSecondary, margin: "0 0 16px 0" }}>
                    {event.description}
                  </p>
                )}

                {/* Meta Info */}
                <div style={{ display: "flex", gap: "16px", marginBottom: "16px", flexWrap: "wrap" }}>
                  {event.location && (
                    <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "13px" }}>
                      <MapPin style={{ width: "14px", height: "14px", color: COLORS.cyan }} />
                      <span style={{ color: COLORS.textSecondary }}>{event.location}</span>
                    </div>
                  )}

                  {event.crew_members_details && event.crew_members_details.length > 0 && (
                    <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "13px" }}>
                      <Users style={{ width: "14px", height: "14px", color: COLORS.cyan }} />
                      <span style={{ color: COLORS.textSecondary }}>
                        {event.crew_members_details.map((m) => m.username).join(", ")}
                      </span>
                    </div>
                  )}
                </div>

                {/* Tags */}
                <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
                  {editingId === event.id ? (
                    <>
                      {/* Edit Mode */}
                      {PREDEFINED_TAGS.map((tag) => (
                        <button
                          key={tag.name}
                          onClick={() => toggleTag(tag.name)}
                          style={{
                            padding: "6px 12px",
                            background: editTags.includes(tag.name) ? tag.color : "transparent",
                            border: `1px solid ${tag.color}`,
                            borderRadius: "4px",
                            color: editTags.includes(tag.name) ? COLORS.bgDark : tag.color,
                            fontSize: "11px",
                            fontWeight: 600,
                            cursor: "pointer",
                            textTransform: "uppercase",
                            display: "flex",
                            alignItems: "center",
                            gap: "4px",
                          }}
                        >
                          {tag.icon} {tag.name}
                        </button>
                      ))}
                      <button
                        onClick={() => saveTags(event.id)}
                        style={{
                          padding: "6px 12px",
                          background: COLORS.green,
                          border: "none",
                          borderRadius: "4px",
                          color: "white",
                          cursor: "pointer",
                        }}
                      >
                        <Check style={{ width: "14px", height: "14px" }} />
                      </button>
                      <button
                        onClick={cancelEdit}
                        style={{
                          padding: "6px 12px",
                          background: COLORS.red,
                          border: "none",
                          borderRadius: "4px",
                          color: "white",
                          cursor: "pointer",
                        }}
                      >
                        <X style={{ width: "14px", height: "14px" }} />
                      </button>
                    </>
                  ) : (
                    <>
                      {/* View Mode */}
                      {event.tags.map((tag) => (
                        <span
                          key={tag}
                          style={{
                            padding: "6px 12px",
                            background: `${getTagColor(tag)}20`,
                            border: `1px solid ${getTagColor(tag)}`,
                            borderRadius: "4px",
                            color: getTagColor(tag),
                            fontSize: "11px",
                            fontWeight: 600,
                            textTransform: "uppercase",
                            display: "flex",
                            alignItems: "center",
                            gap: "4px",
                          }}
                        >
                          {getTagIcon(tag)} {tag}
                        </span>
                      ))}
                      <button
                        onClick={() => startEditTags(event)}
                        style={{
                          padding: "6px 12px",
                          background: "transparent",
                          border: `1px solid ${COLORS.cyan}40`,
                          borderRadius: "4px",
                          color: COLORS.cyan,
                          cursor: "pointer",
                          display: "flex",
                          alignItems: "center",
                          gap: "4px",
                        }}
                      >
                        <Edit2 style={{ width: "14px", height: "14px" }} />
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      <style jsx>{`
        @keyframes spin {
          to {
            transform: rotate(360deg);
          }
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
      `}</style>
    </div>
  );
}