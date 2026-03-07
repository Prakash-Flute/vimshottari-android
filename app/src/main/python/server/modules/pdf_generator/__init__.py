from datetime import datetime, timedelta
from fpdf import FPDF
from io import BytesIO
from apps.config import DASHA_YEARS, SECONDS_IN_YEAR, TOTAL_VIMSHOTTARI, CYCLE_SECONDS
from apps.utils import get_dasha_sequence, calculate_sub_period_duration

def generate_pdf_report(data, mode='full_cycle', cycle_offset=0):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    bg_color = (255, 248, 220)
    header_bg = (139, 0, 0)
    border_color = (184, 134, 11)
    text_color = (0, 0, 0)
    title_color = (139, 0, 0)
    white = (255, 255, 255)
    
    def add_page_background():
        pdf.set_fill_color(*bg_color)
        pdf.rect(0, 0, 210, 297, 'F')
    
    md_start = datetime.strptime(data['md_start_date'], "%d-%b-%Y %H:%M:%S")
    
    if cycle_offset > 0:
        offset_seconds = cycle_offset * CYCLE_SECONDS
        md_start = md_start + timedelta(seconds=offset_seconds)
    
    start_lord = data['nak_lord']
    
    index_data = []
    current_page = 4
    planets = get_dasha_sequence()
    start_idx = planets.index(start_lord)
    
    for i in range(9):
        md_lord = planets[(start_idx + i) % 9]
        md_years = DASHA_YEARS[md_lord]
        index_data.append({'lord': md_lord, 'years': md_years, 'page': current_page})
        current_page += 1
    
    # Page 1: Cover
    pdf.add_page()
    add_page_background()
    pdf.set_draw_color(*border_color)
    pdf.set_line_width(2)
    pdf.rect(10, 10, 190, 277, 'D')
    
    pdf.set_font('Arial', 'B', 24)
    pdf.set_text_color(*title_color)
    pdf.set_xy(0, 40)
    
    if cycle_offset > 0:
        pdf.cell(210, 15, f'VIMSHOTTARI DASHA REPORT - CYCLE {cycle_offset}', 0, 1, 'C')
    else:
        pdf.cell(210, 15, 'VIMSHOTTARI DASHA REPORT', 0, 1, 'C')
    
    pdf.set_font('Arial', 'I', 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(210, 10, f'Generated: {datetime.now().strftime("%d-%b-%Y %H:%M:%S")}', 0, 1, 'C')
    pdf.line(30, 80, 180, 80)
    
    pdf.set_xy(20, 100)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(*border_color)
    pdf.rect(20, 100, 170, 80, 'FD')
    
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(*title_color)
    pdf.set_xy(20, 110)
    pdf.cell(170, 10, 'BIRTH DETAILS', 0, 1, 'C')
    
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(*text_color)
    
    details = [
        ['Date of Birth', data['birth_time']], ['Latitude / Longitude', f"{data['birth_lat']}°N / {data['birth_lon']}°E"],
        ['Timezone', f"UTC {data['birth_tz']:+}"], ['Moon Position', f"{data['moon_sign']} {data['moon_dms']}"],
        ['Sidereal Longitude', f"{data['moon_sid']}°"], ['Nakshatra', f"{data['nak_name']} (#{data['nak_num']})"],
        ['Pada', f"{data['nak_pada']}/4"], ['Nakshatra Lord', data['nak_lord']]
    ]
    
    y_pos = 125
    for label, value in details:
        pdf.set_xy(30, y_pos)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(50, 6, label + ':', 0, 0, 'L')
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, value, 0, 1, 'L')
        y_pos += 7
    
    pdf.set_y(-30)
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, 'Page 1', 0, 0, 'C')
    
    # Page 2: Target Report
    if cycle_offset == 0 and 'day_details' in data and 'error' not in data.get('day_details', {}):
        pdf.add_page()
        add_page_background()
        pdf.set_fill_color(*header_bg)
        pdf.rect(0, 0, 210, 20, 'F')
        pdf.set_font('Arial', 'B', 16)
        pdf.set_text_color(*white)
        pdf.set_xy(0, 6)
        pdf.cell(210, 8, f'TARGET DATE REPORT: {data["day_details"]["target_date"]}', 0, 1, 'C')
        pdf.ln(5)
        
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(*border_color)
        pdf.rect(20, 30, 170, 45, 'FD')
        
        pdf.set_font('Arial', 'B', 11)
        pdf.set_text_color(*title_color)
        pdf.set_xy(25, 35)
        pdf.cell(0, 6, 'CURRENT MAJOR PERIODS', 0, 1, 'L')
        
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(*text_color)
        
        summaries = [
            ['Mahadasha (MD)', data['day_details']['md_lord'], data['day_details']['md_end']],
            ['Antardasha (AD)', data['day_details']['ad_lord'], data['day_details']['ad_end']],
            ['Pratyantar (PD)', data['day_details']['pd_lord'], data['day_details']['pd_end']],
            ['Sookshma (SD)', data['day_details']['sd_lord'], data['day_details']['sd_end']]
        ]
        
        y = 45
        for level, lord, end in summaries:
            pdf.set_xy(25, y)
            pdf.cell(40, 6, level + ':', 0, 0, 'L')
            pdf.cell(40, 6, lord, 0, 0, 'L')
            pdf.cell(0, 6, f'Ends: {end}', 0, 1, 'L')
            y += 7
        
        pdf.ln(10)
        pdf.set_fill_color(*header_bg)
        pdf.set_text_color(*white)
        pdf.set_font('Arial', 'B', 10)
        pdf.set_x(15)
        pdf.cell(25, 8, 'MD', 1, 0, 'C', True)
        pdf.cell(25, 8, 'AD', 1, 0, 'C', True)
        pdf.cell(25, 8, 'PD', 1, 0, 'C', True)
        pdf.cell(25, 8, 'SD', 1, 0, 'C', True)
        pdf.cell(25, 8, 'PR', 1, 0, 'C', True)
        pdf.cell(55, 8, 'End Date & Time', 1, 1, 'C', True)
        
        pdf.set_font('Arial', '', 9)
        for idx, period in enumerate(data['day_details']['periods']):
            pdf.set_x(15)
            if idx % 2 == 0: pdf.set_fill_color(255, 255, 255)
            else: pdf.set_fill_color(245, 245, 245)
            
            pdf.set_text_color(*text_color)
            pdf.cell(25, 6, period['md'], 1, 0, 'C', True)
            pdf.cell(25, 6, period['ad'], 1, 0, 'C', True)
            pdf.cell(25, 6, period['pd'], 1, 0, 'C', True)
            pdf.cell(25, 6, period['sd'], 1, 0, 'C', True)
            pdf.set_text_color(*title_color)
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(25, 6, period['pr'], 1, 0, 'C', True)
            pdf.set_text_color(*text_color)
            pdf.set_font('Arial', '', 9)
            pdf.cell(55, 6, f"{period['end_date']} {period['end_time']}", 1, 1, 'C', True)
        
        pdf.set_y(-15)
        pdf.set_font('Arial', 'I', 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 10, 'Page 2', 0, 0, 'C')
    
    # Page 3: Index
    pdf.add_page()
    add_page_background()
    pdf.set_fill_color(*header_bg)
    pdf.rect(0, 0, 210, 15, 'F')
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(*white)
    pdf.set_xy(0, 4)
    pdf.cell(210, 8, 'INDEX - MAHADASHA NAVIGATION', 0, 1, 'C')
    pdf.ln(10)
    
    pdf.set_fill_color(*header_bg)
    pdf.set_text_color(*white)
    pdf.set_font('Arial', 'B', 11)
    pdf.set_x(20)
    pdf.cell(60, 8, 'Mahadasha', 1, 0, 'C', True)
    pdf.cell(40, 8, 'Duration', 1, 0, 'C', True)
    pdf.cell(40, 8, 'Years', 1, 0, 'C', True)
    pdf.cell(40, 8, 'Page No.', 1, 1, 'C', True)
    
    pdf.set_font('Arial', '', 10)
    for item in index_data:
        pdf.set_x(20)
        pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(*text_color)
        pdf.cell(60, 7, item['lord'], 1, 0, 'C', True)
        pdf.cell(40, 7, f"{item['years']} Years", 1, 0, 'C', True)
        pdf.cell(40, 7, str(item['years']), 1, 0, 'C', True)
        pdf.set_text_color(*title_color)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(40, 7, str(item['page']), 1, 1, 'C', True)
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(*text_color)
    
    pdf.set_y(-15)
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, 'Page 3', 0, 0, 'C')
    
    # Pages 4-12: Mahadasha
    for i in range(9):
        md_lord = planets[(start_idx + i) % 9]
        md_years = DASHA_YEARS[md_lord]
        md_duration = md_years * SECONDS_IN_YEAR
        md_end = md_start + timedelta(seconds=md_duration)
        
        pdf.add_page()
        add_page_background()
        pdf.set_fill_color(*header_bg)
        pdf.rect(0, 0, 210, 18, 'F')
        pdf.set_font('Arial', 'B', 16)
        pdf.set_text_color(*white)
        pdf.set_xy(0, 5)
        pdf.cell(210, 8, f'{md_lord.upper()} MAHADASHA', 0, 1, 'C')
        pdf.set_font('Arial', '', 10)
        pdf.cell(210, 5, f'{md_start.strftime("%d-%b-%Y %H:%M:%S")} to {md_end.strftime("%d-%b-%Y %H:%M:%S")}', 0, 1, 'C')
        pdf.ln(3)
        
        pdf.set_fill_color(*header_bg)
        pdf.set_text_color(*white)
        pdf.set_font('Arial', 'B', 9)
        pdf.set_x(10)
        pdf.cell(28, 7, 'Antardasha', 1, 0, 'C', True)
        pdf.cell(28, 7, 'Pratyantar', 1, 0, 'C', True)
        pdf.cell(28, 7, 'Sookshma', 1, 0, 'C', True)
        pdf.cell(28, 7, 'Prana', 1, 0, 'C', True)
        pdf.cell(78, 7, 'End Date & Time', 1, 1, 'C', True)
        
        ad_start = md_start
        row_count = 0
        pdf.set_font('Arial', '', 8)
        
        for j in range(9):
            ad_lord = planets[(planets.index(md_lord) + j) % 9]
            ad_duration = calculate_sub_period_duration(md_duration, ad_lord)
            pd_start = ad_start
            
            for k in range(9):
                pd_lord = planets[(planets.index(ad_lord) + k) % 9]
                pd_duration = calculate_sub_period_duration(ad_duration, pd_lord)
                sd_start = pd_start
                
                for l in range(9):
                    sd_lord = planets[(planets.index(pd_lord) + l) % 9]
                    sd_duration = calculate_sub_period_duration(pd_duration, sd_lord)
                    pr_start = sd_start
                    
                    for m in range(9):
                        pr_lord = planets[(planets.index(sd_lord) + m) % 9]
                        pr_duration = calculate_sub_period_duration(sd_duration, pr_lord)
                        pr_end = pr_start + timedelta(seconds=pr_duration)
                        
                        pdf.set_x(10)
                        if row_count % 2 == 0: pdf.set_fill_color(255, 255, 255)
                        else: pdf.set_fill_color(245, 245, 245)
                        
                        pdf.set_text_color(*text_color)
                        pdf.cell(28, 5, ad_lord, 1, 0, 'C', True)
                        pdf.cell(28, 5, pd_lord, 1, 0, 'C', True)
                        pdf.cell(28, 5, sd_lord, 1, 0, 'C', True)
                        pdf.set_text_color(*title_color)
                        pdf.cell(28, 5, pr_lord, 1, 0, 'C', True)
                        pdf.set_text_color(*text_color)
                        pdf.cell(78, 5, pr_end.strftime("%d-%b-%Y %H:%M:%S"), 1, 1, 'C', True)
                        
                        row_count += 1
                        pr_start = pr_start + timedelta(seconds=pr_duration)
                    
                    sd_start = sd_start + timedelta(seconds=sd_duration)
                pd_start = pd_start + timedelta(seconds=pd_duration)
            ad_start = ad_start + timedelta(seconds=ad_duration)
        
        md_start = md_start + timedelta(seconds=md_duration)
        pdf.set_y(-15)
        pdf.set_font('Arial', 'I', 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 10, f'Page {i + 4}', 0, 0, 'C')
    
    return pdf.output(dest='S').encode('latin-1')
