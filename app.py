from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = Flask(__name__)
app.secret_key = 'khalil55T#*###'

# إعداد Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_INFO = {
    "type": os.getenv("TYPE"),
    "project_id": os.getenv("PROJECT_ID"),
    "private_key_id": os.getenv("PRIVATE_KEY_ID"),
    "private_key": os.getenv("PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.getenv("CLIENT_EMAIL"),
    "client_id": os.getenv("CLIENT_ID"),
    "auth_uri": os.getenv("AUTH_URI"),
    "token_uri": os.getenv("TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("UNIVERSE_DOMAIN")
}

credentials = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT_INFO, scopes=SCOPES)

service = build('sheets', 'v4', credentials=credentials)

# تحديد معرف Google Sheet
SPREADSHEET_ID = '1sBJC3IHopS-gzzaxHg-ffsk0LFdEYAAzMVVXPKS7w0A'

# تحميل بيانات الولايات والمكاتب من ملف واحد
with open('merged_bureaux_wilayas.json', 'r', encoding='utf-8') as f:
    wilayas_data = json.load(f)

# النصوص المترجمة
translations = {
    'ar': {
        'title': 'تسجيل الطلب',
        'nom_complet': 'الاسم الكامل',
        'telephone1': 'الهاتف 1',
        'telephone2': 'الهاتف 2',
        'delivery_type': 'نوع التوصيل',
        'home_delivery': 'توصيل إلى المنزل',
        'office_delivery': 'توصيل إلى المكتب',
        'wilaya': 'الولاية',
        'commune': 'البلدية',
        'adresse_complet': 'العنوان الكامل',
        'office': 'المكتب',
        'note': 'ملاحظات',
        'reserve': 'حجز',
        'confirmation_title': 'تم تسجيل طلبك بنجاح!',
        'order_details': 'تفاصيل الطلب',
        'back_home': 'العودة إلى الصفحة الرئيسية',
    },
    'fr': {
        'title': 'Enregistrement de la Commande',
        'nom_complet': 'Nom Complet',
        'telephone1': 'Téléphone 1',
        'telephone2': 'Téléphone 2',
        'delivery_type': 'Type de Livraison',
        'home_delivery': 'Livraison à Domicile',
        'office_delivery': 'Livraison au Bureau',
        'wilaya': 'Wilaya',
        'commune': 'Commune',
        'adresse_complet': 'Adresse Complète',
        'office': 'Bureau',
        'note': 'Remarques',
        'reserve': 'Réserver',
        'confirmation_title': 'Votre commande a été enregistrée avec succès!',
        'order_details': 'Détails de la Commande',
        'back_home': 'Retour à la Page d\'Accueil',
    },
    'en': {
        'title': 'Order Registration',
        'nom_complet': 'Full Name',
        'telephone1': 'Phone 1',
        'telephone2': 'Phone 2',
        'delivery_type': 'Delivery Type',
        'home_delivery': 'Home Delivery',
        'office_delivery': 'Office Delivery',
        'wilaya': 'Wilaya',
        'commune': 'Commune',
        'adresse_complet': 'Complete Address',
        'office': 'Office',
        'note': 'Notes',
        'reserve': 'Reserve',
        'confirmation_title': 'Your order has been successfully registered!',
        'order_details': 'Order Details',
        'back_home': 'Back to Home Page',
    }
}

# تحديد اللغة الافتراضية
app.config['DEFAULT_LANGUAGE'] = 'ar'

@app.route('/')
def form():
    language = session.get('language', app.config['DEFAULT_LANGUAGE'])
    return render_template('form.html', wilayas_data=wilayas_data, translations=translations[language])

@app.route('/set_language/<language>')
def set_language(language):
    if language in translations:
        session['language'] = language
    return redirect(request.referrer or url_for('form'))

@app.route('/get_communes')
def get_communes():
    wilaya = request.args.get('wilaya')
    selected_wilaya = next((w for w in wilayas_data if w['locationName'] == wilaya), None)
    if selected_wilaya:
        return jsonify(selected_wilaya.get('subLocations', []))
    return jsonify([])

@app.route('/get_offices')
def get_offices():
    wilaya = request.args.get('wilaya')
    selected_wilaya = next((w for w in wilayas_data if w['locationName'] == wilaya), None)
    if selected_wilaya and 'offices' in selected_wilaya:
        return jsonify(selected_wilaya['offices'])
    return jsonify([])

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # معالجة البيانات المرسلة من النموذج
        order_data = request.form.to_dict()
        session['order_data'] = order_data
        return redirect(url_for('confirmation'))
    except Exception as e:
        return str(e), 500

@app.route('/confirmation')
def confirmation():
    data = session.get('order_data', {})
    return render_template('confirmation.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
