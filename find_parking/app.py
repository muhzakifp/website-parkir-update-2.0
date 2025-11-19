from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'parking_secret_key_2025'

# Data simulasi slot parkir
parking_slots = {
    'car': {
        '1': {
            'status': 'accepted',
            'plate': 'R 7654 MK',
            'user_name': 'Mulyono',
            'vehicle_type': 'car',
            'manager_id': '3456',
            'driver_id': '54324',
            'phone': '081234567890'
        },
        '2': {'status': 'empty', 'plate': '', 'user_name': '', 'vehicle_type': '', 'manager_id': '', 'driver_id': '', 'phone': ''},
        '3': {'status': 'empty', 'plate': '', 'user_name': '', 'vehicle_type': '', 'manager_id': '', 'driver_id': '', 'phone': ''},
        '4': {'status': 'empty', 'plate': '', 'user_name': '', 'vehicle_type': '', 'manager_id': '', 'driver_id': '', 'phone': ''},
        '5': {'status': 'empty', 'plate': '', 'user_name': '', 'vehicle_type': '', 'manager_id': '', 'driver_id': '', 'phone': ''},
        '6': {'status': 'empty', 'plate': '', 'user_name': '', 'vehicle_type': '', 'manager_id': '', 'driver_id': '', 'phone': ''},
        '7': {'status': 'empty', 'plate': '', 'user_name': '', 'vehicle_type': '', 'manager_id': '', 'driver_id': '', 'phone': ''},
        '8': {'status': 'empty', 'plate': '', 'user_name': '', 'vehicle_type': '', 'manager_id': '', 'driver_id': '', 'phone': ''}
    },
    'motorcycle': {
        '1': {'status': 'empty', 'plate': '', 'user_name': '', 'vehicle_type': '', 'manager_id': '', 'driver_id': '', 'phone': ''},
        '2': {'status': 'empty', 'plate': '', 'user_name': '', 'vehicle_type': '', 'manager_id': '', 'driver_id': '', 'phone': ''},
        '3': {
            'status': 'accepted',
            'plate': 'R 8769 W',
            'user_name': 'Deddy Mulyadi',
            'vehicle_type': 'motorcycle',
            'manager_id': '4567',
            'driver_id': '67890',
            'phone': '089876543210'
        },
        '4': {'status': 'empty', 'plate': '', 'user_name': '', 'vehicle_type': '', 'manager_id': '', 'driver_id': '', 'phone': ''},
        '5': {'status': 'empty', 'plate': '', 'user_name': '', 'vehicle_type': '', 'manager_id': '', 'driver_id': '', 'phone': ''},
        '6': {'status': 'empty', 'plate': '', 'user_name': '', 'vehicle_type': '', 'manager_id': '', 'driver_id': '', 'phone': ''},
        '7': {'status': 'empty', 'plate': '', 'user_name': '', 'vehicle_type': '', 'manager_id': '', 'driver_id': '', 'phone': ''},
        '8': {'status': 'empty', 'plate': '', 'user_name': '', 'vehicle_type': '', 'manager_id': '', 'driver_id': '', 'phone': ''}
    }
}

def generate_id(phone_number):
    digits_only = ''.join(filter(str.isdigit, phone_number))
    return (digits_only[-5:] if len(digits_only) >= 5 else digits_only.zfill(5))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login/driver', methods=['GET', 'POST'])
def login_driver():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        plate = request.form.get('plate')
        vehicle_type = request.form.get('vehicle_type')
        if not all([name, phone, plate, vehicle_type]):
            return render_template('login_driver.html', error="Semua field wajib diisi!")
        session.update({
            'user_name': name,
            'phone': phone,
            'plate': plate,
            'vehicle_type': vehicle_type,
            'driver_id': generate_id(phone),
            'is_manager': False
        })
        return redirect(url_for('driver_menu'))
    return render_template('login_driver.html')

@app.route('/login/manager', methods=['GET', 'POST'])
def login_manager():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        if not name or not phone:
            return render_template('login_manager.html', error="Semua field wajib diisi!")
        session.update({
            'user_name': name,
            'phone': phone,
            'manager_id': generate_id(phone),
            'is_manager': True
        })
        return redirect(url_for('manager_menu'))
    return render_template('login_manager.html')

@app.route('/driver/menu')
def driver_menu():
    if not session.get('user_name') or session.get('is_manager'):
        return redirect(url_for('index'))
    return render_template('driver_menu.html',
                           user_name=session['user_name'],
                           driver_id=session['driver_id'],
                           plate=session['plate'])

@app.route('/manager/menu')
def manager_menu():
    if not session.get('user_name') or not session.get('is_manager'):
        return redirect(url_for('index'))
    return render_template('manager_menu.html',
                           user_name=session['user_name'],
                           manager_id=session['manager_id'])

