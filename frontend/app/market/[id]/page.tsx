"use client";

import React, { useState, useEffect } from "react";
import { TrendingUp, TrendingDown, Minus, Activity, MapPin, DollarSign, Package, Clock, Filter, X, Search, ArrowUpDown } from "lucide-react";
import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

type SortOption = "name-asc" | "name-desc" | "price-asc" | "price-desc" | "variation-asc" | "variation-desc" | "locations";

interface Material {
  id: number;
  name: string;
  code: string;
  category: string;
  avg_sell_price: number | null;
  min_buy_price: number | null;
  max_sell_price: number | null;
  best_buy_location: Location | null;
  best_sell_location: Location | null;
  available_at: number;
  variation: number;
}

interface Location {
  id: number;
  name: string;
  code: string;
  system: string;
  full_path: string;
}

// Générer un acronyme depuis un nom de matériau
function generateAcronym(name: string): string {
  const words = name.split(" ");
  if (words.length === 1) {
    return name.substring(0, 3).toUpperCase();
  }
  return words.map(w => w[0]).join("").substring(0, 4).toUpperCase();
}

// Générer des données de variation simulées pour le graphique
function generateMiniChartData(variation: number): number[] {
  const baseValue = 100;
  const points = 20;
  const data: number[] = [];
  
  let current = baseValue;
  for (let i = 0; i < points; i++) {
    const noise = (Math.random() - 0.5) * 5;
    const trend = (variation / points) * i;
    current = baseValue + trend + noise;
    data.push(current);
  }
  
  return data;
}

// Composant pour mini-graphique stylisé Star Citizen
function MiniChart({ data, variation, size = "normal" }: { data: number[]; variation: number; size?: "normal" | "small" }) {
  const width = size === "small" ? 50 : 80;
  const height = size === "small" ? 20 : 30;
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  
  const points = data.map((value, i) => {
    const x = (i / (data.length - 1)) * width;
    const y = height - ((value - min) / range) * height;
    return `${x},${y}`;
  }).join(" ");
  
  const color = variation > 1 ? "#10b981" : variation < -1 ? "#ef4444" : "#71717a";
  const glowColor = variation > 1 ? "rgba(16, 185, 129, 0.5)" : variation < -1 ? "rgba(239, 68, 68, 0.5)" : "rgba(113, 113, 122, 0.3)";
  
  return (
    <svg width={width} height={height} style={{ display: 'block', margin: '0 auto' }}>
      <defs>
        <filter id={`glow-${variation}-${size}`}>
          <feGaussianBlur stdDeviation="1.5" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
        
        <linearGradient id={`gradient-${variation}-${size}`} x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style={{ stopColor: color, stopOpacity: 0.3 }} />
          <stop offset="100%" style={{ stopColor: color, stopOpacity: 0 }} />
        </linearGradient>
      </defs>
      
      <path
        d={`M 0,${height} L ${points} L ${width},${height} Z`}
        fill={`url(#gradient-${variation}-${size})`}
        opacity={0.4}
      />
      
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth={size === "small" ? "1.5" : "2"}
        filter={`url(#glow-${variation}-${size})`}
        style={{ filter: `drop-shadow(0 0 3px ${glowColor})` }}
      />
    </svg>
  );
}

