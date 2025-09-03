import os
import glob
import math
import numpy as np
import pandas as pd

MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December']
SEASONS = {
    'Summer':   ['December','January','February'],
    'Autumn':   ['March','April','May'],
    'Winter':   ['June','July','August'],
    'Spring':   ['September','October','November'],
}

def _canonicalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Strip whitespace and normalize common column names
    df = df.rename(columns={c: c.strip() for c in df.columns})

    # Station name / ID normalization
    name_candidates = ['STATION_NAME','Station_Name','Station','NAME','name']
    id_candidates   = ['STN_ID','Station_ID','ID','id']

    if not any(c in df.columns for c in name_candidates):
        df['STATION_NAME'] = 'UNKNOWN'
    else:
        for c in name_candidates:
            if c in df.columns and c != 'STATION_NAME':
                df = df.rename(columns={c:'STATION_NAME'})
                break

    if not any(c in df.columns for c in id_candidates):
        df['STN_ID'] = np.nan
    else:
        for c in id_candidates:
            if c in df.columns and c != 'STN_ID':
                df = df.rename(columns={c:'STN_ID'})
                break

    # Ensure month columns are numeric (coerce errors to NaN)
    present = [m for m in MONTHS if m in df.columns]
    for m in present:
        df[m] = pd.to_numeric(df[m], errors='coerce')

    return df[['STATION_NAME','STN_ID'] + present]

def load_all_csvs(folder: str) -> pd.DataFrame:
    paths = sorted(glob.glob(os.path.join(folder, '*.csv')))
    if not paths:
        raise FileNotFoundError(f'No .csv files found in folder: {folder}')
    frames = []
    for p in paths:
        df = pd.read_csv(p)
        frames.append(_canonicalize_columns(df))
    return pd.concat(frames, ignore_index=True)

def compute_seasonal_averages(df: pd.DataFrame) -> dict:
    out = {}
    for season, months in SEASONS.items():
        ms = [m for m in months if m in df.columns]
        if not ms:
            out[season] = float('nan')
            continue
        # Flatten all month values across all stations/years & ignore NaN
        vals = df[ms].to_numpy().astype(float).ravel()
        out[season] = float(np.nanmean(vals))
    return out

def melt_long(df: pd.DataFrame) -> pd.DataFrame:
    present = [m for m in MONTHS if m in df.columns]
    long_df = df.melt(id_vars=['STATION_NAME','STN_ID'],
                      value_vars=present,
                      var_name='Month', value_name='Temp')
    return long_df.dropna(subset=['Temp'])

def compute_station_stats(long_df: pd.DataFrame) -> pd.DataFrame:
    # Per-station min, max, std (NaN-safe because we dropped NaNs)
    grp = long_df.groupby('STATION_NAME')['Temp']
    stats = grp.agg(['min','max','std']).rename(columns={'std':'stddev'}).reset_index()
    stats['range'] = stats['max'] - stats['min']
    return stats

def save_seasonal_averages(averages: dict, out_path: str):
    order = ['Summer','Autumn','Winter','Spring']
    with open(out_path, 'w', encoding='utf-8', newline='') as f:
        for s in order:
            val = averages.get(s, float('nan'))
            line = f'{s}: {val:.1f}°C' if not math.isnan(val) else f'{s}: N/A'
            f.write(line + '\n')

def save_largest_temp_range(stats: pd.DataFrame, out_path: str):
    max_range = stats['range'].max()
    winners = stats[np.isclose(stats['range'], max_range)]
    with open(out_path, 'w', encoding='utf-8', newline='') as f:
        for _, row in winners.sort_values('STATION_NAME').iterrows():
            f.write(f"{row['STATION_NAME']}: Range {row['range']:.1f}°C (Max: {row['max']:.1f}°C, Min: {row['min']:.1f}°C)\n")

def save_temperature_stability(stats: pd.DataFrame, out_path: str):
    stats2 = stats.dropna(subset=['stddev']).copy()
    min_std = stats2['stddev'].min()
    max_std = stats2['stddev'].max()
    stable_names   = stats2[np.isclose(stats2['stddev'], min_std)]['STATION_NAME'].sort_values().tolist()
    variable_names = stats2[np.isclose(stats2['stddev'], max_std)]['STATION_NAME'].sort_values().tolist()

    with open(out_path, 'w', encoding='utf-8', newline='') as f:
        if stable_names:
            if len(stable_names) == 1:
                f.write(f"Most Stable: {stable_names[0]}: StdDev {min_std:.1f}°C\n")
            else:
                f.write(f"Most Stable (StdDev {min_std:.1f}°C): " + ", ".join(stable_names) + "\n")
        else:
            f.write("Most Stable: N/A\n")

        if variable_names:
            if len(variable_names) == 1:
                f.write(f"Most Variable: {variable_names[0]}: StdDev {max_std:.1f}°C\n")
            else:
                f.write(f"Most Variable (StdDev {max_std:.1f}°C): " + ", ".join(variable_names) + "\n")
        else:
            f.write("Most Variable: N/A\n")

def main():
    folder = "temperature_data"  # Put all yearly CSVs here
    df = load_all_csvs(folder)

    # 1) Seasonal averages across all stations & years
    avg_by_season = compute_seasonal_averages(df)
    save_seasonal_averages(avg_by_season, "average_temp.txt")

    # 2) Largest temperature range per station (across entire history)
    long_df = melt_long(df)
    stats = compute_station_stats(long_df)
    save_largest_temp_range(stats, "largest_temp_range_station.txt")

    # 3) Temperature stability (std dev) – most stable & most variable stations
    save_temperature_stability(stats, "temperature_stability_stations.txt")

    print("Done. Wrote average_temp.txt, largest_temp_range_station.txt, temperature_stability_stations.txt")

if __name__ == "__main__":
    main()
