from flask import jsonify, request
from datetime import timedelta
import swisseph as swe
from apps.calculations import get_live_planetary_positions, calculate_all_planets
from apps.chakras import calculate_chakras
from apps.utils import parse_flexible_datetime

def api_live_planets():
    try:
        lat = request.args.get('lat', 28.6139, type=float)
        lon = request.args.get('lon', 77.2090, type=float) 
        tz = request.args.get('tz', 5.5, type=float)
        live_data = get_live_planetary_positions(lat, lon, tz)
        return jsonify({'success': True, 'timestamp': live_data.get('timestamp', ''), 'planets': live_data.get('planets', {})})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def calculate_chakras_api():
    try:
        data = request.get_json()
        time_type = data.get('time_type', 'birth')
        lat = float(data.get('lat', 28.6139))
        lon = float(data.get('lon', 77.2090))
        tz = float(data.get('tz', 5.5))
        
        if time_type == 'live':
            live_data = get_live_planetary_positions(lat, lon, tz)
            chakras = calculate_chakras(live_data['planets'])
        else:
            date = data.get('date')
            time = data.get('time', '12:00:00')
            dt = parse_flexible_datetime(date, time)
            dt_utc = dt - timedelta(hours=tz)
            jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600)
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            planets = calculate_all_planets(jd, lat, lon)
            chakras = calculate_chakras(planets)
        
        return jsonify({
            'success': True,
            'sapt_nadi': chakras['sapt_nadi'],
            'mandal': chakras['mandal'],
            'duar': chakras['duar'],
            'planets': chakras['planets']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def receive_gps():
    try:
        data = request.get_json()
        lat = float(data.get('lat', 0))
        lon = float(data.get('lon', 0))
        acc = float(data.get('accuracy', 999))
        return jsonify({
            'success': True,
            'latitude': lat,
            'longitude': lon,
            'accuracy_meters': acc,
            'precision_level': 'EXCELLENT' if acc < 10 else 'GOOD' if acc < 50 else 'FAIR',
            'message': f'GPS locked: {lat:.6f}, {lon:.6f}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
