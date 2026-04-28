from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import psycopg2
import psycopg2.extras
from werkzeug.security import check_password_hash
import re
import html
import cari
from collections import defaultdict
from functools import reduce



app = Flask(__name__)
app.secret_key = 'ppp1234321'

hostname = 'localhost'
database = 'Db_pstdigital'
username = 'postgres'
pwd = 'Fathur27!!..))'
port = '5432'

conn = psycopg2.connect(dbname = database, user = username, password = pwd, host = hostname, port = port)

# Index / Halaman Utama
@app.route('/')
def main():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Ambil data publikasi dari database, urutkan berdasarkan tanggal inputan terbaru
    cursor.execute("SELECT * FROM publikasi ORDER BY Tanggal_Input DESC")
    data_publikasi = cursor.fetchall()

    return render_template('index.html', data_publikasi = data_publikasi)


# Dashboard User after input buku tamu
@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('dashboard_users.html')

# Pengisian Buku Tamu
@app.route('/buku_tamu', methods=['GET', 'POST'])
def buku_tamu(): 
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Periksa apakah permintaan POST "username", "password" dan "email" ada (formulir yang dikirimkan pengguna)
    if request.method == 'POST' and 'nama_lengkap' in request.form and 'nomor_hp' in request.form and 'jenis_kelamin' in request.form and 'tanggal_masuk' in request.form:
        # Buat variabel untuk akses mudah
        nama_lengkap = html.escape(request.form['nama_lengkap'])
        nomor_hp = html.escape(request.form['nomor_hp'])
        jenis_kelamin = html.escape(request.form['jenis_kelamin'])
        tanggal_masuk = html.escape(request.form['tanggal_masuk'])

        if not nama_lengkap or not nomor_hp or not jenis_kelamin or not tanggal_masuk:
            flash('Silakan isi semua kolom.')
        elif not re.match(r'[A-Za-z]', nama_lengkap):
            flash('Nama Lengkap hanya boleh berisi karakter dan angka!')
        elif not re.match(r'[0-9]', nomor_hp):
            flash('Isikan kolom email dengan benar!')
        else:
            cursor.execute("INSERT INTO tamu (nama_lengkap, nomor_handphone, jeniskelamin, tanggal_input) VALUES (%s, %s, %s, %s)", (nama_lengkap, nomor_hp, jenis_kelamin, tanggal_masuk))
            conn.commit()
            flash('Data berhasil disimpan.')
            return redirect(url_for('home'))
        
    # Tampilkan formulir pendaftaran dengan pesan (jika ada)
    return render_template('buku.html')

# Menu Perpustakaan
@app.route('/perpustakaan')
def perpustakaan():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Ambil data publikasi dari publikasi, urutkan berdasarkan tanggal inputan terbaru
    cursor.execute("SELECT * FROM publikasi ORDER BY Tanggal_Input DESC")
    data_publikasi = cursor.fetchall()

    # Ambil data publikasi dan feedback_book, lalu urutkan berdasarkan jumlah rating dari user dan lakukan operasi join tabel
    cursor.execute("""
        SELECT p.*, COALESCE(SUM(CAST(fb.tingkat_kepuasan AS INTEGER)), 0) as jumlah_rating
        FROM publikasi p
        LEFT JOIN feedback_book fb ON p.id_buku = fb.id_buku
        GROUP BY p.id_buku
        ORDER BY jumlah_rating DESC
    """)
    jumlah_rating = cursor.fetchall()

    return render_template('perpustakaan.html', data_publikasi = data_publikasi, jumlah_rating=jumlah_rating)

# Rincian Publikasi setelah memilih beberapa gambar pilihan di menu perpustakaan
@app.route('/publikasi_detail', methods=['GET', 'POST'])
def publikasi_detail():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    publikasi_id = request.args.get('id')
    if publikasi_id:
        cursor.execute("""SELECT p.*, COALESCE(SUM(CAST(fb.tingkat_kepuasan AS INTEGER)), 0) as jumlah_rating FROM publikasi p LEFT JOIN feedback_book fb ON p.id_buku = fb.id_buku WHERE p.id_buku = %s GROUP BY p.id_buku""", (publikasi_id,))
        publikasi = cursor.fetchone()
    else:
        publikasi = None
    return render_template('publikasi_detail.html', publikasi=publikasi)

