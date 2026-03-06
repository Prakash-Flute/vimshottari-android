from flask import render_template, request
from apps.dasha_logic import calculate_dasha

def vimshottari():
    form_data = {}
    if request.method == "POST":
        try:
            lat = float(request.form["lat"])
            lon = float(request.form["lon"])
            tz = float(request.form["tz"])
            
            if not (-90 <= lat <= 90): raise ValueError(f"Latitude {lat} invalid")
            if not (-180 <= lon <= 180): raise ValueError(f"Longitude {lon} invalid")
            if not (-12 <= tz <= 14): raise ValueError(f"Timezone {tz} invalid")
            
            result = calculate_dasha(request.form["dob"], request.form["tob"], lat, lon, tz, request.form["target"])
            form_data = request.form
            return render_template('VIMSHOTTARI/vimshottari.html', result=result, error=None, form_data=form_data)
        except Exception as e:
            form_data = request.form
            return render_template('VIMSHOTTARI/vimshottari.html', result=None, error=str(e), form_data=form_data)
    return render_template('VIMSHOTTARI/vimshottari.html', result=None, error=None, form_data={})
