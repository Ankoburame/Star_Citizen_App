"""
Trade service for Star Citizen App.
Handles trade run simulations and profit calculations.
"""

from typing import Dict, Any


def create_trade_run(
    material_id: int,
    quantity: int,
    buy_price: float,
    sell_price: float,
    buy_location: str,
    sell_location: str,
) -> Dict[str, Any]:
    """
    Simulate a trade run and calculate profit/loss.
    
    This function performs a simulation without affecting actual stock
    or creating database records. It calculates costs, revenue, and profit
    for planning purposes.
    
    Args:
        material_id: ID of the material being traded
        quantity: Quantity to trade
        buy_price: Purchase price per unit
        sell_price: Selling price per unit
        buy_location: Purchase location name
        sell_location: Selling location name
        
    Returns:
        Dictionary containing:
            - material_id: Material ID
            - quantity: Trade quantity
            - buy_location: Purchase location
            - sell_location: Selling location
            - buy_price: Unit purchase price
            - sell_price: Unit selling price
            - total_cost: Total purchase cost
            - total_revenue: Total sales revenue
            - profit: Net profit (revenue - cost)
            - profit_margin: Profit margin percentage
    """
    total_cost = buy_price * quantity
    total_revenue = sell_price * quantity
    profit = total_revenue - total_cost
    profit_margin = (profit / total_cost * 100) if total_cost > 0 else 0
    
    return {
        "material_id": material_id,
        "quantity": quantity,
        "buy_location": buy_location,
        "sell_location": sell_location,
        "buy_price": buy_price,
        "sell_price": sell_price,
        "total_cost": total_cost,
        "total_revenue": total_revenue,
        "profit": profit,
        "profit_margin": round(profit_margin, 2),
    }