"""
build_specs_lookup.py
=====================
Builds an aggregated vehicle specifications lookup table (car_specs.json)
nested by brand → model from car_resale_prices.csv.

Output structure:
{
  "Maruti": {
    "Swift": {
      "engine": 1197, "power": 83, "mileage": 22.4,
      "body": "Hatchback", "fuel": "Petrol", "trans": "Manual",
      "seats": 5, "sample_count": 681
    },
    ...
  },
  "Hyundai": { ... },
  ...
}

Computes per (brand, model) group:
- median engine_capacity
- median max_power
- median mileage
- mode body_type
- mode fuel_type
- mode transmission_type
- mode seats
- sample_count (number of listings)

Usage:
    python build_specs_lookup.py
"""

import json
import re
from pathlib import Path
import pandas as pd
import numpy as np

from preprocess import (
    load_raw, parse_engine_capacity, parse_max_power, parse_mileage
)

ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "car_resale_prices.csv"
OUTPUT_PATH = ROOT / "models" / "car_specs.json"


def extract_brand_model(name: str):
    """Clean full_name into brand and model."""
    s = re.sub(r'^\d{4}\s+', '', str(name).strip())
    parts = s.split()
    if not parts:
        return 'Other', 'Other'
    
    brand = parts[0]
    if len(parts) >= 2:
        if parts[0].lower() in ['land', 'aston', 'alfa'] and len(parts) >= 3:
            brand = f'{parts[0]} {parts[1]}'
            model = parts[2]
        elif parts[0].lower() == 'maruti' and parts[1].lower() == 'suzuki':
            brand = 'Maruti'
            model = parts[2] if len(parts) >= 3 else parts[1]
        elif parts[0].lower() == 'mercedes-benz':
            brand = 'Mercedes-Benz'
            model = parts[1]
        else:
            brand = parts[0]
            if len(parts) >= 3 and parts[1].lower() in [
                'wagon', 'grand', 'swift', 'alto', 's', 'eeco', 'baleno', 
                'corolla', 'innova', 'safari', 'harrier', 'xuv', 'scorpio', 
                'creta', 'venue', 'nexon', 'punch', 'compass', 'seltos', 
                'sonet', 'kwid', 'i20', 'i10', 'city', 'amaze', 'thar', 
                'fortuner', 'brezza', 'carens', 'tiago', 'tigor', 'altroz',
                'taigun', 'kushaq', 'slavia', 'virtus'
            ]:
                if parts[1].lower() == 'wagon' and parts[2].lower() == 'r':
                    model = 'Wagon R'
                elif parts[1].lower() == 'grand' and parts[2].lower().startswith('i'):
                    model = f'Grand {parts[2]}'
                elif parts[1].lower() == 'swift' and parts[2].lower() == 'dzire':
                    model = 'Swift Dzire'
                elif parts[1].lower() == 'alto' and parts[2].lower() in ['k10', '800']:
                    model = f'Alto {parts[2]}'
                elif parts[1].lower() == 'corolla' and parts[2].lower() == 'altis':
                    model = 'Corolla Altis'
                elif parts[1].lower() == 'innova' and parts[2].lower() in ['crysta', 'hycross']:
                    model = f'Innova {parts[2]}' 
                elif parts[1].lower() == 'scorpio' and parts[2].lower() in ['n', 'classic']:
                    model = f'Scorpio {parts[2]}'
                elif parts[1].lower() == 'xuv' and parts[2].lower() in ['700', '300', '500', '3xo', '400']:
                    model = f'XUV{parts[2]}'
                else:
                    model = parts[1]
            else:
                model = parts[1]
    else:
        model = parts[0]

    # Standardize casing
    brand = brand.strip().capitalize()
    if brand.lower() == 'mercedes-benz':
        brand = 'Mercedes-Benz'
    elif brand.lower() == 'bmw':
        brand = 'BMW'
    elif brand.lower() == 'mg':
        brand = 'MG'
    return brand, model.strip()


