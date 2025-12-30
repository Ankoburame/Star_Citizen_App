"use client"

import { useEffect, useState } from "react"
import { getDashboard, getRefiningJobs } from "@/lib/api"

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState<any>(null)
  const [refiningJobs, setRefiningJobs] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const load = async () => {
    try {
      const [dashboardData, refiningData] = await Promise.all([
        getDashboard(),
        getRefiningJobs(),
      ])

      setDashboard(dashboardData)
      setRefiningJobs(refiningData)
    } catch (err) {
      console.error("Dashboard load failed", err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    const interval = setInterval(load, 5000)
    return () => clearInterval(interval)
  }, [])

  if (loading || !dashboard) {
    return <p style={{ opacity: 0.6 }}>Chargement du dashboard…</p>
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 32 }}>

      {/* ===== STATS ===== */}
      <section>
        <h2>Vue d’ensemble</h2>
        <div style={{ display: "flex", gap: 16 }}>
          <Stat title="Stock total" value={`${dashboard.stock_total} SCU`} />
          <Stat title="Raffinages actifs" value={dashboard.active_refining} />
          <Stat
            title="Valeur estimée"
            value={`${dashboard.estimated_stock_value.toLocaleString()} aUEC`}
          />
        </div>
      </section>

      {/* ===== ACTIVE REFINING ===== */}
      <section>
        <h2>Raffinages en cours</h2>

        {refiningJobs.length === 0 ? (
          <div>Aucun raffinage en cours</div>
        ) : (
          refiningJobs.map(job => (
            <RefiningJob
              key={job.id}
              label={job.material_name}
              progress={
                job.total_seconds > 0
                  ? 100 - (job.remaining_seconds / job.total_seconds) * 100
                  : 100
              }
              eta={`${Math.ceil(job.remaining_seconds / 60)} min`}
            />
          ))
        )}
      </section>

      {/* ===== HISTORY ===== */}
      <section>
        <h2>Historique des raffinages</h2>

        {dashboard.refining_history.length === 0 ? (
          <div>Aucun raffinage terminé récemment</div>
        ) : (
          dashboard.refining_history.map((job: any) => (
            <HistoryRow
              key={job.id}
              material={job.material}
              quantity={job.quantity}
              date={job.ended_at}
            />
          ))
        )}
      </section>
    </div>
  )
}

/* ===== UI ===== */

function Stat({ title, value }: any) {
  return (
    <div style={{ background: "#151a23", padding: 16 }}>
      <div>{title}</div>
      <strong>{value}</strong>
    </div>
  )
}

function RefiningJob({ label, progress, eta }: any) {
  return (
    <div style={{ background: "#151a23", padding: 12 }}>
      <div>{label} — ETA {eta}</div>
      <div style={{ height: 6, background: "#222" }}>
        <div
          style={{
            width: `${progress}%`,
            height: "100%",
            background: "#3ddc97",
          }}
        />
      </div>
    </div>
  )
}

function HistoryRow({ material, quantity, date }: any) {
  return (
    <div style={{ background: "#151a23", padding: 12 }}>
      <strong>{material}</strong> — {quantity} SCU —{" "}
      {new Date(date).toLocaleDateString()}
    </div>
  )
}
