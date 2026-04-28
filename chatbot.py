import random

# Daftar pertanyaan dan jawaban
qa_pairs = {
    "Apa itu perpustakaan?": "Perpustakaan adalah tempat di mana koleksi buku dan materi lainnya disimpan untuk penggunaan publik.",
    "Bagaimana cara mendaftar di perpustakaan?": "Anda dapat mendaftar di perpustakaan dengan mengunjungi lokasi perpustakaan dan mengisi formulir pendaftaran.",
    "Apakah perpustakaan menyediakan buku digital?": "Ya, sebagian besar perpustakaan modern menyediakan buku digital dalam berbagai format untuk dipinjam secara online.",
    "Berapa lama waktu peminjaman buku di perpustakaan?": "Waktu peminjaman buku di perpustakaan bervariasi tergantung pada kebijakan perpustakaan tertentu. Namun, umumnya peminjaman buku bisa berlangsung antara satu hingga empat minggu.",
    "Apakah perpustakaan memiliki ruang baca?": "Ya, perpustakaan biasanya menyediakan ruang baca bagi anggota untuk membaca buku atau bekerja dengan tenang.",
    "Apakah perpustakaan menyediakan acara dan kegiatan?": "Ya, perpustakaan sering mengadakan berbagai acara dan kegiatan seperti ceramah, lokakarya, dan klub buku untuk anggota dan masyarakat umum."
}

# Fungsi untuk menjalankan chatbot
def chatbot():
    print("Halo! Saya adalah chatbot perpustakaan. Anda dapat bertanya tentang perpustakaan kepada saya. Untuk keluar, ketik 'exit'.")
    while True:
        user_input = input("Anda: ")
        if user_input.lower() == 'exit':
            print("Terima kasih! Sampai jumpa lagi.")
            break
        elif user_input in qa_pairs:
            print(f"Bot: {qa_pairs[user_input]}")
        else:
            print("Bot: Maaf, saya tidak mengerti pertanyaan Anda. Silakan coba pertanyaan lain.")

# Menjalankan chatbot
chatbot()