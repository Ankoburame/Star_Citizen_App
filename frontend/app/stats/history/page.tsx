"use client";

import { useState, useEffect } from "react";
import { Clock, Plus, Search, Tag, Users, MapPin, DollarSign, Edit2, Trash2, Zap, X } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

interface CrewMember {
  id: number;
  username: string;
}

interface HistoryEvent {
  id: number;
  user_id: number;
  title: string;
  description: string | null;
  event_type: string | null;
  tags: string[];
  crew_members_ids: number[];
  crew_members_details: CrewMember[];
  amount: number | null;
  location: string | null;
  event_date: string;
  created_at: string;
}

const DEFAULT_TAGS = [
  { id: "mining", label: "Mining", icon: "⛏️", color: "#06b6d4" },
  { id: "refining", label: "Refining", icon: "⚙️", color: "#8b5cf6" },
  { id: "trading", label: "Trading", icon: "📦", color: "#10b981" },
  { id: "salvage", label: "Salvage", icon: "🔧", color: "#f59e0b" },
  { id: "combat", label: "Combat", icon: "⚔️", color: "#ef4444" },
  { id: "profit", label: "Profit", icon: "💰", color: "#22c55e" },
  { id: "loss", label: "Loss", icon: "🚨", color: "#dc2626" },
  { id: "crew", label: "Crew", icon: "👥", color: "#3b82f6" },
];

