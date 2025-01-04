from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

app = Flask(__name__)
app.secret_key = 'khalil55T#*###'

# إعداد Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

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
        return jsonify(selected_wilaya['subLocations'])
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
        data = request.form.to_dict()
        print("البيانات المستلمة:", data)

        delivery_type = data.get('delivery_type')
        if delivery_type == 'home':
            values = [
                [
                    data.get('nom_complet'),
                    data.get('telephone1'),
                    data.get('telephone2'),
                    '',
                    '',
                    '',
                    '',
                    '',
                    data.get('adresse_complet'),
                    '',
                    '',
                    data.get('wilaya'),
                    data.get('commune'),
                    '',
                    data.get('note'),
                ]
            ]
        elif delivery_type == 'office':
            values = [
                [
                    data.get('nom_complet'),
                    data.get('telephone1'),
                    data.get('telephone2'),
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    data.get('wilaya'),
                    data.get('office'),
                    '',
                    data.get('note'),
                    '',
                    '',
                    'OUI'
                ]
            ]
        else:
            return jsonify({"status": "error", "message": "نوع التوصيل غير معروف"}), 400

        sheet = service.spreadsheets()
        sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range="form responses!A1:R1",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": values}
        ).execute()

        session['order_data'] = data
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print("حدث خطأ:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/confirmation')
def confirmation():
    data = session.get('order_data', {})
    language = session.get('language', app.config['DEFAULT_LANGUAGE'])
    print("بيانات الجلسة:", data)
    return render_template('confirmation.html', data=data, translations=translations[language])

if __name__ == '__main__':
    app.run(debug=True)