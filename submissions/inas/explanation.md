Vidio Simulasi hasil code: https://drive.google.com/file/d/1_Wg_xNusVW3OjkoukVI2iGbH3heFAZXp/view?usp=sharing 

1. Apa pola terbang yang dibuat? Deskripsikan rutenya.

Pola terbang yang saya buat adalah horizontal lawnmower pattern (pola sapuan bolak-balik horizontal) yang umum digunakan pada drone pertanian untuk penyemprotan atau pemupukan lahan.Lahan yang digunakan berukuran 40 meter (panjang) × 10 meter (lebar) dengan jarak antar baris (spacing) sebesar 4 meter dan ketinggian terbang konstan 3 meter. Rute penerbangan dilakukan sebagai berikut:
Drone takeoff hingga 3 meter.
Baris 1: Drone terbang lurus ke arah Timur sejauh 40 meter.
Drone hover selama 3 detik.
Drone bergeser ke arah Selatan sejauh 4 meter.
Hover kembali 3 detik.
Baris 2: Drone terbang kembali ke arah Barat sejauh 40 meter.
Hover 3 detik.
Geser lagi ke Selatan 4 meter.
Baris 3: Drone terbang ke arah Timur kembali.
Pola ini membentuk lintasan zigzag horizontal yang rapi, sehingga seluruh area lahan tercakup tanpa ada bagian yang terlewat. Metode ini efisien karena tidak memerlukan drone kembali ke titik awal setiap baris, melainkan langsung melanjutkan dari posisi terakhir.

2. Fungsi-fungsi yang dibuat dan kegunaannya

Dalam program ini terdapat tiga fungsi utama:
a. arm_and_takeoff(target_altitude)
Fungsi ini digunakan untuk:
Mengecek apakah drone siap untuk di-arm (is_armable), Mengubah mode ke GUIDED, Melakukan proses arming motor, Mengontrol takeoff hingga mencapai ketinggian target (3 meter).Fungsi ini memastikan bahwa drone benar-benar stabil sebelum memulai misi penyemprotan.

b. send_velocity(vx, vy, vz, duration)

Fungsi ini digunakan untuk menggerakkan drone menggunakan kontrol kecepatan (velocity control).
Parameter:
vx → kecepatan arah Timur/Barat
vy → kecepatan arah Utara/Selatan
vz → kecepatan vertikal
duration → lama waktu pergerakan
Fungsi ini mengirim perintah MAVLink setiap 0.1 detik (10 Hz) agar gerakan drone halus dan tidak patah-patah. Ini penting untuk menghindari gerakan zigzag yang tidak diinginkan.

c. spraying_mission()
Fungsi ini merupakan inti dari program.
Fungsi ini:
Mengatur parameter lahan (panjang, lebar, spacing),Mengatur waktu tempuh tiap baris,Mengatur arah bolak-balik (Timur ↔ Barat), Menambahkan hover 3 detik di setiap belokan, Mengatur perpindahan antar baris
Di dalam fungsi ini juga digunakan variabel direction yang nilainya berubah-ubah (1 atau -1) untuk mengatur arah horizontal.

3. Mode yang digunakan dan situasinya

Dalam program ini digunakan beberapa mode penerbangan:

a. GUIDED
Digunakan saat:
Setelah drone arm, Selama menjalankan misi spraying
Mode GUIDED memungkinkan drone menerima perintah langsung dari script Python (velocity control).

b. LOITER
Digunakan setelah misi selesai.
Fungsinya:
Membuat drone diam dan mempertahankan posisi, Memberi jeda sebelum proses landing

c. LAND
Digunakan pada tahap akhir misi.
Mode ini membuat drone:
Turun secara otomatis, Mematikan motor setelah menyentuh tanah

4. Tantangan yang ditemui dan cara mengatasinya
Selama pembuatan program, terdapat beberapa tantangan:
a. Drone bergerak zigzag saat ke arah Barat
Masalah:
Saat berpindah arah, drone tidak lurus dan terlihat sedikit menyamping.
Penyebab:
Command velocity tidak dikirim cukup sering sehingga autopilot kehilangan referensi.
Solusi:
Saya mengatur pengiriman perintah MAVLink setiap 0.1 detik (10 Hz) agar kontrol lebih stabil dan gerakan menjadi lurus.

b. Ketidaksesuaian arah koordinat (Timur/Barat)
Masalah:
Arah pergerakan kadang tidak sesuai dengan yang diharapkan.
Solusi:
Memastikan penggunaan frame:
MAV_FRAME_LOCAL_NED
Dengan pemahaman:

X = Timur (+)

Y = Utara (+)

Z = Down (+)
Dengan memahami sistem koordinat ini, arah bisa dikontrol dengan benar.

c. Link timeout / heartbeat error
Masalah:
Script kadang tidak terhubung ke SITL.
Solusi: Memastikan:
SITL sudah running
Port koneksi benar (tcp:127.0.0.1:5762)
Mission Planner tidak memblokir koneksi

5. Pengembangan yang ingin dilakukan
Jika ada waktu lebih, beberapa pengembangan yang ingin saya lakukan adalah:

a. Menambahkan kontrol yaw otomatis
Agar drone selalu menghadap ke arah gerak, sehingga lebih realistis seperti drone spraying sungguhan.

b. Menggunakan waypoint berbasis GPS
Saat ini menggunakan velocity control (relative movement). Akan lebih akurat jika menggunakan global waypoint.

c. Menambahkan variasi ketinggian
Misalnya:
Baris ganjil di 3 meter
Baris genap di 2.8 meter
Untuk mensimulasikan overlap semprotan.

d. Simulasi tangki pupuk
Menambahkan variabel volume cairan yang berkurang setiap meter, sehingga lebih realistis sebagai drone pertanian.

Kesimpulan
Program ini berhasil mensimulasikan pola penyemprotan lahan menggunakan metode horizontal lawnmower dengan pergerakan halus dan sistematis. Dengan memanfaatkan mode GUIDED dan kontrol velocity berbasis MAVLink, drone dapat bergerak sesuai pola yang dirancang serta melakukan hover pada setiap pergantian baris. Simulasi ini merepresentasikan konsep dasar sistem autonomous spraying pada drone pertanian modern.