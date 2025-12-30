"use client";

import React, { useState, useEffect } from "react";
import { Activity, Clock, Package, TrendingUp, AlertTriangle, CheckCircle, Loader, ArrowRight, Plus } from "lucide-react";
import { NewJobForm } from "./NewJobForm";

const API_URL = "http://127.0.0.1:8000";

// ============================================================
// CIG COLOR PALETTE (Authentic Star Citizen)
// ============================================================
const COLORS = {
  // Primary
  orange: "#d97706",
  orangeLight: "#f59e0b",
  red: "#dc2626",
  redDark: "#991b1b",
  yellow: "#eab308",
  yellowLight: "#facc15",
  
  // Status
  greenOlive: "#84a98c",
  greenOliveLight: "#a3b18a",
  
  // Backgrounds
  bgDark: "#0f172a",
  bgMedium: "#1e293b",
  bgLight: "#334155",
  
  // Text
  textPrimary: "#e2e8f0",
  textSecondary: "#94a3b8",
  textTertiary: "#64748b",
  
  // Accents
  accent: "#f97316",
  accentDark: "#ea580c"
};

// ============================================================
// INTERFACES (identiques)
// ============================================================

interface Refinery {
  id: number;
  name: string;
  system: string;
  location: string;
  is_active: boolean;
}

interface JobMaterial {
  id: number;
  material_id: number;
  material_name: string;
  quantity_refined: number;
  unit: string;
}

interface RefiningJob {
  id: number;
  refinery_id: number;
  refinery_name: string;
  refinery_system: string;
  job_type: string;
  total_cost: number;
  processing_time: number;
  status: string;
  start_time: string;
  end_time: string;
  seconds_remaining: number;
  progress_percentage: number;
  materials: JobMaterial[];
  notes?: string;
}

interface InventoryItem {
  id: number;
  refinery_id: number;
  refinery_name: string;
  refinery_system: string;
  material_id: number;
  material_name: string;
  quantity: number;
  unit: string;
  estimated_unit_price: number;
  estimated_total_value: number;
  last_updated: string;
}

interface Sale {
  id: number;
  material_name: string;
  quantity_sold: number;
  unit_price: number;
  total_revenue: number;
  profit: number;
  profit_percentage: number;
  sale_date: string;
  sale_location_name?: string;
}

interface SalesStats {
  total_sales: number;
  total_revenue: number;
  total_cost: number;
  total_profit: number;
  avg_profit_percentage: number;
}

// ============================================================
// UTILITY FUNCTIONS
// ============================================================

function formatTime(seconds: number): string {
  if (seconds <= 0) return "READY";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

function formatNumber(num: number): string {
  return new Intl.NumberFormat('en-US').format(Math.round(num));
}

// ============================================================
// COMPOSANT: Hexagonal Background
// ============================================================

function HexBackground() {
  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      zIndex: 0,
      opacity: 0.3,
      background: `
        repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(217,119,6,0.02) 2px, rgba(217,119,6,0.02) 4px),
        repeating-linear-gradient(60deg, transparent, transparent 2px, rgba(217,119,6,0.02) 2px, rgba(217,119,6,0.02) 4px),
        repeating-linear-gradient(120deg, transparent, transparent 2px, rgba(217,119,6,0.02) 2px, rgba(217,119,6,0.02) 4px)
      `,
      pointerEvents: 'none'
    }} />
  );
}

// ============================================================
// COMPOSANT: Scan Line
// ============================================================

function ScanLine() {
  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100%',
      height: '2px',
      background: `linear-gradient(90deg, transparent, ${COLORS.orange}cc, transparent)`,
      animation: 'scan 8s linear infinite',
      zIndex: 1,
      pointerEvents: 'none'
    }} />
  );
}

// ============================================================
// COMPOSANT: Job Card (CIG Style)
// ============================================================

