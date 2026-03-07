from flask import Flask
from .auth_routes import login
from .page_routes import page, load_additional_files
from .vimshottari_routes import vimshottari
from .api_routes import api_live_planets, calculate_chakras_api, receive_gps
from .pdf_routes import download_full_cycle_pdf
from .article_routes import view_article

def register_routes(app):
    app.route('/', methods=['GET', 'POST'])(login)
    app.route('/page<int:page_number>', methods=['GET', 'POST'])(page)
    app.route('/infinite-vimshottari', methods=['GET', 'POST'])(vimshottari)
    app.route('/api/live-planets')(api_live_planets)
    app.route('/calculate-chakras', methods=['POST'])(calculate_chakras_api)
    app.route('/receive-gps', methods=['POST'])(receive_gps)
    app.route('/download-full-cycle-pdf', methods=['POST'])(download_full_cycle_pdf)
    app.route('/article/<filename>')(view_article)
