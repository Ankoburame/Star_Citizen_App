const API_URL = "http://127.0.0.1:8000"

export async function getDashboard() {
  const res = await fetch(`${API_URL}/dashboard`, {
    cache: "no-store",
  })

  if (!res.ok) {
    const text = await res.text()
    console.error("Dashboard API error:", text)
    throw new Error("Dashboard API failed")
  }

  return res.json()
}

export async function getRefiningJobs() {
  const res = await fetch(`${API_URL}/refining/active`, {
    cache: "no-store",
  })

  if (!res.ok) {
    const text = await res.text()
    console.error("Refining API error:", text)
    throw new Error("Failed to fetch refining jobs")
  }

  return res.json()
}
