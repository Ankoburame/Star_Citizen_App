"use client";

import { useState, useEffect } from "react";
import { TrendingUp, TrendingDown, Minus, Activity, MapPin, DollarSign, Package, Clock } from "lucide-react";

const API_URL = "http://127.0.0.1:8000";

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
  variation: number; // Simulé pour l'instant
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
    // Tendance vers la variation finale
    const noise = (Math.random() - 0.5) * 5;
    const trend = (variation / points) * i;
    current = baseValue + trend + noise;
    data.push(current);
  }
  
  return data;
}

// Composant pour mini-graphique stylisé Star Citizen
function MiniChart({ data, variation }: { data: number[]; variation: number }) {
  const width = 80;
  const height = 30;
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  
  // Générer le path SVG
  const points = data.map((value, i) => {
    const x = (i / (data.length - 1)) * width;
    const y = height - ((value - min) / range) * height;
    return `${x},${y}`;
  }).join(" ");
  
  const color = variation > 1 ? "#10b981" : variation < -1 ? "#ef4444" : "#71717a";
  const glowColor = variation > 1 ? "rgba(16, 185, 129, 0.5)" : variation < -1 ? "rgba(239, 68, 68, 0.5)" : "rgba(113, 113, 122, 0.3)";
  
  return (
    <svg width={width} height={height} style={{ display: 'block' }}>
      {/* Glow effect */}
      <defs>
        <filter id={`glow-${variation}`}>
          <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
        
        {/* Gradient fill */}
        <linearGradient id={`gradient-${variation}`} x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style={{ stopColor: color, stopOpacity: 0.3 }} />
          <stop offset="100%" style={{ stopColor: color, stopOpacity: 0 }} />
        </linearGradient>
      </defs>
      
      {/* Area fill */}
      <path
        d={`M 0,${height} L ${points} L ${width},${height} Z`}
        fill={`url(#gradient-${variation})`}
        opacity={0.4}
      />
      
      {/* Line */}
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="2"
        filter={`url(#glow-${variation})`}
        style={{ filter: `drop-shadow(0 0 4px ${glowColor})` }}
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
  let icon = <Minus style={{ width: '14px', height: '14px' }} />;
  
  if (variation > 1) {
    bgColor = "rgba(16, 185, 129, 0.05)";
    borderColor = "rgba(16, 185, 129, 0.3)";
    textColor = "#10b981";
    icon = <TrendingUp style={{ width: '14px', height: '14px' }} />;
  } else if (variation < -1) {
    bgColor = "rgba(239, 68, 68, 0.05)";
    borderColor = "rgba(239, 68, 68, 0.3)";
    textColor = "#ef4444";
    icon = <TrendingDown style={{ width: '14px', height: '14px' }} />;
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
        borderRadius: '6px',
        padding: '12px',
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        boxShadow: isSelected ? '0 0 20px rgba(6, 182, 212, 0.3)' : 'none'
      }}
      onClick={onClick}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '8px'
      }}>
        <div style={{
          fontSize: '16px',
          fontWeight: 700,
          color: 'white',
          fontFamily: 'monospace',
          letterSpacing: '1px'
        }}>
          {acronym}
        </div>
        <div style={{ color: textColor }}>
          {icon}
        </div>
      </div>
      
      {/* Mini chart */}
      <div style={{ marginBottom: '8px' }}>
        <MiniChart data={chartData} variation={variation} />
      </div>
      
      {/* Variation */}
      <div style={{
        fontSize: '13px',
        fontWeight: 600,
        color: textColor,
        fontFamily: 'monospace',
        textAlign: 'right'
      }}>
        {variation > 0 ? '+' : ''}{variation.toFixed(2)}%
      </div>
      
      {/* Tooltip */}
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
  const [materials, setMaterials] = useState<Material[]>([]);
  const [selectedMaterial, setSelectedMaterial] = useState<Material | null>(null);
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;

    async function loadMaterials() {
      try {
        const res = await fetch(`${API_URL}/market/materials`);
        const data = await res.json();
        
        // Ajouter des variations simulées
        const materialsWithVariation = data.map((m: any) => ({
          ...m,
          variation: (Math.random() - 0.5) * 10 // -5% à +5%
        }));
        
        setMaterials(materialsWithVariation);
        
        // Sélectionner un matériau aléatoire si aucun n'est sélectionné
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
    const timer = setInterval(loadMaterials, 30000); // Refresh toutes les 30s
    return () => clearInterval(timer);
  }, [mounted, selectedMaterial]);

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

  return (
    <div style={{ padding: '32px', maxWidth: '1800px' }}>
      {/* HEADER */}
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
              {materials.length} COMMODITÉS
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

      {/* GRID DE MATÉRIAUX */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(50px, 1fr))',
        gap: '12px',
        marginBottom: '48px'
      }}>
        {materials.map((material) => (
          <MaterialCell
            key={material.id}
            material={material}
            isSelected={selectedMaterial?.id === material.id}
            onClick={() => setSelectedMaterial(material)}
          />
        ))}
      </div>

      {/* ZONE D'ANALYSE */}
      {selectedMaterial && (
        <div style={{
          background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.03) 0%, rgba(0, 0, 0, 0.5) 100%)',
          border: '1px solid rgba(6, 182, 212, 0.2)',
          borderRadius: '12px',
          padding: '32px',
          position: 'relative',
          overflow: 'hidden'
        }}>
          {/* Glow corner */}
          <div style={{
            position: 'absolute',
            top: '-100px',
            right: '-100px',
            width: '200px',
            height: '200px',
            background: 'radial-gradient(circle, rgba(6, 182, 212, 0.15) 0%, transparent 70%)',
            pointerEvents: 'none'
          }} />

          {/* Header avec nom du matériau */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '32px',
            position: 'relative',
            zIndex: 1
          }}>
            <div>
              <h2 style={{
                fontSize: '32px',
                fontWeight: 700,
                color: 'white',
                letterSpacing: '3px',
                textTransform: 'uppercase',
                margin: 0,
                marginBottom: '8px'
              }}>
                {selectedMaterial.name}
              </h2>
              <div style={{
                fontSize: '13px',
                color: '#71717a',
                letterSpacing: '2px',
                textTransform: 'uppercase'
              }}>
                {selectedMaterial.category}
              </div>
            </div>
            
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '16px 24px',
              background: selectedMaterial.variation > 1 
                ? 'rgba(16, 185, 129, 0.1)' 
                : selectedMaterial.variation < -1 
                  ? 'rgba(239, 68, 68, 0.1)' 
                  : 'rgba(113, 113, 122, 0.1)',
              border: `2px solid ${
                selectedMaterial.variation > 1 
                  ? '#10b981' 
                  : selectedMaterial.variation < -1 
                    ? '#ef4444' 
                    : '#71717a'
              }`,
              borderRadius: '8px'
            }}>
              {selectedMaterial.variation > 1 ? (
                <TrendingUp style={{ width: '24px', height: '24px', color: '#10b981' }} />
              ) : selectedMaterial.variation < -1 ? (
                <TrendingDown style={{ width: '24px', height: '24px', color: '#ef4444' }} />
              ) : (
                <Minus style={{ width: '24px', height: '24px', color: '#71717a' }} />
              )}
              <div style={{
                fontSize: '28px',
                fontWeight: 700,
                color: selectedMaterial.variation > 1 
                  ? '#10b981' 
                  : selectedMaterial.variation < -1 
                    ? '#ef4444' 
                    : '#71717a',
                fontFamily: 'monospace'
              }}>
                {selectedMaterial.variation > 0 ? '+' : ''}{selectedMaterial.variation.toFixed(2)}%
              </div>
            </div>
          </div>

          {/* Graphique principal */}
          <div style={{
            background: 'rgba(0, 0, 0, 0.4)',
            border: '1px solid rgba(6, 182, 212, 0.2)',
            borderRadius: '8px',
            padding: '24px',
            marginBottom: '32px',
            height: '200px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative',
            zIndex: 1
          }}>
            <svg width="100%" height="180" style={{ display: 'block' }}>
              <defs>
                <linearGradient id="mainGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" style={{ 
                    stopColor: selectedMaterial.variation > 1 ? '#10b981' : selectedMaterial.variation < -1 ? '#ef4444' : '#06b6d4', 
                    stopOpacity: 0.4 
                  }} />
                  <stop offset="100%" style={{ 
                    stopColor: selectedMaterial.variation > 1 ? '#10b981' : selectedMaterial.variation < -1 ? '#ef4444' : '#06b6d4', 
                    stopOpacity: 0 
                  }} />
                </linearGradient>
              </defs>
              
              {/* Grid lines */}
              {[0, 1, 2, 3, 4].map(i => (
                <line
                  key={i}
                  x1="0"
                  y1={i * 45}
                  x2="100%"
                  y2={i * 45}
                  stroke="rgba(6, 182, 212, 0.1)"
                  strokeWidth="1"
                  strokeDasharray="4 4"
                />
              ))}
              
              {(() => {
                const max = Math.max(...largeChartData);
                const min = Math.min(...largeChartData);
                const range = max - min || 1;
                const width = 1600; // Approximation
                
                const points = largeChartData.map((value, i) => {
                  const x = (i / (largeChartData.length - 1)) * width;
                  const y = 180 - ((value - min) / range) * 160;
                  return `${x},${y}`;
                }).join(" ");
                
                const color = selectedMaterial.variation > 1 ? '#10b981' : selectedMaterial.variation < -1 ? '#ef4444' : '#06b6d4';
                
                return (
                  <>
                    {/* Area fill */}
                    <path
                      d={`M 0,180 L ${points} L ${width},180 Z`}
                      fill="url(#mainGradient)"
                    />
                    
                    {/* Line */}
                    <polyline
                      points={points}
                      fill="none"
                      stroke={color}
                      strokeWidth="3"
                      style={{ filter: `drop-shadow(0 0 8px ${color})` }}
                    />
                  </>
                );
              })()}
            </svg>
          </div>

          {/* Informations détaillées */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '24px',
            position: 'relative',
            zIndex: 1
          }}>
            {/* Prix d'achat le plus bas */}
            <div style={{
              background: 'rgba(239, 68, 68, 0.05)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: '8px',
              padding: '24px'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                marginBottom: '16px'
              }}>
                <DollarSign style={{ width: '20px', height: '20px', color: '#ef4444' }} />
                <div style={{
                  fontSize: '12px',
                  color: '#71717a',
                  letterSpacing: '2px',
                  textTransform: 'uppercase',
                  fontWeight: 600
                }}>
                  MEILLEUR PRIX D'ACHAT
                </div>
              </div>
              
              {selectedMaterial.min_buy_price ? (
                <>
                  <div style={{
                    fontSize: '36px',
                    fontWeight: 700,
                    color: '#ef4444',
                    fontFamily: 'monospace',
                    marginBottom: '12px',
                    textShadow: '0 0 20px rgba(239, 68, 68, 0.5)'
                  }}>
                    {selectedMaterial.min_buy_price.toLocaleString()}
                    <span style={{ fontSize: '16px', marginLeft: '8px', color: '#71717a' }}>
                      aUEC
                    </span>
                  </div>
                  
                  {selectedMaterial.best_buy_location && (
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      fontSize: '13px',
                      color: '#a1a1aa'
                    }}>
                      <MapPin style={{ width: '14px', height: '14px' }} />
                      <div>
                        <div style={{ fontWeight: 600, color: 'white' }}>
                          {selectedMaterial.best_buy_location.name}
                        </div>
                        <div style={{ fontSize: '11px', color: '#52525b', fontFamily: 'monospace' }}>
                          {selectedMaterial.best_buy_location.full_path}
                        </div>
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div style={{
                  fontSize: '24px',
                  fontWeight: 700,
                  color: '#3f3f46',
                  fontFamily: 'monospace'
                }}>
                  - -
                </div>
              )}
            </div>

            {/* Prix de vente le plus haut */}
            <div style={{
              background: 'rgba(16, 185, 129, 0.05)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              borderRadius: '8px',
              padding: '24px'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                marginBottom: '16px'
              }}>
                <DollarSign style={{ width: '20px', height: '20px', color: '#10b981' }} />
                <div style={{
                  fontSize: '12px',
                  color: '#71717a',
                  letterSpacing: '2px',
                  textTransform: 'uppercase',
                  fontWeight: 600
                }}>
                  MEILLEUR PRIX DE VENTE
                </div>
              </div>
              
              {selectedMaterial.max_sell_price ? (
                <>
                  <div style={{
                    fontSize: '36px',
                    fontWeight: 700,
                    color: '#10b981',
                    fontFamily: 'monospace',
                    marginBottom: '12px',
                    textShadow: '0 0 20px rgba(16, 185, 129, 0.5)'
                  }}>
                    {selectedMaterial.max_sell_price.toLocaleString()}
                    <span style={{ fontSize: '16px', marginLeft: '8px', color: '#71717a' }}>
                      aUEC
                    </span>
                  </div>
                  
                  {selectedMaterial.best_sell_location && (
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      fontSize: '13px',
                      color: '#a1a1aa'
                    }}>
                      <MapPin style={{ width: '14px', height: '14px' }} />
                      <div>
                        <div style={{ fontWeight: 600, color: 'white' }}>
                          {selectedMaterial.best_sell_location.name}
                        </div>
                        <div style={{ fontSize: '11px', color: '#52525b', fontFamily: 'monospace' }}>
                          {selectedMaterial.best_sell_location.full_path}
                        </div>
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div style={{
                  fontSize: '24px',
                  fontWeight: 700,
                  color: '#3f3f46',
                  fontFamily: 'monospace'
                }}>
                  - -
                </div>
              )}
            </div>
          </div>
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