export default function HistoryPage() {
  const [events, setEvents] = useState<HistoryEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [availableUsers, setAvailableUsers] = useState<CrewMember[]>([]);

  useEffect(() => {
    loadEvents();
    loadUsers();
  }, []);

  const loadEvents = async () => {
    try {
      const params = new URLSearchParams();
      if (searchTerm) params.append("search", searchTerm);
      if (selectedTags.length > 0) params.append("tag", selectedTags[0]);

      const res = await fetch(`${API_URL}/stats/history?${params}`);
      const data = await res.json();
      setEvents(Array.isArray(data) ? data : []);
    } catch (e) {
      console.error("Error loading events:", e);
    } finally {
      setLoading(false);
    }
  };

  const loadUsers = async () => {
    try {
      const res = await fetch(`${API_URL}/stats/history/users/available`);
      const data = await res.json();
      setAvailableUsers(Array.isArray(data) ? data : []);
    } catch (e) {
      console.error("Error loading users:", e);
    }
  };

  const toggleTag = (tagId: string) => {
    setSelectedTags(prev =>
      prev.includes(tagId) ? prev.filter(t => t !== tagId) : [...prev, tagId]
    );
  };

  const deleteEvent = async (id: number) => {
    if (!confirm("Delete this event?")) return;
    try {
      await fetch(`${API_URL}/stats/history/${id}`, { method: "DELETE" });
      loadEvents();
    } catch (e) {
      console.error("Error deleting event:", e);
    }
  };

  useEffect(() => {
    loadEvents();
  }, [searchTerm, selectedTags]);

  return (
    <div style={{ padding: "32px", maxWidth: "1400px", margin: "0 auto" }}>
      {/* SCAN LINES BACKGROUND */}
      <div style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        pointerEvents: "none",
        backgroundImage: "repeating-linear-gradient(0deg, rgba(6, 182, 212, 0.03) 0px, transparent 1px, transparent 2px, rgba(6, 182, 212, 0.03) 3px)",
        zIndex: 0,
      }} />

      {/* HEADER */}
      <div style={{ position: "relative", zIndex: 1, marginBottom: "40px" }}>
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "16px",
          marginBottom: "12px",
        }}>
          <Clock style={{ width: "36px", height: "36px", color: "#06b6d4" }} />
          <h1 style={{
            fontSize: "48px",
            fontWeight: 700,
            color: "white",
            letterSpacing: "6px",
            textTransform: "uppercase",
            margin: 0,
            background: "linear-gradient(90deg, #22d3ee 0%, #06b6d4 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}>
            MISSION LOG
          </h1>
        </div>
        <div style={{
          color: "#71717a",
          fontSize: "14px",
          letterSpacing: "2px",
          textTransform: "uppercase",
          paddingLeft: "52px",
        }}>
          // OPERATIONS HISTORY
        </div>
      </div>

      {/* FILTERS BAR */}
      <div style={{
        background: "linear-gradient(135deg, rgba(6, 182, 212, 0.05) 0%, rgba(0, 0, 0, 0.3) 100%)",
        border: "1px solid rgba(6, 182, 212, 0.2)",
        borderRadius: "12px",
        padding: "24px",
        marginBottom: "32px",
        position: "relative",
        zIndex: 1,
      }}>
        {/* Search */}
        <div style={{ marginBottom: "20px", position: "relative" }}>
          <Search style={{
            position: "absolute",
            left: "16px",
            top: "50%",
            transform: "translateY(-50%)",
            width: "20px",
            height: "20px",
            color: "#52525b",
          }} />
          <input
            type="text"
            placeholder="Search missions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              width: "100%",
              padding: "16px 16px 16px 48px",
              background: "rgba(0, 0, 0, 0.4)",
              border: "1px solid rgba(6, 182, 212, 0.3)",
              borderRadius: "8px",
              color: "white",
              fontSize: "14px",
              outline: "none",
            }}
          />
        </div>

        {/* Tags */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
          {DEFAULT_TAGS.map((tag) => {
            const isSelected = selectedTags.includes(tag.id);
            return (
              <button
                key={tag.id}
                onClick={() => toggleTag(tag.id)}
                style={{
                  padding: "10px 16px",
                  background: isSelected 
                    ? `linear-gradient(135deg, ${tag.color}40 0%, ${tag.color}20 100%)`
                    : "rgba(0, 0, 0, 0.3)",
                  border: `1px solid ${isSelected ? tag.color : "rgba(6, 182, 212, 0.2)"}`,
                  borderRadius: "6px",
                  color: isSelected ? tag.color : "#71717a",
                  fontSize: "13px",
                  fontWeight: isSelected ? 600 : 500,
                  cursor: "pointer",
                  transition: "all 0.2s ease",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = tag.color;
                  e.currentTarget.style.transform = "translateY(-2px)";
                }}
                onMouseLeave={(e) => {
                  if (!isSelected) e.currentTarget.style.borderColor = "rgba(6, 182, 212, 0.2)";
                  e.currentTarget.style.transform = "translateY(0)";
                }}
              >
                <span>{tag.icon}</span>
                <span>{tag.label}</span>
              </button>
            );
          })}
        </div>

        {/* Add Event Button */}
        <button
          onClick={() => setShowAddModal(true)}
          style={{
            marginTop: "20px",
            padding: "14px 24px",
            background: "linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)",
            border: "1px solid #06b6d4",
            borderRadius: "8px",
            color: "white",
            fontSize: "14px",
            fontWeight: 600,
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: "8px",
            boxShadow: "0 4px 12px rgba(6, 182, 212, 0.3)",
            transition: "all 0.2s ease",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = "translateY(-2px)";
            e.currentTarget.style.boxShadow = "0 6px 16px rgba(6, 182, 212, 0.5)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = "translateY(0)";
            e.currentTarget.style.boxShadow = "0 4px 12px rgba(6, 182, 212, 0.3)";
          }}
        >
          <Plus style={{ width: "18px", height: "18px" }} />
          ADD MISSION LOG
        </button>
      </div>

      {/* TIMELINE */}
      {loading ? (
        <div style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: "20px",
          padding: "60px 0",
        }}>
          <div style={{
            width: "50px",
            height: "50px",
            border: "3px solid transparent",
            borderTopColor: "#06b6d4",
            borderRightColor: "#06b6d4",
            borderRadius: "50%",
            animation: "spin 1s linear infinite",
          }} />
          <div style={{ color: "#52525b", fontSize: "14px", letterSpacing: "2px" }}>
            LOADING LOGS...
          </div>
        </div>
      ) : events.length === 0 ? (
        <div style={{
          textAlign: "center",
          padding: "60px 20px",
          color: "#52525b",
          fontSize: "16px",
        }}>
          No mission logs found. Start logging your operations!
        </div>
      ) : (
        <div style={{ position: "relative", paddingLeft: "40px" }}>
          {/* Timeline Line */}
          <div style={{
            position: "absolute",
            left: "20px",
            top: 0,
            bottom: 0,
            width: "2px",
            background: "linear-gradient(180deg, #06b6d4 0%, transparent 100%)",
            opacity: 0.3,
          }} />

          {events.map((event, index) => (
            <EventCard
              key={event.id}
              event={event}
              index={index}
              onDelete={() => deleteEvent(event.id)}
            />
          ))}
        </div>
      )}

      {/* Add Event Modal */}
      {showAddModal && (
        <AddEventModal
          onClose={() => setShowAddModal(false)}
          onSave={() => {
            setShowAddModal(false);
            loadEvents();
          }}
          availableUsers={availableUsers}
        />
      )}

      <style jsx>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