# input pada form rating di rincian publikasi
@app.route('/input_rating', methods=['POST'])
def input_rating():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':
        ulasan = html.escape(request.form['ulasan'])
        rating = html.escape(request.form['rating'])
        id_buku = request.args.get('id')
        
        if id_buku:
            cursor.execute("SELECT * FROM publikasi WHERE id_buku = %s", (id_buku,))
            publikasi = cursor.fetchone()
        else:
            publikasi = None   
        
        if not ulasan or not rating or not id_buku or not publikasi:
            flash('Silakan isi semua kolom atau ID buku tidak valid.')
        else:
            cursor.execute("INSERT INTO feedback_book (ulasan, tingkat_kepuasan, id_buku) VALUES (%s, %s, %s)", (ulasan, rating, id_buku))
            conn.commit()
            flash('Data berhasil disimpan.')
            return redirect(url_for('publikasi_detail', id=id_buku))
    flash('Terjadi kesalahan dalam pemrosesan formulir.')
    return render_template('publikasi_detail.html', publikasi=publikasi)

# Rekomendasi Publikasi, setelah searchbar di Menu Perpustakaan
@app.route('/recommended', methods=['GET', 'POST'])
def rekomendasi():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cari.main(cursor)  # Panggil fungsi main dengan argumen cursor

    query = request.form.get('search')  # Ganti 'query' dengan nama form input yang sesuai
    
    query = cari.tokenisasi(query)

    # Contoh penggunaan fungsi similarity untuk mendapatkan rekomendasi buku
    cursor.execute("SELECT id_buku FROM publikasi")
    book_ids = [row[0] for row in cursor.fetchall()]  # Ganti dengan daftar ID buku yang ingin dibandingkan
    recommendations = []
    for book_id in book_ids:
        
        relevansi_dokumen = cari.intersection(
        [set(cari.postings[term].keys()) for term in query])

        sim = cari.similarity(query, book_id)
        recommendations.extend([(book_id, sim) for book_id in relevansi_dokumen])

    if recommendations:  # Jika rekomendasi berhasil didapatkan
        recommended_books = []
        for book_id, sim in recommendations:
            cursor.execute("SELECT image_url FROM publikasi WHERE id_buku = %s", (book_id,))
            book_image = cursor.fetchone()[0]
            recommended_books.append((book_id, sim, book_image))
            publikasi_id = request.args.get('id')
            if publikasi_id:
                cursor.execute("SELECT * FROM publikasi WHERE id_buku = %s", (publikasi_id,))
                publikasi = cursor.fetchone()
            else:
                publikasi = None
        return render_template('recommend.html', recommended_books=recommended_books, publikasi=publikasi)
    else:
        flash('Keyword yang anda masukkan tidak ditemukan, coba lagi!')
        return redirect(url_for('perpustakaan'))
    
# Menu Pembelian Data
@app.route('/pembelian_data')
def pembelian_data():
    return render_template('pembelian_data.html')

# Menu Chatbot
@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    return render_template('chatbot.html')

# Menu Konsultasi
@app.route('/konsultasi')
def konsultasi():
    return render_template('konsultasi.html')

# Form Konsultasi
@app.route('/form_konsultasi', methods=['GET', 'POST'])
def form_konsultasi():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':
        try:
            email = html.escape(request.form['email'])
            jenis_konsultasi = html.escape(request.form['jenis_konsultasi'])
            pesan_konsultasi = html.escape(request.form['pesan'])

            if not email or not jenis_konsultasi or not pesan_konsultasi:
                flash('Silakan isi semua kolom.')
            else:
                cursor.execute("INSERT INTO konsultasi (email, jenis_konsultasi, pesan_konsultasi) VALUES (%s, %s, %s)", (email, jenis_konsultasi, pesan_konsultasi))
                conn.commit()
                flash('Data berhasil disimpan.')
                return redirect(url_for('form_konsultasi'))

        except Exception as e:
            conn.rollback()  # Lakukan rollback jika terjadi kesalahan
            flash(f'Error: {str(e)}')

        finally:
            cursor.close()

    return render_template('form_konsultasi.html')


