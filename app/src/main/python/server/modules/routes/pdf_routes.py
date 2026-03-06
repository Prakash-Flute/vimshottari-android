from flask import send_file, request
from io import BytesIO
from apps.dasha_logic import calculate_dasha
from apps.pdf_generator import generate_pdf_report

def download_full_cycle_pdf():
    try:
        dob = request.form["dob"]
        tob = request.form["tob"]
        lat = float(request.form["lat"])
        lon = float(request.form["lon"])
        tz = float(request.form["tz"])
        target = request.form["target"]
        cycle_offset = int(request.form.get("cycle_offset", 0))
        
        result = calculate_dasha(dob, tob, lat, lon, tz, target)
        pdf_bytes = generate_pdf_report(result, mode='full_cycle', cycle_offset=cycle_offset)
        
        pdf_stream = BytesIO(pdf_bytes)
        pdf_stream.seek(0)
        
        if cycle_offset == 0: 
            download_name = f'Vimshottari_Full_{dob}.pdf'
        else: 
            download_name = f'Vimshottari_Cycle_{cycle_offset}_{dob}.pdf'
        
        return send_file(
            pdf_stream, 
            as_attachment=True, 
            download_name=download_name, 
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return f"Error: {str(e)}", 500