// Composant pour une cellule de matériau
function MaterialCell({ material, isSelected, onClick }: { 
  material: Material; 
  isSelected: boolean;
  onClick: () => void;
}) {
  const [showTooltip, setShowTooltip] = useState(false);
  const variation = material.variation;
  const chartData = generateMiniChartData(variation);
  
  let bgColor = "rgba(0, 0, 0, 0.4)";
  let borderColor = "rgba(82, 82, 91, 0.3)";
  let textColor = "#a1a1aa";
  let icon = <Minus style={{ width: '10px', height: '10px' }} />;
  
  if (variation > 1) {
    bgColor = "rgba(16, 185, 129, 0.05)";
    borderColor = "rgba(16, 185, 129, 0.3)";
    textColor = "#10b981";
    icon = <TrendingUp style={{ width: '10px', height: '10px' }} />;
  } else if (variation < -1) {
    bgColor = "rgba(239, 68, 68, 0.05)";
    borderColor = "rgba(239, 68, 68, 0.3)";
    textColor = "#ef4444";
    icon = <TrendingDown style={{ width: '10px', height: '10px' }} />;
  }
  
  if (isSelected) {
    bgColor = "rgba(6, 182, 212, 0.15)";
    borderColor = "#06b6d4";
  }
  
  const acronym = generateAcronym(material.name);
  
  return (
    <div
      style={{
        position: 'relative',
        background: bgColor,
        border: `1px solid ${borderColor}`,
        borderRadius: '4px',
        padding: '6px',
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        boxShadow: isSelected ? '0 0 20px rgba(6, 182, 212, 0.3)' : 'none',
        minHeight: '85px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between'
      }}
      onClick={onClick}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '4px'
      }}>
        <div style={{
          fontSize: '11px',
          fontWeight: 700,
          color: 'white',
          fontFamily: 'monospace',
          letterSpacing: '0.5px'
        }}>
          {acronym}
        </div>
        <div style={{ color: textColor }}>
          {icon}
        </div>
      </div>
      
      <div style={{ marginBottom: '4px', height: '20px' }}>
        <MiniChart data={chartData} variation={variation} size="small" />
      </div>
      
      <div style={{
        fontSize: '10px',
        fontWeight: 600,
        color: textColor,
        fontFamily: 'monospace',
        textAlign: 'right'
      }}>
        {variation > 0 ? '+' : ''}{variation.toFixed(1)}%
      </div>
      
      {showTooltip && (
        <div style={{
          position: 'absolute',
          top: '100%',
          left: '50%',
          transform: 'translateX(-50%)',
          marginTop: '8px',
          background: 'linear-gradient(135deg, #0a0e1a 0%, #050810 100%)',
          border: '1px solid rgba(6, 182, 212, 0.3)',
          borderRadius: '6px',
          padding: '12px 16px',
          minWidth: '200px',
          zIndex: 1000,
          boxShadow: '0 8px 24px rgba(0, 0, 0, 0.8)',
          pointerEvents: 'none'
        }}>
          <div style={{
            fontSize: '14px',
            fontWeight: 600,
            color: 'white',
            marginBottom: '6px'
          }}>
            {material.name}
          </div>
          <div style={{
            fontSize: '12px',
            color: '#71717a',
            marginBottom: '4px'
          }}>
            Catégorie: {material.category}
          </div>
          {material.max_sell_price && (
            <div style={{
              fontSize: '12px',
              color: '#06b6d4',
              fontFamily: 'monospace'
            }}>
              Max: {material.max_sell_price.toLocaleString()} aUEC
            </div>
          )}
          <div style={{
            fontSize: '11px',
            color: '#52525b',
            marginTop: '4px'
          }}>
            Disponible à {material.available_at} locations
          </div>
        </div>
      )}
    </div>
  );
}