def build_specs_lookup(save_path: Path = OUTPUT_PATH) -> dict:
    print("[INFO] Loading raw data for specs lookup table...")
    df = load_raw(DATA_PATH)

    df['engine_clean'] = parse_engine_capacity(df['engine_capacity'])
    df['power_clean'] = parse_max_power(df['max_power'])
    df['mileage_clean'] = parse_mileage(df['mileage'])
    df['seats_clean'] = pd.to_numeric(df['seats'], errors='coerce')

    df['body_type'] = df['body_type'].astype(str).str.strip()
    df['fuel_type'] = df['fuel_type'].astype(str).str.strip()
    df['transmission_type'] = df['transmission_type'].astype(str).str.strip()

    bm = df['full_name'].apply(extract_brand_model)
    df['brand'] = [b for b, m in bm]
    df['model'] = [m for b, m in bm]

    overall_engine_med = int(round(df['engine_clean'].median())) if not pd.isna(df['engine_clean'].median()) else 1200
    overall_power_med = int(round(df['power_clean'].median())) if not pd.isna(df['power_clean'].median()) else 85
    overall_mileage_med = round(float(df['mileage_clean'].median()), 1) if not pd.isna(df['mileage_clean'].median()) else 18.0
    overall_seats_med = int(round(df['seats_clean'].median())) if not pd.isna(df['seats_clean'].median()) else 5

    # Build nested brand → model dict
    nested: dict = {}
    for (brand_val, model_val), grp in df.groupby(['brand', 'model']):
        if len(grp) < 1:
            continue
        
        engine = grp['engine_clean'].median()
        engine_val = int(round(engine)) if not pd.isna(engine) and engine > 0 else overall_engine_med
        
        power = grp['power_clean'].median()
        power_val = int(round(power)) if not pd.isna(power) and power > 0 else overall_power_med
        
        mileage = grp['mileage_clean'].median()
        mileage_val = round(float(mileage), 1) if not pd.isna(mileage) and mileage > 0 else overall_mileage_med
        
        seats = grp['seats_clean'].dropna()
        if len(seats) > 0:
            seats_mode = seats.mode()
            seat_val = int(seats_mode.iloc[0]) if len(seats_mode) > 0 else overall_seats_med
        else:
            seat_val = overall_seats_med
        
        body = grp['body_type'].dropna()
        body_val = str(body.mode().iloc[0]) if len(body) > 0 and body.mode().iloc[0] != 'nan' else 'Sedan'
        
        fuel = grp['fuel_type'].dropna()
        fuel_val = str(fuel.mode().iloc[0]) if len(fuel) > 0 and fuel.mode().iloc[0] != 'nan' else 'Petrol'
        
        trans = grp['transmission_type'].dropna()
        trans_val = str(trans.mode().iloc[0]) if len(trans) > 0 and trans.mode().iloc[0] != 'nan' else 'Manual'

        if brand_val not in nested:
            nested[brand_val] = {}
        
        nested[brand_val][model_val] = {
            'engine': engine_val,
            'power': power_val,
            'mileage': mileage_val,
            'body': body_val,
            'fuel': fuel_val,
            'trans': trans_val,
            'seats': seat_val,
            'sample_count': int(len(grp))
        }

    # Sort brands alphabetically; sort each brand's models by sample_count desc
    sorted_nested = {}
    for brand_key in sorted(nested.keys()):
        sorted_nested[brand_key] = dict(
            sorted(nested[brand_key].items(), key=lambda x: -x[1]['sample_count'])
        )

    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(sorted_nested, f, indent=2, ensure_ascii=False)

    total_models = sum(len(models) for models in sorted_nested.values())
    print(f"[SUCCESS] Built nested specs lookup: {len(sorted_nested)} brands, {total_models} models → {save_path}")
    return sorted_nested


if __name__ == "__main__":
    build_specs_lookup()