# Menu Feedback
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':
        umpan_balik = html.escape(request.form['umpan_balik'])
        tingkat_kepuasan = request.form['tingkat_kepuasan']

        if not umpan_balik or not tingkat_kepuasan:
            flash('Silakan isi semua kolom.')
        else:
            cursor.execute("INSERT INTO feedback (umpan_balik, tingkat_kepuasan) VALUES (%s, %s)", (umpan_balik, tingkat_kepuasan))
            conn.commit()
            flash('Data berhasil disimpan.')
            return redirect(url_for('feedback'))

    return render_template('feedback.html')

# Menu Logout (Keluar Aplikasi)
@app.route('/logout')
def logout():
    # Hapus data sesi, ini akan mengeluarkan pengguna
   session.pop('loggedin', None)
   session.pop('nama_lengkap', None)
   # Redirect ke halaman utama
   return redirect(url_for('main'))

# -------------------------- Admin Alur ------------------------- #

# dashboard_admin
@app.route('/dashboard_admin', methods=['GET', 'POST'])
def dashboard_admin():
    # Kondisi jika pengguna masuk
    if 'loggedin' in session:
        # Jika email dan password benar, lanjut ke dashboard admin
        return render_template('dashboard_admin.html', email=session['email'])
    # Jika email dan password salah, redirect di halaman login
    return redirect(url_for('login_admin'))

# login Admin
@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Periksa apakah permintaan POST "username", "password" dan "email" ada (formulir yang dikirimkan pengguna)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = html.escape(request.form['email'])
        password = html.escape(request.form['password'])
 
        # Periksa apakah akun menggunakan MySQL
        cursor.execute('SELECT * FROM admin WHERE email = %s', (email, ))
        # Ambil satu catatan dan kembalikan hasilnya
        account = cursor.fetchone()
        print(account)
        if account:
            password_rs = account['password']
            print(password_rs)
            # Jika akun ada di tabel pengguna di luar database
            if check_password_hash(password_rs, password):
                # Buat data sesi, kita dapat mengakses data ini di rute lain
                session['loggedin'] = True
                session['email'] = account['email']
                # Redirect ke home admin
                return redirect(url_for('dashboard_admin'))
            else:
                # Akun tidak ada atau nama pengguna/kata sandi salah
                flash('Email / Password terdapat kesalahan!')
        else:
            # Akun tidak ada atau nama pengguna/kata sandi salah
            flash('Email / Password terdapat kesalahan!')
    return render_template('login_admin.html')

# Grafik
@app.route('/jumlah_tamu', methods=['GET', 'POST'])
def jumlah_tamu():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Ambil data publikasi dari database, urutkan berdasarkan tanggal inputan terbaru
    cursor.execute("SELECT COUNT(Nama_Lengkap) FROM tamu")
    jumlah_tamu = cursor.fetchone()[0]
    return jumlah_tamu

# Daftar Tamu
@app.route('/daftar_tamu', methods=['GET', 'POST'])
def daftar_tamu():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Ambil data publikasi dari database, urutkan berdasarkan tanggal inputan terbaru
    cursor.execute("SELECT * FROM tamu ORDER BY id_tamu ASC")
    daftar_tamu = cursor.fetchall()
    return render_template('daftar_tamu.html', daftar_tamu = daftar_tamu)

# Edit Data Tamu
@app.route('/edit_tamu', methods=['GET', 'POST'])
def edit_tamu():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    id_tamu = request.args.get('id')
    if id_tamu:
        cursor.execute("SELECT * FROM tamu WHERE id_tamu = %s", (id_tamu,))
        tamu = cursor.fetchone()
    else:
        tamu = None
    return render_template('edit-tamu.html', tamu=tamu)

# Tambah Data Tamu
@app.route('/tambah_tamu', methods=['GET', 'POST'])
def tambah_tamu():
    return render_template('tambah-tamu.html')

@app.route('/grafik_data_tamu')
def grafik_data_tamu():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT jeniskelamin, COUNT(id_tamu) FROM tamu GROUP BY jeniskelamin")
    data_tamu = cursor.fetchall()

    labels = [item['jeniskelamin'] for item in data_tamu]
    values = [item['count'] for item in data_tamu]

    # Return data in the correct format
    return jsonify({'labels': labels, 'values': values})

