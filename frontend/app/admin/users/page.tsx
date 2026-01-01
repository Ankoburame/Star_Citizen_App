"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Users, UserPlus, Trash2, Shield, Eye } from "lucide-react";

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
  cyan: "#06b6d4",
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

interface User {
  id: number;
  username: string;
  email: string | null;
  role: string;
  is_active: boolean;
  created_at: string;
}

export default function UsersManagementPage() {
  const router = useRouter();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [currentUser, setCurrentUser] = useState<any>(null);

  // Form states
  const [newUsername, setNewUsername] = useState("");
  const [newEmail, setNewEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newRole, setNewRole] = useState("member");
  const [error, setError] = useState("");
  const [creating, setCreating] = useState(false);

  // Check if user is admin
  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (!storedUser) {
      router.push("/login");
      return;
    }

    const user = JSON.parse(storedUser);
    setCurrentUser(user);

    if (user.role !== "admin") {
      router.push("/");
      return;
    }

    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${API_URL}/auth/users`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUsers(data);
      }
    } catch (err) {
      console.error("Failed to load users:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setCreating(true);

    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${API_URL}/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          username: newUsername,
          email: newEmail || null,
          password: newPassword,
          role: newRole,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to create user");
      }

      // Reset form
      setNewUsername("");
      setNewEmail("");
      setNewPassword("");
      setNewRole("member");
      setShowCreateModal(false);

      // Reload users
      loadUsers();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setCreating(false);
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case "admin":
        return <Shield style={{ width: "16px", height: "16px", color: COLORS.red }} />;
      case "member":
        return <Users style={{ width: "16px", height: "16px", color: COLORS.cyan }} />;
      case "viewer":
        return <Eye style={{ width: "16px", height: "16px", color: COLORS.textSecondary }} />;
      default:
        return null;
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case "admin":
        return COLORS.red;
      case "member":
        return COLORS.cyan;
      case "viewer":
        return COLORS.textSecondary;
      default:
        return COLORS.textSecondary;
    }
  };

  if (loading) {
    return (
      <div style={{
        minHeight: "100vh",
        background: COLORS.bgDark,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        color: COLORS.textPrimary
      }}>
        Loading...
      </div>
    );
  }

  return (
    <div style={{
      minHeight: "100vh",
      background: COLORS.bgDark,
      padding: "40px 20px"
    }}>
      <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
        {/* Header */}
        <div style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "32px"
        }}>
          <div>
            <h1 style={{
              fontSize: "28px",
              fontWeight: 700,
              color: COLORS.textPrimary,
              letterSpacing: "2px",
              textTransform: "uppercase",
              margin: 0,
              fontFamily: "monospace"
            }}>
              USER MANAGEMENT
            </h1>
            <div style={{
              fontSize: "12px",
              color: COLORS.textSecondary,
              marginTop: "8px",
              fontFamily: "monospace"
            }}>
              // ADMIN PANEL
            </div>
          </div>

          <button
            onClick={() => setShowCreateModal(true)}
            style={{
              padding: "12px 24px",
              background: `linear-gradient(135deg, ${COLORS.yellow} 0%, ${COLORS.orange} 100%)`,
              border: `1px solid ${COLORS.yellow}`,
              borderRadius: "4px",
              color: COLORS.bgDark,
              fontSize: "13px",
              fontWeight: 700,
              letterSpacing: "1px",
              textTransform: "uppercase",
              cursor: "pointer",
              fontFamily: "monospace",
              display: "flex",
              alignItems: "center",
              gap: "8px",
              boxShadow: `0 0 20px ${COLORS.yellow}40`
            }}
          >
            <UserPlus style={{ width: "16px", height: "16px" }} />
            CREATE USER
          </button>
        </div>

        {/* Users Table */}
        <div style={{
          background: `linear-gradient(135deg, ${COLORS.bgMedium} 0%, ${COLORS.bgDark} 100%)`,
          border: `1px solid ${COLORS.cyan}40`,
          borderRadius: "4px",
          overflow: "hidden"
        }}>
          {/* Table Header */}
          <div style={{
            display: "grid",
            gridTemplateColumns: "2fr 2fr 1fr 1fr 1fr",
            padding: "16px 24px",
            background: `${COLORS.cyan}10`,
            borderBottom: `1px solid ${COLORS.cyan}40`,
            fontSize: "11px",
            color: COLORS.textSecondary,
            letterSpacing: "1px",
            textTransform: "uppercase",
            fontWeight: 700,
            fontFamily: "monospace"
          }}>
            <div>USERNAME</div>
            <div>EMAIL</div>
            <div>ROLE</div>
            <div>STATUS</div>
            <div>ACTIONS</div>
          </div>

          {/* Table Rows */}
          {users.map((user) => (
            <div
              key={user.id}
              style={{
                display: "grid",
                gridTemplateColumns: "2fr 2fr 1fr 1fr 1fr",
                padding: "16px 24px",
                borderBottom: `1px solid ${COLORS.bgLight}40`,
                fontSize: "13px",
                fontFamily: "monospace",
                alignItems: "center"
              }}
            >
              <div style={{ color: COLORS.textPrimary, fontWeight: 600 }}>
                {user.username}
              </div>
              <div style={{ color: COLORS.textSecondary }}>
                {user.email || "-"}
              </div>
              <div style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                color: getRoleColor(user.role),
                textTransform: "uppercase",
                fontSize: "11px",
                fontWeight: 700
              }}>
                {getRoleIcon(user.role)}
                {user.role}
              </div>
              <div>
                <span style={{
                  padding: "4px 12px",
                  background: user.is_active ? `${COLORS.greenOlive}20` : `${COLORS.red}20`,
                  border: `1px solid ${user.is_active ? COLORS.greenOlive : COLORS.red}`,
                  borderRadius: "12px",
                  fontSize: "10px",
                  color: user.is_active ? COLORS.greenOlive : COLORS.red,
                  fontWeight: 700,
                  textTransform: "uppercase"
                }}>
                  {user.is_active ? "ACTIVE" : "INACTIVE"}
                </span>
              </div>
              <div>
                <button
                  style={{
                    padding: "6px 12px",
                    background: "transparent",
                    border: `1px solid ${COLORS.red}40`,
                    borderRadius: "4px",
                    color: COLORS.red,
                    fontSize: "11px",
                    cursor: "pointer",
                    fontFamily: "monospace"
                  }}
                  disabled={user.id === currentUser?.id}
                >
                  <Trash2 style={{ width: "14px", height: "14px" }} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Create User Modal */}
      {showCreateModal && (
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
          padding: "20px"
        }}>
          <div style={{
            width: "100%",
            maxWidth: "500px",
            background: `linear-gradient(135deg, #030712 0%, #000000 100%)`,
            border: `1px solid ${COLORS.cyan}60`,
            borderRadius: "4px",
            padding: "32px",
            boxShadow: `0 0 40px ${COLORS.cyan}30`
          }}>
            <h2 style={{
              fontSize: "20px",
              fontWeight: 700,
              color: COLORS.textPrimary,
              letterSpacing: "2px",
              textTransform: "uppercase",
              margin: "0 0 24px 0",
              fontFamily: "monospace"
            }}>
              CREATE NEW USER
            </h2>

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

            <form onSubmit={handleCreateUser}>
              <div style={{ marginBottom: "20px" }}>
                <label style={{
                  display: "block",
                  fontSize: "10px",
                  color: COLORS.textSecondary,
                  letterSpacing: "1px",
                  textTransform: "uppercase",
                  marginBottom: "8px",
                  fontFamily: "monospace"
                }}>
                  USERNAME *
                </label>
                <input
                  type="text"
                  value={newUsername}
                  onChange={(e) => setNewUsername(e.target.value)}
                  required
                  style={{
                    width: "100%",
                    padding: "12px",
                    background: COLORS.bgDark,
                    border: `1px solid ${COLORS.bgLight}`,
                    borderRadius: "2px",
                    color: COLORS.textPrimary,
                    fontSize: "14px",
                    fontFamily: "monospace",
                    outline: "none",
                    boxSizing: "border-box"
                  }}
                />
              </div>

              <div style={{ marginBottom: "20px" }}>
                <label style={{
                  display: "block",
                  fontSize: "10px",
                  color: COLORS.textSecondary,
                  letterSpacing: "1px",
                  textTransform: "uppercase",
                  marginBottom: "8px",
                  fontFamily: "monospace"
                }}>
                  EMAIL
                </label>
                <input
                  type="email"
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "12px",
                    background: COLORS.bgDark,
                    border: `1px solid ${COLORS.bgLight}`,
                    borderRadius: "2px",
                    color: COLORS.textPrimary,
                    fontSize: "14px",
                    fontFamily: "monospace",
                    outline: "none",
                    boxSizing: "border-box"
                  }}
                />
              </div>

              <div style={{ marginBottom: "20px" }}>
                <label style={{
                  display: "block",
                  fontSize: "10px",
                  color: COLORS.textSecondary,
                  letterSpacing: "1px",
                  textTransform: "uppercase",
                  marginBottom: "8px",
                  fontFamily: "monospace"
                }}>
                  PASSWORD *
                </label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  style={{
                    width: "100%",
                    padding: "12px",
                    background: COLORS.bgDark,
                    border: `1px solid ${COLORS.bgLight}`,
                    borderRadius: "2px",
                    color: COLORS.textPrimary,
                    fontSize: "14px",
                    fontFamily: "monospace",
                    outline: "none",
                    boxSizing: "border-box"
                  }}
                />
              </div>

              <div style={{ marginBottom: "28px" }}>
                <label style={{
                  display: "block",
                  fontSize: "10px",
                  color: COLORS.textSecondary,
                  letterSpacing: "1px",
                  textTransform: "uppercase",
                  marginBottom: "8px",
                  fontFamily: "monospace"
                }}>
                  ROLE *
                </label>
                <select
                  value={newRole}
                  onChange={(e) => setNewRole(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "12px",
                    background: COLORS.bgDark,
                    border: `1px solid ${COLORS.bgLight}`,
                    borderRadius: "2px",
                    color: COLORS.textPrimary,
                    fontSize: "14px",
                    fontFamily: "monospace",
                    outline: "none",
                    cursor: "pointer"
                  }}
                >
                  <option value="member">Member</option>
                  <option value="viewer">Viewer</option>
                  <option value="admin">Admin</option>
                </select>
              </div>

              <div style={{ display: "flex", gap: "12px" }}>
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateModal(false);
                    setError("");
                    setNewUsername("");
                    setNewEmail("");
                    setNewPassword("");
                    setNewRole("member");
                  }}
                  style={{
                    flex: 1,
                    padding: "12px",
                    background: "transparent",
                    border: `1px solid ${COLORS.bgLight}`,
                    borderRadius: "2px",
                    color: COLORS.textSecondary,
                    fontSize: "13px",
                    fontWeight: 700,
                    letterSpacing: "1px",
                    textTransform: "uppercase",
                    cursor: "pointer",
                    fontFamily: "monospace"
                  }}
                >
                  CANCEL
                </button>

                <button
                  type="submit"
                  disabled={creating}
                  style={{
                    flex: 1,
                    padding: "12px",
                    background: creating
                      ? COLORS.bgLight
                      : `linear-gradient(135deg, ${COLORS.yellow} 0%, ${COLORS.orange} 100%)`,
                    border: `1px solid ${creating ? COLORS.bgLight : COLORS.yellow}`,
                    borderRadius: "2px",
                    color: COLORS.bgDark,
                    fontSize: "13px",
                    fontWeight: 700,
                    letterSpacing: "1px",
                    textTransform: "uppercase",
                    cursor: creating ? "not-allowed" : "pointer",
                    fontFamily: "monospace",
                    boxShadow: creating ? "none" : `0 0 20px ${COLORS.yellow}40`
                  }}
                >
                  {creating ? "CREATING..." : "CREATE"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}