"use client"

import { useState } from "react"
import { LineChart, Line, XAxis, YAxis } from "recharts"

export default function Home() {
  const [data, setData] = useState<any[]>([])
  const [history, setHistory] = useState<any>({})

  async function search(e: any) {
    const q = e.target.value
    const res = await fetch(`http://localhost:8000/search?q=${q}`)
    const json = await res.json()
    setData(json)
  }

  async function loadHistory(id: number) {
    const res = await fetch(`http://localhost:8000/price-history/${id}`)
    const json = await res.json()

    setHistory((prev: any) => ({
      ...prev,
      [id]: json
    }))
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>SneakPeak</h1>

      <input
        onChange={search}
        placeholder="Search sneakers..."
        style={{ padding: 10, width: 300 }}
      />

      {data.map((shoe) => (
        <div key={shoe.id} style={{ border: "1px solid white", margin: 10, padding: 10 }}>
          <h3>{shoe.name}</h3>
          <p>₹{shoe.price}</p>
          <p>{shoe.platform}</p>

          <button onClick={() => loadHistory(shoe.id)}>
            Show Price History
          </button>

          {history[shoe.id] ? (
  history[shoe.id].length > 0 ? (
    <LineChart width={300} height={200} data={history[shoe.id]}>
      <XAxis dataKey="time" hide />
      <YAxis />
      <Line type="monotone" dataKey="price" dot />
    </LineChart>
  ) : (
    <p>No price history yet</p>
  )
) : null}
        </div>
      ))}
    </div>
  )
}