// Event Card Component
function EventCard({ event, index, onDelete }: { event: HistoryEvent; index: number; onDelete: () => void }) {
  const [expanded, setExpanded] = useState(false);

  const tagColors: Record<string, string> = {
    mining: "#06b6d4",
    refining: "#8b5cf6",
    trading: "#10b981",
    salvage: "#f59e0b",
    combat: "#ef4444",
    profit: "#22c55e",
    loss: "#dc2626",
    crew: "#3b82f6",
  };

  return (
    <div
      style={{
        marginBottom: "24px",
        animation: `fadeInUp 0.4s ease ${index * 0.1}s both`,
        position: "relative",
      }}
    >
      {/* Timeline Dot */}
      <div style={{
        position: "absolute",
        left: "-29px",
        top: "24px",
        width: "10px",
        height: "10px",
        background: "#06b6d4",
        borderRadius: "50%",
        boxShadow: "0 0 12px #06b6d4",
        border: "2px solid #0a0e1a",
      }} />

      <div
        onClick={() => setExpanded(!expanded)}
        style={{
          background: "linear-gradient(135deg, rgba(6, 182, 212, 0.08) 0%, rgba(0, 0, 0, 0.4) 100%)",
          border: "1px solid rgba(6, 182, 212, 0.2)",
          borderRadius: "12px",
          padding: "24px",
          cursor: "pointer",
          transition: "all 0.3s ease",
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.borderColor = "rgba(6, 182, 212, 0.5)";
          e.currentTarget.style.transform = "translateX(4px)";
          e.currentTarget.style.boxShadow = "0 8px 24px rgba(6, 182, 212, 0.15)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.borderColor = "rgba(6, 182, 212, 0.2)";
          e.currentTarget.style.transform = "translateX(0)";
          e.currentTarget.style.boxShadow = "none";
        }}
      >
        {/* Header */}
        <div style={{ display: "flex", alignItems: "flex-start", gap: "16px", marginBottom: "12px" }}>
          <div style={{ flex: 1 }}>
            <h3 style={{
              fontSize: "20px",
              fontWeight: 700,
              color: "white",
              margin: "0 0 8px 0",
              letterSpacing: "1px",
            }}>
              {event.title}
            </h3>
            
            <div style={{
              display: "flex",
              flexWrap: "wrap",
              gap: "12px",
              fontSize: "13px",
              color: "#71717a",
            }}>
              <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <Clock style={{ width: "14px", height: "14px" }} />
                {new Date(event.event_date).toLocaleString()}
              </span>
              {event.location && (
                <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                  <MapPin style={{ width: "14px", height: "14px" }} />
                  {event.location}
                </span>
              )}
              {event.amount !== null && (
                <span style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                  color: event.amount >= 0 ? "#22c55e" : "#ef4444",
                  fontWeight: 600,
                }}>
                  <DollarSign style={{ width: "14px", height: "14px" }} />
                  {event.amount.toLocaleString()} UEC
                </span>
              )}
            </div>
          </div>

          {/* Actions */}
          <div style={{ display: "flex", gap: "8px" }}>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete();
              }}
              style={{
                padding: "8px",
                background: "rgba(239, 68, 68, 0.1)",
                border: "1px solid rgba(239, 68, 68, 0.3)",
                borderRadius: "6px",
                color: "#ef4444",
                cursor: "pointer",
                transition: "all 0.2s ease",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = "rgba(239, 68, 68, 0.2)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "rgba(239, 68, 68, 0.1)";
              }}
            >
              <Trash2 style={{ width: "16px", height: "16px" }} />
            </button>
          </div>
        </div>

        {/* Tags */}
        {event.tags && event.tags.length > 0 && (
          <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginBottom: "12px" }}>
            {event.tags.map((tag) => {
              const tagInfo = DEFAULT_TAGS.find(t => t.id === tag);
              const color = tagColors[tag] || "#06b6d4";
              return (
                <span
                  key={tag}
                  style={{
                    padding: "4px 10px",
                    background: `${color}20`,
                    border: `1px solid ${color}40`,
                    borderRadius: "4px",
                    color: color,
                    fontSize: "11px",
                    fontWeight: 600,
                    textTransform: "uppercase",
                    letterSpacing: "0.5px",
                    display: "flex",
                    alignItems: "center",
                    gap: "4px",
                  }}
                >
                  {tagInfo?.icon} {tag}
                </span>
              );
            })}
          </div>
        )}

        {/* Crew Members */}
        {event.crew_members_details && event.crew_members_details.length > 0 && (
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            padding: "10px 12px",
            background: "rgba(6, 182, 212, 0.05)",
            borderRadius: "6px",
            marginBottom: "12px",
          }}>
            <Users style={{ width: "16px", height: "16px", color: "#06b6d4" }} />
            <span style={{ color: "#71717a", fontSize: "13px" }}>Crew:</span>
            {event.crew_members_details.map((member, idx) => (
              <span
                key={member.id}
                style={{
                  color: "#06b6d4",
                  fontSize: "13px",
                  fontWeight: 600,
                }}
              >
                @{member.username}{idx < event.crew_members_details.length - 1 ? "," : ""}
              </span>
            ))}
          </div>
        )}

        {/* Description (expanded) */}
        {expanded && event.description && (
          <div style={{
            marginTop: "16px",
            padding: "16px",
            background: "rgba(0, 0, 0, 0.3)",
            borderRadius: "6px",
            borderLeft: "3px solid #06b6d4",
            color: "#a1a1aa",
            fontSize: "14px",
            lineHeight: 1.6,
          }}>
            {event.description}
          </div>
        )}
      </div>

      <style jsx>{`
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

// Add Event Modal (continued in next file due to length)
function AddEventModal({ onClose, onSave, availableUsers }: any) {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    amount: "",
    location: "",
    tags: [] as string[],
    crew_members: [] as number[],
    event_date: new Date().toISOString().slice(0, 16),
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await fetch(`${API_URL}/stats/history`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...formData,
          amount: formData.amount ? parseFloat(formData.amount) : null,
          event_date: new Date(formData.event_date).toISOString(),
        }),
      });
      onSave();
    } catch (e) {
      console.error("Error creating event:", e);
    }
  };

  const toggleTag = (tagId: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.includes(tagId)
        ? prev.tags.filter(t => t !== tagId)
        : [...prev.tags, tagId],
    }));
  };

  const toggleCrewMember = (userId: number) => {
    setFormData(prev => ({
      ...prev,
      crew_members: prev.crew_members.includes(userId)
        ? prev.crew_members.filter(id => id !== userId)
        : [...prev.crew_members, userId],
    }));
  };

  return (
    <div style={{
      position: "fixed",
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: "rgba(0, 0, 0, 0.8)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      zIndex: 1000,
      padding: "20px",
    }}>
      <div style={{
        background: "linear-gradient(135deg, #0a0e1a 0%, #050810 100%)",
        border: "1px solid rgba(6, 182, 212, 0.3)",
        borderRadius: "16px",
        padding: "32px",
        maxWidth: "600px",
        width: "100%",
        maxHeight: "90vh",
        overflowY: "auto",
        boxShadow: "0 20px 60px rgba(0, 0, 0, 0.5)",
      }}>
        <div style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "24px",
        }}>
          <h2 style={{
            fontSize: "24px",
            fontWeight: 700,
            color: "#06b6d4",
            margin: 0,
            letterSpacing: "2px",
          }}>
            ADD MISSION LOG
          </h2>
          <button
            onClick={onClose}
            style={{
              padding: "8px",
              background: "transparent",
              border: "1px solid rgba(6, 182, 212, 0.3)",
              borderRadius: "6px",
              color: "#71717a",
              cursor: "pointer",
            }}
          >
            <X style={{ width: "20px", height: "20px" }} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: "20px" }}>
            <label style={{
              display: "block",
              color: "#71717a",
              fontSize: "13px",
              fontWeight: 600,
              marginBottom: "8px",
              textTransform: "uppercase",
              letterSpacing: "1px",
            }}>
              Title *
            </label>
            <input
              type="text"
              required
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              style={{
                width: "100%",
                padding: "12px",
                background: "rgba(0, 0, 0, 0.4)",
                border: "1px solid rgba(6, 182, 212, 0.3)",
                borderRadius: "6px",
                color: "white",
                fontSize: "14px",
                outline: "none",
              }}
            />
          </div>

          <div style={{ marginBottom: "20px" }}>
            <label style={{
              display: "block",
              color: "#71717a",
              fontSize: "13px",
              fontWeight: 600,
              marginBottom: "8px",
              textTransform: "uppercase",
              letterSpacing: "1px",
            }}>
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={3}
              style={{
                width: "100%",
                padding: "12px",
                background: "rgba(0, 0, 0, 0.4)",
                border: "1px solid rgba(6, 182, 212, 0.3)",
                borderRadius: "6px",
                color: "white",
                fontSize: "14px",
                outline: "none",
                resize: "vertical",
              }}
            />
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "20px" }}>
            <div>
              <label style={{
                display: "block",
                color: "#71717a",
                fontSize: "13px",
                fontWeight: 600,
                marginBottom: "8px",
                textTransform: "uppercase",
                letterSpacing: "1px",
              }}>
                Amount (UEC)
              </label>
              <input
                type="number"
                value={formData.amount}
                onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                style={{
                  width: "100%",
                  padding: "12px",
                  background: "rgba(0, 0, 0, 0.4)",
                  border: "1px solid rgba(6, 182, 212, 0.3)",
                  borderRadius: "6px",
                  color: "white",
                  fontSize: "14px",
                  outline: "none",
                }}
              />
            </div>

            <div>
              <label style={{
                display: "block",
                color: "#71717a",
                fontSize: "13px",
                fontWeight: 600,
                marginBottom: "8px",
                textTransform: "uppercase",
                letterSpacing: "1px",
              }}>
                Location
              </label>
              <input
                type="text"
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                style={{
                  width: "100%",
                  padding: "12px",
                  background: "rgba(0, 0, 0, 0.4)",
                  border: "1px solid rgba(6, 182, 212, 0.3)",
                  borderRadius: "6px",
                  color: "white",
                  fontSize: "14px",
                  outline: "none",
                }}
              />
            </div>
          </div>

          <div style={{ marginBottom: "20px" }}>
            <label style={{
              display: "block",
              color: "#71717a",
              fontSize: "13px",
              fontWeight: 600,
              marginBottom: "8px",
              textTransform: "uppercase",
              letterSpacing: "1px",
            }}>
              Date & Time *
            </label>
            <input
              type="datetime-local"
              required
              value={formData.event_date}
              onChange={(e) => setFormData({ ...formData, event_date: e.target.value })}
              style={{
                width: "100%",
                padding: "12px",
                background: "rgba(0, 0, 0, 0.4)",
                border: "1px solid rgba(6, 182, 212, 0.3)",
                borderRadius: "6px",
                color: "white",
                fontSize: "14px",
                outline: "none",
              }}
            />
          </div>

          <div style={{ marginBottom: "20px" }}>
            <label style={{
              display: "block",
              color: "#71717a",
              fontSize: "13px",
              fontWeight: 600,
              marginBottom: "12px",
              textTransform: "uppercase",
              letterSpacing: "1px",
            }}>
              Tags
            </label>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
              {DEFAULT_TAGS.map((tag) => {
                const isSelected = formData.tags.includes(tag.id);
                return (
                  <button
                    key={tag.id}
                    type="button"
                    onClick={() => toggleTag(tag.id)}
                    style={{
                      padding: "8px 12px",
                      background: isSelected ? `${tag.color}30` : "rgba(0, 0, 0, 0.3)",
                      border: `1px solid ${isSelected ? tag.color : "rgba(6, 182, 212, 0.2)"}`,
                      borderRadius: "6px",
                      color: isSelected ? tag.color : "#71717a",
                      fontSize: "12px",
                      cursor: "pointer",
                      transition: "all 0.2s ease",
                    }}
                  >
                    {tag.icon} {tag.label}
                  </button>
                );
              })}
            </div>
          </div>

          <div style={{ marginBottom: "24px" }}>
            <label style={{
              display: "block",
              color: "#71717a",
              fontSize: "13px",
              fontWeight: 600,
              marginBottom: "12px",
              textTransform: "uppercase",
              letterSpacing: "1px",
            }}>
              Crew Members
            </label>
            <div style={{
              maxHeight: "150px",
              overflowY: "auto",
              background: "rgba(0, 0, 0, 0.3)",
              border: "1px solid rgba(6, 182, 212, 0.2)",
              borderRadius: "6px",
              padding: "12px",
            }}>
              {availableUsers.map((user: CrewMember) => {
                const isSelected = formData.crew_members.includes(user.id);
                return (
                  <label
                    key={user.id}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "12px",
                      padding: "8px",
                      cursor: "pointer",
                      borderRadius: "4px",
                      transition: "all 0.2s ease",
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = "rgba(6, 182, 212, 0.1)";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = "transparent";
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => toggleCrewMember(user.id)}
                      style={{ cursor: "pointer" }}
                    />
                    <span style={{
                      color: isSelected ? "#06b6d4" : "#71717a",
                      fontSize: "14px",
                      fontWeight: isSelected ? 600 : 400,
                    }}>
                      @{user.username}
                    </span>
                  </label>
                );
              })}
            </div>
          </div>

          <div style={{ display: "flex", gap: "12px", justifyContent: "flex-end" }}>
            <button
              type="button"
              onClick={onClose}
              style={{
                padding: "12px 24px",
                background: "rgba(0, 0, 0, 0.4)",
                border: "1px solid rgba(6, 182, 212, 0.3)",
                borderRadius: "6px",
                color: "#71717a",
                fontSize: "14px",
                fontWeight: 600,
                cursor: "pointer",
                transition: "all 0.2s ease",
              }}
            >
              CANCEL
            </button>
            <button
              type="submit"
              style={{
                padding: "12px 24px",
                background: "linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)",
                border: "1px solid #06b6d4",
                borderRadius: "6px",
                color: "white",
                fontSize: "14px",
                fontWeight: 600,
                cursor: "pointer",
                boxShadow: "0 4px 12px rgba(6, 182, 212, 0.3)",
                transition: "all 0.2s ease",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = "translateY(-2px)";
                e.currentTarget.style.boxShadow = "0 6px 16px rgba(6, 182, 212, 0.5)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow = "0 4px 12px rgba(6, 182, 212, 0.3)";
              }}
            >
              SAVE LOG
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}