@app.route('/tamu_detail')
def tamu_detail():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM tamu")
    tamu = cursor.fetchone()
    # ... (proses data tamu)
    return render_template('dashboard_admin.html', tamu=tamu)
    
# Daftar Publikasi
@app.route('/daftar_publikasi', methods=['GET', 'POST'])
def daftar_publikasi():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Ambil data publikasi dari database, urutkan berdasarkan tanggal inputan terbaru
    cursor.execute("SELECT * FROM publikasi ORDER BY id_buku ASC")
    daftar_publikasi = cursor.fetchall()
    return render_template('daftar_publikasi.html', daftar_publikasi = daftar_publikasi)

# Edit Publikasi
@app.route('/edit_publikasi', methods=['GET', 'POST'])
def edit_publikasi():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    id_publikasi = request.args.get('id')
    if id_publikasi:
        cursor.execute("SELECT * FROM publikasi WHERE id_buku = %s", (id_publikasi,))
        publikasi = cursor.fetchone()
    else:
        publikasi = None
    return render_template('edit-publikasi.html', publikasi=publikasi)

# Tambah Data Publikasi
@app.route('/tambah_publikasi', methods=['GET', 'POST'])
def tambah_publikasi():
    return render_template('tambah-publikasi.html')

# Daftar Konsultasi
@app.route('/daftar_konsultasi', methods=['GET', 'POST'])
def daftar_konsultasi():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Ambil data konsultasi dari database, urutkan berdasarkan tanggal inputan terbaru
    cursor.execute("SELECT * FROM konsultasi ORDER BY id_konsultasi ASC")
    daftar_konsultasi = cursor.fetchall()
    return render_template('daftar_konsultasi.html', daftar_konsultasi = daftar_konsultasi)

# Edit Konsultasi
@app.route('/edit_konsultasi', methods=['GET', 'POST'])
def edit_konsultasi():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    id_konsultasi = request.args.get('id')
    if id_konsultasi:
        cursor.execute("SELECT * FROM konsultasi WHERE id_konsultasi = %s", (id_konsultasi,))
        konsultasi = cursor.fetchone()
    else:
        konsultasi = None
    return render_template('edit-konsultasi.html', konsultasi=konsultasi)

# Tambah Data Konsultasi
@app.route('/tambah_konsultasi', methods=['GET', 'POST'])
def tambah_konsultasi():
    return render_template('tambah-konsultasi.html')

# Survey Kepuasan
@app.route('/survey_kepuasan', methods=['GET', 'POST'])
def survey_kepuasan():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Ambil data feedback dari database, urutkan berdasarkan tanggal inputan terbaru
    cursor.execute("SELECT * FROM feedback ORDER BY id_kepuasan ASC")
    survey_kepuasan = cursor.fetchall()
    return render_template('survey_kepuasan.html', survey_kepuasan = survey_kepuasan)

# Edit Survey Kepuasan
@app.route('/edit_survey', methods=['GET', 'POST'])
def edit_survey():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    id_survey = request.args.get('id')
    if id_survey:
        cursor.execute("SELECT * FROM feedback WHERE id_kepuasan = %s", (id_survey,))
        feedback = cursor.fetchone()
    else:
        feedback = None
    return render_template('edit-survey.html', feedback=feedback)

# Tambah Data Survey Kepuasan
@app.route('/tambah_survey', methods=['GET', 'POST'])
def tambah_survey():
    return render_template('tambah-survey.html')

@app.route('/grafik_data_survey_kepuasan')
def grafik_data_survey_kepuasan():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT tingkat_kepuasan, COUNT(id_kepuasan) FROM feedback GROUP BY tingkat_kepuasan")
    data_survey = cursor.fetchall()

    labels = [item['tingkat_kepuasan'] for item in data_survey]
    values = [item['count'] for item in data_survey]

    # Return data in the correct format
    return jsonify({'labels': labels, 'values': values})


# Main Flask
if __name__ == '__main__':
    app.run(debug=True)