export default function MarketPage() {
  const router = useRouter();
  const [materials, setMaterials] = useState<Material[]>([]);
  const [filteredMaterials, setFilteredMaterials] = useState<Material[]>([]);
  const [selectedMaterial, setSelectedMaterial] = useState<Material | null>(null);
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);
  
  // Filtres
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [sortOption, setSortOption] = useState<SortOption>("name-asc");

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;

    async function loadMaterials() {
      try {
        const res = await fetch(`${API_URL}/market/materials`);
        const data = await res.json();
        
        const materialsWithVariation = data.map((m: any) => ({
          ...m,
          variation: (Math.random() - 0.5) * 10
        }));
        
        setMaterials(materialsWithVariation);
        setFilteredMaterials(materialsWithVariation);
        
        if (!selectedMaterial && materialsWithVariation.length > 0) {
          const randomIndex = Math.floor(Math.random() * materialsWithVariation.length);
          setSelectedMaterial(materialsWithVariation[randomIndex]);
        }
        
        setLoading(false);
      } catch (e) {
        console.error("Error loading materials:", e);
        setLoading(false);
      }
    }

    loadMaterials();
    const timer = setInterval(loadMaterials, 30000);
    return () => clearInterval(timer);
  }, [mounted, selectedMaterial]);

  // Appliquer les filtres ET le tri
  useEffect(() => {
    let filtered = materials;
    
    // Filtre par catégorie
    if (selectedCategory !== "all") {
      filtered = filtered.filter(m => m.category === selectedCategory);
    }
    
    // Filtre par recherche
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(m => 
        m.name.toLowerCase().includes(query) ||
        generateAcronym(m.name).toLowerCase().includes(query)
      );
    }
    
    // Tri
    const sorted = [...filtered].sort((a, b) => {
      switch (sortOption) {
        case "name-asc":
          return a.name.localeCompare(b.name);
        case "name-desc":
          return b.name.localeCompare(a.name);
        case "price-asc":
          return (a.avg_sell_price || 0) - (b.avg_sell_price || 0);
        case "price-desc":
          return (b.avg_sell_price || 0) - (a.avg_sell_price || 0);
        case "variation-asc":
          return a.variation - b.variation;
        case "variation-desc":
          return b.variation - a.variation;
        case "locations":
          return b.available_at - a.available_at;
        default:
          return 0;
      }
    });
    
    setFilteredMaterials(sorted);
  }, [selectedCategory, searchQuery, sortOption, materials]);

  if (!mounted || loading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        flexDirection: 'column',
        gap: '20px'
      }}>
        <div style={{
          width: '60px',
          height: '60px',
          border: '4px solid transparent',
          borderTopColor: '#06b6d4',
          borderRightColor: '#06b6d4',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }} />
        <div style={{
          color: '#52525b',
          fontSize: '14px',
          letterSpacing: '3px',
          fontWeight: 600
        }}>
          CHARGEMENT DU MARCHÉ...
        </div>
      </div>
    );
  }

  const largeChartData = selectedMaterial ? generateMiniChartData(selectedMaterial.variation) : [];
  const categories = ["all", ...Array.from(new Set(materials.map(m => m.category)))];

  const sortOptions: {value: SortOption, label: string}[] = [
    { value: "name-asc", label: "Nom (A-Z)" },
    { value: "name-desc", label: "Nom (Z-A)" },
    { value: "price-asc", label: "Prix ↑" },
    { value: "price-desc", label: "Prix ↓" },
    { value: "variation-desc", label: "Top gainers" },
    { value: "variation-asc", label: "Top losers" },
    { value: "locations", label: "Plus disponible" },
  ];

  return (
    <div style={{ padding: '32px', maxWidth: '1800px' }}>
      {/* HEADER - identique */}
      <div style={{
        marginBottom: '40px',
        position: 'relative',
        paddingBottom: '20px'
      }}>
        <div style={{
          position: 'absolute',
          left: 0,
          top: 0,
          width: '4px',
          height: '100%',
          background: 'linear-gradient(180deg, #06b6d4 0%, transparent 100%)'
        }} />
        
        <div style={{ paddingLeft: '24px' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            marginBottom: '8px'
          }}>
            <Activity style={{ width: '28px', height: '28px', color: '#06b6d4' }} />
            <h1 style={{
              fontSize: '36px',
              fontWeight: 700,
              color: 'white',
              letterSpacing: '4px',
              textTransform: 'uppercase',
              margin: 0
            }}>
              GALACTIC MARKET
            </h1>
          </div>
          <div style={{
            display: 'flex',
            gap: '32px',
            alignItems: 'center'
          }}>
            <div style={{
              color: '#71717a',
              fontSize: '13px',
              letterSpacing: '2px',
              textTransform: 'uppercase'
            }}>
              // TRADE DEVELOPMENT DIVISION
            </div>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '12px',
              color: '#06b6d4',
              fontFamily: 'monospace'
            }}>
              <Package style={{ width: '14px', height: '14px' }} />
              {filteredMaterials.length} / {materials.length} COMMODITÉS
            </div>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '12px',
              color: '#10b981',
              fontFamily: 'monospace'
            }}>
              <Clock style={{ width: '14px', height: '14px' }} />
              MISE À JOUR EN TEMPS RÉEL
            </div>
          </div>
        </div>

        <div style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: '1px',
          background: 'linear-gradient(90deg, #06b6d4 0%, transparent 50%, #06b6d4 100%)',
          opacity: 0.3
        }} />
      </div>

      {/* FILTRES, RECHERCHE ET TRI */}
      <div style={{
        display: 'flex',
        gap: '16px',
        marginBottom: '24px',
        flexWrap: 'wrap'
      }}>
        {/* Recherche */}
        <div style={{
          position: 'relative',
          flex: '1 1 250px',
          minWidth: '200px',
          maxWidth: '400px'
        }}>
          <Search style={{
            position: 'absolute',
            left: '12px',
            top: '50%',
            transform: 'translateY(-50%)',
            width: '18px',
            height: '18px',
            color: '#71717a',
            pointerEvents: 'none'
          }} />
          <input
            type="text"
            placeholder="Rechercher..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '12px 12px 12px 42px',
              background: 'rgba(0, 0, 0, 0.4)',
              border: '1px solid rgba(82, 82, 91, 0.3)',
              borderRadius: '6px',
              color: 'white',
              fontSize: '14px',
              fontFamily: 'monospace',
              outline: 'none',
              transition: 'all 0.2s ease'
            }}
            onFocus={(e) => {
              e.target.style.borderColor = 'rgba(6, 182, 212, 0.5)';
              e.target.style.background = 'rgba(6, 182, 212, 0.05)';
            }}
            onBlur={(e) => {
              e.target.style.borderColor = 'rgba(82, 82, 91, 0.3)';
              e.target.style.background = 'rgba(0, 0, 0, 0.4)';
            }}
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              style={{
                position: 'absolute',
                right: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                background: 'transparent',
                border: 'none',
                color: '#71717a',
                cursor: 'pointer',
                padding: '4px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <X style={{ width: '16px', height: '16px' }} />
            </button>
          )}
        </div>

        {/* Menu TRI - ✅ NOUVEAU */}
        <div style={{
          position: 'relative',
          flex: '0 0 auto'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '12px 16px',
            background: 'rgba(0, 0, 0, 0.4)',
            border: '1px solid rgba(82, 82, 91, 0.3)',
            borderRadius: '6px',
            cursor: 'pointer'
          }}>
            <ArrowUpDown style={{ width: '16px', height: '16px', color: '#71717a' }} />
            <select
              value={sortOption}
              onChange={(e) => setSortOption(e.target.value as SortOption)}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'white',
                fontSize: '12px',
                fontWeight: 600,
                textTransform: 'uppercase',
                letterSpacing: '1px',
                cursor: 'pointer',
                outline: 'none',
                fontFamily: 'monospace'
              }}
            >
              {sortOptions.map(opt => (
                <option key={opt.value} value={opt.value} style={{ background: '#0a0e1a' }}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Filtres catégories */}
        <div style={{
          display: 'flex',
          gap: '8px',
          flexWrap: 'wrap',
          alignItems: 'center'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            color: '#71717a',
            fontSize: '11px',
            letterSpacing: '1px',
            textTransform: 'uppercase',
            fontWeight: 600,
            whiteSpace: 'nowrap'
          }}>
            <Filter style={{ width: '14px', height: '14px' }} />
            CAT:
          </div>
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              style={{
                padding: '8px 16px',
                background: selectedCategory === cat 
                  ? 'rgba(6, 182, 212, 0.2)' 
                  : 'rgba(0, 0, 0, 0.4)',
                border: `1px solid ${selectedCategory === cat ? '#06b6d4' : 'rgba(82, 82, 91, 0.3)'}`,
                borderRadius: '6px',
                color: selectedCategory === cat ? '#06b6d4' : '#a1a1aa',
                fontSize: '12px',
                fontWeight: 600,
                textTransform: 'uppercase',
                letterSpacing: '1px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                fontFamily: 'monospace'
              }}
              onMouseEnter={(e) => {
                if (selectedCategory !== cat) {
                  e.currentTarget.style.background = 'rgba(6, 182, 212, 0.05)';
                  e.currentTarget.style.borderColor = 'rgba(6, 182, 212, 0.3)';
                }
              }}
              onMouseLeave={(e) => {
                if (selectedCategory !== cat) {
                  e.currentTarget.style.background = 'rgba(0, 0, 0, 0.4)';
                  e.currentTarget.style.borderColor = 'rgba(82, 82, 91, 0.3)';
                }
              }}
            >
              {cat === "all" ? "TOUS" : cat.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* GRID - identique, juste le reste du code... */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(90px, 1fr))',
        gap: '8px',
        marginBottom: '48px'
      }}>
        {filteredMaterials.map((material) => (
          <MaterialCell
            key={material.id}
            material={material}
            isSelected={selectedMaterial?.id === material.id}
            onClick={() => router.push(`/market/${material.id}`)}
          />
        ))}
      </div>

      {filteredMaterials.length === 0 && (
        <div style={{
          textAlign: 'center',
          padding: '60px 20px',
          color: '#71717a',
          fontSize: '14px',
          letterSpacing: '2px'
        }}>
          AUCUN MATÉRIAU TROUVÉ
        </div>
      )}

      <style jsx>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}