@app.route('/parking/car')
def car_parking():
    if 'user_name' not in session:
        return redirect(url_for('index'))
    slots = parking_slots['car']
    total = len(slots)
    used = sum(1 for s in slots.values() if s['status'] == 'accepted')
    empty = total - used
    notification = session.pop('notification', None)
    return render_template('car_parking.html',
                           slots=slots,
                           total_slots=total,
                           used_slots=used,
                           empty_slots=empty,
                           is_manager=session.get('is_manager', False),
                           notification=notification)

@app.route('/parking/motorcycle')
def motorcycle_parking():
    if 'user_name' not in session:
        return redirect(url_for('index'))
    slots = parking_slots['motorcycle']
    total = len(slots)
    used = sum(1 for s in slots.values() if s['status'] == 'accepted')
    empty = total - used
    notification = session.pop('notification', None)
    return render_template('motorcycle_parking.html',
                           slots=slots,
                           total_slots=total,
                           used_slots=used,
                           empty_slots=empty,
                           is_manager=session.get('is_manager', False),
                           notification=notification)

@app.route('/use_slot/<vehicle_type>/<slot_id>')
def use_slot(vehicle_type, slot_id):
    if 'user_name' not in session:
        return redirect(url_for('index'))
    if vehicle_type not in parking_slots or slot_id not in parking_slots[vehicle_type]:
        return "Slot tidak ditemukan", 404

    # Cek apakah driver sudah punya slot aktif
    if not session.get('is_manager'):
        for v_type, slots in parking_slots.items():
            for s_id, s_data in slots.items():
                if s_data.get('driver_id') == session.get('driver_id') and s_data['status'] in ['pending', 'accepted']:
                    session['notification'] = "Anda sudah memiliki slot parkir aktif."
                    return redirect(url_for(f'{vehicle_type}_parking'))

    slot = parking_slots[vehicle_type][slot_id]

    if session.get('is_manager'):
        if slot['status'] == 'pending':
            slot.update({'status': 'accepted', 'manager_id': session.get('manager_id', 'MGR001')})
        elif slot['status'] == 'accepted':
            return redirect(url_for('slot_detail', vehicle_type=vehicle_type, slot_id=slot_id))
    else:
        if slot['status'] == 'empty':
            slot.update({
                'status': 'pending',
                'plate': session['plate'],
                'user_name': session['user_name'],
                'vehicle_type': session['vehicle_type'],
                'driver_id': session['driver_id'],
                'phone': session.get('phone', '')  # ✅ Simpan nomor HP
            })
        elif slot['status'] == 'accepted':
            return redirect(url_for('slot_detail', vehicle_type=vehicle_type, slot_id=slot_id))

    return redirect(url_for('car_parking') if vehicle_type == 'car' else url_for('motorcycle_parking'))

@app.route('/slot_detail/<vehicle_type>/<slot_id>')
def slot_detail(vehicle_type, slot_id):
    if vehicle_type not in parking_slots or slot_id not in parking_slots[vehicle_type]:
        return "Slot tidak ditemukan", 404
    slot = parking_slots[vehicle_type][slot_id]
    
    if slot['status'] != 'accepted':
        return "Slot tidak valid.", 400

    # Ambil nomor HP (hanya untuk manager)
    driver_phone = slot.get('phone', '') if session.get('is_manager') else ''

    return render_template('popup_info.html',
                           vehicle_type=vehicle_type,
                           slot_id=slot_id,
                           slot_data=slot,
                           is_manager=session.get('is_manager', False),
                           driver_phone=driver_phone)

@app.route('/edit_slot/<vehicle_type>', methods=['GET', 'POST'])
def edit_slot(vehicle_type):
    if not session.get('is_manager'):
        return redirect(url_for('index'))

    if vehicle_type not in parking_slots:
        return "Jenis kendaraan tidak valid", 400

    if request.method == 'POST':
        try:
            new_count = int(request.form.get('slot_count', 8))
            if new_count < 1:
                new_count = 8
            current_slots = parking_slots[vehicle_type]
            current_count = len(current_slots)

            # Tambah slot
            for i in range(current_count + 1, new_count + 1):
                current_slots[str(i)] = {
                    'status': 'empty',
                    'plate': '',
                    'user_name': '',
                    'vehicle_type': vehicle_type,
                    'manager_id': '',
                    'driver_id': '',
                    'phone': ''
                }
            # Kurangi slot
            for i in range(new_count + 1, current_count + 1):
                if str(i) in current_slots:
                    del current_slots[str(i)]

            return redirect(url_for('car_parking') if vehicle_type == 'car' else url_for('motorcycle_parking'))
        except (ValueError, TypeError):
            pass

    total = len(parking_slots[vehicle_type])
    return render_template('edit_slot.html',
                           vehicle_type=vehicle_type,
                           total_slots=total)

@app.route('/back_to_menu')
def back_to_menu():
    return redirect(url_for('manager_menu') if session.get('is_manager') else url_for('driver_menu'))

@app.route('/exit')
def exit_app():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)