function JobCard({ job, onCollect }: { job: RefiningJob; onCollect: (id: number) => void }) {
  const [localSeconds, setLocalSeconds] = useState(job.seconds_remaining);
  const isReady = job.status === "ready" || localSeconds <= 0;
  const isCollected = job.status === "collected";
  
  useEffect(() => {
    if (job.status === "processing" && localSeconds > 0) {
      const timer = setInterval(() => {
        setLocalSeconds(prev => Math.max(0, prev - 1));
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [job.status, localSeconds]);
  
  const progress = isReady ? 100 : job.progress_percentage;
  const barColor = isReady ? COLORS.greenOlive : COLORS.orange;
  const statusColor = isCollected ? COLORS.textTertiary : isReady ? COLORS.greenOlive : COLORS.orange;
  const statusBg = isCollected ? COLORS.bgMedium : isReady ? COLORS.greenOlive : COLORS.orange;
  
  return (
    <div style={{
      background: `linear-gradient(135deg, ${COLORS.bgDark}f0 0%, ${COLORS.bgMedium}f0 100%)`,
      border: `1px solid ${statusColor}50`,
      borderRadius: '4px',
      padding: '20px',
      position: 'relative',
      overflow: 'hidden',
      clipPath: 'polygon(0 0, calc(100% - 10px) 0, 100% 10px, 100% 100%, 10px 100%, 0 calc(100% - 10px))',
      boxShadow: `0 2px 10px ${COLORS.bgDark}80, inset 0 0 40px ${COLORS.bgDark}40`,
      transition: 'all 0.3s ease'
    }}>
      {/* Corner accents CIG style */}
      <div style={{
        position: 'absolute',
        top: 0,
        right: 0,
        width: '10px',
        height: '10px',
        borderTop: `1px solid ${statusColor}`,
        borderRight: `1px solid ${statusColor}`
      }} />
      <div style={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        width: '10px',
        height: '10px',
        borderBottom: `1px solid ${statusColor}`,
        borderLeft: `1px solid ${statusColor}`
      }} />
      
      {/* Header bar (rouge CIG) */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '3px',
        background: `linear-gradient(90deg, ${COLORS.red}, ${COLORS.redDark})`
      }} />
      
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: '16px',
        paddingTop: '4px'
      }}>
        <div>
          <div style={{
            fontSize: '10px',
            color: COLORS.textSecondary,
            letterSpacing: '1.5px',
            textTransform: 'uppercase',
            fontWeight: 600,
            marginBottom: '6px',
            fontFamily: 'monospace'
          }}>
            // {job.refinery_system} :: {job.job_type.toUpperCase()}
          </div>
          <div style={{
            fontSize: '18px',
            fontWeight: 700,
            color: COLORS.textPrimary,
            letterSpacing: '0.5px',
            fontFamily: 'monospace',
            textShadow: `0 0 8px ${statusColor}60`
          }}>
            {job.refinery_name}
          </div>
        </div>
        
        {!isCollected && (
          <div style={{
            padding: '5px 12px',
            background: `${statusBg}25`,
            border: `1px solid ${statusColor}`,
            borderRadius: '2px',
            fontSize: '10px',
            fontWeight: 700,
            color: statusColor,
            letterSpacing: '1px',
            textTransform: 'uppercase',
            fontFamily: 'monospace'
          }}>
            {isReady ? "READY" : "PROCESSING"}
          </div>
        )}
      </div>
      
      {/* Materials (style CIG) */}
      <div style={{
        marginBottom: '16px',
        padding: '12px',
        background: `${COLORS.bgDark}60`,
        borderLeft: `2px solid ${COLORS.orange}60`,
        borderRadius: '2px'
      }}>
        {job.materials.map((mat, idx) => (
          <div key={idx} style={{
            display: 'flex',
            justifyContent: 'space-between',
            fontSize: '12px',
            fontFamily: 'monospace',
            marginBottom: idx < job.materials.length - 1 ? '6px' : 0,
            alignItems: 'center'
          }}>
            <span style={{ color: COLORS.textSecondary, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ 
                display: 'inline-block', 
                width: '6px', 
                height: '6px', 
                background: COLORS.orange,
                clipPath: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)'
              }} />
              {mat.material_name}
            </span>
            <span style={{ color: COLORS.orange, fontWeight: 700 }}>
              {formatNumber(mat.quantity_refined)} {mat.unit}
            </span>
          </div>
        ))}
      </div>
      
      {/* Progress bar (style CIG) */}
      {!isCollected && (
        <>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            fontSize: '10px',
            fontFamily: 'monospace',
            marginBottom: '8px',
            color: COLORS.textSecondary,
            letterSpacing: '1px',
            textTransform: 'uppercase'
          }}>
            <span>// PROGRESS</span>
            <span style={{ color: statusColor, fontWeight: 700 }}>
              {isReady ? "COMPLETE" : formatTime(localSeconds)}
            </span>
          </div>
          
          <div style={{
            width: '100%',
            height: '20px',
            background: COLORS.bgDark,
            borderRadius: '2px',
            overflow: 'hidden',
            border: `1px solid ${COLORS.bgLight}`,
            position: 'relative',
            marginBottom: '16px'
          }}>
            <div style={{
              width: `${progress}%`,
              height: '100%',
              background: `linear-gradient(90deg, ${barColor}, ${barColor}dd)`,
              transition: 'width 0.5s ease',
              position: 'relative',
              overflow: 'hidden'
            }}>
              <div style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                background: 'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.15) 50%, transparent 100%)',
                animation: isReady ? 'none' : 'shimmer 2s infinite'
              }} />
            </div>
            
            <div style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              fontSize: '10px',
              fontWeight: 700,
              color: COLORS.textPrimary,
              fontFamily: 'monospace',
              textShadow: `0 0 4px ${COLORS.bgDark}`,
              letterSpacing: '1px'
            }}>
              {Math.round(progress)}%
            </div>
          </div>
        </>
      )}
      
      {/* Actions (boutons jaune CIG) */}
      <div style={{
        display: 'flex',
        gap: '12px',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{
          fontSize: '10px',
          color: COLORS.textSecondary,
          fontFamily: 'monospace',
          textTransform: 'uppercase'
        }}>
          TOTAL COST: <span style={{ color: COLORS.orange, fontWeight: 700 }}>{formatNumber(job.total_cost)} aUEC</span>
        </div>
        
        {isReady && !isCollected && (
          <button
            onClick={() => onCollect(job.id)}
            style={{
              padding: '10px 20px',
              background: `linear-gradient(135deg, ${COLORS.yellow} 0%, ${COLORS.yellowLight} 100%)`,
              border: `1px solid ${COLORS.yellow}`,
              borderRadius: '2px',
              color: COLORS.bgDark,
              fontSize: '11px',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '1px',
              cursor: 'pointer',
              fontFamily: 'monospace',
              boxShadow: `0 0 15px ${COLORS.yellow}40`,
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.boxShadow = `0 0 25px ${COLORS.yellow}60`;
              e.currentTarget.style.transform = 'translateY(-1px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.boxShadow = `0 0 15px ${COLORS.yellow}40`;
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            <CheckCircle style={{ width: '12px', height: '12px', display: 'inline', marginRight: '6px' }} />
            COLLECT CARGO
          </button>
        )}
        
        {isCollected && (
          <div style={{
            padding: '10px 20px',
            background: `${COLORS.bgLight}40`,
            border: `1px solid ${COLORS.textTertiary}`,
            borderRadius: '2px',
            color: COLORS.textTertiary,
            fontSize: '11px',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '1px',
            fontFamily: 'monospace'
          }}>
            ✓ COLLECTED
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================================
// COMPOSANT: Inventory Card (CIG Style)
// ============================================================

function InventoryCard({ item }: { item: InventoryItem }) {
  return (
    <div style={{
      background: `linear-gradient(135deg, ${COLORS.bgDark}f5 0%, ${COLORS.bgMedium}f5 100%)`,
      border: `1px solid ${COLORS.orange}40`,
      borderRadius: '2px',
      padding: '16px',
      position: 'relative',
      overflow: 'hidden',
      transition: 'all 0.2s ease'
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.borderColor = `${COLORS.orange}80`;
      e.currentTarget.style.boxShadow = `0 0 15px ${COLORS.orange}20`;
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.borderColor = `${COLORS.orange}40`;
      e.currentTarget.style.boxShadow = 'none';
    }}>
      <div style={{
        fontSize: '10px',
        color: COLORS.textSecondary,
        letterSpacing: '1px',
        textTransform: 'uppercase',
        marginBottom: '8px',
        fontFamily: 'monospace'
      }}>
        {item.refinery_name} :: {item.refinery_system}
      </div>
      
      <div style={{
        fontSize: '16px',
        fontWeight: 700,
        color: COLORS.textPrimary,
        marginBottom: '4px',
        textShadow: `0 0 8px ${COLORS.orange}40`
      }}>
        {item.material_name}
      </div>
      
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'baseline',
        marginBottom: '12px'
      }}>
        <span style={{
          fontSize: '20px',
          fontWeight: 700,
          color: COLORS.orange,
          fontFamily: 'monospace'
        }}>
          {formatNumber(item.quantity)}
        </span>
        <span style={{
          fontSize: '10px',
          color: COLORS.textSecondary,
          fontFamily: 'monospace'
        }}>
          {item.unit}
        </span>
      </div>
      
      <div style={{
        padding: '8px',
        background: `${COLORS.greenOlive}15`,
        borderRadius: '2px',
        borderLeft: `2px solid ${COLORS.greenOlive}`
      }}>
        <div style={{
          fontSize: '9px',
          color: COLORS.textSecondary,
          letterSpacing: '1px',
          marginBottom: '2px',
          fontFamily: 'monospace',
          textTransform: 'uppercase'
        }}>
          ESTIMATED VALUE
        </div>
        <div style={{
          fontSize: '14px',
          fontWeight: 700,
          color: COLORS.greenOlive,
          fontFamily: 'monospace'
        }}>
          {formatNumber(item.estimated_total_value)} aUEC
        </div>
      </div>
    </div>
  );
}

// ============================================================
// MAIN COMPONENT (avec couleurs CIG)
// ============================================================

export default function ProductionPage() {
  const [jobs, setJobs] = useState<RefiningJob[]>([]);
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [sales, setSales] = useState<Sale[]>([]);
  const [stats, setStats] = useState<SalesStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);
  const [activeTab, setActiveTab] = useState<"jobs" | "inventory" | "sales">("jobs");

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;
    
    async function loadData() {
      try {
        const [jobsRes, invRes, salesRes, statsRes] = await Promise.all([
          fetch(`${API_URL}/production/jobs?status=processing`),
          fetch(`${API_URL}/production/inventory`),
          fetch(`${API_URL}/production/sales?limit=10`),
          fetch(`${API_URL}/production/sales/stats`)
        ]);
        
        setJobs(await jobsRes.json());
        setInventory(await invRes.json());
        setSales(await salesRes.json());
        setStats(await statsRes.json());
        setLoading(false);
      } catch (e) {
        console.error("Error loading production data:", e);
        setLoading(false);
      }
    }

    loadData();
    const timer = setInterval(loadData, 5000);
    return () => clearInterval(timer);
  }, [mounted]);

  const handleCollect = async (jobId: number) => {
    try {
      await fetch(`${API_URL}/production/jobs/${jobId}/collect`, { method: 'POST' });
      const jobsRes = await fetch(`${API_URL}/production/jobs?status=processing`);
      const invRes = await fetch(`${API_URL}/production/inventory`);
      setJobs(await jobsRes.json());
      setInventory(await invRes.json());
    } catch (e) {
      console.error("Error collecting job:", e);
    }
  };
 const refreshData = async () => {
    try {
      const [jobsRes, invRes, salesRes, statsRes] = await Promise.all([
        fetch(`${API_URL}/production/jobs?status=processing`),
        fetch(`${API_URL}/production/inventory`),
        fetch(`${API_URL}/production/sales?limit=10`),
        fetch(`${API_URL}/production/sales/stats`)
      ]);
      
      setJobs(await jobsRes.json());
      setInventory(await invRes.json());
      setSales(await salesRes.json());
      setStats(await statsRes.json());
    } catch (e) {
      console.error("Error refreshing data:", e);
    }
  };

  if (!mounted || loading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        flexDirection: 'column',
        gap: '20px',
        background: COLORS.bgDark
      }}>
        <Loader style={{ width: '48px', height: '48px', color: COLORS.orange, animation: 'spin 1s linear infinite' }} />
        <div style={{
          color: COLORS.orange,
          fontSize: '12px',
          letterSpacing: '3px',
          fontWeight: 600,
          fontFamily: 'monospace',
          textTransform: 'uppercase'
        }}>
          INITIALIZING REFINERY TERMINAL...
        </div>
      </div>
    );
  }

  const activeJobs = jobs.filter(j => j.status === "processing");
  const totalInventoryValue = inventory.reduce((sum, item) => sum + item.estimated_total_value, 0);

  return (
    <div style={{
      minHeight: '100vh',
      background: COLORS.bgDark,
      position: 'relative',
      padding: '32px'
    }}>
      <HexBackground />
      <ScanLine />
      
      <div style={{
        maxWidth: '1800px',
        margin: '0 auto',
        position: 'relative',
        zIndex: 2
      }}>
        {/* HEADER (rouge CIG) */}
        <div style={{
          marginBottom: '40px',
          position: 'relative',
          paddingBottom: '20px',
          borderBottom: `1px solid ${COLORS.red}40`
        }}>
          {/* Red header bar */}
          <div style={{
            position: 'absolute',
            top: -8,
            left: 0,
            right: 0,
            height: '3px',
            background: `linear-gradient(90deg, ${COLORS.red}, ${COLORS.redDark}, transparent)`
          }} />
          
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '16px',
            marginBottom: '12px'
          }}>
            <div style={{
              width: '3px',
              height: '60px',
              background: `linear-gradient(180deg, ${COLORS.orange} 0%, transparent 100%)`
            }} />
            <div>
              <div style={{
                fontSize: '11px',
                color: COLORS.red,
                letterSpacing: '2px',
                textTransform: 'uppercase',
                fontWeight: 700,
                marginBottom: '8px',
                fontFamily: 'monospace'
              }}>
                // REFINERY SYSTEM C47.02
              </div>
              <h1 style={{
                fontSize: '38px',
                fontWeight: 700,
                color: COLORS.textPrimary,
                letterSpacing: '3px',
                textTransform: 'uppercase',
                margin: 0,
                fontFamily: 'monospace',
                textShadow: `0 0 15px ${COLORS.orange}40`
              }}>
                INDUSTRIAL OPERATIONS
              </h1>
            </div>
          </div>
          
          <div style={{
            display: 'flex',
            gap: '32px',
            fontSize: '11px',
            fontFamily: 'monospace',
            color: COLORS.textSecondary,
            letterSpacing: '1px',
            marginLeft: '20px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Activity style={{ width: '12px', height: '12px', color: COLORS.orange }} />
              <span style={{ color: COLORS.orange, fontWeight: 600 }}>{activeJobs.length}</span> ACTIVE JOBS
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Package style={{ width: '12px', height: '12px', color: COLORS.greenOlive }} />
              <span style={{ color: COLORS.greenOlive, fontWeight: 600 }}>{inventory.length}</span> MATERIALS IN STOCK
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <TrendingUp style={{ width: '12px', height: '12px', color: COLORS.yellow }} />
              <span style={{ color: COLORS.yellow, fontWeight: 600 }}>{formatNumber(totalInventoryValue)}</span> aUEC ESTIMATED
            </div>
          </div>
        </div>

        {/* TABS (style CIG) */}
        <div style={{
          display: 'flex',
          gap: '6px',
          marginBottom: '32px'
        }}>
          {[
            { key: "jobs", label: "REFINING JOBS", icon: Activity },
            { key: "inventory", label: "CARGO MANIFEST", icon: Package },
            { key: "sales", label: "SALES RECORDS", icon: TrendingUp }
          ].map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.key;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                style={{
                  padding: '10px 20px',
                  background: isActive ? `linear-gradient(135deg, ${COLORS.orange}30 0%, ${COLORS.orange}20 100%)` : COLORS.bgMedium,
                  border: `1px solid ${isActive ? COLORS.orange : COLORS.bgLight}`,
                  borderRadius: '2px',
                  color: isActive ? COLORS.orange : COLORS.textSecondary,
                  fontSize: '11px',
                  fontWeight: 700,
                  letterSpacing: '1px',
                  textTransform: 'uppercase',
                  cursor: 'pointer',
                  fontFamily: 'monospace',
                  transition: 'all 0.2s ease',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  boxShadow: isActive ? `0 0 15px ${COLORS.orange}30` : 'none',
                  borderBottom: isActive ? `2px solid ${COLORS.orange}` : 'none'
                }}
                onMouseEnter={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.borderColor = `${COLORS.orange}60`;
                    e.currentTarget.style.color = COLORS.textPrimary;
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.borderColor = COLORS.bgLight;
                    e.currentTarget.style.color = COLORS.textSecondary;
                  }
                }}
              >
                <Icon style={{ width: '14px', height: '14px' }} />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* NEW JOB FORM */}
        {activeTab === "jobs" && <NewJobForm onJobCreated={refreshData} />}
        
        {/* CONTENT */}
        {activeTab === "jobs" && (
          <div>
            {activeJobs.length === 0 ? (
              <div style={{
                textAlign: 'center',
                padding: '80px 20px',
                background: COLORS.bgMedium,
                border: `1px dashed ${COLORS.orange}40`,
                borderRadius: '2px'
              }}>
                <AlertTriangle style={{ width: '48px', height: '48px', color: COLORS.textTertiary, margin: '0 auto 16px' }} />
                <div style={{
                  color: COLORS.textSecondary,
                  fontSize: '12px',
                  letterSpacing: '2px',
                  fontFamily: 'monospace',
                  textTransform: 'uppercase'
                }}>
                  NO ACTIVE REFINING JOBS
                </div>
              </div>
            ) : (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))',
                gap: '20px'
              }}>
                {activeJobs.map(job => (
                  <JobCard key={job.id} job={job} onCollect={handleCollect} />
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "inventory" && (
          <div>
            {inventory.length === 0 ? (
              <div style={{
                textAlign: 'center',
                padding: '80px 20px',
                background: COLORS.bgMedium,
                border: `1px dashed ${COLORS.orange}40`,
                borderRadius: '2px'
              }}>
                <Package style={{ width: '48px', height: '48px', color: COLORS.textTertiary, margin: '0 auto 16px' }} />
                <div style={{
                  color: COLORS.textSecondary,
                  fontSize: '12px',
                  letterSpacing: '2px',
                  fontFamily: 'monospace',
                  textTransform: 'uppercase'
                }}>
                  CARGO MANIFEST EMPTY
                </div>
              </div>
            ) : (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                gap: '16px'
              }}>
                {inventory.map(item => (
                  <InventoryCard key={item.id} item={item} />
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "sales" && (
          <div>
            {stats && (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                gap: '16px',
                marginBottom: '32px'
              }}>
                {[
                  { label: "TOTAL REVENUE", value: stats.total_revenue, color: COLORS.greenOlive },
                  { label: "TOTAL COST", value: stats.total_cost, color: COLORS.orange },
                  { label: "NET PROFIT", value: stats.total_profit, color: COLORS.yellow },
                  { label: "AVG PROFIT %", value: stats.avg_profit_percentage, color: COLORS.greenOliveLight, suffix: "%" }
                ].map((stat, idx) => (
                  <div key={idx} style={{
                    padding: '18px',
                    background: `linear-gradient(135deg, ${COLORS.bgDark}f5 0%, ${COLORS.bgMedium}f5 100%)`,
                    border: `1px solid ${stat.color}50`,
                    borderRadius: '2px',
                    borderLeft: `3px solid ${stat.color}`
                  }}>
                    <div style={{
                      fontSize: '10px',
                      color: COLORS.textSecondary,
                      letterSpacing: '1px',
                      marginBottom: '8px',
                      fontFamily: 'monospace',
                      textTransform: 'uppercase'
                    }}>
                      // {stat.label}
                    </div>
                    <div style={{
                      fontSize: '24px',
                      fontWeight: 700,
                      color: stat.color,
                      fontFamily: 'monospace',
                      textShadow: `0 0 10px ${stat.color}60`
                    }}>
                      {formatNumber(stat.value)}{stat.suffix || ' aUEC'}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {sales.length === 0 ? (
              <div style={{
                textAlign: 'center',
                padding: '80px 20px',
                background: COLORS.bgMedium,
                border: `1px dashed ${COLORS.orange}40`,
                borderRadius: '2px'
              }}>
                <TrendingUp style={{ width: '48px', height: '48px', color: COLORS.textTertiary, margin: '0 auto 16px' }} />
                <div style={{
                  color: COLORS.textSecondary,
                  fontSize: '12px',
                  letterSpacing: '2px',
                  fontFamily: 'monospace',
                  textTransform: 'uppercase'
                }}>
                  NO SALES RECORDED
                </div>
              </div>
            ) : (
              <div style={{
                background: `linear-gradient(135deg, ${COLORS.bgDark}f5 0%, ${COLORS.bgMedium}f5 100%)`,
                border: `1px solid ${COLORS.orange}40`,
                borderRadius: '2px',
                overflow: 'hidden'
              }}>
                <div style={{
                  padding: '14px 20px',
                  background: `${COLORS.orange}20`,
                  borderBottom: `1px solid ${COLORS.orange}40`,
                  fontSize: '11px',
                  fontWeight: 700,
                  letterSpacing: '2px',
                  color: COLORS.orange,
                  textTransform: 'uppercase',
                  fontFamily: 'monospace'
                }}>
                  // RECENT TRANSACTIONS
                </div>
                {sales.map((sale, idx) => (
                  <div key={sale.id} style={{
                    padding: '14px 20px',
                    borderBottom: idx < sales.length - 1 ? `1px solid ${COLORS.bgLight}` : 'none',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    fontSize: '12px',
                    fontFamily: 'monospace',
                    transition: 'background 0.2s ease'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = `${COLORS.orange}10`}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}>
                    <div style={{ flex: 1 }}>
                      <div style={{ color: COLORS.textPrimary, fontWeight: 600, marginBottom: '4px' }}>
                        {sale.material_name}
                      </div>
                      <div style={{ color: COLORS.textSecondary, fontSize: '10px' }}>
                        {formatNumber(sale.quantity_sold)} units @ {formatNumber(sale.unit_price)} aUEC
                      </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ color: COLORS.greenOlive, fontWeight: 700 }}>
                          +{formatNumber(sale.total_revenue)} aUEC
                        </div>
                        <div style={{ color: COLORS.greenOliveLight, fontSize: '10px' }}>
                          {sale.profit_percentage > 0 ? '+' : ''}{sale.profit_percentage.toFixed(1)}% profit
                        </div>
                      </div>
                      <ArrowRight style={{ width: '14px', height: '14px', color: COLORS.textTertiary }} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      <style jsx>{`
        @keyframes scan {
          0% { transform: translateY(0); opacity: 0; }
          50% { opacity: 1; }
          100% { transform: translateY(100vh); opacity: 0; }
        }
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}